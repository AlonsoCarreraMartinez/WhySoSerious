import os
import argparse # Read command line arguments.
import numpy as np # Math operations.
import pandas as pd # Load CSV datasets.
import torch # PyTorch.
from datasets import Dataset # Convert pandas data to a Hugging Face dataset format.
from transformers import ( # Hugging Face toolkit for BERT.
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
import evaluate
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datasets import DatasetDict # Multiple splits in one object.

################################################################################################
# The purpose of this class is fine-tune a BERT model with Hugging Face to predict three scores#
################################################################################################

# pip install -r requirements.txt

# Defines all the options you can pass when running your training script.
def parse_args():
    parser = argparse.ArgumentParser(description="Train BERT regression (3 outputs: politeness, sarcasm, toxicity).")
    parser.add_argument("--csv_path", type=str, default="data/wss_train.csv",
                        help="Path to training CSV with columns: text, politeness, sarcasm, toxicity.")
    parser.add_argument("--model_name", type=str, default="distilbert-base-uncased",
                    help="HF model checkpoint to fine-tune (English DistilBERT model).")
    parser.add_argument("--output_dir", type=str, default="models/hf_bert_reg",
                        help="Where to save the trained model.")
    parser.add_argument("--test_size", type=float, default=0.2, help="Fraction for test split.")
    parser.add_argument("--max_length", type=int, default=256, help="Max sequence length for tokenizer.")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate.")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs.")
    parser.add_argument("--train_bs", type=int, default=16, help="Per-device train batch size.")
    parser.add_argument("--eval_bs", type=int, default=32, help="Per-device eval batch size.")
    parser.add_argument("--fp16", action="store_true", help="Use mixed precision (FP16) if supported.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser.parse_args()

# Load and clean dataset.
def load_dataframe(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required = ["text", "politeness", "sarcasm", "toxicity"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in {csv_path}")
    df = df.dropna(subset=required)
    df["text"] = df["text"].astype(str)
    for col in ["politeness", "sarcasm", "toxicity"]:
        df[col] = df[col].astype(float).clip(0.0, 10.0)
    return df

# Convert pandas data to a Hugging Face dataset format and split it in train and test.
def make_hf_dataset(df: pd.DataFrame, test_size: float, seed: int) -> Dataset:
    ds = Dataset.from_pandas(
        df[["text", "politeness", "sarcasm", "toxicity"]],
        preserve_index=False
    )
    if len(df) < 20: 
        print(f"[INFO] Dataset too small ({len(df)} samples). Using all data for both train and test.")
        ds = DatasetDict({"train": ds, "test": ds})
    else:
        ds = ds.train_test_split(test_size=test_size, seed=seed)
    return ds

# Convert text into numbers so BERT can understand it.
def tokenize_function(batch, tokenizer, max_length):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=max_length
    )

# python train_bert.py --csv_path data/wss_train.csv --model_name distilbert-base-uncased --output_dir models/hf_bert_reg --epochs 1 --train_bs 4 --eval_bs 8
def main():

    args = parse_args()
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    df = load_dataframe(args.csv_path)
    ds = make_hf_dataset(df, args.test_size, args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    ds = ds.map( # Tokenize dataset
        lambda batch: tokenize_function(batch, tokenizer, args.max_length),
        batched=True
    )

    def pack_labels(example): # Group the three target scores into one label vector for training.
        example["labels"] = np.array([
            example["politeness"],
            example["sarcasm"],
            example["toxicity"]
        ], dtype=np.float32)
        return example

    ds = ds.map(pack_labels)

    keep_cols = ["input_ids", "attention_mask", "labels"] # Remove original scalar columns to avoid Trainer confusion.
    train_cols = [c for c in ds["train"].column_names if c in keep_cols]
    test_cols = [c for c in ds["test"].column_names if c in keep_cols]
    ds["train"].set_format(type="torch", columns=train_cols)
    ds["test"].set_format(type="torch", columns=test_cols)

    model = AutoModelForSequenceClassification.from_pretrained(# Load BERT and adapt it for three output.
        args.model_name,
        num_labels=3,
        problem_type="regression"
    )

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer) # Pad batches to the same length during training.

    def compute_metrics(eval_pred): # Compute regression metrics (MAE, RMSE, R2)

        logits, labels = eval_pred
        preds = np.asarray(logits)
        labels = np.asarray(labels)
        preds = np.clip(preds, 0.0, 10.0)

        mae_p = mean_absolute_error(labels[:, 0], preds[:, 0])
        mae_s = mean_absolute_error(labels[:, 1], preds[:, 1])
        mae_t = mean_absolute_error(labels[:, 2], preds[:, 2])

        mse_p = mean_squared_error(labels[:, 0], preds[:, 0])
        mse_s = mean_squared_error(labels[:, 1], preds[:, 1])
        mse_t = mean_squared_error(labels[:, 2], preds[:, 2])

        rmse_p = float(np.sqrt(mse_p))
        rmse_s = float(np.sqrt(mse_s))
        rmse_t = float(np.sqrt(mse_t))

        r2_p = r2_score(labels[:, 0], preds[:, 0])
        r2_s = r2_score(labels[:, 1], preds[:, 1])
        r2_t = r2_score(labels[:, 2], preds[:, 2])

        mae_macro = float(np.mean([mae_p, mae_s, mae_t]))
        rmse_macro = float(np.mean([rmse_p, rmse_s, rmse_t]))
        r2_macro = float(np.mean([r2_p, r2_s, r2_t]))

        return {
            "mae_macro": mae_macro,
            "rmse_macro": rmse_macro,
            "r2_macro": r2_macro,
            "mae_politeness": mae_p,
            "mae_sarcasm": mae_s,
            "mae_toxicity": mae_t,
            "rmse_politeness": rmse_p,
            "rmse_sarcasm": rmse_s,
            "rmse_toxicity": rmse_t,
            "r2_politeness": r2_p,
            "r2_sarcasm": r2_s,
            "r2_toxicity": r2_t,
        }

    training_args = TrainingArguments( # Training args 
        output_dir=args.output_dir,
        learning_rate=args.lr,
        per_device_train_batch_size=args.train_bs,
        per_device_eval_batch_size=args.eval_bs,
        num_train_epochs=args.epochs,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="mae_macro",
        greater_is_better=False,
        fp16=args.fp16,
        logging_steps=50,
        report_to="none",  
        seed=args.seed,
        remove_unused_columns=False,
    )
    
    trainer = Trainer( # Trainer
        model=model,
        args=training_args,
        tokenizer=tokenizer,
        train_dataset=ds["train"],
        eval_dataset=ds["test"],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train() # Train

    # Save final model and tokenizer
    os.makedirs(args.output_dir, exist_ok=True)
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    print(f"Model saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
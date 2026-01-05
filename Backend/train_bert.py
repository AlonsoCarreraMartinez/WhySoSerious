import os
import argparse # Read command line arguments.
from transformers import ( # Hugging Face toolkit.
    AutoTokenizer,
    AutoModelForSequenceClassification
)

#############################################################################
# The purpose of this script is to dowload and save the 3 Specialist Models.#
#############################################################################

# pip install -r requirements.txt


def parse_args():
    parser = argparse.ArgumentParser(description="Download and Save Specialist Models (Toxicity, Sarcasm, Politeness).")
    
    
    parser.add_argument("--output_dir", type=str, default="models/hf_bert_reg",
                        help="Root directory where the models will be saved locally.")
    
    return parser.parse_args()

# Helper function to download from Hugging Face and save to disk.
def download_and_save_model(model_name, base_output_dir, subfolder_name):
    """
    Downloads the model and tokenizer and saves them to output_dir/subfolder_name.
    """
    print(f"Downloading model: {model_name}...")
    
    try:
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        save_path = os.path.join(base_output_dir, subfolder_name)
        os.makedirs(save_path, exist_ok=True)
        
        print(f"Saving to: {save_path}")
        tokenizer.save_pretrained(save_path)
        model.save_pretrained(save_path)
        
    except Exception as e:
        print(f"Error handling {model_name}: {e}")

def main():
    args = parse_args()
    
    # Configuration of the 3 Expert Models to replace the old single BERT.
    # Toxicity: unitary/unbiased-toxic-roberta
    # Sarcasm: cardiffnlp/twitter-roberta-base-irony
    # Politeness (Sentiment): cardiffnlp/twitter-roberta-base-sentiment-latest
    models_config = {
        "toxicity": "unitary/unbiased-toxic-roberta",
        "sarcasm": "cardiffnlp/twitter-roberta-base-irony",
        "politeness": "cardiffnlp/twitter-roberta-base-sentiment-latest"
    }

    print(f"--- STARTING MODEL DOWNLOAD PROCESS ---")
    print(f"Target Directory: {args.output_dir}")
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    for key, model_name in models_config.items():
        print(f"\n--- Processing {key.upper()} Model ---")
        download_and_save_model(model_name, args.output_dir, key)

    print(f"\n--- SUCCESS ---")
    print(f"All models have been saved to '{args.output_dir}'.")
    print("You can now run your backend/prediction scripts using these local models.")

if __name__ == "__main__":
    main()
import os
import argparse 
from transformers import ( 
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

def parse_args():
    parser = argparse.ArgumentParser(description="Download and Save MBI Specialist Models.")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.dirname(current_dir)
    default_output = os.path.join(server_dir, "weights", "models", "hf_bert_reg")
    
    parser.add_argument("--output_dir", type=str, default=default_output,
                        help="Root directory where the models will be saved locally.")
    
    return parser.parse_args()

def download_and_save_model(model_name, base_output_dir, subfolder_name):
    print(f"Downloading model: {model_name}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        save_path = os.path.join(base_output_dir, subfolder_name)
        os.makedirs(save_path, exist_ok=True)
        
        tokenizer.save_pretrained(save_path)
        model.save_pretrained(save_path)
        print(f"Successfully saved to: {save_path}")
    except Exception as e:
        print(f"Error handling {model_name}: {e}")


def main():
    args = parse_args()
    
    models_config = {
        "cynicism": "unitary/unbiased-toxic-roberta",
        "exhaustion": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "inefficacy": "facebook/bart-large-mnli" 
    }

    print(f"STARTING MBI MODEL DOWNLOAD")
    os.makedirs(args.output_dir, exist_ok=True)
    
    for key, model_name in models_config.items():
        print(f"\nProcessing {key.upper()}")
        download_and_save_model(model_name, args.output_dir, key)

    print(f"\nAll MBI models ready in {args.output_dir}")

if __name__ == "__main__":
    main()
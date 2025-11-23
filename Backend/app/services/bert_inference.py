import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


MODEL_DIR = "models/hf_bert_reg"
MAX_LENGTH = 256

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR) # Load the tokenizer that converts text into numerical tokens.
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR) # Load the fine-tuned BERT model saved after training.
model.eval() # Set the model to evaluation mode

# python bert_inference.py
def analyze_text(text: str) -> dict:
    
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=MAX_LENGTH,
    )

    with torch.no_grad():  # Get predictions
        outputs = model(**inputs)
        logits = outputs.logits.squeeze(0).cpu().numpy()

    scores = np.clip(logits, 0.0, 10.0)

    return {
        "politeness": float(round(scores[0], 2)),
        "sarcasm": float(round(scores[1], 2)),
        "toxicity": float(round(scores[2], 2)),
    }

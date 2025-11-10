import torch # PyTorch
import numpy as np # Math operations.
import requests  # Ollama
import json 
from transformers import AutoTokenizer, AutoModelForSequenceClassification # Hugging Face toolkit for BERT.

MODEL_DIR = "models/hf_bert_reg"
MAX_LENGTH = 256
OLLAMA_MODEL = "llama3:instruct"

# Calls local Ollama model to translate Spanish text to English.
def translate_to_english(text: str) -> str:
    prompt = f"Translate this text from Spanish to English, keeping tone and meaning:\n\n{text}"
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt},
            stream=True,  
            timeout=30
        )
        response.raise_for_status()
        translated = ""
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                try:
                    data = json.loads(line)
                    if "response" in data:
                        translated += data["response"]
                except json.JSONDecodeError:
                    pass  

        return translated.strip() or text
    except Exception as e:
        print(f"[WARN] Translation failed ({e}), using original text.")
        return text


tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR) # Load the tokenizer that converts text into numerical tokens.
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR) # Load the fine-tuned BERT model saved after training.
model.eval() # Set the model to evaluation mode

print("Type a sentence to analyze or 'exit' to quit.\n")

# python predict_bert.py
while True:
    text = input("TEXT: ")

    if text.lower().strip() == "exit":
        break

    translated = translate_to_english(text) 

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=MAX_LENGTH) # Tokenize the input text

    with torch.no_grad(): # Get predictions
        outputs = model(**inputs)
        logits = outputs.logits.squeeze(0).cpu().numpy()

    scores = np.clip(logits, 0.0, 10.0)

    print({ # Results
        "politeness": round(float(scores[0]), 2),
        "sarcasm": round(float(scores[1]), 2),
        "toxicity": round(float(scores[2]), 2),
    })
    print()  
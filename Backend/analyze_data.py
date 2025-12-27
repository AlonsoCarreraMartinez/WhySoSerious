import os
import numpy as np
import torch
from pymongo import MongoClient
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSequenceClassification


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whysoserious_db"
COLLECTION_NAME = "messages"

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "hf_bert_reg")
MAX_LENGTH = 256

def analyze_message_batch():
    if not MONGO_URI:
        print("ERROR: Missing MONGO_URI in .env")
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Find unanalyzed messages looking for documents where 'analyzed' is False or does not exist.
    query = {"$or": [{"analyzed": False}, {"analyzed": {"$exists": False}}]}
    pending = list(collection.find(query))

    if not pending:
        print("All up to date. No new messages found.")
        return

    print(f"Analyzing {len(pending)} messages...")

    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
        model.eval()
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    count = 0
    for msg in pending:
        text = msg.get("content", "")
        if not text: continue

        try:
            # AI inference
            inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=MAX_LENGTH)
            with torch.no_grad():
                outputs = model(**inputs)
                scores = np.clip(outputs.logits.squeeze(0).cpu().numpy(), 0.0, 10.0)

            results = {
                "politeness": float(round(scores[0], 2)),
                "sarcasm": float(round(scores[1], 2)),
                "toxicity": float(round(scores[2], 2))
            }

            # Save to Database
            collection.update_one(
                {"_id": msg["_id"]},
                {"$set": {"analyzed": True, "scores": results}}
            )
            print(f"({count+1}/{len(pending)}) Processed.")
            count += 1
        except Exception as e:
            print(f"Error processing message: {e}")

    print(f"Finished. {count} messages updated.")

if __name__ == "__main__":
    analyze_message_batch()
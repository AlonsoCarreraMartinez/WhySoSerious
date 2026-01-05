import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.services.bert_inference import BertPredictor

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "whysoserious_db"
COLLECTION_NAME = "messages"

def analyze_message_batch():
    if not MONGO_URI:
        print("ERROR: Missing MONGO_URI in .env")
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    query = {"$or": [{"analyzed": False}, {"analyzed": {"$exists": False}}]}
    pending = list(collection.find(query))

    if not pending:
        print("All up to date. No new messages found.")
        return

    print(f"Analyzing {len(pending)} messages using Hybrid AI...")

    try:
        predictor = BertPredictor()
    except Exception as e:
        print(f"Error initializing AI: {e}")
        return

    count = 0
    for msg in pending:
        text = msg.get("content", "")
        if not text: 
            collection.update_one(
                {"_id": msg["_id"]},
                {"$set": {"analyzed": True, "scores": {"politeness": 0.0, "sarcasm": 0.0, "toxicity": 0.0}}}
            )
            continue

        try:
            results = predictor.predict(text)

            collection.update_one(
                {"_id": msg["_id"]},
                {"$set": {"analyzed": True, "scores": results}}
            )
            print(f"({count+1}/{len(pending)}) Processed.")
            count += 1
        except Exception as e:
            print(f"Error processing message {msg['_id']}: {e}")

    print(f"Finished. {count} messages updated.")

if __name__ == "__main__":
    analyze_message_batch()
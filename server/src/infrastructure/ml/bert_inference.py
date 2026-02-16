import os
import numpy as np
from transformers import pipeline

class BertPredictor:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(current_dir)
        backend_dir = os.path.dirname(app_dir)
        
        model_dir = os.path.join(backend_dir, "models", "hf_bert_reg")

        print(f"LOADING MODELS FROM: {model_dir}")
        
        try:
            toxic_path = os.path.join(model_dir, "toxicity")
            self.toxic_pipe = pipeline("text-classification", model=toxic_path, tokenizer=toxic_path, top_k=None)

            sarcasm_path = os.path.join(model_dir, "sarcasm")
            self.sarcasm_pipe = pipeline("text-classification", model=sarcasm_path, tokenizer=sarcasm_path, top_k=None)

            politeness_path = os.path.join(model_dir, "politeness")
            self.sentiment_pipe = pipeline("sentiment-analysis", model=politeness_path, tokenizer=politeness_path, top_k=None)
            
            print("MODELS LOADED SUCCESSFULLY")
            
        except Exception as e:
            print(f"CRITICAL ERROR LOADING MODELS: {e}")
            self.toxic_pipe = None

    def predict(self, text):
        if not text or not self.toxic_pipe:
            return {"politeness": 0.0, "sarcasm": 0.0, "toxicity": 0.0}

        try:
            text_lower = text.lower()
            word_count = len(text.split())

            toxic_results = self.toxic_pipe(text)[0]
            toxic_scores = []
            target_labels = ['toxicity', 'severe_toxicity', 'insult', 'threat', 'obscene', 'identity_attack']
            for res in toxic_results:
                if res['label'] in target_labels:
                    toxic_scores.append(res['score'])
            toxic_score = max(toxic_scores) if toxic_scores else 0.0
            
            sarcasm_results = self.sarcasm_pipe(text)[0]
            sarcasm_score = 0.0
            for res in sarcasm_results:
                if res['label'] == 'irony':
                    sarcasm_score = res['score']

            sent_results = self.sentiment_pipe(text)[0]
            top_sentiment = max(sent_results, key=lambda x: x['score'])
            label = top_sentiment['label']
            score = top_sentiment['score']

            politeness_score = 5.0
            if label == 'positive':
                politeness_score = 5.0 + (score * 5.0)
            elif label == 'neutral':
                politeness_score = 5.0
            elif label == 'negative':
                politeness_score = 5.0 - (score * 5.0)

            if word_count < 4 and toxic_score < 0.3:
                sarcasm_score *= 0.2

            status_keywords = ["successfully", "fixed", "resolved", "completed", "scheduled", "maintenance", "updated", "deployed"]
            is_status_msg = any(word in text_lower for word in status_keywords)
            
            if is_status_msg and toxic_score < 0.3:
                sarcasm_score *= 0.2 

            condescending_phrases = ["maybe you should", "i guess i have to", "clearly you didn't", "obvious", "explain everything"]
            if any(phrase in text_lower for phrase in condescending_phrases):
                politeness_score = min(politeness_score, 3.0)

            if sarcasm_score * 10.0 > 7.5 and politeness_score > 6.0:
                 politeness_score = max(0.0, 10.0 - politeness_score)

            polite_keywords = ["please", "thank", "appreciate", "kindly", "excuse me", "grateful"]
            if any(word in text_lower for word in polite_keywords):
                if sarcasm_score * 10.0 < 7.5:
                    if politeness_score < 7.0: politeness_score = 7.5
                    else: politeness_score = min(10.0, politeness_score + 1.0)

            if politeness_score < 3.5 and toxic_score < 0.2:
                toxic_score += 0.25 

            return {
                "politeness": round(float(np.clip(politeness_score, 0.0, 10.0)), 2),
                "sarcasm": round(float(np.clip(sarcasm_score * 10.0, 0.0, 10.0)), 2),
                "toxicity": round(float(np.clip(toxic_score * 10.0, 0.0, 10.0)), 2)
            }

        except Exception as e:
            print(f"PREDICTION ERROR: {e}")
            return {"politeness": 0.0, "sarcasm": 0.0, "toxicity": 0.0}
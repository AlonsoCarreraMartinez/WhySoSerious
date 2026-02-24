import os
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from pathlib import Path

class BertPredictor:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        infra_dir = os.path.dirname(current_dir)
        src_dir = os.path.dirname(infra_dir)
        backend_dir = os.path.dirname(src_dir)
        
        weights_base = Path(backend_dir) / "weights" / "models" / "hf_bert_reg"
        
        try:
            print(f"LOADING MODELS FROM: {weights_base}")

            self.toxic_pipe = self._load_local_pipeline(weights_base / "toxicity", "text-classification")
            self.sarcasm_pipe = self._load_local_pipeline(weights_base / "sarcasm", "text-classification")
            self.sentiment_pipe = self._load_local_pipeline(weights_base / "politeness", "sentiment-analysis")
            
            print("MODELS LOADED SUCCESSFULLY")
            
        except Exception as e:
            print(f"CRITICAL ERROR LOADING MODELS: {e}")
            self.toxic_pipe = None

    def _load_local_pipeline(self, path, task):
        model_path = os.path.abspath(str(path))
        model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        return pipeline(task, model=model, tokenizer=tokenizer)

    def _get_results_safely(self, pipe, text):
        raw = pipe(text, top_k=None)
        if isinstance(raw, list) and len(raw) > 0:
            return raw[0] if isinstance(raw[0], list) else raw
        return []

    def predict(self, text):
        if not text or not self.toxic_pipe:
            return {"politeness": 0.0, "sarcasm": 0.0, "toxicity": 0.0}

        try:
            text_lower = text.lower()
            word_count = len(text.split())

            toxic_results = self._get_results_safely(self.toxic_pipe, text)
            toxic_scores = []
            target_labels = ['toxicity', 'severe_toxicity', 'insult', 'threat', 'obscene', 'identity_attack']
            for res in toxic_results:
                if isinstance(res, dict) and res.get('label') in target_labels:
                    toxic_scores.append(res.get('score', 0.0))
            toxic_score = max(toxic_scores) if toxic_scores else 0.0
            
            sarcasm_results = self._get_results_safely(self.sarcasm_pipe, text)
            sarcasm_score = 0.0
            for res in sarcasm_results:
                if isinstance(res, dict) and res.get('label') == 'irony':
                    sarcasm_score = res.get('score', 0.0)

            sent_results = self._get_results_safely(self.sentiment_pipe, text)
            if sent_results:
                top_sentiment = max(sent_results, key=lambda x: x.get('score', 0.0))
                label = top_sentiment.get('label')
                score = top_sentiment.get('score', 0.0)
            else:
                label, score = 'neutral', 0.0

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
            if any(word in text_lower for word in status_keywords) and toxic_score < 0.3:
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
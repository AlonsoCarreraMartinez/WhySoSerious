import os
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from pathlib import Path

class BertPredictor:
    
    # Resolve absolute paths and load local model weights.
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        infra_dir = os.path.dirname(current_dir)
        src_dir = os.path.dirname(infra_dir)
        backend_dir = os.path.dirname(src_dir)
        
        weights_base = Path(backend_dir) / "weights" / "models" / "hf_bert_reg"
        
        try:
            print(f"LOADING MODELS")

            self.cynicism_pipe = self.load_local_pipeline(weights_base / "cynicism", "text-classification")
            self.exhaustion_pipe = self.load_local_pipeline(weights_base / "exhaustion", "sentiment-analysis")
            self.inefficacy_pipe = self.load_local_pipeline(weights_base / "inefficacy", "zero-shot-classification")
            
            print("MODELS LOADED SUCCESSFULLY")
        except Exception as e:
            print(f"ERROR: {e}")
            self.cynicism_pipe = None

    # Helper to initialize a transformer pipeline from local storage.
    def load_local_pipeline(self, path, task):
        model_path = os.path.abspath(str(path))
        return pipeline(task, model=model_path, tokenizer=model_path)

    # Analyze text to extract mathematical probabilities for MBI dimensions.
    def extract_content_features(self, text: str) -> dict:
        if not text or not self.cynicism_pipe:
            return {"exhaustion": 0.0, "cynicism": 0.0, "inefficacy": 0.0, "burnout_index": 0.0}

        try:
            # Cynicism
            toxic_raw = self.cynicism_pipe(text)[0]
            if isinstance(toxic_raw, list):
                cynicism_prob = max([r['score'] for r in toxic_raw if r.get('label') != 'neutral'], default=0.0)
            else:
                cynicism_prob = toxic_raw['score'] if toxic_raw.get('label') != 'neutral' else 0.0

            # Exhaustion
            sent_raw = self.exhaustion_pipe(text)[0]
            if isinstance(sent_raw, list): 
                sent_raw = sent_raw[0]
            exhaustion_prob = sent_raw['score'] if sent_raw.get('label') in ['negative', 'LABEL_0'] else 0.0

            # Inefficacy (Zero-shot)
            candidate_labels = ["technical block", "stuck", "making progress", "task completed"]
            zs_res = self.inefficacy_pipe(text, candidate_labels=candidate_labels)
            
            inefficacy_prob = 0.0
            if zs_res['labels'][0] in ["technical block", "stuck"]:
                inefficacy_prob = zs_res['scores'][0]

            e_val = round(float(exhaustion_prob), 2)
            c_val = round(float(cynicism_prob), 2)
            i_val = round(float(inefficacy_prob), 2)
            b_index = round((e_val + c_val + i_val) / 3, 2)

            return {
                "exhaustion": e_val,
                "cynicism": c_val,
                "inefficacy": i_val,
                "burnout_index": b_index
            }
        except Exception as e:
            print(f"INFERENCE ERROR: {e}")
            return {"exhaustion": 0.0, "cynicism": 0.0, "inefficacy": 0.0, "burnout_index": 0.0}
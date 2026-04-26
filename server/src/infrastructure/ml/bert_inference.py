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

            self.cynicism_pipe = self.load_local_pipeline(weights_base / "cynicism", "zero-shot-classification")
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
    def extract_content_features(self, text: str):
        if not text or not text.strip():
            return {"exhaustion": 0.0, "cynicism": 0.0, "inefficacy": 0.0, "burnout_index": 0.0}

        words = text.split()
        chunk_size = 200 
        
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        e_scores = []
        c_scores = []
        i_scores = []

        for chunk in chunks:
            if not chunk.strip():
                continue

            # Cynicism
            cyn_candidate_labels = [
                "sarcastic or passive-aggressive",
                "apathy and lack of interest",
                "complaining about others",
                "constructive technical feedback",
                "normal team communication"
            ]
            zs_cyn_res = self.cynicism_pipe(chunk, candidate_labels=cyn_candidate_labels)
            
            cynicism_prob = 0.0
            if zs_cyn_res['labels'][0] in ["sarcastic or passive-aggressive", "apathy and lack of interest", "complaining about others"]:
                if zs_cyn_res['scores'][0] > 0.45:
                    cynicism_prob = zs_cyn_res['scores'][0]

            # Exhaustion
            sent_raw = self.exhaustion_pipe(chunk)[0]
            if isinstance(sent_raw, list): 
                sent_raw = sent_raw[0]
            exhaustion_prob = sent_raw['score'] if sent_raw.get('label') in ['negative', 'LABEL_0'] else 0.0

            # Inefficacy 
            candidate_labels = [
                "feeling incompetent",     
                "wasted effort",           
                "struggling with code",    
                "external system failure", 
                "making progress",         
                "task completed"           
            ]
            zs_res = self.inefficacy_pipe(chunk, candidate_labels=candidate_labels)
            
            inefficacy_prob = 0.0
            if zs_res['labels'][0] in ["feeling incompetent", "wasted effort", "struggling with code"]:
                if zs_res['scores'][0] > 0.45:
                    inefficacy_prob = zs_res['scores'][0]

            e_scores.append(exhaustion_prob)
            c_scores.append(cynicism_prob)
            i_scores.append(inefficacy_prob)

        if not e_scores: 
            return {"exhaustion": 0.0, "cynicism": 0.0, "inefficacy": 0.0, "burnout_index": 0.0}

        e_val = round(sum(e_scores) / len(e_scores), 2)
        c_val = round(sum(c_scores) / len(c_scores), 2)
        i_val = round(sum(i_scores) / len(i_scores), 2)
        
        b_index = round((e_val + c_val + i_val) / 3.0, 2)

        return {
            "exhaustion": e_val,
            "cynicism": c_val,
            "inefficacy": i_val,
            "burnout_index": b_index
        }
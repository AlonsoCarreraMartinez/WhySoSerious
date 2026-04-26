import os
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from pathlib import Path

class BertPredictor:
    
    def __init__(self):
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        weights_base = Path(current_dir).parent / "weights" / "models" / "hf_bert_reg"
        
        try:
            print("LOADING MODELS...")
            self.cynicism_pipe = self.load_local_pipeline(weights_base / "cynicism", "zero-shot-classification")
            self.exhaustion_pipe = self.load_local_pipeline(weights_base / "exhaustion", "sentiment-analysis")
            self.inefficacy_pipe = self.load_local_pipeline(weights_base / "inefficacy", "zero-shot-classification")
            print("MODELS LOADED SUCCESSFULLY")
        except Exception as e:
            print(f"ERROR: {e}")
            self.cynicism_pipe = None

    def load_local_pipeline(self, path, task):
        model_path = os.path.abspath(str(path))
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
        return pipeline(task, model=model, tokenizer=tokenizer)

    def predict(self, text):
        if not text or not self.cynicism_pipe:
            return {"exhaustion": 0.0, "cynicism": 0.0, "inefficacy": 0.0, "burnout_index": 0.0}

        words = text.split()
        chunk_size = 200 
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

        e_scores, c_scores, i_scores = [], [], []

        for chunk in chunks:
            if not chunk.strip():
                continue

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

            sent_raw = self.exhaustion_pipe(chunk)[0]
            if isinstance(sent_raw, list): 
                sent_raw = sent_raw[0]
            exhaustion_prob = sent_raw['score'] if sent_raw.get('label') in ['negative', 'LABEL_0'] else 0.0

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

if __name__ == "__main__":
    predictor = BertPredictor()
    
    while True:
        try:
            prev_lines = []
            print("PREVIOUS CONTEXT (type 'EOF' to finish, 'exit' to quit):")
            while True:
                line = input()
                if line.strip() == "EOF":
                    break
                prev_lines.append(line)
            
            if not prev_lines or prev_lines[0].lower() == "exit":
                break
            previous_context = " ".join(prev_lines).strip()

            curr_lines = []
            print("CURRENT MESSAGE (type 'EOF' to finish, 'exit' to quit):")
            while True:
                line = input()
                if line.strip() == "EOF":
                    break
                curr_lines.append(line)
                
            if not curr_lines or curr_lines[0].lower() == "exit":
                break
            current_message = " ".join(curr_lines).strip()

            combined_text = f"{previous_context} {current_message}".strip()
            
            if combined_text:
                result = predictor.predict(combined_text)
                print(f"({result['exhaustion']}, {result['cynicism']}, {result['inefficacy']}, {result['burnout_index']})\n")

        except EOFError:
            break
        except KeyboardInterrupt:
            break
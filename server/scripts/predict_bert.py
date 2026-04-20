import os
from transformers import pipeline

class BertPredictor:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(current_dir, '..', 'weights', 'models', 'hf_bert_reg')
        
        try:
            cynicism_path = os.path.join(model_dir, "cynicism")
            self.cynicism_pipe = pipeline("text-classification", model=cynicism_path, tokenizer=cynicism_path)

            exhaustion_path = os.path.join(model_dir, "exhaustion")
            self.exhaustion_pipe = pipeline("sentiment-analysis", model=exhaustion_path, tokenizer=exhaustion_path)

            inefficacy_path = os.path.join(model_dir, "inefficacy")
            self.inefficacy_pipe = pipeline("zero-shot-classification", model=inefficacy_path, tokenizer=inefficacy_path)
            
        except Exception as e:
            print(f"[ERROR] {e}")
            self.cynicism_pipe = None

    def predict(self, text):
        if not text or not self.cynicism_pipe:
            return {"exhaustion": 0.0, "cynicism": 0.0, "inefficacy": 0.0, "burnout_index": 0.0}

        words = text.split()
        chunk_size = 350 
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        e_scores, c_scores, i_scores = [], [], []

        for chunk in chunks:
            if not chunk.strip():
                continue

            toxic_raw = self.cynicism_pipe(chunk)[0]
            if isinstance(toxic_raw, list):
                cynicism_prob = max([r['score'] for r in toxic_raw if r.get('label') != 'neutral'], default=0.0)
            else:
                cynicism_prob = toxic_raw['score'] if toxic_raw.get('label') != 'neutral' else 0.0

            sent_raw = self.exhaustion_pipe(chunk)[0]
            if isinstance(sent_raw, list): 
                sent_raw = sent_raw[0]
            exhaustion_prob = sent_raw['score'] if sent_raw.get('label') in ['negative', 'LABEL_0'] else 0.0

            candidate_labels = ["technical block", "stuck", "making progress", "task completed"]
            zs_res = self.inefficacy_pipe(chunk, candidate_labels=candidate_labels)
            
            inefficacy_prob = 0.0
            if zs_res['labels'][0] in ["technical block", "stuck"]:
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
    print("\n--- SCRIPT ANALYZER ---")
    
    while True:
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "EXIT":
                    exit()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            except EOFError:
                break
        
        text = "\n".join(lines)
        if text.strip():
            print(predictor.predict(text))
            print("-" * 40 + "\nPaste next conversation (or type 'EXIT'):\n")
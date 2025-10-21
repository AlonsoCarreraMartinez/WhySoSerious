import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Politeness 
df_polite = pd.read_csv(os.path.join(BASE_DIR, "Politeness.csv"))
df_polite = df_polite.rename(columns={"utterance": "text", "category": "label"})
df_polite["source"] = "politeness"

if not pd.api.types.is_numeric_dtype(df_polite["label"]):
    df_polite["label"] = df_polite["label"].astype("category").cat.codes

# Normalize 0–10
df_polite["label"] = (df_polite["label"] - df_polite["label"].min()) / (df_polite["label"].max() - df_polite["label"].min()) * 10


# Toxicity 
df_toxic = pd.read_csv(os.path.join(BASE_DIR, "toxicity.csv"))
df_toxic["label"] = df_toxic[["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]].mean(axis=1) * 10
df_toxic = df_toxic.rename(columns={"comment_text": "text"})
df_toxic["source"] = "toxicity"


# Sarcasm 
sarcasm_path = os.path.join(BASE_DIR, "Sarcasm.json")

with open(sarcasm_path, "r", encoding="utf-8") as f:
    sarcasm_data = [json.loads(line) for line in f]

df_sarcasm = pd.DataFrame(sarcasm_data)
df_sarcasm = df_sarcasm.rename(columns={"headline": "text", "is_sarcastic": "label"})
df_sarcasm["label"] = df_sarcasm["label"].astype(float) * 10
df_sarcasm["source"] = "sarcasm"

# Union
df_final = pd.concat(
    [df_polite[["text", "label", "source"]],
     df_toxic[["text", "label", "source"]],
     df_sarcasm[["text", "label", "source"]]],
    ignore_index=True
)

df_final = df_final.drop_duplicates(subset="text").dropna(subset=["text"])


output_path = os.path.join(BASE_DIR, "WhySoSeriousDataset.csv")
df_final.to_csv(output_path, index=False, encoding="utf-8")


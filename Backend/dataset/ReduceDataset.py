import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(BASE_DIR, "WhySoSeriousDataset.csv")
output_path = os.path.join(BASE_DIR, "WhySoSeriousDataset_50k.csv")

print(f"Loading original dataset from: {input_path}")
df = pd.read_csv(input_path)
print(f"Original rows: {len(df)}")
df_sample = df.sample(n=50000, random_state=42)

df_sample.to_csv(output_path, index=False, encoding="utf-8")
print(f"Reduced dataset saved: {output_path}")
print(f"NewRows: {len(df_sample)}")

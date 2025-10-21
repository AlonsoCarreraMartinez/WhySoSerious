import os
import hashlib
import pandas as pd
from neo4j import GraphDatabase

NEO4J_URI = "bolt://127.0.0.1:7687"  
NEO4J_USER = "neo4j"
NEO4J_PASS = "neo4j123"               

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "dataset", "WhySoSeriousDataset_50k.csv") #CSV

def review_id(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()

# Avoid duplicates
CYPHER = """
MERGE (r:Review {id: $rid})
  ON CREATE SET r.text = $text
  ON MATCH  SET r.text = coalesce(r.text, $text)

MERGE (src:Source {name: $source})

MERGE (r)-[:FROM_SOURCE]->(src)

MERGE (sc:Score {review_id: $rid, type: $source})
  ON CREATE SET sc.value = $score
  ON MATCH  SET sc.value = $score

MERGE (r)-[:HAS_SCORE]->(sc)
"""

def main():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV doesn't found: {CSV_PATH}")

    print(f"Reading: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)

    for col in ("text", "label", "source"):
        if col not in df.columns:
            raise ValueError(f"The column '{col}' doesn't found")

    df = df.dropna(subset=["text"]).drop_duplicates(subset=["text"])

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    total = len(df)

    with driver.session(database="WhySoSerious") as session:   # Remember put the correct name of the dataset
        for i, row in df.iterrows():
            text = str(row["text"])
            score = float(row["label"])
            source = str(row["source"])
            rid = review_id(text)

            session.run(
                CYPHER,
                rid=rid,
                text=text,
                score=score,
                source=source
            )

            if (i + 1) % 500 == 0 or i + 1 == total:
                print(f"{i+1}/{total} charged rows")

    driver.close()
    print("COMPLETE")

if __name__ == "__main__":
    main()

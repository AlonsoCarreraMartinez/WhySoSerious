import os
import json
import time
from typing import List, Tuple, Dict
import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer # Embeddings (PyTorch)
import faiss # Find similar vectors (Facebook AI Similarity Search)
from ollama import Client
from rich.console import Console
from rich.panel import Panel

console = Console()

# Neo4j configuration
NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "neo4j123")
NEO4J_DB   = os.getenv("NEO4J_DB",   "WhySoSerious")

# Ollama configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:instruct")
OLLAMA_HOST  = os.getenv("OLLAMA_HOST",  "http://127.0.0.1:11434")

# all-MiniLM-L6-v2 is the model of PyTorch that transform phrases in vectors of 384 dimensions
EMB_MODEL_NAME = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
INDEX_DIR = os.getenv("INDEX_DIR", "./faiss_index")
TOP_K = int(os.getenv("TOP_K", "5"))

os.makedirs(INDEX_DIR, exist_ok=True)
INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")
META_PATH  = os.path.join(INDEX_DIR, "meta.json")
VEC_PATH   = os.path.join(INDEX_DIR, "vectors.npy")

# Create driver to connect Database
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# Loading reviews
def fetch_reviews(limit: int | None = None) -> pd.DataFrame:
    query = """
    MATCH (r:Review)
    RETURN r.id AS id, r.text AS text
    """
    if limit:
        query += "\nLIMIT $lim"
    with get_driver().session(database=NEO4J_DB) as ses:
        recs = ses.run(query, lim=limit).data()
    df = pd.DataFrame(recs)
    df = df.dropna(subset=["id","text"]).drop_duplicates(subset=["id"])
    return df

# Return toxicity, politeness, sarcasm and the overall score
def fetch_scores(review_ids: List[str]) -> Dict[str, Dict[str, float]]:
    result: Dict[str, Dict[str, float]] = {}
    with get_driver().session(database=NEO4J_DB) as ses:
        query = """
        UNWIND $ids AS rid
        MATCH (:Review {id: rid})-[:HAS_SCORE]->(sc:Score)
        RETURN rid, sc.type AS type, sc.value AS value
        """
        for rec in ses.run(query, ids=review_ids):
            rid = rec["rid"]
            result.setdefault(rid, {"by_source": {}, "overall": None})
            result[rid]["by_source"][rec["type"]] = float(rec["value"])
    for rid, d in result.items():
        tox = d["by_source"].get("toxicity", 5)
        sar = d["by_source"].get("sarcasm", 5)
        pol = d["by_source"].get("politeness", 5)
        d["overall"] = round((tox * 0.4) + (sar * 0.4) + ((10 - pol) * 0.2)) # BETA
    return result 


"""

Loads or builds a FAISS index to perform fast semantic similarity search
between user queries and stored reviews using PyTorch embeddings.

"""
def build_or_load_index() -> Tuple[faiss.IndexFlatIP, SentenceTransformer, List[str], List[str]]:
    model = SentenceTransformer(EMB_MODEL_NAME)  # uses PyTorch to generate text embeddings

    # If the index already exists, load it directly from disk 
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH) and os.path.exists(VEC_PATH):
        console.print("[green]Loading FAISS index from disk...[/green]")
        index = faiss.read_index(INDEX_PATH)
        vectors = np.load(VEC_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        ids = meta["ids"]
        texts = meta["texts"]
        assert vectors.shape[0] == len(ids) == len(texts)  # sanity check
        return index, model, ids, texts

    # Otherwise, build the index from scratch 
    console.print("[yellow]Building FAISS index for the first time... this may take a few minutes[/yellow]")
    df = fetch_reviews()  # get all reviews from Neo4j
    df = df.dropna(subset=["text"]).reset_index(drop=True)
    texts = df["text"].tolist()
    ids = df["id"].tolist()

    # Encode texts into vectors (embeddings) with SentenceTransformer
    embs = model.encode(texts, batch_size=256, show_progress_bar=True, normalize_embeddings=True)
    embs = np.array(embs).astype("float32")

    # Create FAISS index 
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)

    # Save the index and metadata
    faiss.write_index(index, INDEX_PATH)
    np.save(VEC_PATH, embs)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump({"ids": ids, "texts": texts}, f, ensure_ascii=False)

    console.print(f"[green]Index created successfully: {len(ids)} reviews indexed[/green]")
    return index, model, ids, texts


"""

Encodes the user query into an embedding vector and searches for the
most semantically similar reviews in the FAISS index.

"""
def search_similar(
    query: str,
    index: faiss.IndexFlatIP,
    model: SentenceTransformer,
    ids: List[str],
    texts: List[str],
    k: int = TOP_K
):
    # Encode the user's question into a PyTorch vector 
    qv = model.encode([query], normalize_embeddings=True)
    qv = np.array(qv).astype("float32")

    # Use FAISS to find the k most similar vectors 
    D, I = index.search(qv, k) # D = similarity scores , I = indices of the matching reviews
    
    hits = []
    for score, idx in zip(D[0], I[0]):
        if idx == -1:  
            continue
        hits.append({
            "id": ids[idx],
            "text": texts[idx],
            "sim": float(score)
        })
    
    return hits


# LLM used: llama3:instruct
def answer_with_llm(
    client: Client,
    question: str,
    contexts: List[Dict],
    scores: Dict[str, Dict[str, float]]
) -> str:
    # Context for the model (relevant reviews, similarity and scores)
    snippets = []
    for i, h in enumerate(contexts, 1):
        rid = h["id"]
        sc = scores.get(rid, {})
        overall = sc.get("overall")
        per_src = sc.get("by_source", {})

        # Build score line (overall + individual scores)
        score_line = f"overall={overall:.1f}" if overall is not None else "overall=?"
        if per_src:
            parts = ", ".join(f"{k}={v:.1f}" for k, v in per_src.items())
            score_line += f" ({parts})"

        # Append the context snippet
        snippets.append(f"[{i}] id={rid} sim={h['sim']:.3f} {score_line}\n{h['text']}")

    context_block = "\n\n".join(snippets)

    # prompt
    system = (
        "You are WhySoSerious, an AI assistant specialized in analyzing text-based communication within corporate environments. "
        "Your goal is to detect early signs of burnout, quiet quitting, or emotional exhaustion from the language used in messages or reviews. "
        "You analyze linguistic tone, motivation level, emotional charge, and stress indicators to estimate a global risk score from 0 to 10. "
        "Respond ALWAYS with a single integer (0–10) representing the burnout or disengagement intensity: "
        "0 = no signs of burnout, 10 = critical burnout. "
        "Do NOT provide explanations, text, or justification — return ONLY the integer."
    )

    user_msg = (
        f"User question:\n{question}\n\n"
        f"Relevant context (sample reviews):\n{context_block}\n\n"
        "Respond ONLY with an integer from 0 to 10 (no text, no punctuation, no explanation)."
    )

   
    resp = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg}
        ],
        options={"temperature": 0.0}  
    )

    # Extract and clean numeric response
    content = resp["message"]["content"].strip()
    digits = "".join(ch for ch in content if ch.isdigit())
    if not digits:
        return "0"  
    score = int(digits)
    score = max(0, min(10, score))
    return str(score)

def main():

    index, emb_model, ids, texts = build_or_load_index()
    client = Client(host=OLLAMA_HOST)

    while True:
        try:
            q = input("Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            q = "salir"
        if q.lower() in {"salir", "exit", "quit"} or not q:
            break

        hits = search_similar(q, index, emb_model, ids, texts, k=TOP_K)
        rids = [h["id"] for h in hits]
        scores = fetch_scores(rids)
        ans = answer_with_llm(client, q, hits, scores)

        print(ans)

if __name__ == "__main__":
    main()

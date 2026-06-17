import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional

try:
    MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    raise ImportError(f"[Matcher] Failed to load SBERT model: {e}")

def generate_embedding(text: str) -> Optional[np.ndarray]:
    if not isinstance(text, str):
        raise TypeError(f"[Matcher] Expected str, got {type(text).__name__}")
    if not text.strip():
        return None
    return MODEL.encode(text, convert_to_numpy=True)

def calculate_similarity(resume_text: str,job_text: str) -> float:
    resume_emb = generate_embedding(resume_text)
    job_emb = generate_embedding(job_text)
    if resume_emb is None or job_emb is None:
        return 0.0
    score = cosine_similarity(resume_emb.reshape(1, -1),job_emb.reshape(1, -1))[0][0]
    return float(np.clip(score, 0.0, 1.0))

def rank_jobs(resume_text: str,jobs: List[Dict],top_k: Optional[int] = None) -> List[Dict]:
    if not jobs:
        return []
    resume_emb = generate_embedding(resume_text)
    if resume_emb is None:
        return []
    descriptions = [job.get("description", "")for job in jobs]
    job_embeddings = MODEL.encode(descriptions,convert_to_numpy=True)
    scores = cosine_similarity(resume_emb.reshape(1, -1),job_embeddings)[0]
    ranked_jobs = []
    for job, score in zip(jobs, scores):
        job_copy = job.copy()
        semantic_score = float(np.clip(score, 0.0, 1.0))
        job_copy["semantic_score"] = round(semantic_score,4)
        job_copy["semantic_percentage"] = round(semantic_score * 100,2)
        ranked_jobs.append(job_copy)
    ranked_jobs.sort(key=lambda x: x["semantic_score"],reverse=True)
    if top_k:
        ranked_jobs = ranked_jobs[:top_k]
    return ranked_jobs
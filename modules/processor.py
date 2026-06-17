import re
from typing import List

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"Expected string input, got {type(text).__name__}")
    if not text.strip():
        return ""
    text = text.lower()
    text = text.replace("\xa0", " ")
    text = re.sub(r"[|/\\]", " ", text)
    text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+"," ",text)
    text = re.sub(r"https?://\S+|www\.\S+"," ",text)
    text = re.sub(r"\+?\d[\d\s\-\(\).]{7,}\d"," ",text)
    text = re.sub(r"[●•▪▫■□◆►▶✓✔✦★☆➢→]"," ",text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def clean_texts(texts: List[str]) -> List[str]:
    if not isinstance(texts, list):
        raise TypeError(f"Expected list of strings, got {type(texts).__name__}")
    cleaned = []
    for t in texts:
        if isinstance(t, str):
            cleaned.append(clean_text(t))
    return cleaned
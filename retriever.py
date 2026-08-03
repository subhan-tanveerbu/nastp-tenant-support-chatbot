import pickle
import faiss

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

from pathlib import Path
import pickle
import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
VECTOR_DB = BASE_DIR / "vector_db"

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index(str(VECTOR_DB / "index.faiss"))

with open(VECTOR_DB / "chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

def retrieve(question, top_k=3):

    embedding = model.encode([question])

    distances, indices = index.search(embedding, top_k)

    results = []

    for idx in indices[0]:
        results.append(chunks[idx])

    return "\n\n".join(results)
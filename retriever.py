import pickle
import faiss

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("vector_db/index.faiss")

with open("vector_db/chunks.pkl","rb") as f:
    chunks = pickle.load(f)

def retrieve(question, top_k=3):

    embedding = model.encode([question])

    distances, indices = index.search(embedding, top_k)

    results = []

    for idx in indices[0]:
        results.append(chunks[idx])

    return "\n\n".join(results)
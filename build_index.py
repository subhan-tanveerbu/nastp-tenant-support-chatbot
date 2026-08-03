import os
import pickle
import faiss

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("knowledge/nastp_info.txt", encoding="utf-8") as f:
    text = f.read()

chunks = text.split("\n\n")

embeddings = model.encode(chunks)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

os.makedirs("vector_db", exist_ok=True)

faiss.write_index(index, "vector_db/index.faiss")

with open("vector_db/chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

print("Done!")
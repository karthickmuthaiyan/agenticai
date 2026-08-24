"""Example: use ChromaDB as a document store and FAISS for vector search.

Install:
	pip install chromadb faiss-cpu sentence-transformers
"""

from __future__ import annotations

import faiss
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer


DOCUMENTS = [
	"Python is commonly used for data science and machine learning.",
	"FAISS is a library for efficient similarity search over dense vectors.",
	"ChromaDB stores documents, metadata, and embeddings for retrieval systems.",
	"FastAPI is a Python framework for building HTTP APIs.",
]


def main() -> None:
	model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

	# Chroma owns the documents and metadata. Disable its default embedding
	# function because FAISS will be the search backend in this example.
	client = chromadb.PersistentClient(path="./chroma_data")
	collection = client.get_or_create_collection(
		name="knowledge",
		embedding_function=None,
	)

	embeddings = model.encode(DOCUMENTS, normalize_embeddings=True)
	vectors = np.asarray(embeddings, dtype="float32")
	ids = [f"doc-{i}" for i in range(len(DOCUMENTS))]

	collection.upsert(
		ids=ids,
		documents=DOCUMENTS,
		embeddings=vectors.tolist(),
		metadatas=[{"source": "example"} for _ in DOCUMENTS],
	)

	# Inner product on normalized vectors is cosine similarity.
	index = faiss.IndexFlatIP(vectors.shape[1])
	index.add(vectors)

	query = "Which database can store embeddings?"
	query_vector = np.asarray(
		model.encode([query], normalize_embeddings=True), dtype="float32"
	)
	scores, positions = index.search(query_vector, k=2)

	# Use FAISS positions to fetch the canonical records from ChromaDB.
	result_ids = [ids[position] for position in positions[0] if position >= 0]
	records = collection.get(ids=result_ids, include=["documents", "metadatas"])
	by_id = dict(zip(records["ids"], zip(records["documents"], records["metadatas"])))

	print(f"Query: {query}\n")
	for score, document_id in zip(scores[0], result_ids):
		document, metadata = by_id[document_id]
		print(f"{float(score):.3f} | {document_id} | {metadata['source']} | {document}")


if __name__ == "__main__":
	main()

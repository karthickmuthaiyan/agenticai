import chromadb

# Create (or open) a persistent ChromaDB database
client = chromadb.PersistentClient(path=r"D:\git\AgenticAI\agenticai\14_advanced\04_rag\chroma_db")
collection = client.get_or_create_collection("crud_demo")

# Start from a clean collection so the demo is repeatable
try:
    collection.delete(ids=collection.get()["ids"])
except Exception:
    pass

collection.add(
    ids=[str(i) for i in range(1, 5)],
    documents=[
        "Python is a popular programming language for AI and data science.",
        "Machine learning enables computers to learn from data.",
        "ChromaDB is a vector database used in Retrieval-Augmented Generation (RAG).",
        "Toodle is a 5th grader who loves to play soccer and read books about space.",
    ],
    metadatas=[
        {"topic": "programming"},
        {"topic": "ai"},
        {"topic": "database"},
        {"topic": "education"},
    ]
)

#Querying documents
query = input("Enter your search query: ")
results = collection.query(
    query_texts=[query],
    n_results=1
)

print("\nTop 1 Semantic Search Results:\n")
for i, doc in enumerate(results["documents"][0], start=1):
    print(f"{i}. {doc}")
    print(f" Full Result: {results["distances"][0]}\n")
import chromadb

# Create (or open) a persistent ChromaDB database
client = chromadb.PersistentClient(path=r"D:\git\AgenticAI\agenticai\14_advanced\04_rag\chroma_db")
collection = client.get_or_create_collection("articles")

# Clear any existing data (optional)
try:
    collection.delete(ids=collection.get()["ids"])
except:
    pass

# Sample documents
documents = [
    "Python is a popular programming language for AI and data science.",
    "Machine learning enables computers to learn from data.",
    "ChromaDB is a vector database used in Retrieval-Augmented Generation (RAG).",
    "FastAPI is a modern Python framework for building REST APIs.",
    "SQLite is a lightweight relational database.",
    "Transformers are deep learning models used in natural language processing.",
    "LangChain helps developers build LLM-powered applications.",
    "Pandas is a Python library for data analysis and manipulation.",
    "Joshua is a 5th grader who loves to play soccer and read books about space."
]

print("Length of documents:", len(documents))

# Store documents
collection.add(
    ids=[str(i) for i in range(1, len(documents) + 1)],
    documents=documents
)

# Semantic search
query = input("Enter your search query: ")

results = collection.query(
    query_texts=[query],
    n_results=1
)

#print("\nResults: ", results)


print("\nTop 3 Semantic Search Results:\n")
for i, doc in enumerate(results["documents"][0], start=1):
    print(f"{i}. {doc}")
    
for i, distance in enumerate(results["distances"][0], start=1):
    print(f"Distance for result {i}: {distance:.4f}")
    
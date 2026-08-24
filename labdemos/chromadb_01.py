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

#reading documents
def read_document(doc_id):
    result = collection.get(ids=[doc_id])
    print(f"Read by id '{doc_id}':")
    print(f"  Document: {result['documents'][0]}")
    print(f"  Metadata: {result['metadatas'][0]}\n")

read_document("2")
#update documents
collection.update(
    ids=["2"],
    documents=["Machine learning enables computers to learn patterns from data without explicit programming."],
    metadatas=[{"topic": "ai", "updated": True}],
)

read_document("2")

#delete documents
collection.delete(ids=["2"])

for i in range(1, 5):
    try:
        read_document(str(i))
    except Exception as e:
        print(f"Error reading document with id '{i}': {e}")

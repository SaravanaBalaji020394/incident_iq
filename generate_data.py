import os
import json
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def seed_vector_db():
    print("🔄 Initializing embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Establish dynamic paths relative to file location
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, "..", "data", "incidents_corpus.json")
    persist_directory = os.path.join(current_dir, "..", "chroma_db")
    
    # Ensure raw data source file exists cleanly
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ Target data file missing at: {json_path}")
        
    print(f"📖 Parsing raw JSON incident data source from: {json_path}")
    with open(json_path, "r") as f:
        incidents = json.load(f)
        
    texts = []
    metadatas = []
    
    # Construct distinct rich text blocks for the semantic vector search engine
    for inc in incidents:
        text_block = (
            f"Runbook Reference: {inc['id']} - {inc['title']}\n"
            f"Context / Error Profile: {inc['description']}\n"
            f"Standard Fix Step: {inc['resolution']}"
        )
        texts.append(text_block)
        metadatas.append({
            "incident_id": inc["id"],
            "category": inc["category"],
            "target_severity": inc["severity"]
        })
        
    print(f"📦 Injecting {len(texts)} highly structured incident profiles into ChromaDB...")
    
    # Build and persist the vector index
    vector_db = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=persist_directory
    )
    print("✅ Real JSON-sourced ChromaDB RAG Corpus successfully deployed!")

if __name__ == "__main__":
    seed_vector_db()
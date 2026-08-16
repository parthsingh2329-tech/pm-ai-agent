import chromadb
import uuid

chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="project_notes")


def add_note(text):
    note_id = str(uuid.uuid4())[:8]
    collection.add(documents=[text], ids=[note_id])
    return {"note_id": note_id, "added": True}


def search_memory(query):
    results = collection.query(query_texts=[query], n_results=3)
    matches = results["documents"][0] if results["documents"] else []
    return {"matches": matches}
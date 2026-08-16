import chromadb
import uuid
from session_state import get_current_project

chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="project_notes")


def add_note(text):
    project_id = get_current_project()
    note_id = str(uuid.uuid4())[:8]
    collection.add(documents=[text], ids=[note_id], metadatas=[{"project_id": project_id}])
    return {"note_id": note_id, "added": True}


def search_memory(query):
    project_id = get_current_project()
    results = collection.query(query_texts=[query], n_results=3, where={"project_id": project_id})
    matches = results["documents"][0] if results["documents"] else []
    return {"matches": matches}
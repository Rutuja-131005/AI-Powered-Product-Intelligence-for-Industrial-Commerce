import os
import glob
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import pypdf
import docx

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "rag_collection"
MODEL_NAME = "all-MiniLM-L6-v2"
_EF = None

def parse_pdf(file_path):
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def parse_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text

def parse_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

def load_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    elif ext == ".txt":
        return parse_txt(file_path)
    else:
        print(f"Unsupported file type: {ext}")
        return ""

def split_text(text, chunk_size=1000, overlap=200):
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks

def ingest_file(file_path):
    filename = os.path.basename(file_path)
    print(f"Ingesting file: {filename}")
    
    text = load_file(file_path)
    if not text:
        print(f"ERROR: No text extracted from {filename}")
        return False
    
    chunks = split_text(text)
    if not chunks:
        print("ERROR: No chunks created")
        return False

    chunked_texts = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        chunked_texts.append(chunk)
        metadatas.append({"source": filename, "chunk_id": i})
        ids.append(f"{filename}_{i}")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # Use global EF if available, otherwise initialize (though it should be global ideally)
    global _EF
    if _EF is None:
        _EF = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    
    collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=_EF)

    collection.upsert(
        documents=chunked_texts,
        metadatas=metadatas,
        ids=ids
    )
    return True

def ingest_directory(directory="data"):
    files = glob.glob(os.path.join(directory, "*"))
    for f in files:
        if os.path.isfile(f):
            ingest_file(f)

def get_collection_stats():
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
        try:
            collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
            return collection.count()
        except ValueError:
            return 0
    except Exception as e:
        print(f"Error getting stats: {e}")
        return 0

if __name__ == "__main__":
    ingest_directory()

def delete_file_embeddings(filename):
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        
        # Delete items where metadata 'source' matches the filename
        # Note: ChromaDB delete expects ids or where/where_document filter
        collection.delete(where={"source": filename})
        return True
    except Exception as e:
        print(f"Error deleting embeddings for {filename}: {e}")
        return False

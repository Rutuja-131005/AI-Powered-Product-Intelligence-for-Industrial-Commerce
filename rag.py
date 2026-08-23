"""
Ground-Truth Retrieval-Augmented Generation (RAG) Engine
Combines ChromaDB Vector Store + Hugging Face Embeddings (SentenceTransformers) + OpenRouter LLM.
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from services.openrouter_service import OpenRouterLLM

load_dotenv()

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "rag_collection"
MODEL_NAME = "all-MiniLM-L6-v2"

def query_rag(query_text, history=None):
    """
    Executes grounded semantic search on Vector DB and answers using OpenRouter LLM / Gemini.
    """
    if history is None:
        history = []

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    
    try:
        collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)
    except Exception:
        return {"answer": "Vector DB not initialized. Please upload technical documents or ingest products first.", "citations": []}

    search_query = query_text

    # Query the Vector DB (Hugging Face embeddings)
    try:
        results = collection.query(
            query_texts=[search_query],
            n_results=4
        )
    except Exception as e:
        results = {'documents': [[]], 'metadatas': [[]]}

    context_str = ""
    citations = []
    sources_list = []

    if results.get('documents') and results['documents'][0]:
        retrieved_docs = results['documents'][0]
        metadatas = results['metadatas'][0] if results.get('metadatas') else [{}] * len(retrieved_docs)
        
        for i, doc in enumerate(retrieved_docs):
            meta = metadatas[i] or {}
            source = meta.get("source", "Technical Catalog")
            chunk_id = meta.get("chunk_id", str(i+1))
            context_str += f"---\nSource: {source} (Chunk {chunk_id})\nContent: {doc}\n"
            citations.append(f"{source}: Chunk {chunk_id}")
            sources_list.append({"source": source, "chunk_id": chunk_id, "text": doc})

    if not context_str:
        context_str = "Industrial Catalog database containing products from Diablo, 3M, Milwaukee, Festool, Dewalt, Makita, GE, Trex, Leviton, Philips."

    # 1. Primary: OpenRouter LLM
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        answer = OpenRouterLLM.answer_qa(query_text, context_str)
        if answer and "No direct answer" not in answer:
            return {
                "answer": answer,
                "sources": sources_list,
                "citations": citations
            }

    # 2. Fallback: Gemini LLM
    gemini_key = os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""You are ProdIntellix AI, an industrial product intelligence assistant.
            Answer the following question based on the provided technical catalog context:
            Context: {context_str}
            Question: {query_text}
            Answer:"""
            res = model.generate_content(prompt)
            return {
                "answer": res.text,
                "sources": sources_list,
                "citations": citations
            }
        except Exception:
            pass

    # 3. Local fallback response if offline
    return {
        "answer": f"Based on the industrial catalog context: {context_str[:250]}... For '{query_text}', refer to verified manufacturer specifications.",
        "sources": sources_list,
        "citations": citations
    }

if __name__ == "__main__":
    result = query_rag("What sanding discs are available?")
    print(result['answer'])

import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "rag_collection"
MODEL_NAME = "all-MiniLM-L6-v2"

def query_rag(query_text, history=None):
    if history is None:
        history = []

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    except ValueError:
        return {"answer": "System not initialized. Please upload documents first.", "citations": []}

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
         return {"answer": "API Key missing. Please check server configuration.", "citations": []}
         
    genai.configure(api_key=api_key)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = next((m for m in available_models if 'gemini' in m and 'flash' in m), None)
    if not model_name:
        model_name = next((m for m in available_models if 'gemini' in m), None)
    
    if not model_name:
        return {"answer": "No available Gemini models found.", "citations": []}
        
    model = genai.GenerativeModel(model_name)

    search_query = query_text
    if history:
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]]) 
        rewrite_prompt = f"""
        Given the following conversation history, rewrite the last user query to be a standalone question that includes all necessary context.
        If the query is already standalone, return it exactly as is.
        
        History:
        {history_str}
        
        Last User Query: {query_text}
        
        Rewritten Query:"""
        
        try:
            rewrite_response = model.generate_content(rewrite_prompt)
            search_query = rewrite_response.text.strip()
        except Exception as e:
            print(f"Error rewriting query: {e}. Using original.")

    results = collection.query(
        query_texts=[search_query],
        n_results=3
    )
    
    if not results['documents'] or not results['documents'][0]:
        return {"answer": "I couldn't find any relevant information in the documents.", "citations": []}

    retrieved_docs = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    context_str = ""
    citations = []
    
    for i, doc in enumerate(retrieved_docs):
        source = metadatas[i].get("source", "Unknown")
        chunk_id = metadatas[i].get("chunk_id", "Unknown")
        context_str += f"---\nSource: {source} (Chunk {chunk_id})\nContent: {doc}\n"
        citations.append(f"{source}: Chunk {chunk_id}")

    prompt = f"""You are a helpful assistant. Answer the user's question based strictly on the context provided below.
    
    Instructions:
    1. If the user's input is a greeting (e.g., "Hello", "Hi") or small talk, reply politely and ask how you can help with their documents.
    2. If the user asks about the technical implementation (e.g., "How do you work?", "What stack is this?"), reply exactly: "I am built using Python, FastAPI, ChromaDB (Vector DB), SentenceTransformers (Embeddings), and Google Gemini (LLM)."
    3. For all other questions, answer STRICTLY based on the provided Context.
    4. If the answer is not in the Context, say: "I couldn't find any relevant information in the documents."
    
    Context:
    {context_str}
    
    Question: {query_text}
    
    Answer:"""
    
    try:
        response = model.generate_content(prompt)

        return {
            "answer": response.text,
            "sources": [
                {"source": m.get("source"), "chunk_id": m.get("chunk_id"), "text": d} 
                for m, d in zip(metadatas, retrieved_docs)
            ]
        }
            
    except Exception as e:
        return {"answer": f"Error generating response: {str(e)}", "sources": []}

if __name__ == "__main__":
    result = query_rag("What is the Turing test?")
    print(result['answer'])

# Document RAG System
A full-stack Retrieval-Augmented Generation (RAG) system built with Python, FastAPI, and Google Gemini.

## 🚀 Features
- **Document Ingestion**: Seamless support for PDF, DOCX, and TXT files.
- **RAG Pipeline**: Semantic search using ChromaDB and answer generation via Google Gemini.
- **Modern UI**: Streamlit-style dark dashboard with Cyan theme and bold, columnar source citations.
- **Deployment Ready**: Configured for easy deployment on Render.

## 📋 Agile Documentation
- [Sprint Tracking & Backlog](https://docs.google.com/spreadsheets/d/1eCy74VCtDegFtVy0vvR7MFqczYW7Rmu5DOku6FNwvoc/edit?usp=sharing)

## 🏁 Milestones

### Milestone 1: Document Ingestion & Indexing
- **Objective**: Build a robust data pipeline for processing and indexing documents.
- **Tasks**: Select and set up a vector database; develop scripts for document ingestion and text splitting; generate and store document embeddings.
- **Evaluation Criteria**: The document ingestion and indexing pipeline is operational, and documents can be successfully embedded and stored in the vector database.

### Milestone 2: RAG Pipeline Development
- **Objective**: Implement the core Retrieval-Augmented Generation logic.
- **Tasks**: Integrate the retrieval mechanism with the vector database; connect to an LLM API; develop the logic for synthesizing answers from retrieved chunks and citing sources.
- **Evaluation Criteria**: The RAG pipeline is functional, and the system can retrieve relevant document chunks and generate coherent, grounded answers.

### Milestone 3: Conversational Interface & Dialogue Management
- **Objective**: Develop a user-friendly interface for interacting with the system.
- **Tasks**: Design and implement a web-based chat interface; Ensure the system can handle multi-turn conversations and maintain context.
- **Evaluation Criteria**: The web interface is responsive, supports file uploads, and enables natural language interaction with the RAG pipeline.

### Milestone 4: Deployment & Final Evaluation
- **Objective**: Deploy the full system and conduct a comprehensive evaluation.
- **Status**: Ready! See `DEPLOYMENT_RENDER.md` for detailed deployment instructions.
- **Evaluation Criteria**: The system is containerized, performance metrics are documented (Ingestion/Retrieval), and the system is ready for production use.

## 🛠️ Prerequisites
- Python 3.9+
- A Google Cloud API Key (for Gemini)

## 📦 Installation
1. **Clone/Download** this repository.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Setup Environment**:
   - Open the `.env` file.
   - Add your API Key: `GOOGLE_API_KEY=AIzaSy...`

## ▶️ How to Run
1. **Start the Server**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```
2. **Access the Application**:
   - Open your web browser.
   - Go to: `http://localhost:8000`

## 📂 Project Structure
- `app.py`: FastAPI Backend.
- `rag.py`: RAG logic (Retrieval & Generation).
- `ingest.py`: Document processing.
- `templates/index.html`: Frontend UI.
- `static/`: CSS and JS files.

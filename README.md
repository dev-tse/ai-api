# 🤖 AI Document API

REST API for chatting with documents using RAG (Retrieval-Augmented Generation). Upload any text document and ask questions — get answers based only on the document content.

## ✨ Features

- 📄 Upload text documents
- 🔍 Vector-based semantic search
- 💬 Ask questions, get context-aware answers
- 🚫 No hallucinations — answers only from document content
- 💾 SQLite persistence — documents survive server restarts
- 🔄 Reset endpoint to clear document
- 📚 Auto-generated Swagger docs

## 🛠 Tech Stack

- Python
- FastAPI
- Groq API (llama-3.3-70b)
- Sentence Transformers (vector embeddings)
- SQLite (data persistence)
- Pydantic (data validation)

## 🚀 Run locally

1. Clone the repo
2. Create virtual environment
   \```bash
   python3 -m venv venv
   source venv/bin/activate
   \```
3. Install dependencies
   \```bash
   pip install -r requirements.txt
   \```
4. Create `.env` file
   \```
   GROQ_API_KEY=your_key
   \```
5. Run
   \```bash
   uvicorn main:app --reload
   \```
6. Open docs at `http://localhost:8000/docs`

## 📌 Endpoints

| Method | Endpoint  | Description |
|--------|-----------|-------------|
| GET    | /status   | Check if a document is loaded |
| POST   | /upload   | Upload a text document (saved to SQLite) |
| POST   | /ask      | Ask a question about the document |
| DELETE | /reset    | Clear the loaded document |

## 📝 Example

\```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.txt"

curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
\```

from fastapi import FastAPI, UploadFile, File, HTTPException
from groq import Groq
from dotenv import load_dotenv
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
import sqlite3
import json

conn = sqlite3.connect('document_store.db', check_same_thread=False)
cursor = conn.cursor()

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2')

app = FastAPI(title="AI Document API")

class AskQuestion(BaseModel):
    question: str

cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               chunks TEXT,
               filename TEXT
               )
""")

# Храним документ в памяти
document_store = {
    "text": None,
    "chunks": [],
    "filename": None
}

@app.get("/")
def root():
    return {"message": "AI Document API is running"}

@app.get("/status")
def status():
    # верни: загружен ли документ (True/False) и имя файла
    if document_store['filename']:
        return {"loaded": True, "filename": document_store['filename']}
    else:
        return {"loaded": False, "filename": None}
    
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    data_file = await file.read()
    decode_file = data_file.decode("utf-8")
    # Правильно — каждое поле отдельно:
    document_store['filename'] = file.filename
    document_store['text'] = decode_file
    document_store['chunks'] = split_into_chunks(decode_file)
    document_store['embeddings'] = model.encode(document_store['chunks'])
    chunks_json = json.dumps(document_store['chunks'], ensure_ascii=False)
    cursor.execute('INSERT INTO documents (chunks,filename) VALUES(?, ?)', (chunks_json, document_store['filename']))
    conn.commit()

    return {
        "message": "Файл загружен",
        "filename": file.filename,
        "size": len(decode_file.split())
    }

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def vector_search(query, knowledge_base, kb_embeddings, top_k=2):
    vector_query = model.encode(query)
    results = []
    for i, chunk in enumerate(knowledge_base):
        score = cosine_similarity(vector_query, kb_embeddings[i])
        results.append((score, chunk))
    results = sorted(results, key=lambda x:x[0], reverse=True)
    results = [chunk for score, chunk in results]
    return results[:top_k]

def split_into_chunks(text, chunk_size=50): 
    text_result = []
    text_temp = []
    text_array = text.split()
    for word in text_array:
        text_temp.append(word)
        if len(text_temp) == chunk_size:
            text_result.append(' '.join(text_temp))
            text_temp = []
    text_result.append(' '.join(text_temp))
    text_temp = []
    return text_result

@app.post("/ask")
def ask(request: AskQuestion):
    if (document_store["filename"] == None):
        raise HTTPException(status_code=400, detail="Документ не загружен")
    else:
        answer = vector_search(
        request.question,
        document_store['chunks'],
        document_store['embeddings']
        )
        context = "\n".join(answer)
        prompt = f"""Контекст:
        {context}
        Вопрос: {request.question}
        Отвечай только на основе контекста. Если ответа нет в контексте — скажи об этом."""
        response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        cursor.execute("SELECT * FROM documents")
        rows = cursor.fetchall()
        print(rows)
        
        return answer
    
@app.delete("/reset")
def reset():
    document_store['filename'] = None
    document_store['text'] = None
    document_store['chunks'] = []
    document_store['embeddings'] = []
    cursor.execute('DELETE from documents')
    conn.commit()

    return {'message': 'Документ очищен'}

@app.on_event("shutdown")
def shutdown():
    conn.close()

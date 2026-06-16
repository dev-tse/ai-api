from fastapi import FastAPI

app = FastAPI(title="AI Document API")

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
        
import traceback
from fastapi import FastAPI, Request
from pydantic import BaseModel
from rag_pipeline import add_document, query_rag

app = FastAPI()

class Doc(BaseModel):
    text: str

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "FastAPI is running."}

@app.post("/add")
async def add_doc(request: Request):
    try:
        data = await request.json()
        text = data.get("text")
        if not text:
            return {"error": "Missing 'text' field"}
        return add_document(text)
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/query")
async def query_doc(request: Request):
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            return {"error": "Missing 'question' field"}
        return {"answer": query_rag(question)}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/respond")
def respond(data: Query):
    return {"response": f"Echo: {data.text}"}
from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import add_document, query_rag

app = FastAPI()

class Doc(BaseModel):
    text: str

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "FastAPI is running"}

@app.post("/add")
def add_doc(doc: Doc):
    return add_document(doc.text)

@app.post("/query")
def ask(q: Query):
    answer = query_rag(q.question)
    return {"answer": answer}

@app.post("/respond")
def respond(data: Query):
    return {"response": f"Echo: {data.text}"}
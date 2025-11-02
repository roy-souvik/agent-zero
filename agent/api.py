from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import add_document, query_rag
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

class Doc(BaseModel):
    text: str

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "FastAPI is running"}

@app.post("/add")
async def add_doc(request: Request):
    try:
        data = await request.json()
        text = data.get("text")
        if not text:
            return {"error": "Missing 'text' field"}
        return add_document(text)
    except Exception as e:
        import traceback
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
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/respond")
def respond(data: Query):
    return {"response": f"Echo: {data.text}"}
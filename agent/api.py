from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "FastAPI is running"}

@app.post("/respond")
def respond(data: Query):
    return {"response": f"Echo: {data.text}"}

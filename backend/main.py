from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

from backend.graph.graph import app as rag_app


app = FastAPI(title="Agentic RAG API")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "API running"}


@app.post("/chat")
def chat(request: ChatRequest):
    result = rag_app.invoke({"question": request.message})
    return {"response": result["generation"]}

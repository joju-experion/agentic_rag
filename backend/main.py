from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

from backend.graph.graph import app as rag_app
from backend.logging_utils import capture_workflow_logs


app = FastAPI(title="Agentic RAG API")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "API running"}


@app.post("/chat")
def chat(request: ChatRequest):
    with capture_workflow_logs() as logs:
        result = rag_app.invoke({"question": request.message})

    return {"response": result["generation"], "logs": logs}

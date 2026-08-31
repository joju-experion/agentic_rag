from typing import Any, Dict
from backend.graph.state import GraphState
from backend.ingestion import retriever

def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    
    question = state['question']
    documents = retriever.invoke(question)
    
    return {"documents": documents}

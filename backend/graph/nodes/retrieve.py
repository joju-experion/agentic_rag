from typing import Any, Dict
from backend.graph.state import GraphState
from backend.ingestion import retriever
from backend.logging_utils import workflow_log

def retrieve(state: GraphState) -> Dict[str, Any]:
    workflow_log("Querying the vector store", component="RETRIEVAL")
    
    question = state['question']
    documents = retriever.invoke(question)
    
    return {"documents": documents}

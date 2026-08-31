from typing import Any, Dict

from backend.graph.chains.generation import generation_chain
from backend.graph.state import GraphState
from backend.logging_utils import workflow_log


def generate(state: GraphState) -> Dict[str, Any]:
    workflow_log("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    generation = generation_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

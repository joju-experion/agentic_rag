from typing import Any, Dict

from backend.graph.chains.retrieval_grader import retrieval_grader
from backend.graph.state import GraphState
from backend.logging_utils import workflow_log


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated web_search state
    """

    workflow_log(
        "Checking retrieved document relevance",
        component="RETRIEVAL",
    )
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    web_search = False
    for document_number, d in enumerate(documents, start=1):
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade.lower() == "yes":
            workflow_log(
                f"Document {document_number} marked relevant",
                component="RETRIEVAL",
            )
            filtered_docs.append(d)
        else:
            workflow_log(
                f"Document {document_number} marked not relevant",
                component="RETRIEVAL",
                level="WARN",
            )
            web_search = True
            continue
    return {"documents": filtered_docs, "question": question, "web_search": web_search}

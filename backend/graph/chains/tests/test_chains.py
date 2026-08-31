from dotenv import load_dotenv
load_dotenv()

from pprint import pprint
from backend.graph.chains.retrieval_grader import GradeDocument, retrieval_grader
from backend.ingestion import retriever
from backend.graph.chains.generation import generation_chain
from backend.graph.chains.hallucination_grader import (
    GradeHallucinations,
    hallucination_grader,
)
from backend.graph.chains.router import RouteQuery, question_router

def test_retrieval_grader_answer_yes() -> None:
    question = "agent memory"
    docs = retriever.invoke(question)
    doc_txt = docs[1].page_content
    
    res: GradeDocument = retrieval_grader.invoke({"question": question, "document": doc_txt})
    
    assert res.binary_score == "yes"
    
    
def test_retrieval_grader_answer_no() -> None:
    question = "Best pizza place?"
    docs = retriever.invoke(question)
    doc_txt = docs[1].page_content
    
    res: GradeDocument = retrieval_grader.invoke({"question": question, "document": doc_txt})
    
    assert res.binary_score == "no"
    
    
def test_generation_chain() -> None: 
    question = "agent memory"
    docs = retriever.invoke(question)
    
    generation = generation_chain.invoke({"context": docs, "question": question})
    pprint(generation)
    
def test_hallucination_grader_answer_yes() -> None:
    question = "agent memory"
    docs = retriever.invoke(question)
    generation = generation_chain.invoke({"question": question, "context": docs})
    
    res: GradeHallucinations = hallucination_grader.invoke({"documents": docs, "generation": generation})
    
    assert res.binary_score
    
def test_hallucination_grader_answer_no() -> None:
    question = "agent memory"
    docs = retriever.invoke(question)
    
    
    res: GradeHallucinations = hallucination_grader.invoke({"documents": docs, "generation": "In order to make pizza we need to first start with the dough."})
    
    assert not res.binary_score
    
def test_router_to_vectorstore() -> None:
    question = "agent memory"
    
    res: RouteQuery = question_router.invoke({"question": question})
    
    assert res.datasource == "vectorstore"
    
    
def test_router_to_web_search() -> None:
    question = "How to make a pizza?"
    
    res: RouteQuery = question_router.invoke({"question": question})
    
    assert res.datasource == "websearch"
    
    
    
    

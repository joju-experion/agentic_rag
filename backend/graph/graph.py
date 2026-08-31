from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from backend.graph.consts import GENERATE, GRADE_DOCUMENTS, RETRIEVE, WEBSEARCH
from backend.graph.nodes import generate, grade_documents, retrieve, web_search
from backend.graph.state import GraphState
from backend.graph.chains.hallucination_grader import hallucination_grader
from backend.graph.chains.answer_grader import answer_grader
from backend.graph.chains.router import question_router, RouteQuery
from backend.logging_utils import workflow_log

load_dotenv()


def decide_to_generate(state):
    workflow_log("Assessing retrieved context", component="DECISION")

    if state["web_search"]:
        workflow_log(
            "Some documents were not relevant; adding web search context",
            component="DECISION",
            level="WARN",
        )
        return WEBSEARCH
    else:
        workflow_log(
            "Relevant context is available; generating an answer",
            component="DECISION",
        )
        return GENERATE

def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    workflow_log("Checking answer grounding", component="VALIDATION")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    
    score = hallucination_grader.invoke({"documents": documents, "generation": generation})
    
    if hallucination_grade := score.binary_score:
        workflow_log(
            "Answer is grounded in the retrieved context",
            component="VALIDATION",
        )
        workflow_log(
            "Checking whether the answer addresses the question",
            component="VALIDATION",
        )
        
        score = answer_grader.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            workflow_log(
                "Answer addresses the question",
                component="VALIDATION",
            )
            return "useful"
        else:
            workflow_log(
                "Answer does not fully address the question; using web search",
                component="VALIDATION",
                level="WARN",
            )
            return "not useful"
    else:
        workflow_log(
            "Answer is not grounded in the context; regenerating",
            component="VALIDATION",
            level="WARN",
        )
        return "not supported"
    
def route_question(state: GraphState) -> str:
    workflow_log("Evaluating the question", component="ROUTER")
    question = state["question"]
    source: RouteQuery = question_router.invoke({"question": question})
    if source.datasource == WEBSEARCH:
        workflow_log("Selected web search", component="ROUTER")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        workflow_log("Selected the local vector store", component="ROUTER")
        return RETRIEVE
            

workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

workflow.set_conditional_entry_point(route_question, {
    WEBSEARCH: WEBSEARCH, 
    RETRIEVE: RETRIEVE
})

workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE,
    },
)

workflow.add_conditional_edges(
    GENERATE, 
    grade_generation_grounded_in_documents_and_question, 
    {
        "not supported": GENERATE,
        "useful": END,
        "not useful": WEBSEARCH
    }
)

workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_edge(GENERATE, END)

app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph.png")

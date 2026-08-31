from typing import List, TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
    """

    question: str           # user query | what to search online 
    generation: str         # LLM generated answer
    web_search: bool        # weather to search for extra results
    documents: List[str]    # retrived documents | documents we get back from the search result
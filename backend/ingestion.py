from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.logging_utils import ingestion_log

load_dotenv()


COLLECTION_NAME = "rag-chroma"
PERSIST_DIRECTORY = Path(__file__).resolve().parents[1] / ".chroma"

URLS = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
]


def initialize_vectorstore() -> Chroma:
    """Create the vector index only when the persisted collection is empty."""
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(PERSIST_DIRECTORY),
        embedding_function=OpenAIEmbeddings(),
    )

    if vectorstore.get(limit=1, include=[]).get("ids"):
        ingestion_log("Existing vector index found; skipping ingestion")
        return vectorstore

    ingestion_log("Building vector index")
    docs = [WebBaseLoader(url).load() for url in URLS]
    docs_list = [document for source_docs in docs for document in source_docs]

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250,
        chunk_overlap=0,
    )
    doc_splits = text_splitter.split_documents(docs_list)
    vectorstore.add_documents(doc_splits)
    ingestion_log(f"Stored {len(doc_splits)} document chunks")

    return vectorstore


retriever = initialize_vectorstore().as_retriever()

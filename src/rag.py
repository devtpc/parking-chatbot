from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCS_PATH = DATA_DIR / "parking_policy.md"
CHROMA_DIR = DATA_DIR / "chroma"


def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")


def get_vectorstore():
    return Chroma(
        collection_name="parking_docs",
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )


def load_documents() -> list[Document]:
    text = DOCS_PATH.read_text(encoding="utf-8")
    return [Document(page_content=text, metadata={"source": DOCS_PATH.name})]


def ingest_documents() -> None:
    docs = load_documents()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    split_docs = splitter.split_documents(docs)

    vectorstore = get_vectorstore()
    vectorstore.reset_collection()
    vectorstore.add_documents(split_docs)


def retrieve_parking_info(question: str, k: int = 3) -> str:
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(question, k=k)

    if not docs:
        return "I could not find relevant parking information."

    return "\n\n".join(doc.page_content for doc in docs)
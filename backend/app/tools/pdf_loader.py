from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter


def process_pdf(file_path: str) -> list[Document]:
    """
    Load a PDF document and split it into chunks.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    return splitter.split_documents(documents)


@tool
def load_document(file_path: str) -> list[Document]:
    """
    Tool wrapper for loading and splitting PDF documents.
    """
    return process_pdf(file_path)
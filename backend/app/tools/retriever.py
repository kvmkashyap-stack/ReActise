from langchain_core.tools import tool
from app.core.vector_store import VectorStore


vector_store = VectorStore()


@tool
def retrieve_context(
    query: str,
    user_id: str,
) -> str:
    """
    Retrieve relevant document chunks.
    """

    documents = vector_store.similarity_search(query, user_id=user_id)

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    return context
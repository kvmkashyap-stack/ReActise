from langchain_community.vectorstores import SupabaseVectorStore, FAISS
from langchain_core.documents import Document

from app.core.embeddings import embeddings  # Imports HuggingFace embeddings instance
from app.core.supabase import supabase


class VectorStore:
    """
    Handles storage and retrieval of document embeddings.
    Integrates Supabase vector search, falling back automatically to 
    an in-memory local FAISS vector store if Supabase is offline or not configured.
    """

    def __init__(
        self,
        table_name: str = "documents",
        query_name: str = "match_documents",
    ):
        self.table_name = table_name
        self.query_name = query_name
        self._supabase_store = None
        self._local_store = None
        self.use_supabase = False

        try:
            self._supabase_store = SupabaseVectorStore(
                client=supabase,
                embedding=embeddings,
                table_name=self.table_name,
                query_name=self.query_name,
            )
            self.use_supabase = True
        except Exception as e:
            print(f"[vector_store] Supabase VectorStore init failed: {e}. Falling back to FAISS.")

    def _get_local_store(self, documents: list[Document] = None):
        if self._local_store is None:
            if documents:
                self._local_store = FAISS.from_documents(documents, embeddings)
            else:
                # Initialize store with a system placeholder document
                dummy = Document(page_content="init", metadata={"user_id": "system"})
                self._local_store = FAISS.from_documents([dummy], embeddings)
        elif documents:
            self._local_store.add_documents(documents)
        return self._local_store

    def add_documents(
        self,
        documents: list[Document],
        user_id: str,
    ) -> list[str]:
        """
        Attaches user_id metadata and indexes document vector embeddings.
        """
        for doc in documents:
            doc.metadata["user_id"] = user_id

        if self.use_supabase:
            try:
                return self._supabase_store.add_documents(documents)
            except Exception as e:
                print(f"[vector_store] Supabase write failed: {e}. Falling back to FAISS store.")
                self.use_supabase = False

        self._get_local_store(documents)
        return [str(i) for i in range(len(documents))]

    def similarity_search(
        self,
        query: str,
        user_id: str,
        k: int = 4,
    ) -> list[Document]:
        """
        Retrieves similar document chunks filtered strictly by user_id.
        """
        if self.use_supabase:
            try:
                return self._supabase_store.similarity_search(
                    query=query,
                    k=k,
                    filter={"user_id": user_id},
                )
            except Exception as e:
                print(f"[vector_store] Supabase search failed: {e}. Searching via FAISS.")
                self.use_supabase = False

        local = self._get_local_store()
        # Retrieve slightly more than k elements to filter by user_id metadata in memory
        results = local.similarity_search(query, k=k * 2)
        filtered = [doc for doc in results if doc.metadata.get("user_id") == user_id]
        return filtered[:k]


# Singleton instance for easy application-wide import
vector_store = VectorStore()
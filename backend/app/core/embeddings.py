import httpx
from typing import List
from langchain_core.embeddings import Embeddings


class HuggingFaceAPIEmbeddings(Embeddings):
    """
    Query HuggingFace Inference API to retrieve 384-dimensional vectors.
    Bypasses PyTorch and sentence-transformers installations entirely
    to fit within serverless deployment bundle budgets.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"

    def _query_api(self, texts: List[str]) -> List[List[float]]:
        try:
            # Query free Hugging Face feature extraction endpoint
            response = httpx.post(
                self.api_url,
                json={"inputs": texts, "options": {"wait_for_model": True}},
                timeout=30.0
            )
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], list):
                        return [[float(x) for x in vector] for vector in result]
                    elif isinstance(result[0], float):
                        # API returned single vector for single text
                        return [[float(x) for x in result]]
            print(f"[Embeddings] Hugging Face API Error ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"[Embeddings] Hugging Face API Connection Error: {e}")

        # Fallback to zero vectors in case of network/service failure
        return [[0.0] * 384 for _ in texts]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._query_api(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._query_api([text])[0]


embeddings = HuggingFaceAPIEmbeddings()
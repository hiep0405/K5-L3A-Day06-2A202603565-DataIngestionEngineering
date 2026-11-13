"""Real embedding provider adapter using local multilingual SentenceTransformers."""
import os
from typing import Protocol

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from sentence_transformers import SentenceTransformer


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """Production embedder using sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2."""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        # Verify vector dimension with sample input
        test_emb = self.model.encode(["test"], convert_to_numpy=True)
        self.dimensions = int(test_emb.shape[1])

    def embed_documents(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return [vec.tolist() for vec in embeddings]

    def embed_query(self, question: str) -> list[float]:
        emb = self.model.encode(
            [question],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return emb[0].tolist()

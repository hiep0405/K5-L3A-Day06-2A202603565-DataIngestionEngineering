"""Store and search vectors using persistent ChromaDB."""
from pathlib import Path
from typing import Any
import chromadb
from chromadb.config import Settings
from .models import Chunk


class ChromaVectorStore:
    """Persistent on-disk vector store with Cosine distance and metadata filtering."""

    def __init__(self, persist_directory: str = "./chroma_db", dimensions: int = 384) -> None:
        self.persist_directory = Path(persist_directory).resolve()
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.dimensions = dimensions
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

    def _get_collection(self, strategy: str):
        collection_name = f"collection_strategy_{strategy.lower()}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def create_schema(self) -> None:
        """Initialize collections for Strategy A, B, and C."""
        for strat in ["a", "b", "c"]:
            self._get_collection(strat)

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]], batch_size: int = 100) -> None:
        """Validate dimensions and write stable IDs without duplicates. Overwrites existing IDs."""
        if not chunks:
            return
        if len(chunks) != len(vectors):
            raise ValueError(f"Chunk count ({len(chunks)}) != vector count ({len(vectors)})")
        
        collection = self._get_collection(strategy)
        
        total = len(chunks)
        for i in range(0, total, batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_vectors = vectors[i:i + batch_size]
            
            ids = [c.chunk_id for c in batch_chunks]
            documents = [c.text for c in batch_chunks]
            # Flatten metadata so chroma can store clean primitives
            metadatas = []
            for c in batch_chunks:
                meta = {
                    "document_id": str(c.document_id),
                    "source": str(c.source),
                    "page": int(c.page),
                    "chapter": str(c.metadata.get("chapter", "")),
                    "strategy": str(strategy).upper()
                }
                metadatas.append(meta)
                
            collection.upsert(
                ids=ids,
                embeddings=batch_vectors,
                documents=documents,
                metadatas=metadatas
            )

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Filter metadata, rank by cosine distance, and return top-k."""
        collection = self._get_collection(strategy)
        
        where_clause = None
        if filters:
            # Chroma expects key-value dict for simple eq filter
            where_clause = {k: v for k, v in filters.items()}
            
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_clause
        )
        
        hits: list[dict[str, Any]] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return hits
            
        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(ids)
        
        for chunk_id, doc, meta, dist in zip(ids, docs, metas, distances):
            # Cosine similarity = 1 - cosine distance
            score = round(1.0 - float(dist), 4)
            hits.append({
                "chunk_id": chunk_id,
                "text": doc,
                "score": score,
                "page": meta.get("page"),
                "source": meta.get("source"),
                "chapter": meta.get("chapter"),
                "metadata": meta
            })
            
        return hits

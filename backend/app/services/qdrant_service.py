from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from app.core.config import settings


class QdrantService:
    def __init__(self) -> None:
        self._client: QdrantClient | None = None
        if settings.qdrant_url:
            self._client = QdrantClient(url=settings.qdrant_url, timeout=5.0)

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def ensure_collection(self) -> None:
        if not self._client:
            return
        collections = self._client.get_collections().collections
        exists = any(col.name == settings.qdrant_collection for col in collections)
        if not exists:
            self._client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE),
            )

    def upsert_chunks(self, rows: list[dict]) -> None:
        if not self._client or not rows:
            return
        self.ensure_collection()
        points = [
            PointStruct(id=row["id"], vector=row["vector"], payload=row["payload"])
            for row in rows
        ]
        self._client.upsert(collection_name=settings.qdrant_collection, points=points)

    def search(self, vector: list[float], limit: int = 8, kb_id: int | None = None) -> list[dict]:
        if not self._client:
            return []
        self.ensure_collection()
        found = self._client.search(
            collection_name=settings.qdrant_collection,
            query_vector=vector,
            limit=limit,
            with_payload=True,
        )
        items: list[dict] = []
        for item in found:
            payload = item.payload or {}
            if kb_id is not None and payload.get("kb_id") != kb_id:
                continue
            items.append(
                {
                    "chunk_id": payload.get("chunk_id", str(item.id)),
                    "text": payload.get("text", ""),
                    "score": float(item.score),
                    "kb_id": payload.get("kb_id"),
                    "document_id": payload.get("document_id"),
                    "source_type": payload.get("source_type", "kb"),
                    "jump_url": payload.get("jump_url", ""),
                }
            )
        return items

    def delete_document_chunks(self, kb_id: int, document_id: int) -> None:
        if not self._client:
            return
        self.ensure_collection()
        self._client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=Filter(
                must=[
                    FieldCondition(key="kb_id", match=MatchValue(value=kb_id)),
                    FieldCondition(key="document_id", match=MatchValue(value=document_id)),
                ]
            ),
        )


qdrant_service = QdrantService()

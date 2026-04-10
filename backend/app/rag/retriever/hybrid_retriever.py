from __future__ import annotations

import re

from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service
from app.services.store import store


class HybridRetriever:
    _TERM_RE = re.compile(r"[A-Za-z0-9]{2,}|[\u4e00-\u9fff]{2,}")

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", "", str(text or "")).lower()

    def _extract_terms(self, query: str) -> list[str]:
        compact = self._normalize(query)
        raw_terms = [item for item in self._TERM_RE.findall(compact) if len(item) >= 2]
        expanded: list[str] = []

        for term in raw_terms:
            expanded.append(term)
            if re.fullmatch(r"[\u4e00-\u9fff]{4,}", term):
                for size in (2, 3, 4):
                    if len(term) <= size:
                        continue
                    expanded.extend(term[index : index + size] for index in range(0, len(term) - size + 1))

        if len(compact) >= 2:
            expanded.append(compact)

        unique: list[str] = []
        seen: set[str] = set()
        for term in sorted(expanded, key=len, reverse=True):
            if term in seen:
                continue
            seen.add(term)
            unique.append(term)
        return unique[:24]

    def _lexical_rank(self, query: str, kb_id: int, limit: int) -> list[dict]:
        rows = store.chunks.get(kb_id, [])
        compact_query = self._normalize(query)
        terms = self._extract_terms(query)
        hits: list[dict] = []

        for row in rows:
            text = str(row.get("text", "") or "")
            compact_text = self._normalize(text)
            if not compact_text:
                continue

            score = 0.0
            matched_terms = 0
            if compact_query and compact_query in compact_text:
                score += 10.0
                matched_terms += 1

            lead = compact_text[:180]
            for term in terms:
                if term not in compact_text:
                    continue
                matched_terms += 1
                boost = min(4.6, 0.6 + len(term) * 0.55)
                if re.fullmatch(r"[a-z0-9]{2,}", term):
                    boost += 0.8
                if term in lead:
                    boost += 0.7
                score += boost

            if matched_terms == 0 and terms:
                continue

            hits.append(
                {
                    "chunk_id": row["chunk_id"],
                    "text": text,
                    "score": score if score > 0 else 0.2,
                    "source_type": row.get("source_type", "kb"),
                    "jump_url": row.get("jump_url", ""),
                }
            )

        hits.sort(key=lambda item: (float(item.get("score", 0.0)), len(str(item.get("text", "")))), reverse=True)
        return hits[:limit]

    def _merge_ranked(self, by_vector: list[dict], lexical: list[dict], top_k: int) -> list[dict]:
        if not by_vector:
            return lexical[:top_k]
        if not lexical:
            return by_vector[:top_k]

        vector_max = max(float(item.get("score", 0.0) or 0.0) for item in by_vector) or 1.0
        lexical_max = max(float(item.get("score", 0.0) or 0.0) for item in lexical) or 1.0
        merged: dict[str, dict] = {}

        for item in by_vector:
            chunk_id = str(item.get("chunk_id", ""))
            merged[chunk_id] = {
                **item,
                "_combined_score": (float(item.get("score", 0.0) or 0.0) / vector_max) * 0.7,
            }

        for item in lexical:
            chunk_id = str(item.get("chunk_id", ""))
            lexical_score = (float(item.get("score", 0.0) or 0.0) / lexical_max) * 0.8
            if chunk_id in merged:
                merged[chunk_id]["_combined_score"] += lexical_score
                if not merged[chunk_id].get("text"):
                    merged[chunk_id]["text"] = item.get("text", "")
                if not merged[chunk_id].get("jump_url"):
                    merged[chunk_id]["jump_url"] = item.get("jump_url", "")
                if not merged[chunk_id].get("source_type"):
                    merged[chunk_id]["source_type"] = item.get("source_type", "kb")
            else:
                merged[chunk_id] = {
                    **item,
                    "_combined_score": lexical_score,
                }

        ranked = sorted(
            merged.values(),
            key=lambda item: (float(item.get("_combined_score", 0.0)), float(item.get("score", 0.0) or 0.0)),
            reverse=True,
        )
        for item in ranked:
            item.pop("_combined_score", None)
        return ranked[:top_k]

    def retrieve(self, query: str, kb_id: int, top_k: int = 20) -> list[dict]:
        lexical = self._lexical_rank(query=query, kb_id=kb_id, limit=max(top_k * 2, 20))
        vector = embedding_service.embed(query)
        by_vector = qdrant_service.search(vector=vector, limit=max(top_k * 2, 20), kb_id=kb_id)
        return self._merge_ranked(by_vector=by_vector, lexical=lexical, top_k=top_k)


hybrid_retriever = HybridRetriever()

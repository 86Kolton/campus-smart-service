from __future__ import annotations

import httpx

from app.core.config import settings


class RerankProvider:
    @staticmethod
    def _local_rank(candidates: list[dict], top_k: int) -> list[dict]:
        return sorted(candidates, key=lambda x: float(x.get("score", 0.0)), reverse=True)[:top_k]

    async def _remote_rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict] | None:
        base_url = str(settings.rerank_base_url or "").strip().rstrip("/")
        api_key = str(settings.rerank_api_key or "").strip()
        model = str(settings.rerank_model or "").strip()
        if not base_url or not api_key or not model:
            return None

        docs = [str(item.get("text", "") or "") for item in candidates]
        if not docs:
            return []

        payload = {
            "model": model,
            "query": str(query or ""),
            "documents": docs,
            "top_n": max(1, int(top_k or 8)),
            "return_documents": False,
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        timeout = max(3, int(settings.qa_timeout_seconds or 25))
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{base_url}/rerank", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results") or data.get("data") or []
        if not isinstance(results, list) or not results:
            return None

        ranked: list[dict] = []
        used = set()
        for row in results:
            try:
                idx = int(row.get("index"))
            except Exception:
                continue
            if idx < 0 or idx >= len(candidates) or idx in used:
                continue
            used.add(idx)
            item = dict(candidates[idx])
            score = row.get("relevance_score", row.get("score", item.get("score", 0.0)))
            try:
                item["score"] = float(score)
            except Exception:
                pass
            ranked.append(item)
            if len(ranked) >= top_k:
                break
        return ranked or None

    async def rerank(self, query: str, candidates: list[dict], top_k: int = 8) -> list[dict]:
        provider = str(settings.rerank_provider or "none").strip().lower()
        if provider in {"none", "", "off"}:
            return candidates[:top_k]
        if provider in {"openai_compatible", "openai", "siliconflow"}:
            try:
                ranked = await self._remote_rerank(query=query, candidates=candidates, top_k=top_k)
                if ranked is not None:
                    return ranked
            except Exception:
                return self._local_rank(candidates, top_k)
        return self._local_rank(candidates, top_k)


rerank_provider = RerankProvider()

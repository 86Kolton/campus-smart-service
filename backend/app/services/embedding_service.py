from hashlib import sha256

import httpx

from app.core.config import settings


class EmbeddingService:
    def _normalize_dim(self, vec: list[float]) -> list[float]:
        dim = max(8, int(settings.embedding_dim or 1024))
        safe = [float(x) for x in vec]
        if len(safe) == dim:
            return safe
        if len(safe) > dim:
            return safe[:dim]
        return safe + [0.0] * (dim - len(safe))

    def _embed_local_stub(self, text: str) -> list[float]:
        # Deterministic local fallback vector.
        digest = sha256(text.encode("utf-8")).digest()
        dim = max(8, int(settings.embedding_dim or 1024))
        vec: list[float] = []
        for i in range(dim):
            b = digest[i % len(digest)]
            vec.append((b / 255.0) * 2.0 - 1.0)
        return vec

    def _embed_openai_compatible(self, text: str) -> list[float] | None:
        base_url = str(settings.embedding_base_url or "").strip().rstrip("/")
        api_key = str(settings.embedding_api_key or "").strip()
        model = str(settings.embedding_model or "").strip()
        if not base_url or not api_key or not model:
            return None

        payload = {"model": model, "input": text}
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            with httpx.Client(timeout=max(3, int(settings.embedding_timeout_seconds or 25))) as client:
                resp = client.post(f"{base_url}/embeddings", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            rows = data.get("data") or []
            if not rows:
                return None
            vec = rows[0].get("embedding")
            if not isinstance(vec, list) or not vec:
                return None
            return [float(x) for x in vec]
        except Exception:
            return None

    def embed(self, text: str) -> list[float]:
        provider = str(settings.embedding_provider or "local_stub").strip().lower()
        safe_text = str(text or "").strip()

        if provider in {"openai_compatible", "openai"}:
            remote_vec = self._embed_openai_compatible(safe_text)
            if remote_vec:
                return self._normalize_dim(remote_vec)

        if provider in {"local_stub", "hash_stub", "local", "hash"}:
            return self._normalize_dim(self._embed_local_stub(safe_text))

        # Unknown provider: fallback to local stub to keep service available.
        return self._normalize_dim(self._embed_local_stub(safe_text))


embedding_service = EmbeddingService()

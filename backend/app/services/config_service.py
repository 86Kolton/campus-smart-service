from __future__ import annotations

from pathlib import Path


ALLOWED_CONFIG_KEYS = {
    "BOOTSTRAP_DEMO_DATA",
    "WECHAT_APP_ID",
    "WECHAT_APP_SECRET",
    "WECHAT_CODE2SESSION_URL",
    "WECHAT_TIMEOUT_SECONDS",
    "WECHAT_MOCK_ENABLED",
    "QA_PROVIDER",
    "QA_BASE_URL",
    "QA_API_KEY",
    "QA_MODEL",
    "QA_TIMEOUT_SECONDS",
    "EVOLUTION_AI_REVIEW_ENABLED",
    "EVOLUTION_AI_REVIEW_PROVIDER",
    "EVOLUTION_AI_REVIEW_BASE_URL",
    "EVOLUTION_AI_REVIEW_API_KEY",
    "EVOLUTION_AI_REVIEW_MODEL",
    "EVOLUTION_AI_REVIEW_TIMEOUT_SECONDS",
    "EVOLUTION_AI_REVIEW_MIN_SCORE",
    "EMBEDDING_PROVIDER",
    "EMBEDDING_BASE_URL",
    "EMBEDDING_API_KEY",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIM",
    "EMBEDDING_TIMEOUT_SECONDS",
    "RERANK_PROVIDER",
    "RERANK_BASE_URL",
    "RERANK_API_KEY",
    "RERANK_MODEL",
    "QDRANT_URL",
    "QDRANT_COLLECTION",
}

MASK_KEYS = {"WECHAT_APP_SECRET", "QA_API_KEY", "EVOLUTION_AI_REVIEW_API_KEY", "RERANK_API_KEY", "EMBEDDING_API_KEY"}


class ConfigService:
    def __init__(self) -> None:
        self.env_path = Path(__file__).resolve().parents[2] / ".env"

    def _read_lines(self) -> list[str]:
        if not self.env_path.exists():
            return []
        return self.env_path.read_text(encoding="utf-8").splitlines()

    def get_config(self) -> dict:
        lines = self._read_lines()
        values: dict[str, str] = {}
        for line in lines:
            text = str(line).strip()
            if not text or text.startswith("#") or "=" not in text:
                continue
            key, value = text.split("=", 1)
            key = key.strip()
            if key in ALLOWED_CONFIG_KEYS:
                values[key] = value.strip()

        for key in ALLOWED_CONFIG_KEYS:
            values.setdefault(key, "")

        masked = {}
        for key, value in values.items():
            if key in MASK_KEYS and value:
                if len(value) <= 8:
                    masked[key] = "*" * len(value)
                else:
                    masked[key] = f"{value[:4]}***{value[-3:]}"
            else:
                masked[key] = value
        return {"values": values, "masked": masked}

    def update_config(self, updates: dict[str, str]) -> dict:
        safe_updates = {k: str(v) for k, v in updates.items() if k in ALLOWED_CONFIG_KEYS}
        if not safe_updates:
            return self.get_config()

        lines = self._read_lines()
        if not lines and not self.env_path.exists():
            self.env_path.parent.mkdir(parents=True, exist_ok=True)

        seen = set()
        new_lines: list[str] = []
        for line in lines:
            text = str(line)
            stripped = text.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                new_lines.append(text)
                continue
            key = stripped.split("=", 1)[0].strip()
            if key in safe_updates:
                new_lines.append(f"{key}={safe_updates[key]}")
                seen.add(key)
            else:
                new_lines.append(text)

        for key, value in safe_updates.items():
            if key not in seen:
                new_lines.append(f"{key}={value}")

        self.env_path.write_text("\n".join(new_lines).strip() + "\n", encoding="utf-8")
        return self.get_config()


config_service = ConfigService()

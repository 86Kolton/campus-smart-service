from pathlib import Path
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Campus Smart Service Backend", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    allowed_origins_raw: str = Field(
        default="http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:5500,http://localhost:5500,null",
        alias="ALLOWED_ORIGINS",
    )

    postgres_url: str = Field(default="sqlite:///./campus.db", alias="POSTGRES_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    qdrant_url: str = Field(default="", alias="QDRANT_URL")
    qdrant_collection: str = Field(default="campus_kb_chunks", alias="QDRANT_COLLECTION")

    jwt_secret: str = Field(default="change-this", alias="JWT_SECRET")
    jwt_expire_minutes: int = Field(default=720, alias="JWT_EXPIRE_MINUTES")
    jwt_refresh_days: int = Field(default=14, alias="JWT_REFRESH_DAYS")
    admin_username: str = Field(default="", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="", alias="ADMIN_PASSWORD")
    admin_login_max_attempts: int = Field(default=5, alias="ADMIN_LOGIN_MAX_ATTEMPTS")
    admin_login_lock_minutes: int = Field(default=20, alias="ADMIN_LOGIN_LOCK_MINUTES")
    admin_login_window_minutes: int = Field(default=10, alias="ADMIN_LOGIN_WINDOW_MINUTES")

    wechat_app_id: str = Field(default="", alias="WECHAT_APP_ID")
    wechat_app_secret: str = Field(default="", alias="WECHAT_APP_SECRET")
    wechat_code2session_url: str = Field(
        default="https://api.weixin.qq.com/sns/jscode2session",
        alias="WECHAT_CODE2SESSION_URL",
    )
    wechat_timeout_seconds: int = Field(default=10, alias="WECHAT_TIMEOUT_SECONDS")
    wechat_mock_enabled: bool = Field(default=True, alias="WECHAT_MOCK_ENABLED")

    qa_provider: str = Field(default="openai_compatible", alias="QA_PROVIDER")
    qa_base_url: str = Field(default="", alias="QA_BASE_URL")
    qa_api_key: str = Field(default="", alias="QA_API_KEY")
    qa_model: str = Field(default="", alias="QA_MODEL")
    qa_timeout_seconds: int = Field(default=25, alias="QA_TIMEOUT_SECONDS")

    evolution_ai_review_enabled: bool = Field(default=True, alias="EVOLUTION_AI_REVIEW_ENABLED")
    evolution_ai_review_provider: str = Field(default="qa_reuse", alias="EVOLUTION_AI_REVIEW_PROVIDER")
    evolution_ai_review_base_url: str = Field(default="", alias="EVOLUTION_AI_REVIEW_BASE_URL")
    evolution_ai_review_api_key: str = Field(default="", alias="EVOLUTION_AI_REVIEW_API_KEY")
    evolution_ai_review_model: str = Field(default="", alias="EVOLUTION_AI_REVIEW_MODEL")
    evolution_ai_review_timeout_seconds: int = Field(default=25, alias="EVOLUTION_AI_REVIEW_TIMEOUT_SECONDS")
    evolution_ai_review_min_score: int = Field(default=72, alias="EVOLUTION_AI_REVIEW_MIN_SCORE")

    rerank_provider: str = Field(default="none", alias="RERANK_PROVIDER")
    rerank_base_url: str = Field(default="", alias="RERANK_BASE_URL")
    rerank_api_key: str = Field(default="", alias="RERANK_API_KEY")
    rerank_model: str = Field(default="", alias="RERANK_MODEL")

    embedding_provider: str = Field(default="local_stub", alias="EMBEDDING_PROVIDER")
    embedding_base_url: str = Field(default="", alias="EMBEDDING_BASE_URL")
    embedding_api_key: str = Field(default="", alias="EMBEDDING_API_KEY")
    embedding_model: str = Field(default="BAAI/bge-m3", alias="EMBEDDING_MODEL")
    embedding_dim: int = Field(default=1024, alias="EMBEDDING_DIM")
    embedding_timeout_seconds: int = Field(default=25, alias="EMBEDDING_TIMEOUT_SECONDS")

    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")
    bootstrap_demo_data_raw: str = Field(default="", alias="BOOTSTRAP_DEMO_DATA")

    @field_validator("postgres_url", mode="before")
    @classmethod
    def normalize_postgres_url(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text.startswith("sqlite:///"):
            return text
        raw_path = text.removeprefix("sqlite:///")
        path = Path(raw_path)
        if path.is_absolute() or (len(raw_path) >= 2 and raw_path[1] == ":"):
            return text
        resolved = (ENV_FILE.parent / path).resolve().as_posix()
        return f"sqlite:///{resolved}"

    @property
    def allowed_origins(self) -> list[str]:
        items = [item.strip() for item in self.allowed_origins_raw.split(",") if item.strip()]
        if self.is_dev_mode:
            return items
        return [item for item in items if item.lower() != "null"]

    @property
    def is_dev_mode(self) -> bool:
        return str(self.app_env or "").strip().lower() in {"dev", "local", "test"}

    @property
    def is_production(self) -> bool:
        return str(self.app_env or "").strip().lower() in {"prod", "production"}

    @property
    def wechat_mock_effective(self) -> bool:
        return self.is_dev_mode and bool(self.wechat_mock_enabled)

    @property
    def bootstrap_demo_data(self) -> bool:
        if self.is_production:
            return False
        raw = str(self.bootstrap_demo_data_raw or "").strip().lower()
        if raw in {"1", "true", "yes", "on"}:
            return True
        if raw in {"0", "false", "no", "off"}:
            return False
        return self.is_dev_mode

    @property
    def startup_issues(self) -> list[str]:
        issues: list[str] = []
        if self.is_production and str(self.jwt_secret or "").strip() in {"", "change-this"}:
            issues.append("JWT_SECRET must be configured with a non-default value in production")
        return issues


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

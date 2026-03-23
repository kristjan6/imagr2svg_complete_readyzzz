from __future__ import annotations
import os

class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    postgres_db: str = os.getenv("POSTGRES_DB", "blueprint")
    postgres_user: str = os.getenv("POSTGRES_USER", "blueprint")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "blueprint")
    postgres_host: str = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    rq_queue: str = os.getenv("RQ_QUEUE", "blueprint")
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "http://minio:9000")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_bucket: str = os.getenv("S3_BUCKET", "blueprint2dwg")
    s3_access_key_id: str = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
    s3_secret_access_key: str = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
    s3_public_base_url: str = os.getenv("S3_PUBLIC_BASE_URL", "http://localhost:9000")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "100"))
    enable_dwg: bool = os.getenv("ENABLE_DWG", "false").lower() == "true"
    oda_executable: str = os.getenv("ODA_EXECUTABLE", "")
    public_api_base: str = os.getenv("PUBLIC_API_BASE", "http://localhost:8000")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

settings = Settings()

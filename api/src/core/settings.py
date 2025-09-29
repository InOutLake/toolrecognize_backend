from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    app_port: int = 8000
    pythonunbuffered: int = 1

    # Celery
    celery_app: str = "main:celery_app"
    celery_loglevel: str = "info"
    celery_concurrency: int = 1
    worker_count: int = 2
    celery_broker_url: str = "amqp://guest:guest@rabbitmq:5672//"
    celery_result_backend: str = "rpc://"

    # Database
    postgres_db: str = "toolrecognize"
    postgres_user: str = "tooluser"
    postgres_password: str = "toolpass"
    postgres_port: int = 5432
    postgres_host: str = "postgres"

    # RabbitMQ
    rabbitmq_default_user: str = "guest"
    rabbitmq_default_pass: str = "guest"
    rabbitmq_port: int = 5672
    rabbitmq_management_port: int = 15672

    # MinIO
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_port: int = 9000
    minio_console_port: int = 9001

    # S3 / MinIO
    s3_endpoint_url: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_region: str = "us-east-1"
    s3_bucket: str = "files"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = "local.env"
        case_sensitive = False


SETTINGS = Settings()

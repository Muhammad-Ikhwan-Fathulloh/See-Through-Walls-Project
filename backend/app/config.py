"""
Konfigurasi aplikasi, dibaca dari environment variable / file .env.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+psycopg://stw:stw@db:5432/stw"

    # Auth
    jwt_secret: str = "CHANGE_ME_super_secret_key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 hari

    # Storage
    map_storage_dir: str = "storage/maps"

    # Realtime
    max_pose_rate_hz: float = 20.0  # sesuai referensi Ray-Ban ~20Hz di proyek asli

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

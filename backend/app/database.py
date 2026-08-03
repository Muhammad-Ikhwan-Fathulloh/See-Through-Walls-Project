from sqlmodel import SQLModel, create_engine, Session

from app.config import settings

engine = create_engine(settings.database_url, echo=False)


def init_db() -> None:
    """Buat semua tabel kalau belum ada. Untuk proyek production, ganti dengan Alembic migration."""
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

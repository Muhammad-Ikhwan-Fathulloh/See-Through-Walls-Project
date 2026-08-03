import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


def _uuid() -> str:
    return str(uuid.uuid4())


class User(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SpatialMap(SQLModel, table=True):
    """
    Representasi satu 'map' hasil scanning ruangan.
    file_path menunjuk ke mesh/point-cloud yang diupload (lihat routers/maps.py).
    Field feature_index_path disiapkan untuk menyimpan hasil ekstraksi fitur
    (mis. keypoint descriptors) yang dipakai proses localization nantinya —
    lihat services/localization.py untuk penjelasan kenapa ini masih stub.
    """
    id: str = Field(default_factory=_uuid, primary_key=True)
    name: str
    owner_id: str = Field(foreign_key="user.id")
    file_path: str
    feature_index_path: Optional[str] = None
    mapset_id: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ARSession(SQLModel, table=True):
    """Satu 'room' multiplayer. Analogi dengan Start Host di sample Unity asli,
    tapi di sini room di-track di server supaya device bisa join lintas jaringan."""
    id: str = Field(default_factory=_uuid, primary_key=True)
    code: str = Field(unique=True, index=True)  # kode pendek yang diketik user, mis. "ABC123"
    host_user_id: str = Field(foreign_key="user.id")
    map_id: str = Field(foreign_key="spatialmap.id")
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

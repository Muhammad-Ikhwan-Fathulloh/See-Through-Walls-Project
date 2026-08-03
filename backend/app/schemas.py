from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---- Auth ----
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Maps ----
class MapOut(BaseModel):
    id: str
    name: str
    mapset_id: Optional[str]
    created_at: datetime


# ---- Sessions (rooms) ----
class SessionCreateRequest(BaseModel):
    map_id: str


class SessionOut(BaseModel):
    id: str
    code: str
    map_id: str
    active: bool
    created_at: datetime


# ---- Localization (stub) ----
class LocalizeRequest(BaseModel):
    map_id: str
    # Di implementasi asli: kirim frame gambar (base64/multipart) atau descriptor fitur.
    # Untuk stub ini kita cuma terima placeholder supaya kontrak API sudah siap dipakai.
    frame_base64: Optional[str] = None


class Pose(BaseModel):
    position: tuple[float, float, float]
    rotation: tuple[float, float, float, float]  # quaternion x,y,z,w


class LocalizeResponse(BaseModel):
    success: bool
    pose: Optional[Pose] = None
    message: str


# ---- Realtime pose messages (dikirim lewat WebSocket, dokumentasi kontrak JSON) ----
class PoseUpdateMessage(BaseModel):
    type: str = "pose"
    player_name: str
    color: str  # hex, mis. "#3B8BD4"
    position: tuple[float, float, float]
    rotation: tuple[float, float, float, float]

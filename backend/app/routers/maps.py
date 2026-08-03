import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.auth import get_current_user
from app.config import settings
from app.database import get_session
from app.models import SpatialMap, User
from app.schemas import MapOut

router = APIRouter(prefix="/maps", tags=["maps"])

ALLOWED_EXTENSIONS = {".obj", ".ply", ".glb", ".gltf", ".zip"}


@router.post("", response_model=MapOut, status_code=201)
def upload_map(
    name: str = Form(...),
    mapset_id: str | None = Form(default=None),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Upload hasil scan ruangan (mesh/point-cloud export dari scanning app-mu).
    Ini menggantikan langkah 'upload map ke MultiSet dashboard' di alur asli —
    tapi ekstraksi fitur untuk localization TIDAK dilakukan otomatis di sini,
    lihat services/localization.py.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Ekstensi {ext} tidak didukung. Gunakan salah satu: {sorted(ALLOWED_EXTENSIONS)}",
        )

    os.makedirs(settings.map_storage_dir, exist_ok=True)
    stored_filename = f"{uuid.uuid4()}{ext}"
    dest_path = os.path.join(settings.map_storage_dir, stored_filename)

    with open(dest_path, "wb") as f:
        f.write(file.file.read())

    spatial_map = SpatialMap(
        name=name,
        owner_id=user.id,
        file_path=dest_path,
        mapset_id=mapset_id,
    )
    session.add(spatial_map)
    session.commit()
    session.refresh(spatial_map)

    return MapOut(
        id=spatial_map.id,
        name=spatial_map.name,
        mapset_id=spatial_map.mapset_id,
        created_at=spatial_map.created_at,
    )


@router.get("", response_model=list[MapOut])
def list_my_maps(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    maps = session.exec(select(SpatialMap).where(SpatialMap.owner_id == user.id)).all()
    return [
        MapOut(id=m.id, name=m.name, mapset_id=m.mapset_id, created_at=m.created_at)
        for m in maps
    ]


@router.get("/{map_id}", response_model=MapOut)
def get_map(
    map_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    m = session.get(SpatialMap, map_id)
    if not m or m.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Map tidak ditemukan")
    return MapOut(id=m.id, name=m.name, mapset_id=m.mapset_id, created_at=m.created_at)


@router.delete("/{map_id}", status_code=204)
def delete_map(
    map_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    m = session.get(SpatialMap, map_id)
    if not m or m.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Map tidak ditemukan")
    if os.path.exists(m.file_path):
        os.remove(m.file_path)
    session.delete(m)
    session.commit()

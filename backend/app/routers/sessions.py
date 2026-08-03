import random
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth import get_current_user
from app.database import get_session
from app.models import ARSession, SpatialMap, User
from app.schemas import SessionCreateRequest, SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("", response_model=SessionOut, status_code=201)
def create_session(
    body: SessionCreateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Analogi 'Start Host' di sample Unity asli, tapi room-nya di-track di server
    supaya client bisa join dari WebSocket meskipun beda jaringan."""
    spatial_map = session.get(SpatialMap, body.map_id)
    if not spatial_map:
        raise HTTPException(status_code=404, detail="Map tidak ditemukan")

    code = _generate_code()
    while session.exec(select(ARSession).where(ARSession.code == code)).first():
        code = _generate_code()

    ar_session = ARSession(code=code, host_user_id=user.id, map_id=body.map_id)
    session.add(ar_session)
    session.commit()
    session.refresh(ar_session)

    return SessionOut(
        id=ar_session.id,
        code=ar_session.code,
        map_id=ar_session.map_id,
        active=ar_session.active,
        created_at=ar_session.created_at,
    )


@router.get("/{code}", response_model=SessionOut)
def get_session_by_code(code: str, session: Session = Depends(get_session)):
    """Endpoint publik (tidak perlu auth) supaya client cukup tahu kode room
    untuk join — dipakai sebelum connect WebSocket."""
    ar_session = session.exec(select(ARSession).where(ARSession.code == code.upper())).first()
    if not ar_session or not ar_session.active:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan atau sudah berakhir")
    return SessionOut(
        id=ar_session.id,
        code=ar_session.code,
        map_id=ar_session.map_id,
        active=ar_session.active,
        created_at=ar_session.created_at,
    )


@router.post("/{code}/close", status_code=204)
def close_session(
    code: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    ar_session = session.exec(select(ARSession).where(ARSession.code == code.upper())).first()
    if not ar_session:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan")
    if ar_session.host_user_id != user.id:
        raise HTTPException(status_code=403, detail="Hanya host yang boleh menutup sesi")
    ar_session.active = False
    session.add(ar_session)
    session.commit()

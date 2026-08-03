from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models import User
from app.schemas import LocalizeRequest, LocalizeResponse
from app.services.localization import localize as localize_service

router = APIRouter(prefix="/localize", tags=["localization"])


@router.post("", response_model=LocalizeResponse)
def localize(body: LocalizeRequest, user: User = Depends(get_current_user)):
    """Lihat services/localization.py — endpoint ini stub, belum ada CV asli."""
    return localize_service(body)

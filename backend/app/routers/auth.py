from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_session
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == body.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username sudah dipakai")

    user = User(username=body.username, hashed_password=hash_password(body.password))
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == body.username)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Username atau password salah")

    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, localize, maps, sessions, ws

app = FastAPI(
    title="See-Through-Walls Self-Hosted Backend",
    description=(
        "Alternatif self-hosted untuk sebagian fungsi MultiSet.ai: auth, map storage, "
        "session/room management, dan realtime pose relay lewat WebSocket. "
        "Localization masih stub — lihat app/services/localization.py."
    ),
    version="0.1.0",
)

# Longgarkan CORS untuk development. Untuk production, ganti allow_origins
# dengan domain spesifik.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(maps.router)
app.include_router(sessions.router)
app.include_router(localize.router)
app.include_router(ws.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}

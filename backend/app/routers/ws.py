from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select

from app.auth import decode_token
from app.database import engine
from app.models import ARSession
from app.services.pose_relay import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/sessions/{code}")
async def session_pose_relay(
    websocket: WebSocket,
    code: str,
    token: str = Query(...),
    name: str = Query(...),
):
    """
    Kontrak pesan JSON yang dikirim/diterima lewat koneksi ini (lihat
    schemas.PoseUpdateMessage):

        {
          "type": "pose",
          "player_name": "Alice",
          "color": "#3B8BD4",
          "position": [x, y, z],
          "rotation": [x, y, z, w]
        }

    Server broadcast pesan ini ke semua device lain yang connect ke room `code`
    yang sama. Sender tidak menerima balik pesannya sendiri.
    """
    user_id = decode_token(token)
    if user_id is None:
        await websocket.close(code=4401)  # custom close code = unauthorized
        return

    code = code.upper()
    with Session(engine) as db_session:
        ar_session = db_session.exec(select(ARSession).where(ARSession.code == code)).first()
    if not ar_session or not ar_session.active:
        await websocket.close(code=4404)  # custom close code = room not found
        return

    await manager.connect(code, websocket, name)
    try:
        while True:
            raw = await websocket.receive_json()
            # Broadcast apa adanya ke player lain di room — validasi ringan saja,
            # supaya latency tetap rendah (~20Hz target, lihat config.max_pose_rate_hz)
            if raw.get("type") == "pose":
                await manager.broadcast(code, websocket, raw)
    except WebSocketDisconnect:
        manager.disconnect(code, websocket)

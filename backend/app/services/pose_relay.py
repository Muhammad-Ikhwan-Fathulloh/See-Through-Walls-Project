"""
Connection manager untuk relay pose real-time.

Ini menggantikan peran P2P (Netcode over UTP di Flow 1, Apple MultipeerConnectivity
di Flow 2) pada proyek asli — bedanya semua device kirim pose ke server ini, server
broadcast ke device lain di room yang sama. Konsekuensinya:
  + Bisa dipakai lintas jaringan/internet (tidak wajib satu WiFi lokal)
  - Nambah latency (extra hop lewat server) dibanding P2P langsung
  - Server ini jadi single point of failure untuk sesi yang sedang berjalan

Untuk skala banyak instance server (horizontal scaling), ganti in-memory dict di
bawah ini dengan Redis pub/sub per room code.
"""
from __future__ import annotations

import json
from collections import defaultdict

from fastapi import WebSocket


class RoomConnectionManager:
    def __init__(self) -> None:
        # room_code -> {websocket: player_name}
        self._rooms: dict[str, dict[WebSocket, str]] = defaultdict(dict)

    async def connect(self, room_code: str, websocket: WebSocket, player_name: str) -> None:
        await websocket.accept()
        self._rooms[room_code][websocket] = player_name

    def disconnect(self, room_code: str, websocket: WebSocket) -> None:
        room = self._rooms.get(room_code)
        if room and websocket in room:
            del room[websocket]
        if room is not None and not room:
            del self._rooms[room_code]

    async def broadcast(self, room_code: str, sender: WebSocket, message: dict) -> None:
        """Kirim pesan ke semua device lain di room yang sama (tidak dikirim balik ke sender)."""
        room = self._rooms.get(room_code, {})
        payload = json.dumps(message)
        for ws in list(room.keys()):
            if ws is sender:
                continue
            try:
                await ws.send_text(payload)
            except Exception:
                # Connection sudah putus, biarkan bersih sendiri lewat disconnect()
                pass

    def player_count(self, room_code: str) -> int:
        return len(self._rooms.get(room_code, {}))


manager = RoomConnectionManager()

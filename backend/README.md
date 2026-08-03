# Backend — See-Through-Walls Self-Hosted

Alternatif self-hosted untuk sebagian fungsi MultiSet.ai.

## Jalankan (Docker, direkomendasikan)

```bash
cp .env.example .env
# edit .env, minimal ganti JWT_SECRET
docker compose up --build
```

Buka `http://localhost:8000/docs` untuk Swagger UI interaktif.

## Jalankan tanpa Docker (dev lokal)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# butuh Postgres jalan sendiri, atau ganti DATABASE_URL di .env ke SQLite:
# DATABASE_URL=sqlite:///./dev.db

cp .env.example .env
uvicorn app.main:app --reload
```

## Alur pemakaian API

1. `POST /auth/register` → dapat JWT
2. `POST /maps` (multipart, header `Authorization: Bearer <token>`) → upload hasil scan ruangan, dapat `map_id`
3. `POST /sessions` dengan `map_id` → dapat `code` room (host)
4. Device lain: `GET /sessions/{code}` → validasi room ada
5. Semua device: connect `ws://.../ws/sessions/{code}?token=<jwt>&name=<nama>`
6. Kirim/terima pose lewat WebSocket, format JSON:
   ```json
   {
     "type": "pose",
     "player_name": "Alice",
     "color": "#3B8BD4",
     "position": [1.2, 0.0, 3.4],
     "rotation": [0, 0, 0, 1]
   }
   ```
7. (Opsional, masih stub) `POST /localize` dengan `map_id` — lihat `app/services/localization.py`
   untuk penjelasan kenapa ini belum menghasilkan pose asli dan opsi cara mengisinya.

## Struktur

- `app/routers/auth.py` — register & login (JWT)
- `app/routers/maps.py` — upload & manajemen file map
- `app/routers/sessions.py` — create/join room (analogi Start Host)
- `app/routers/ws.py` — WebSocket realtime pose relay (analogi P2P Netcode/MultipeerConnectivity)
- `app/routers/localize.py` + `app/services/localization.py` — stub localization

## Yang belum ada (perlu kamu tambah kalau mau production-ready)

- Rate limiting per koneksi WebSocket (biar 1 device nakal tidak flood room)
- S3/object storage untuk file map (saat ini local disk di container)
- Alembic migration (saat ini `create_all` langsung, oke untuk dev, tidak untuk schema change di production)
- Implementasi CV asli untuk `/localize`
- Redis pub/sub kalau backend di-scale ke lebih dari 1 instance

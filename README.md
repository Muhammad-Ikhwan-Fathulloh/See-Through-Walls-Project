# See-Through-Walls (Custom Fork)

Multiplayer AR "wall vision" — lihat teman lewat tembok dalam AR, di HP atau Meta Ray-Ban glasses.

Fork/ekstensi dari [bilawalsidhu/see-through-walls](https://github.com/bilawalsidhu/see-through-walls),
dengan tambahan **backend self-hosted (FastAPI)** sebagai alternatif MultiSet.ai cloud.

## Dua mode backend

| | MultiSet.ai (default) | Self-hosted (folder `backend/`) |
|---|---|---|
| Localization / VPS | Cloud, siap pakai, akurat | Stub — perlu kamu isi algoritma CV asli |
| Map storage | Cloud MultiSet | PostgreSQL + local/S3 storage |
| Sinkronisasi pose antar player | P2P WiFi lokal (Netcode / MultipeerConnectivity) | WebSocket lewat server — bisa lintas jaringan/internet |
| Auth user | Tidak ada (cuma nama label) | JWT, register/login |
| Biaya | Sesuai pricing MultiSet | Kamu tanggung sendiri (hosting) |
| Kompleksitas setup | Rendah | Tinggi |

> **Kenapa localization di backend sendiri cuma stub?**
> VPS asli butuh: scanning ruangan jadi point cloud/mesh, feature extraction & matching (mis. ORB, SIFT, atau learned features),
> pose estimation (PnP + RANSAC), map merging antar sesi scan. Ini project riset/engineering tersendiri (mirip yang dikerjakan
> tim MultiSet, atau proyek seperti COLMAP / ORB-SLAM3 / ARCore Cloud Anchors). Backend di repo ini menyediakan
> **arsitektur lengkap di sekitarnya** (auth, map storage, room/session, realtime pose relay) dengan endpoint localization
> yang jelas ditandai `TODO` — supaya kamu bisa colok algoritma CV pilihanmu sendiri, atau integrasi ke layanan VPS lain
/// atau tetap fallback ke MultiSet.ai untuk localization saja sambil pakai backend ini untuk sisanya.

## Struktur repo

```
see-through-walls-project/
├── backend/                  # FastAPI backend self-hosted (opsional, alternatif MultiSet.ai)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── auth.py
│   │   ├── routers/          # auth, maps, sessions, websocket pose relay
│   │   └── services/         # pose relay manager, localization stub
│   ├── storage/maps/         # file map/mesh yang diupload
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
├── unity-client/
│   └── Scripts/Backend/      # C# script untuk konek ke backend custom (REST + WebSocket)
│       ├── ApiClient.cs
│       ├── PoseWebSocketClient.cs
│       └── BackendConfig.cs
├── docs/
│   ├── ARCHITECTURE.md
│   └── SETUP-WINDOWS.md
└── README.md
```

> Catatan: `unity-client/` berisi **script tambahan** untuk dipasang ke dalam project Unity yang sudah kamu buat
> mengikuti sample resmi MultiSet (lihat `docs/SETUP-WINDOWS.md`). Ini bukan project Unity utuh — asset besar
> (scene, model 3D, package MultiSet SDK) tetap diambil dari Unity Package Manager seperti biasa, karena
> binary Unity project tidak cocok ditaruh mentah di sini.

## Quick start backend

```bash
cd backend
cp .env.example .env
docker compose up --build
```

Backend jalan di `http://localhost:8000`, dokumentasi interaktif di `http://localhost:8000/docs`.

Detail lengkap arsitektur: lihat [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
Detail setup Unity/Windows/Ray-Ban: lihat [`docs/SETUP-WINDOWS.md`](docs/SETUP-WINDOWS.md).

## Lisensi

MIT — lihat [LICENSE](LICENSE). Proyek asli oleh Bilawal Sidhu, kode tambahan di repo ini oleh kamu.

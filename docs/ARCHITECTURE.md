# Arsitektur

## Versi asli (MultiSet.ai)

```
Unity App (host)  <--- WiFi lokal, Netcode/MultipeerConnectivity, P2P --->  Unity App / Ray-Ban client
       |                                                                            |
       +--------------------------- MultiSet Cloud VPS ---------------------------+
                       (map storage + localization, lewat SDK)
```

Tidak ada backend custom. Semua real-time sync pose antar player lewat koneksi
P2P langsung di WiFi lokal — cepat, tapi device wajib satu jaringan.

## Versi dengan backend self-hosted (repo ini)

```
Unity App (host)  ---REST (auth,map,session)--->  FastAPI Backend  <---REST---  Unity App / client
       |                                                  |                            |
       |                                            PostgreSQL                         |
       |                                        (users, maps, sessions)                |
       |                                                                                |
       +----------------------- WebSocket pose relay (lewat backend) -----------------+
                              (bisa lintas jaringan/internet)

Localization: tetap lewat MultiSet SDK (default), ATAU lewat POST /localize
              di backend (stub, perlu diisi pipeline CV sendiri)
```

### Kenapa pose relay lewat server, bukan tetap P2P?

Trade-off yang diambil:
- **P2P (asli)**: latency terendah, tapi wajib satu WiFi lokal, tidak bisa lintas gedung/kota
- **Server relay (backend ini)**: bisa dipakai lintas jaringan lewat internet, tapi nambah 1 hop
  (device → server → device lain), dan server jadi single point of failure untuk sesi aktif

### Komponen backend

| Komponen | Tanggung jawab | Menggantikan apa di versi asli |
|---|---|---|
| `routers/auth.py` | Register/login, JWT | Tidak ada di versi asli (versi asli cuma nama label, tanpa akun) |
| `routers/maps.py` | Upload & simpan file mesh/point-cloud hasil scan | MultiSet dashboard map upload |
| `routers/sessions.py` | Create/join room, kode sesi | `Start Host` / IP address manual di versi asli |
| `routers/ws.py` + `services/pose_relay.py` | Broadcast pose real-time antar device di room yang sama | Netcode over UTP (Flow 1) / MultipeerConnectivity (Flow 2) |
| `routers/localize.py` + `services/localization.py` | **Stub.** Kontrak API siap, algoritma belum ada | MultiSet VPS localization |

### Skalabilitas (untuk dipikirkan sebelum production)

- `RoomConnectionManager` di `pose_relay.py` saat ini in-memory per instance server —
  kalau backend di-deploy lebih dari 1 instance (mis. di belakang load balancer),
  dua device di room yang sama bisa nyasar ke instance berbeda dan tidak saling lihat.
  Solusinya: ganti ke Redis pub/sub per room code.
- File map disimpan di local disk container (`storage/maps/`) — untuk production,
  pindah ke object storage (S3-compatible) supaya tidak hilang saat container di-redeploy.
- Localization asli (kalau diimplementasikan) kemungkinan besar CPU/GPU-intensive —
  pertimbangkan worker terpisah (mis. Celery/RQ) supaya tidak blocking request HTTP.

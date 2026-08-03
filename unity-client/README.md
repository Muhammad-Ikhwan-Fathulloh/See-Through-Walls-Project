# Unity Client — Integrasi Backend Self-Hosted

Script di folder `Scripts/Backend/` ini **ditambahkan ke dalam** project Unity yang sudah
kamu setup mengikuti sample resmi MultiSet (lihat `docs/SETUP-WINDOWS.md` di root repo).
Bukan pengganti seluruh project Unity.

## Cara pasang

1. Sudah punya project Unity dengan MultiSet SDK terinstall & scene `MultiPlayerSample` bisa jalan (Flow A/B seperti biasa)
2. Copy folder `Scripts/Backend/` ke dalam `Assets/` project Unity kamu
3. Buat asset config: klik kanan di Project window → **Create → SeeThroughWalls → BackendConfig**
   - Isi `baseUrl` sesuai alamat backend FastAPI kamu
4. Tambahkan komponen `ApiClient` dan `PoseWebSocketClient` ke GameObject (mis. GameObject `NetworkUI` yang sudah ada), drag BackendConfig asset ke field `config` masing-masing

## Yang perlu kamu sambungkan sendiri ke `MultiplayerManager` yang ada

Script ini **tidak otomatis** menggantikan `MultiplayerManager`/`MultisetMultipeerBridge` bawaan —
kamu perlu modifikasi scene supaya:

- Saat **Start Host**: panggil `ApiClient.CreateSession(mapId, ...)`, lalu `PoseWebSocketClient.Connect(code, name, color)`
- Saat **Start Client**: panggil `ApiClient.GetSession(code, ...)` untuk validasi, lalu `PoseWebSocketClient.Connect(...)`
- Di loop update posisi kamera lokal (biasanya sudah ada di `MultiplayerManager`): panggil
  `PoseWebSocketClient.SendPose(camera.position, camera.rotation)` tiap frame
- Subscribe `PoseWebSocketClient.OnRemotePoseReceived` untuk update/spawn avatar remote player
  (gantikan bagian yang sebelumnya baca dari Netcode/MultipeerConnectivity)

## Localization tetap perlu sumber lain

`ApiClient` di sini tidak mengurus localization (menentukan posisi device di map). Untuk sementara,
tetap pakai `SingleFrameLocalizationManager` dari MultiSet SDK seperti biasa (baca posisi hasil
localize-nya, lalu kirim lewat `PoseWebSocketClient.SendPose`). Endpoint `POST /localize` di backend
baru berguna kalau kamu sudah isi pipeline CV asli — lihat `backend/app/services/localization.py`.

# Flow Lengkap: See-Through-Walls di Windows

> Dokumen ini fokus setup MultiSet.ai (cara default). Kalau mau pakai backend
> self-hosted (folder `backend/` di repo ini) sebagai pengganti sebagian fungsi
> MultiSet, lihat `backend/README.md` untuk setup server-nya dan
> `unity-client/README.md` untuk cara sambungkan Unity ke backend tersebut.
> Localization tetap disarankan pakai MultiSet SDK sampai kamu isi sendiri
> pipeline CV di `backend/app/services/localization.py`.

Dua versi:
- **Versi A — HP ↔ HP (tanpa Ray-Ban)** — 100% bisa dikerjakan di Windows.
- **Versi B — iPhone + Meta Ray-Ban** — sebagian besar di Windows, tapi build companion app WAJIB pakai Mac (fisik atau cloud), karena itu proyek Xcode/Swift.

---

## FASE 0 — Persiapan (berlaku untuk kedua versi)

### 0.1 Software di PC Windows
- [ ] Unity Hub → install **Unity 6000.0.36f1+** (minimum 2022.3.36)
  - Saat install, centang module: **Android Build Support** (SDK + NDK + OpenJDK)
  - Kalau versi B juga jalan: centang **iOS Build Support** juga (untuk build Unity host ke iPhone)
- [ ] Git untuk Windows
- [ ] (Opsional) Android Studio — buat lihat log lewat `adb logcat` kalau ada bug

### 0.2 Akun & kredensial
- [ ] Daftar akun di [multiset.ai](https://multiset.ai)
- [ ] Dari dashboard MultiSet, generate:
  - `clientId`
  - `clientSecret`
- [ ] Simpan kedua nilai ini — dipakai di semua device (Unity & Xcode)

### 0.3 Map ruangan (WAJIB sebelum multiplayer bisa jalan)
- [ ] Scan ruangan fisik yang mau dipakai testing, upload ke MultiSet (lihat docs.multiset.ai untuk cara scan)
- [ ] Catat kode hasil scan:
  - `mapCode` (kalau satu map tunggal), **atau**
  - `mapsetCode` (kalau gabungan beberapa map)
- [ ] ⚠️ Kode ini harus **identik** di semua device yang join sesi yang sama

### 0.4 Hardware
- [ ] Minimal 2 device untuk testing (HP Android/iOS, atau kombinasi)
- [ ] Semua device harus terhubung ke **WiFi lokal yang sama** — tidak ada relay cloud, koneksi murni P2P

---

## VERSI A — Flow HP ↔ HP (tanpa Ray-Ban)

### A.1 Setup project Unity
1. Unity Hub → New Project → template 3D
2. Window → Package Manager → tombol **+** → **Add package from git URL**:
   ```
   https://github.com/MultiSet-AI/multiset-unity-sdk.git
   ```
3. Di Package Manager, klik **MultiSet-SDK** → tab **Samples** → **Import** di samping *Sample Scenes*
4. Buka scene:
   ```
   Assets/MultiSet/Scenes/MultiplayerSample/MultiPlayerSample.unity
   ```

### A.2 Konfigurasi wajib
1. **Credentials** — buka asset `MultiSetConfig` di `Assets/MultiSet/Resources`, isi `clientId` & `clientSecret`
2. **Map code** — di komponen `SingleFrameLocalizationManager` pada scene `MultiPlayerSample`, isi `mapCode` **atau** `mapsetCode`
3. **Layer khusus** — Edit → Project Settings → Tags and Layers → tambah User Layer bernama **persis** `CollisionMesh` (case-sensitive)
   - Layer ini dipakai `MapMeshColliderSetup` untuk raycast skeleton-through-walls; kalau nama salah, efek gagal diam-diam
4. **Build target** — File → Build Settings → pilih platform (Android dan/atau iOS) → **Switch Platform**

### A.3 Build & install
1. File → Build Settings → Build → hasilkan APK (Android) — bisa langsung dari Windows
2. Kalau target iOS: Build akan menghasilkan project Xcode → **butuh Mac** untuk compile jadi IPA & install (langkah ini satu-satunya bagian versi A yang perlu Mac, kalau device-nya iPhone)
3. Install APK/IPA ke masing-masing device
4. Pastikan semua device satu WiFi

### A.4 Menjalankan sesi
1. Buka app di **Device A** dan **Device B**, keduanya di scene `MultiplayerSample`
2. Isi **nama** di kolom masing-masing device (label avatar)
3. **Device A (host):** tap **Start Host**
4. Cari IP Device A:
   - iOS: Settings → Wi-Fi → tap (i) di jaringan aktif → IP Address
   - Android: Settings → About phone → Status (atau Network & internet → Wi-Fi → nama jaringan → View more)
   - Biasanya berbentuk `192.168.x.x` atau `10.0.x.x`
5. **Device B (client):** masukkan IP Device A → tap **Start Client** → tunggu status *"Connected to host"*
6. **Localize di kedua device**: arahkan kamera keliling ruangan, trigger localize dari UI scene
   - Kedua device harus sukses localize dulu sebelum avatar muncul
7. **Main:** setelah localize sukses, avatar lawan main muncul di posisi real-world. Jalan di belakang tembok yang termasuk geometri map → avatar berubah jadi skeleton silhouette di layar lawan

### A.5 Troubleshooting cepat
| Gejala | Kemungkinan penyebab |
|---|---|
| Tidak connect Host/Client | Beda WiFi, atau firewall Windows blokir Unity saat testing di PC |
| Avatar tidak muncul | Salah satu device belum sukses localize |
| Skeleton-through-walls tidak jalan | Layer `CollisionMesh` salah nama/belum dibuat |
| Localize gagal terus | mapCode salah, atau ruangan aslinya beda dari yang discan |

---

## VERSI B — Flow iPhone + Meta Ray-Ban

Role di versi ini **fixed**: Unity app selalu jadi **host** dan **wajib di iOS**; app `MultisetRayBanTracking` selalu jadi **client** yang dipasangkan ke kacamata.

### B.1 Kebutuhan tambahan
- [ ] Mac (fisik, atau cloud seperti MacinCloud/MacStadium, atau GitHub Actions macOS runner untuk CI build)
- [ ] Xcode 15+ di Mac tersebut
- [ ] iOS 17+ di iPhone yang akan pairing dengan glasses
- [ ] Meta Ray-Ban glasses + app **Meta AI** terinstall di iPhone tsb
- [ ] Apple Developer account (untuk sign & install app ke device fisik)
- [ ] (Untuk streaming beneran dari kacamata) `CLIENT_TOKEN` / `META_APP_ID` sesuai setup Meta DAT — tidak wajib kalau cuma mau build & lihat UI

### B.2 Setup companion app (di Mac)
1. Clone repo:
   ```
   git clone https://github.com/bilawalsidhu/see-through-walls.git
   ```
2. Buka project:
   ```
   open see-through-walls/Multiset-RayBan-Tracking/MultisetRayBanTracking.xcodeproj
   ```
3. Set kredensial: `MULTISET_CLIENT_ID` & `MULTISET_CLIENT_SECRET` sebagai build settings di Xcode
   - Fallback cepat: isi `defaultClientID` / `defaultClientSecret` di `MultisetRayBanTracking/Services/LocalizationConfig.swift`
4. Build & install ke iPhone yang akan dipasangkan ke glasses (iOS 17+)

### B.3 Setup Meta Ray-Ban
1. Di iPhone yang sama, install **Meta AI** app
2. Pairing Ray-Ban Meta glasses lewat Meta AI app
3. Di Meta AI app → Settings → aktifkan **Developer Mode** (wajib, tanpa ini glasses tidak bisa diminta akses kamera)

### B.4 Sinkronkan map code
1. Buka app `MultisetRayBanTracking` → Settings (ikon gear)
2. Masukkan `mapCode`/`mapsetCode` yang **sama persis** dengan yang diisi di `SingleFrameLocalizationManager` pada Unity scene

### B.5 Setup Unity host (bisa dikerjakan di Windows, sama seperti Versi A langkah A.1–A.2)
- Ikuti Fase A.1 dan A.2 seperti biasa
- Build target: **iOS** (bukan Android)
- Hasil build Unity untuk iOS berupa project Xcode → langkah compile jadi IPA & install ke iPhone host **butuh Mac**

### B.6 Menjalankan sesi
1. **Di iPhone Unity (host):** buka scene `MultiplayerSample`, isi nama host, tap **Start Host**
2. **Di iPhone yang pairing glasses:** buka `MultisetRayBanTracking` → tap **"Connect My Glasses"** (tunggu indikator hijau)
3. Dari feature selection screen, pilih **Multiplayer Demo**
4. Isi display name (atau pakai default nama device) → tap **Join Session**
   - App otomatis cari host lewat Apple MultipeerConnectivity di WiFi lokal, tidak perlu ketik IP
   - Saat muncul prompt **Local Network permission**, tap **Allow**
5. Tap **Start Streaming** — video dari glasses mulai dikirim ke iPhone dan dilokalisasi terhadap map MultiSet
6. Setelah localize sukses, pose glasses-wearer dikirim ke Unity host **~20x/detik**
7. Selama dipakai, wearable app re-localize otomatis **~tiap 1 detik** di background untuk jaga akurasi
8. Keluar dari layar Multiplayer Demo → koneksi & video stream ditutup otomatis dengan bersih

### B.7 Catatan teknis tambahan
- Transport: **Apple MultipeerConnectivity**, service type `multiset-sdk`, tanpa internet setelah kedua device connect
- Pose dikirim sebagai **unreliable datagram ~20Hz** (prioritas kecepatan, bukan keandalan); identitas player (nama + warna avatar) dikirim **reliable**
- Re-localization pakai **video-frame fast path**, bukan foto still — hindari round-trip Bluetooth ke glasses
- Koordinat pakai **left-handed system** (default Unity), jadi pose dari client langsung cocok tanpa konversi (`isRightHanded=false`)
- Tidak ada bunyi sukses/gagal re-localize di speaker glasses selama mode multiplayer (silent by design)

### B.8 Troubleshooting cepat
| Gejala | Kemungkinan penyebab |
|---|---|
| Glasses gagal connect di Meta AI app | Developer Mode belum aktif |
| Wearable app tidak nemu host | Beda WiFi, atau Local Network permission ditolak |
| Localize gagal di glasses | mapCode di app Settings tidak sama dengan Unity |
| Streaming tidak jalan sama sekali | `CLIENT_TOKEN`/`META_APP_ID` (Meta DAT) belum diset — ini wajib untuk streaming asli, bukan cuma build |

---

## Ringkasan: apa yang bisa & tidak bisa di Windows

| Tugas | Bisa di Windows? |
|---|---|
| Setup & konfigurasi project Unity | ✅ Ya |
| Build APK Android | ✅ Ya, langsung |
| Build project Unity untuk iOS (generate Xcode project) | ✅ Ya, tapi hasil akhirnya tetap perlu Mac untuk compile ke IPA |
| Compile IPA (Unity host iOS) | ❌ Butuh Mac |
| Build companion app `MultisetRayBanTracking` | ❌ Butuh Mac (ini native Xcode/Swift project) |
| Testing Flow A (Android-Android) | ✅ Sepenuhnya di Windows |
| Testing Flow B (iPhone+glasses) | ⚠️ Setup Unity di Windows, tapi compile & pairing tetap butuh Mac + iPhone fisik |

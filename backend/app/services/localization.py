"""
STUB — bukan implementasi VPS (Visual Positioning System) yang sesungguhnya.

Localization asli (yang dilakukan MultiSet, Niantic Lightship, ARCore Cloud Anchors, dll)
umumnya butuh pipeline seperti ini:

  1. Offline, saat scanning map:
     - Rekam video/foto ruangan dari banyak sudut
     - Structure-from-Motion (mis. COLMAP) untuk hasilkan point cloud + pose kamera
     - Ekstrak feature descriptor tiap keypoint 3D (mis. SIFT/ORB/learned features
       seperti SuperPoint) dan simpan sebagai index yang bisa dicari cepat

  2. Online, saat device mau localize:
     - Device kirim 1 frame kamera (atau descriptor yang sudah diekstrak on-device)
     - Server (atau on-device, tergantung arsitektur) cocokkan feature frame ini
       dengan index map tersimpan (feature matching, mis. FLANN/kNN)
     - Dari korespondensi 2D-3D yang match, hitung pose kamera pakai PnP + RANSAC
     - Kembalikan pose (posisi + rotasi) relatif terhadap origin map

Implementasi penuh ini di luar scope skeleton backend ini. Fungsi di bawah cuma
placeholder supaya kontrak API (`POST /localize`) sudah siap dipakai dari Unity/iOS,
dan gampang diganti nanti dengan salah satu opsi:
  a) Isi pipeline CV sendiri (COLMAP untuk mapping offline + custom matching service)
  b) Panggil layanan VPS pihak ketiga dari sini (termasuk tetap pakai MultiSet API
     khusus untuk langkah localization saja, sementara sisanya pakai backend ini)
  c) Pakai ARCore/ARKit Cloud Anchors kalau targetnya cukup 1 vendor platform
"""
from app.schemas import LocalizeRequest, LocalizeResponse, Pose


def localize(request: LocalizeRequest) -> LocalizeResponse:
    # TODO: ganti implementasi ini dengan pipeline CV asli.
    # Saat ini selalu mengembalikan failure supaya tidak menyesatkan seolah-olah
    # localization sungguhan sudah berjalan.
    return LocalizeResponse(
        success=False,
        pose=None,
        message=(
            "Localization belum diimplementasikan di backend self-hosted ini. "
            "Lihat docstring services/localization.py untuk opsi implementasi."
        ),
    )

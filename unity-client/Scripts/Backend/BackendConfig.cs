using UnityEngine;

namespace SeeThroughWalls.Backend
{
    /// <summary>
    /// ScriptableObject konfigurasi untuk backend self-hosted.
    /// Buat instance-nya lewat Assets/Create/SeeThroughWalls/BackendConfig,
    /// isi baseUrl sesuai alamat server FastAPI kamu (mis. http://192.168.1.10:8000
    /// untuk testing di WiFi lokal, atau domain publik kalau sudah di-deploy).
    /// </summary>
    [CreateAssetMenu(fileName = "BackendConfig", menuName = "SeeThroughWalls/BackendConfig")]
    public class BackendConfig : ScriptableObject
    {
        [Tooltip("Contoh: http://192.168.1.10:8000 (tanpa trailing slash)")]
        public string baseUrl = "http://localhost:8000";

        [Tooltip("Diisi otomatis setelah login/register lewat ApiClient")]
        public string accessToken;

        public string WebSocketUrl(string sessionCode, string playerName)
        {
            string wsBase = baseUrl.Replace("http://", "ws://").Replace("https://", "wss://");
            string encodedName = UnityEngine.Networking.UnityWebRequest.EscapeURL(playerName);
            return $"{wsBase}/ws/sessions/{sessionCode}?token={accessToken}&name={encodedName}";
        }
    }
}

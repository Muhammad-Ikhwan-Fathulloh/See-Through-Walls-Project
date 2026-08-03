using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace SeeThroughWalls.Backend
{
    /// <summary>
    /// Client REST minimal untuk backend FastAPI self-hosted.
    /// Menggantikan sebagian fungsi MultiSet SDK (auth, map, session) —
    /// localization tetap lewat MultiSet SDK kecuali kamu sudah isi
    /// pipeline CV asli di backend/app/services/localization.py.
    ///
    /// Cara pakai (contoh login):
    ///   StartCoroutine(apiClient.Login("alice", "password123", token => {
    ///       Debug.Log("Token: " + token);
    ///   }, error => Debug.LogError(error)));
    /// </summary>
    public class ApiClient : MonoBehaviour
    {
        public BackendConfig config;

        [Serializable]
        private class TokenResponse
        {
            public string access_token;
            public string token_type;
        }

        [Serializable]
        private class RegisterOrLoginBody
        {
            public string username;
            public string password;
        }

        [Serializable]
        private class SessionCreateBody
        {
            public string map_id;
        }

        [Serializable]
        public class SessionResponse
        {
            public string id;
            public string code;
            public string map_id;
            public bool active;
            public string created_at;
        }

        public IEnumerator Register(string username, string password, Action<string> onSuccess, Action<string> onError)
        {
            yield return AuthRequest("/auth/register", username, password, onSuccess, onError);
        }

        public IEnumerator Login(string username, string password, Action<string> onSuccess, Action<string> onError)
        {
            yield return AuthRequest("/auth/login", username, password, onSuccess, onError);
        }

        private IEnumerator AuthRequest(string path, string username, string password, Action<string> onSuccess, Action<string> onError)
        {
            var body = JsonUtility.ToJson(new RegisterOrLoginBody { username = username, password = password });
            using var req = new UnityWebRequest(config.baseUrl + path, "POST");
            req.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");

            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                onError?.Invoke($"{req.error}: {req.downloadHandler.text}");
                yield break;
            }

            var parsed = JsonUtility.FromJson<TokenResponse>(req.downloadHandler.text);
            config.accessToken = parsed.access_token;
            onSuccess?.Invoke(parsed.access_token);
        }

        /// <summary>Buat room baru (host). Butuh sudah login (config.accessToken terisi).</summary>
        public IEnumerator CreateSession(string mapId, Action<SessionResponse> onSuccess, Action<string> onError)
        {
            var body = JsonUtility.ToJson(new SessionCreateBody { map_id = mapId });
            using var req = new UnityWebRequest(config.baseUrl + "/sessions", "POST");
            req.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(body));
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            req.SetRequestHeader("Authorization", "Bearer " + config.accessToken);

            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                onError?.Invoke($"{req.error}: {req.downloadHandler.text}");
                yield break;
            }

            onSuccess?.Invoke(JsonUtility.FromJson<SessionResponse>(req.downloadHandler.text));
        }

        /// <summary>Validasi room ada sebelum client connect WebSocket. Tidak butuh auth.</summary>
        public IEnumerator GetSession(string code, Action<SessionResponse> onSuccess, Action<string> onError)
        {
            using var req = UnityWebRequest.Get($"{config.baseUrl}/sessions/{code}");
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                onError?.Invoke($"{req.error}: {req.downloadHandler.text}");
                yield break;
            }

            onSuccess?.Invoke(JsonUtility.FromJson<SessionResponse>(req.downloadHandler.text));
        }
    }
}

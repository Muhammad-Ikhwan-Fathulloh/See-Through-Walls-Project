using System;
using System.Collections.Concurrent;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace SeeThroughWalls.Backend
{
    [Serializable]
    public class PoseUpdateMessage
    {
        public string type = "pose";
        public string player_name;
        public string color;
        public float[] position;   // [x, y, z]
        public float[] rotation;   // quaternion [x, y, z, w]
    }

    /// <summary>
    /// Client WebSocket untuk realtime pose relay, menggantikan peran
    /// MultiplayerManager + MultisetMultipeerBridge dari sample asli saat
    /// memakai backend self-hosted alih-alih P2P WiFi lokal.
    ///
    /// Catatan platform: pakai System.Net.WebSockets.ClientWebSocket di sini karena
    /// built-in di .NET dan cukup untuk target iOS/Android dengan IL2CPP. Kalau
    /// butuh dukungan WebGL juga, ganti dengan package NativeWebSocket
    /// (https://github.com/endel/NativeWebSocket) yang API-nya mirip.
    ///
    /// Kirim pose tiap frame lewat SendPose(), dan baca RemotePoses untuk pose
    /// player lain (di-update dari background thread, baca dari Update() di
    /// MonoBehaviour lain untuk spawn/gerakkan avatar).
    /// </summary>
    public class PoseWebSocketClient : MonoBehaviour
    {
        public BackendConfig config;

        [Tooltip("Target kirim pose per detik, samakan dengan referensi ~20Hz di proyek asli")]
        public float sendRateHz = 20f;

        public event Action<PoseUpdateMessage> OnRemotePoseReceived;
        public event Action OnConnected;
        public event Action<string> OnError;

        private ClientWebSocket _socket;
        private CancellationTokenSource _cts;
        private readonly ConcurrentQueue<PoseUpdateMessage> _incomingQueue = new();
        private float _sendInterval;
        private float _sendTimer;
        private string _localPlayerName;
        private string _localColor;

        private void Update()
        {
            // Drain pesan yang diterima di background thread, dispatch di main thread
            while (_incomingQueue.TryDequeue(out var msg))
            {
                OnRemotePoseReceived?.Invoke(msg);
            }
        }

        public async void Connect(string sessionCode, string playerName, string colorHex)
        {
            _localPlayerName = playerName;
            _localColor = colorHex;
            _sendInterval = 1f / Mathf.Max(1f, sendRateHz);

            _socket = new ClientWebSocket();
            _cts = new CancellationTokenSource();

            try
            {
                var uri = new Uri(config.WebSocketUrl(sessionCode, playerName));
                await _socket.ConnectAsync(uri, _cts.Token);
                OnConnected?.Invoke();
                _ = ReceiveLoop(_cts.Token);
            }
            catch (Exception e)
            {
                OnError?.Invoke(e.Message);
            }
        }

        /// <summary>Panggil ini tiap frame (mis. dari Update di script host pose);
        /// internal throttling memastikan tidak melebihi sendRateHz.</summary>
        public async void SendPose(Vector3 position, Quaternion rotation)
        {
            if (_socket == null || _socket.State != WebSocketState.Open) return;

            _sendTimer += Time.deltaTime;
            if (_sendTimer < _sendInterval) return;
            _sendTimer = 0f;

            var msg = new PoseUpdateMessage
            {
                player_name = _localPlayerName,
                color = _localColor,
                position = new[] { position.x, position.y, position.z },
                rotation = new[] { rotation.x, rotation.y, rotation.z, rotation.w },
            };

            string json = JsonUtility.ToJson(msg);
            var bytes = Encoding.UTF8.GetBytes(json);

            try
            {
                await _socket.SendAsync(
                    new ArraySegment<byte>(bytes),
                    WebSocketMessageType.Text,
                    true,
                    _cts.Token);
            }
            catch (Exception e)
            {
                OnError?.Invoke(e.Message);
            }
        }

        private async Task ReceiveLoop(CancellationToken token)
        {
            var buffer = new byte[4096];
            try
            {
                while (_socket.State == WebSocketState.Open && !token.IsCancellationRequested)
                {
                    var result = await _socket.ReceiveAsync(new ArraySegment<byte>(buffer), token);
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        break;
                    }

                    string json = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    var msg = JsonUtility.FromJson<PoseUpdateMessage>(json);
                    _incomingQueue.Enqueue(msg);
                }
            }
            catch (Exception e)
            {
                OnError?.Invoke(e.Message);
            }
        }

        private async void OnDestroy()
        {
            _cts?.Cancel();
            if (_socket != null && _socket.State == WebSocketState.Open)
            {
                await _socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "closing", CancellationToken.None);
            }
            _socket?.Dispose();
        }
    }
}

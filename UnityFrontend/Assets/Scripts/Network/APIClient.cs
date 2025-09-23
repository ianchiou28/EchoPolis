using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace EchoPolis.Network
{
    public class APIClient : MonoBehaviour
    {
        [SerializeField] private string baseURL = "http://localhost:8000";
        
        public static APIClient Instance { get; private set; }
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        public void CreateAvatar(string mbtiType, string name, Action<string> onSuccess, Action<string> onError)
        {
            StartCoroutine(PostRequest("/api/avatar/create", $"{{\"mbti_type\":\"{mbtiType}\",\"name\":\"{name}\"}}", onSuccess, onError));
        }
        
        public void GetAvatarStatus(Action<string> onSuccess, Action<string> onError)
        {
            StartCoroutine(GetRequest("/api/avatar/status", onSuccess, onError));
        }
        
        public void SendEcho(string message, Action<string> onSuccess, Action<string> onError)
        {
            StartCoroutine(PostRequest("/api/avatar/echo", $"{{\"message\":\"{message}\"}}", onSuccess, onError));
        }
        
        private IEnumerator GetRequest(string endpoint, Action<string> onSuccess, Action<string> onError)
        {
            using (UnityWebRequest request = UnityWebRequest.Get(baseURL + endpoint))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    onSuccess?.Invoke(request.downloadHandler.text);
                }
                else
                {
                    onError?.Invoke(request.error);
                }
            }
        }
        
        private IEnumerator PostRequest(string endpoint, string jsonData, Action<string> onSuccess, Action<string> onError)
        {
            using (UnityWebRequest request = new UnityWebRequest(baseURL + endpoint, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    onSuccess?.Invoke(request.downloadHandler.text);
                }
                else
                {
                    onError?.Invoke(request.error);
                }
            }
        }
    }
}
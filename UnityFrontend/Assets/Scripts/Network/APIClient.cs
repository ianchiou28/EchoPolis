using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace EchoPolis
{
    public class APIClient : MonoBehaviour
    {
        public static APIClient Instance { get; private set; }
        
        [Header("API Settings")]
        public string baseURL = "http://localhost:8000/api/unity";
        public int timeoutSeconds = 30;

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

        public IEnumerator PostRequest<T>(string endpoint, object data, Action<T> onSuccess, Action<string> onError)
        {
            string url = baseURL + endpoint;
            string jsonData = JsonConvert.SerializeObject(data);
            
            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                request.timeout = timeoutSeconds;

                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        string responseText = request.downloadHandler.text;
                        UnityResponse response = JsonConvert.DeserializeObject<UnityResponse>(responseText);
                        
                        if (response.status == "success")
                        {
                            T result = JsonConvert.DeserializeObject<T>(response.data.ToString());
                            onSuccess?.Invoke(result);
                        }
                        else
                        {
                            onError?.Invoke(response.message);
                        }
                    }
                    catch (Exception e)
                    {
                        onError?.Invoke($"解析响应失败: {e.Message}");
                    }
                }
                else
                {
                    onError?.Invoke($"网络请求失败: {request.error}");
                }
            }
        }

        public IEnumerator GetRequest<T>(string endpoint, Action<T> onSuccess, Action<string> onError)
        {
            string url = baseURL + endpoint;
            
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.timeout = timeoutSeconds;
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        string responseText = request.downloadHandler.text;
                        UnityResponse response = JsonConvert.DeserializeObject<UnityResponse>(responseText);
                        
                        if (response.status == "success")
                        {
                            T result = JsonConvert.DeserializeObject<T>(response.data.ToString());
                            onSuccess?.Invoke(result);
                        }
                        else
                        {
                            onError?.Invoke(response.message);
                        }
                    }
                    catch (Exception e)
                    {
                        onError?.Invoke($"解析响应失败: {e.Message}");
                    }
                }
                else
                {
                    onError?.Invoke($"网络请求失败: {request.error}");
                }
            }
        }

        // 具体的API调用方法
        public IEnumerator Login(LoginRequest loginData, Action<object> onSuccess, Action<string> onError)
        {
            yield return PostRequest("/auth/login", loginData, onSuccess, onError);
        }

        public IEnumerator CreateAvatar(CreateAvatarRequest avatarData, Action<AvatarData> onSuccess, Action<string> onError)
        {
            yield return PostRequest("/avatar/create", avatarData, onSuccess, onError);
        }

        public IEnumerator GetGameState(string userId, Action<GameState> onSuccess, Action<string> onError)
        {
            yield return GetRequest($"/game/state/{userId}", onSuccess, onError);
        }

        public IEnumerator GetCurrentSituation(string userId, Action<SituationData> onSuccess, Action<string> onError)
        {
            yield return GetRequest($"/game/situation/{userId}", onSuccess, onError);
        }

        public IEnumerator SubmitDecision(DecisionRequest decisionData, Action<object> onSuccess, Action<string> onError)
        {
            yield return PostRequest("/game/decision", decisionData, onSuccess, onError);
        }
    }
}
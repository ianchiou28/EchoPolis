using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace EchoPolis
{
    public class TestBackendConnection : MonoBehaviour
    {
        [Header("Test Settings")]
        public string apiUrl = "http://localhost:8000/api/unity/health";
        public bool testOnStart = true;

        private void Start()
        {
            if (testOnStart)
            {
                StartCoroutine(TestConnection());
            }
        }

        [ContextMenu("Test Connection")]
        public void TestConnectionButton()
        {
            StartCoroutine(TestConnection());
        }

        private IEnumerator TestConnection()
        {
            Debug.Log("Testing backend connection...");
            
            using (UnityWebRequest request = UnityWebRequest.Get(apiUrl))
            {
                request.timeout = 10;
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log($"✅ Backend connection successful!");
                    Debug.Log($"Response: {request.downloadHandler.text}");
                }
                else
                {
                    Debug.LogError($"❌ Backend connection failed: {request.error}");
                    Debug.LogError($"Response Code: {request.responseCode}");
                }
            }
        }

        [ContextMenu("Test Login")]
        public void TestLogin()
        {
            StartCoroutine(TestLoginAPI());
        }

        private IEnumerator TestLoginAPI()
        {
            string loginUrl = "http://localhost:8000/api/unity/auth/login";
            string jsonData = "{\"username\":\"test_user\",\"password\":\"123456\"}";

            using (UnityWebRequest request = new UnityWebRequest(loginUrl, "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                request.timeout = 10;

                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log($"✅ Login test successful!");
                    Debug.Log($"Response: {request.downloadHandler.text}");
                }
                else
                {
                    Debug.LogError($"❌ Login test failed: {request.error}");
                    Debug.LogError($"Response: {request.downloadHandler.text}");
                }
            }
        }
    }
}
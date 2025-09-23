using UnityEngine;
using EchoPolis.Network;

namespace EchoPolis.Core
{
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }
        
        [Header("Game State")]
        public bool hasAvatar = false;
        public string currentAvatarName = "";
        public string currentMBTI = "";
        
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
        
        private void Start()
        {
            CheckAvatarStatus();
        }
        
        public void CreateNewAvatar(string mbtiType, string name)
        {
            APIClient.Instance.CreateAvatar(mbtiType, name, OnAvatarCreated, OnError);
        }
        
        public void SendEchoMessage(string message)
        {
            if (!hasAvatar)
            {
                Debug.LogWarning("No avatar created yet!");
                return;
            }
            
            APIClient.Instance.SendEcho(message, OnEchoSent, OnError);
        }
        
        private void CheckAvatarStatus()
        {
            APIClient.Instance.GetAvatarStatus(OnStatusReceived, OnError);
        }
        
        private void OnAvatarCreated(string response)
        {
            Debug.Log("Avatar created: " + response);
            hasAvatar = true;
            // Parse response to get avatar details
        }
        
        private void OnStatusReceived(string response)
        {
            Debug.Log("Status received: " + response);
            // Parse response to update game state
        }
        
        private void OnEchoSent(string response)
        {
            Debug.Log("Echo sent: " + response);
            // Handle AI response
        }
        
        private void OnError(string error)
        {
            Debug.LogError("API Error: " + error);
        }
    }
}
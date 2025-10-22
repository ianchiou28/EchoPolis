using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace EchoPolis
{
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Game Settings")]
        public string apiBaseUrl = "http://localhost:8000/api";
        public bool debugMode = true;

        [Header("Current Game State")]
        public string currentUserId;
        public bool isGameActive = false;

        // Events
        public System.Action<string> OnGameMessage;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeGame();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void InitializeGame()
        {
            Debug.Log("EchoPolis Game Manager Initialized");
        }

        public void StartNewGame(string userId)
        {
            currentUserId = userId;
            isGameActive = true;
            Debug.Log($"Starting new game for user: {userId}");
        }

        public void SubmitDecision(int optionId, string userInput = "")
        {
            if (!isGameActive)
            {
                Debug.LogWarning("Game is not active");
                return;
            }

            Debug.Log($"Submitting decision: Option {optionId}, Input: {userInput}");
            OnGameMessage?.Invoke($"Decision submitted: Option {optionId}");
            
            // Call APIClient to submit decision
            if (APIClient.Instance != null)
            {
                DecisionRequest request = new DecisionRequest
                {
                    situationId = "current",
                    optionId = optionId,
                    userInput = userInput
                };
                
                StartCoroutine(APIClient.Instance.SubmitDecision(request,
                    (result) => {
                        Debug.Log("Decision submitted successfully");
                        OnGameMessage?.Invoke("Decision submitted successfully");
                    },
                    (error) => {
                        Debug.LogError($"Failed to submit decision: {error}");
                        OnGameMessage?.Invoke($"Decision submission failed: {error}");
                    }));
            }
        }

        public void EndGame(string reason = "")
        {
            isGameActive = false;
            Debug.Log($"Game ended: {reason}");
            OnGameMessage?.Invoke($"Game ended: {reason}");
        }
    }
}
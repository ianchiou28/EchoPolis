using System.Collections;
using UnityEngine;

namespace EchoPolis
{
    public class GameController : MonoBehaviour
    {
        [Header("UI References")]
        public MainGameUI mainGameUI;
        
        [Header("Game Settings")]
        public string testUserId = "test_user";
        public bool autoStartGame = true;
        
        private GameState currentGameState;
        private bool isInitialized = false;

        private void Start()
        {
            StartCoroutine(InitializeGame());
        }

        private IEnumerator InitializeGame()
        {
            Debug.Log("Initializing EchoPolis Game Controller...");
            
            // Wait for managers to initialize
            yield return new WaitForSeconds(0.5f);
            
            // Ensure all managers exist
            if (GameManager.Instance == null)
            {
                GameObject gameManagerGO = new GameObject("GameManager");
                gameManagerGO.AddComponent<GameManager>();
            }
            
            if (APIClient.Instance == null)
            {
                GameObject apiClientGO = new GameObject("APIClient");
                apiClientGO.AddComponent<APIClient>();
            }
            
            // Find UI if not assigned
            if (mainGameUI == null)
            {
                mainGameUI = FindObjectOfType<MainGameUI>();
            }
            
            // Subscribe to events
            if (GameManager.Instance != null)
            {
                GameManager.Instance.OnGameMessage += OnGameMessage;
            }
            
            isInitialized = true;
            Debug.Log("Game Controller initialized successfully!");
            
            if (autoStartGame)
            {
                yield return new WaitForSeconds(1f);
                StartNewGame();
            }
        }

        public void StartNewGame()
        {
            if (!isInitialized)
            {
                Debug.LogWarning("Game Controller not initialized yet");
                return;
            }
            
            Debug.Log($"Starting new game for user: {testUserId}");
            
            if (mainGameUI != null)
            {
                mainGameUI.ShowMessage("Starting new game...");
            }
            
            // Start the game through GameManager
            if (GameManager.Instance != null)
            {
                GameManager.Instance.StartNewGame(testUserId);
            }
            
            // Load initial game state
            StartCoroutine(LoadGameState());
        }

        private IEnumerator LoadGameState()
        {
            if (APIClient.Instance == null) yield break;
            
            Debug.Log("Loading game state...");
            
            yield return StartCoroutine(APIClient.Instance.GetGameState(testUserId,
                (gameState) => {
                    currentGameState = gameState;
                    UpdateUI();
                    LoadCurrentSituation();
                },
                (error) => {
                    Debug.LogError($"Failed to load game state: {error}");
                    if (mainGameUI != null)
                    {
                        mainGameUI.ShowMessage($"Failed to load game: {error}");
                    }
                }));
        }

        private void LoadCurrentSituation()
        {
            if (APIClient.Instance == null) return;
            
            Debug.Log("Loading current situation...");
            
            StartCoroutine(APIClient.Instance.GetCurrentSituation(testUserId,
                (situation) => {
                    if (mainGameUI != null)
                    {
                        mainGameUI.UpdateSituation(situation.title, situation.description);
                        mainGameUI.SetDecisionOptions(situation.options);
                    }
                },
                (error) => {
                    Debug.LogError($"Failed to load situation: {error}");
                    if (mainGameUI != null)
                    {
                        mainGameUI.ShowMessage($"Failed to load situation: {error}");
                    }
                }));
        }

        private void UpdateUI()
        {
            if (mainGameUI == null || currentGameState == null) return;
            
            // Update avatar info
            if (currentGameState.avatar != null)
            {
                mainGameUI.UpdateAvatarInfo(
                    currentGameState.avatar.name,
                    currentGameState.avatar.mbti_type,
                    currentGameState.avatar.trust_level,
                    currentGameState.avatar.health,
                    currentGameState.avatar.energy,
                    currentGameState.avatar.stress
                );
            }
            
            // Update financial info
            if (currentGameState.finances != null)
            {
                mainGameUI.UpdateFinancialInfo(
                    currentGameState.finances.cash,
                    currentGameState.finances.total_assets,
                    currentGameState.finances.monthly_income,
                    currentGameState.finances.monthly_expenses
                );
            }
        }

        private void OnGameMessage(string message)
        {
            Debug.Log($"[Game] {message}");
            if (mainGameUI != null)
            {
                mainGameUI.ShowMessage(message);
            }
        }

        // Public methods for UI buttons
        public void OnLoginButtonClicked()
        {
            StartCoroutine(TestLogin());
        }

        public void OnCreateAvatarButtonClicked()
        {
            StartCoroutine(TestCreateAvatar());
        }

        public void OnRefreshGameStateButtonClicked()
        {
            StartCoroutine(LoadGameState());
        }

        private IEnumerator TestLogin()
        {
            if (APIClient.Instance == null) yield break;
            
            LoginRequest loginRequest = new LoginRequest
            {
                username = testUserId,
                password = "123456"
            };
            
            yield return StartCoroutine(APIClient.Instance.Login(loginRequest,
                (result) => {
                    Debug.Log("Login successful!");
                    if (mainGameUI != null)
                    {
                        mainGameUI.ShowMessage("Login successful!");
                    }
                },
                (error) => {
                    Debug.LogError($"Login failed: {error}");
                    if (mainGameUI != null)
                    {
                        mainGameUI.ShowMessage($"Login failed: {error}");
                    }
                }));
        }

        private IEnumerator TestCreateAvatar()
        {
            if (APIClient.Instance == null) yield break;
            
            CreateAvatarRequest avatarRequest = new CreateAvatarRequest
            {
                name = "Alex Chen",
                mbti_type = "INTP"
            };
            
            yield return StartCoroutine(APIClient.Instance.CreateAvatar(avatarRequest,
                (avatarData) => {
                    Debug.Log("Avatar created successfully!");
                    if (mainGameUI != null)
                    {
                        mainGameUI.ShowMessage("Avatar created!");
                        mainGameUI.UpdateAvatarInfo(
                            avatarData.name,
                            avatarData.mbti_type,
                            avatarData.trust_level,
                            avatarData.health,
                            avatarData.energy,
                            avatarData.stress
                        );
                    }
                },
                (error) => {
                    Debug.LogError($"Avatar creation failed: {error}");
                    if (mainGameUI != null)
                    {
                        mainGameUI.ShowMessage($"Avatar creation failed: {error}");
                    }
                }));
        }

        private void OnDestroy()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.OnGameMessage -= OnGameMessage;
            }
        }
    }
}
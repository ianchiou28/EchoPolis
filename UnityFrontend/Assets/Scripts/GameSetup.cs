using UnityEngine;

namespace EchoPolis
{
    public class GameSetup : MonoBehaviour
    {
        [Header("Auto Setup")]
        public bool setupOnStart = true;
        
        private void Start()
        {
            if (setupOnStart)
            {
                SetupGame();
            }
        }
        
        [ContextMenu("Setup Game")]
        public void SetupGame()
        {
            Debug.Log("Setting up EchoPolis game...");
            
            // 确保GameManager存在
            if (GameManager.Instance == null)
            {
                GameObject gameManagerGO = new GameObject("GameManager");
                gameManagerGO.AddComponent<GameManager>();
                Debug.Log("✅ GameManager created");
            }
            
            // 确保APIClient存在
            if (APIClient.Instance == null)
            {
                GameObject apiClientGO = new GameObject("APIClient");
                apiClientGO.AddComponent<APIClient>();
                Debug.Log("✅ APIClient created");
            }
            
            // 确保TestBackendConnection存在
            if (FindObjectOfType<TestBackendConnection>() == null)
            {
                GameObject testerGO = new GameObject("BackendTester");
                testerGO.AddComponent<TestBackendConnection>();
                Debug.Log("✅ BackendTester created");
            }
            
            // 确保SimpleGameUI存在
            if (FindObjectOfType<SimpleGameUI>() == null)
            {
                GameObject uiGO = new GameObject("SimpleGameUI");
                uiGO.AddComponent<SimpleGameUI>();
                Debug.Log("✅ SimpleGameUI created");
            }
            
            Debug.Log("🎮 EchoPolis setup complete!");
            Debug.Log("📋 Available components:");
            Debug.Log("   - GameManager: Game state management");
            Debug.Log("   - APIClient: Backend communication");
            Debug.Log("   - TestBackendConnection: Connection testing");
            Debug.Log("   - SimpleGameUI: Debug interface");
        }
    }
}
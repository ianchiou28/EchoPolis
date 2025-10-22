using System.Collections;
using UnityEngine;

namespace EchoPolis
{
    public class SimpleGameUI : MonoBehaviour
    {
        [Header("Debug Settings")]
        public bool showDebugGUI = true;
        public string currentMessage = "EchoPolis Ready";
        
        private void OnGUI()
        {
            if (!showDebugGUI) return;
            
            GUILayout.BeginArea(new Rect(10, 10, 400, 300));
            GUILayout.Label("EchoPolis Debug UI", GUI.skin.box);
            
            GUILayout.Label($"Status: {currentMessage}");
            
            if (GUILayout.Button("Test Backend Connection"))
            {
                TestConnection();
            }
            
            if (GUILayout.Button("Test Login"))
            {
                TestLogin();
            }
            
            if (GUILayout.Button("Start Game"))
            {
                StartGame();
            }
            
            GUILayout.EndArea();
        }
        
        private void TestConnection()
        {
            var tester = FindObjectOfType<TestBackendConnection>();
            if (tester != null)
            {
                tester.TestConnectionButton();
                currentMessage = "Testing connection...";
            }
            else
            {
                currentMessage = "TestBackendConnection not found";
            }
        }
        
        private void TestLogin()
        {
            var tester = FindObjectOfType<TestBackendConnection>();
            if (tester != null)
            {
                tester.TestLogin();
                currentMessage = "Testing login...";
            }
            else
            {
                currentMessage = "TestBackendConnection not found";
            }
        }
        
        private void StartGame()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.StartNewGame("test_user");
                currentMessage = "Game started for test_user";
            }
            else
            {
                currentMessage = "GameManager not found";
            }
        }
    }
}
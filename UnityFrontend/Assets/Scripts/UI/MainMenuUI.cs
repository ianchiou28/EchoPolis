using UnityEngine;
using UnityEngine.UI;
using TMPro;
using EchoPolis.Core;

namespace EchoPolis.UI
{
    public class MainMenuUI : MonoBehaviour
    {
        [Header("UI Elements")]
        public TMP_Dropdown mbtiDropdown;
        public TMP_InputField nameInput;
        public Button createButton;
        public Button startGameButton;
        
        [Header("Panels")]
        public GameObject createAvatarPanel;
        public GameObject gamePanel;
        
        private void Start()
        {
            SetupMBTIDropdown();
            createButton.onClick.AddListener(OnCreateAvatar);
            startGameButton.onClick.AddListener(OnStartGame);
            
            // Show appropriate panel based on game state
            UpdateUI();
        }
        
        private void SetupMBTIDropdown()
        {
            mbtiDropdown.ClearOptions();
            mbtiDropdown.AddOptions(new System.Collections.Generic.List<string>
            {
                "INTJ", "INTP", "ENTJ", "ENTP",
                "INFJ", "INFP", "ENFJ", "ENFP",
                "ISTJ", "ISFJ", "ESTJ", "ESFJ",
                "ISTP", "ISFP", "ESTP", "ESFP"
            });
        }
        
        private void OnCreateAvatar()
        {
            string selectedMBTI = mbtiDropdown.options[mbtiDropdown.value].text;
            string avatarName = nameInput.text;
            
            if (string.IsNullOrEmpty(avatarName))
            {
                Debug.LogWarning("Please enter a name for your avatar!");
                return;
            }
            
            GameManager.Instance.CreateNewAvatar(selectedMBTI, avatarName);
            UpdateUI();
        }
        
        private void OnStartGame()
        {
            createAvatarPanel.SetActive(false);
            gamePanel.SetActive(true);
        }
        
        private void UpdateUI()
        {
            bool hasAvatar = GameManager.Instance.hasAvatar;
            createAvatarPanel.SetActive(!hasAvatar);
            startGameButton.gameObject.SetActive(hasAvatar);
        }
    }
}
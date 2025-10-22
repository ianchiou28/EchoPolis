using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace EchoPolis
{
    public class MainGameUI : MonoBehaviour
    {
        [Header("Avatar Panel")]
        public TextMeshProUGUI avatarNameText;
        public TextMeshProUGUI mbtiTypeText;
        public Slider trustSlider;
        public Slider healthSlider;
        public Slider energySlider;
        public Slider stressSlider;

        [Header("Financial Panel")]
        public TextMeshProUGUI cashText;
        public TextMeshProUGUI assetsText;
        public TextMeshProUGUI incomeText;
        public TextMeshProUGUI expensesText;

        [Header("Situation Panel")]
        public TextMeshProUGUI situationTitleText;
        public TextMeshProUGUI situationDescriptionText;
        public Transform decisionButtonParent;
        public GameObject decisionButtonPrefab;

        [Header("Input Panel")]
        public TMP_InputField userInputField;
        public Button submitInputButton;

        [Header("Message Panel")]
        public GameObject messagePanel;
        public TextMeshProUGUI messageText;

        private List<GameObject> currentDecisionButtons = new List<GameObject>();
        private SituationData currentSituation;

        private void Start()
        {
            InitializeUI();
            
            // Subscribe to game events
            if (GameManager.Instance != null)
            {
                GameManager.Instance.OnGameMessage += ShowMessage;
            }

            if (submitInputButton != null)
            {
                submitInputButton.onClick.AddListener(OnSubmitInput);
            }
        }

        private void InitializeUI()
        {
            ShowMessage("Welcome to EchoPolis!");
            
            // Initialize with default values
            UpdateAvatarInfo("Loading...", "INTP", 50, 100, 100, 0);
            UpdateFinancialInfo(0, 0, 0, 0);
            UpdateSituation("Initializing game...", "Please wait while we set up your AI avatar.");
        }

        public void UpdateAvatarInfo(string name, string mbti, int trust, int health, int energy, int stress)
        {
            if (avatarNameText != null) avatarNameText.text = name;
            if (mbtiTypeText != null) mbtiTypeText.text = mbti;
            if (trustSlider != null) trustSlider.value = trust / 100f;
            if (healthSlider != null) healthSlider.value = health / 100f;
            if (energySlider != null) energySlider.value = energy / 100f;
            if (stressSlider != null) stressSlider.value = stress / 100f;
        }

        public void UpdateFinancialInfo(float cash, float assets, float income, float expenses)
        {
            if (cashText != null) cashText.text = $"Cash: ¥{cash:N0}";
            if (assetsText != null) assetsText.text = $"Assets: ¥{assets:N0}";
            if (incomeText != null) incomeText.text = $"Income: ¥{income:N0}/month";
            if (expensesText != null) expensesText.text = $"Expenses: ¥{expenses:N0}/month";
        }

        public void UpdateSituation(string title, string description)
        {
            if (situationTitleText != null)
            {
                StartCoroutine(TypewriterEffect(situationTitleText, title));
            }
            
            if (situationDescriptionText != null)
            {
                StartCoroutine(TypewriterEffect(situationDescriptionText, description));
            }
        }

        public void SetDecisionOptions(List<DecisionOption> options)
        {
            // Clear existing buttons
            foreach (GameObject button in currentDecisionButtons)
            {
                if (button != null) Destroy(button);
            }
            currentDecisionButtons.Clear();

            // Create new decision buttons
            if (options != null && decisionButtonPrefab != null && decisionButtonParent != null)
            {
                for (int i = 0; i < options.Count; i++)
                {
                    DecisionOption option = options[i];
                    GameObject buttonObj = Instantiate(decisionButtonPrefab, decisionButtonParent);
                    
                    Button button = buttonObj.GetComponent<Button>();
                    TextMeshProUGUI buttonText = buttonObj.GetComponentInChildren<TextMeshProUGUI>();
                    
                    if (buttonText != null)
                    {
                        buttonText.text = $"{option.title}\n<size=12><color=#888888>{option.description}</color></size>";
                    }

                    if (button != null)
                    {
                        int optionId = option.id;
                        button.onClick.AddListener(() => OnDecisionSelected(optionId));
                    }

                    currentDecisionButtons.Add(buttonObj);
                }
            }
        }

        private void OnDecisionSelected(int optionId)
        {
            string userInput = userInputField != null ? userInputField.text : "";
            
            // Disable all decision buttons
            foreach (GameObject buttonObj in currentDecisionButtons)
            {
                Button button = buttonObj.GetComponent<Button>();
                if (button != null) button.interactable = false;
            }

            // Submit decision
            if (GameManager.Instance != null)
            {
                GameManager.Instance.SubmitDecision(optionId, userInput);
            }

            // Clear input
            if (userInputField != null) userInputField.text = "";
        }

        private void OnSubmitInput()
        {
            if (userInputField != null && !string.IsNullOrEmpty(userInputField.text))
            {
                ShowMessage($"You said: {userInputField.text}");
                // Here you could send the input to AI for processing
                userInputField.text = "";
            }
        }

        public void ShowMessage(string message)
        {
            if (messageText != null) messageText.text = message;
            if (messagePanel != null)
            {
                messagePanel.SetActive(true);
                StartCoroutine(HideMessageAfterDelay(3f));
            }
            Debug.Log($"[UI] {message}");
        }

        private IEnumerator HideMessageAfterDelay(float delay)
        {
            yield return new WaitForSeconds(delay);
            if (messagePanel != null) messagePanel.SetActive(false);
        }

        private IEnumerator TypewriterEffect(TextMeshProUGUI textComponent, string text)
        {
            if (textComponent == null) yield break;
            
            textComponent.text = "";
            for (int i = 0; i <= text.Length; i++)
            {
                textComponent.text = text.Substring(0, i);
                yield return new WaitForSeconds(0.03f);
            }
        }

        // Public methods for testing
        [ContextMenu("Test Update Avatar")]
        public void TestUpdateAvatar()
        {
            UpdateAvatarInfo("Alex Chen", "INTP", 75, 85, 60, 25);
        }

        [ContextMenu("Test Update Financial")]
        public void TestUpdateFinancial()
        {
            UpdateFinancialInfo(25000, 45000, 8000, 3500);
        }

        [ContextMenu("Test Situation")]
        public void TestSituation()
        {
            UpdateSituation("Investment Opportunity", "You received an invitation to a quantitative investment course...");
            
            List<DecisionOption> testOptions = new List<DecisionOption>
            {
                new DecisionOption { id = 1, title = "Invest in Education", description = "Pay ¥12,000 for the course" },
                new DecisionOption { id = 2, title = "Save Money", description = "Keep the money in savings" },
                new DecisionOption { id = 3, title = "High Risk Investment", description = "Invest in tech stocks" }
            };
            
            SetDecisionOptions(testOptions);
        }

        private void OnDestroy()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.OnGameMessage -= ShowMessage;
            }
        }
    }
}
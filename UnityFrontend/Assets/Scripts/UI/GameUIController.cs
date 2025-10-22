using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace EchoPolis
{
    public class GameUIController : MonoBehaviour
    {
        [Header("UI References")]
        public TextMeshProUGUI situationTitleText;
        public TextMeshProUGUI situationDescriptionText;
        public TextMeshProUGUI avatarNameText;
        public TextMeshProUGUI cashText;
        public TextMeshProUGUI trustLevelText;
        public Slider healthSlider;
        public Slider energySlider;
        public Slider stressSlider;

        [Header("Decision UI")]
        public Transform decisionButtonParent;
        public Button decisionButtonPrefab;
        public TMP_InputField userInputField;
        public Button submitInputButton;

        [Header("Message UI")]
        public TextMeshProUGUI messageText;
        public GameObject messagePanel;

        private List<Button> currentDecisionButtons = new List<Button>();
        private SituationData currentSituation;

        private void Start()
        {
            // 订阅游戏管理器事件
            if (GameManager.Instance != null)
            {
                GameManager.Instance.OnGameMessage += ShowMessage;
            }

            // 设置提交按钮事件
            if (submitInputButton != null)
            {
                submitInputButton.onClick.AddListener(OnSubmitUserInput);
            }
        }

        public void UpdateGameState(GameState gameState)
        {
            if (gameState == null) return;

            // 更新化身信息
            if (avatarNameText != null && gameState.avatar != null)
            {
                avatarNameText.text = $"{gameState.avatar.name} ({gameState.avatar.mbti_type})";
            }

            // 更新财务信息
            if (cashText != null && gameState.finances != null)
            {
                cashText.text = $"现金: ¥{gameState.finances.cash:N0}";
            }

            // 更新化身状态
            if (gameState.avatar != null)
            {
                if (trustLevelText != null)
                    trustLevelText.text = $"信任度: {gameState.avatar.trust_level}/100";

                if (healthSlider != null)
                    healthSlider.value = gameState.avatar.health / 100f;

                if (energySlider != null)
                    energySlider.value = gameState.avatar.energy / 100f;

                if (stressSlider != null)
                    stressSlider.value = gameState.avatar.stress / 100f;
            }
        }

        public void UpdateSituation(SituationData situation)
        {
            currentSituation = situation;

            if (situation == null) return;

            // 更新情况文本
            if (situationTitleText != null)
            {
                StartCoroutine(TypewriterEffect(situationTitleText, situation.title));
            }

            if (situationDescriptionText != null)
            {
                StartCoroutine(TypewriterEffect(situationDescriptionText, situation.description));
            }

            // 创建决策按钮
            CreateDecisionButtons(situation.options);
        }

        private void CreateDecisionButtons(List<DecisionOption> options)
        {
            // 清除现有按钮
            foreach (Button button in currentDecisionButtons)
            {
                if (button != null)
                    Destroy(button.gameObject);
            }
            currentDecisionButtons.Clear();

            // 创建新按钮
            if (options != null && decisionButtonPrefab != null && decisionButtonParent != null)
            {
                for (int i = 0; i < options.Count; i++)
                {
                    DecisionOption option = options[i];
                    Button newButton = Instantiate(decisionButtonPrefab, decisionButtonParent);
                    
                    // 设置按钮文本
                    TextMeshProUGUI buttonText = newButton.GetComponentInChildren<TextMeshProUGUI>();
                    if (buttonText != null)
                    {
                        buttonText.text = $"{option.title}\n<size=12>{option.description}</size>";
                    }

                    // 设置按钮事件
                    int optionId = option.id;
                    newButton.onClick.AddListener(() => OnDecisionButtonClicked(optionId));

                    currentDecisionButtons.Add(newButton);
                }
            }
        }

        private void OnDecisionButtonClicked(int optionId)
        {
            string userInput = userInputField != null ? userInputField.text : "";
            
            if (GameManager.Instance != null)
            {
                GameManager.Instance.SubmitDecision(optionId, userInput);
            }

            // 禁用所有决策按钮
            foreach (Button button in currentDecisionButtons)
            {
                button.interactable = false;
            }

            // 清空输入框
            if (userInputField != null)
            {
                userInputField.text = "";
            }
        }

        private void OnSubmitUserInput()
        {
            if (userInputField != null && !string.IsNullOrEmpty(userInputField.text))
            {
                // 这里可以实现纯文本输入的处理逻辑
                ShowMessage($"你说: {userInputField.text}");
                userInputField.text = "";
            }
        }

        public void ShowMessage(string message)
        {
            if (messageText != null)
            {
                messageText.text = message;
            }

            if (messagePanel != null)
            {
                messagePanel.SetActive(true);
                StartCoroutine(HideMessageAfterDelay(3f));
            }
        }

        private IEnumerator HideMessageAfterDelay(float delay)
        {
            yield return new WaitForSeconds(delay);
            if (messagePanel != null)
            {
                messagePanel.SetActive(false);
            }
        }

        private IEnumerator TypewriterEffect(TextMeshProUGUI textComponent, string text)
        {
            textComponent.text = "";
            
            for (int i = 0; i <= text.Length; i++)
            {
                textComponent.text = text.Substring(0, i);
                yield return new WaitForSeconds(0.03f);
            }
        }

        private void OnDestroy()
        {
            // 取消订阅事件
            if (GameManager.Instance != null)
            {
                GameManager.Instance.OnGameMessage -= ShowMessage;
            }
        }
    }
}
using System;
using System.Collections.Generic;

namespace EchoPolis
{
    [Serializable]
    public class UnityResponse
    {
        public string status;
        public string message;
        public object data;
        public string error_code;
    }

    [Serializable]
    public class AvatarData
    {
        public string name;
        public string mbti_type;
        public int trust_level;
        public string current_emotion;
        public int health;
        public int energy;
        public int stress;
    }

    [Serializable]
    public class FinancialData
    {
        public float cash;
        public float total_assets;
        public float monthly_income;
        public float monthly_expenses;
        public float investment_value;
        public float debt;
    }

    [Serializable]
    public class DecisionOption
    {
        public int id;
        public string title;
        public string description;
        public string consequence;
        public string risk_level;
        public float financial_impact;
    }

    [Serializable]
    public class SituationData
    {
        public string id;
        public string title;
        public string description;
        public string context;
        public List<DecisionOption> options;
        public int? time_limit;
    }

    [Serializable]
    public class GameState
    {
        public string user_id;
        public AvatarData avatar;
        public FinancialData finances;
        public SituationData current_situation;
        public int game_month;
        public bool is_game_over;
        public string game_over_reason;
    }

    [Serializable]
    public class DecisionRequest
    {
        public string situationId;
        public int optionId;
        public string userInput;
    }

    [Serializable]
    public class LoginRequest
    {
        public string username;
        public string password;
    }

    [Serializable]
    public class CreateAvatarRequest
    {
        public string name;
        public string mbti_type;
    }
}
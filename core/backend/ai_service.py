"""
AI服务后端 - 处理AI决策和情况生成
"""
import json
import random
from typing import Dict, List, Optional

class AIService:
    def __init__(self):
        self.situation_cache = {}
        self.decision_history = []
    
    def generate_situation(self, avatar_context: Dict) -> Dict:
        """生成决策情况"""
        situations = [
            {
                "situation": f"作为{avatar_context['mbti']}类型的{avatar_context['name']}，你发现了一个投资机会...",
                "options": [
                    "投资10万CP到新兴科技股",
                    "投资5万CP到稳健基金", 
                    "暂时观望，继续研究"
                ]
            },
            {
                "situation": f"你的朋友向你推荐了一个创业项目，需要资金支持...",
                "options": [
                    "投资20万CP支持朋友",
                    "投资5万CP小额支持",
                    "礼貌拒绝投资"
                ]
            }
        ]
        
        chosen = random.choice(situations)
        return {
            "success": True,
            "situation": chosen["situation"],
            "options": chosen["options"],
            "context_type": "investment"
        }
    
    def make_decision(self, avatar_context: Dict, situation: Dict, player_echo: Optional[str] = None) -> Dict:
        """AI做决策"""
        options = situation["options"]
        mbti = avatar_context.get("mbti", "INTP")
        
        if mbti in ["ENTJ", "ESTP"]:
            chosen_idx = 0
        elif mbti in ["ISTJ", "ISFJ"]:
            chosen_idx = len(options) - 1
        else:
            chosen_idx = random.randint(0, len(options) - 1)
        
        chosen_option = options[chosen_idx]
        thoughts = f"作为{mbti}类型，我选择了{chosen_option}"
        if player_echo:
            thoughts += f"，考虑了你的建议：{player_echo}"
        
        return {
            "success": True,
            "chosen_option": chosen_option,
            "ai_thoughts": thoughts,
            "trust_change": random.randint(-1, 3)
        }

ai_service = AIService()
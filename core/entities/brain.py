"""
Brain模块 - 参考AIvilization的Brain结构
"""
from typing import Dict, List, Optional, TYPE_CHECKING
from enum import Enum
import random

# 尝试导入deepseek_engine，如果失败则设为None
try:
    from ..ai.deepseek_engine import DeepSeekEngine
    # 尝试初始化DeepSeek引擎
    deepseek_engine = DeepSeekEngine()
except (ImportError, Exception) as e:
    print(f"[WARN] DeepSeek engine not available: {e}")
    deepseek_engine = None

from ..systems.asset_calculator import asset_calculator

if TYPE_CHECKING:
    from .person import Person

class ThoughtType(Enum):
    """思维类型"""
    LOGICAL = "logical"
    EMOTIONAL = "emotional"
    INTUITIVE = "intuitive"
    PRACTICAL = "practical"

class Brain:
    """大脑模块 - 处理思考和决策"""
    
    def __init__(self, person: 'Person'):
        self.person = person
        self.thoughts: List[Dict] = []
        self.decision_patterns: Dict = {}
        
    def process_decision(self, situation: str, options: List[str], player_echo: Optional[str] = None, current_round: int = 1) -> Dict:
        """处理决策过程"""
        # 生成思维过程
        thought = self._generate_thought(situation, options, player_echo)
        self.thoughts.append(thought)
        
        # 做出决策
        if deepseek_engine:
            decision = self._ai_decision(situation, options, player_echo, current_round)
        else:
            decision = self._rule_decision(situation, options, player_echo)
        
        # 处理AI决策的财务影响
        if 'decision_impact' in decision and decision['decision_impact']:
            impact = decision['decision_impact']
            
            # 更新属性
            old_credits = self.person.attributes.credits
            attribute_changes = {}
            
            # 财务变化
            if 'cash_change' in impact:
                attribute_changes['credits'] = impact['cash_change']
            
            # 状态变化
            for attr in ['health', 'happiness', 'energy']:
                if f'{attr}_change' in impact:
                    attribute_changes[attr] = impact[f'{attr}_change']
            
            # 信任度变化
            if 'trust_change' in impact:
                attribute_changes['trust_level'] = impact['trust_change']
            
            self.person.update_attributes(attribute_changes)
            
            # 保存投资到数据库
            if 'investment' in decision and decision['investment']:
                inv = decision['investment']
                try:
                    from ..database import db
                    # 获取session_id和username
                    session_id = getattr(self.person, 'session_id', None)
                    username = getattr(self.person, 'username', None)
                    
                    if session_id and username:
                        # 映射投资类型
                        type_map = {
                            'SHORT_TERM': '短期',
                            'MEDIUM_TERM': '中期',
                            'LONG_TERM': '长期'
                        }
                        inv_type = type_map.get(inv.get('type', 'SHORT_TERM'), '短期')
                        
                        # 计算月收益（如果有）
                        monthly_return = inv.get('monthly_return', 0)
                        return_rate = inv.get('return_rate', 0.05)
                        
                        db.save_investment(
                            username=username,
                            session_id=session_id,
                            name=inv.get('name', '投资项目'),
                            amount=inv.get('amount', 0),
                            investment_type=inv_type,
                            remaining_months=inv.get('duration', 3),
                            monthly_return=monthly_return,
                            return_rate=return_rate,
                            created_round=current_round,
                            ai_thoughts=decision.get('ai_thoughts', '')
                        )
                        print(f"[投资记录] 已保存: {inv.get('name')} - {inv.get('amount')}CP")
                except Exception as e:
                    print(f"[投资记录] 保存失败: {e}")
            
            return {
                **decision,
                'thought': thought,
                'asset_change': impact.get('cash_change', 0),
                'asset_desc': f"决策影响: {impact.get('cash_change', 0):+,}CP",
                'old_credits': old_credits,
                'new_credits': self.person.attributes.credits,
                'attribute_changes': attribute_changes
            }
        else:
            # 使用传统资产计算
            asset_change, asset_desc = asset_calculator.calculate_decision_impact(
                decision['chosen_option'], self.person.attributes.credits, current_round
            )
            
            old_credits = self.person.attributes.credits
            self.person.update_attributes({'credits': asset_change})
            
            return {
                **decision,
                'thought': thought,
                'asset_change': asset_change,
                'asset_desc': asset_desc,
                'old_credits': old_credits,
                'new_credits': self.person.attributes.credits
            }
    
    def _generate_thought(self, situation: str, options: List[str], player_echo: Optional[str]) -> Dict:
        """生成思维过程"""
        mbti = self.person.attributes.mbti_type
        
        # 根据MBTI确定思维类型
        thought_type = self._get_thought_type(mbti)
        
        # 生成思维内容
        considerations = []
        
        # 财务状况考虑
        if self.person.attributes.credits < 10000:
            considerations.append("资金紧张，需要谨慎决策")
        elif self.person.attributes.credits > 100000:
            considerations.append("资金充裕，可以考虑更多选择")
        
        # 状态考虑
        if self.person.attributes.stress > 70:
            considerations.append("压力很大，需要缓解")
        elif self.person.attributes.happiness < 30:
            considerations.append("心情低落，希望改善")
        elif self.person.attributes.health < 50:
            considerations.append("健康状况不佳，需要关注")
        
        # 玩家建议考虑
        if player_echo:
            trust_level = self.person.attributes.trust_level
            if trust_level > 70:
                considerations.append(f"玩家建议很有价值: {player_echo}")
            elif trust_level > 40:
                considerations.append(f"会参考玩家建议: {player_echo}")
            else:
                considerations.append(f"听到了建议但持保留态度: {player_echo}")
        
        # MBTI特质考虑
        mbti_str = mbti.value
        if "J" in mbti_str:
            considerations.append("倾向于有计划的决策")
        if "P" in mbti_str:
            considerations.append("保持灵活性和开放性")
        
        # 计算信心度
        confidence = 0.7
        if self.person.attributes.stress > 60:
            confidence -= 0.2
        if player_echo and self.person.attributes.trust_level > 60:
            confidence += 0.1
        
        confidence = max(0.3, min(0.95, confidence))
        
        return {
            "type": thought_type.value,
            "considerations": considerations,
            "confidence": confidence,
            "mbti_influence": mbti_str
        }
    
    def _get_thought_type(self, mbti) -> ThoughtType:
        """根据MBTI获取思维类型"""
        thinking_types = {
            "NT": ThoughtType.LOGICAL,
            "NF": ThoughtType.INTUITIVE,
            "ST": ThoughtType.PRACTICAL,
            "SF": ThoughtType.EMOTIONAL
        }
        
        mbti_str = mbti.value
        for pattern, thought_type in thinking_types.items():
            if all(char in mbti_str for char in pattern):
                return thought_type
        
        return ThoughtType.LOGICAL
    
    def _ai_decision(self, situation: str, options: List[str], player_echo: Optional[str], current_round: int = 1) -> Dict:
        """AI决策"""
        context = {
            "name": self.person.attributes.name,
            "age": self.person.attributes.age,
            "mbti": self.person.attributes.mbti_type.value,
            "cash": self.person.attributes.credits,
            "invested_assets": 0,  # TODO: 从投资系统获取
            "total_assets": self.person.attributes.credits,
            "health": self.person.attributes.health,
            "happiness": self.person.attributes.happiness,
            "energy": getattr(self.person.attributes, 'energy', 100),
            "stress": self.person.attributes.stress,
            "trust": self.person.attributes.trust_level,
            "current_month": current_round,
            "situation": situation,
            "options": options,
            "player_echo": player_echo
        }
        
        try:
            result = deepseek_engine.make_decision(context)
            if "error" not in result:
                return {
                    "chosen_option": result["chosen_option"],
                    "ai_thoughts": result["ai_thoughts"],
                    "decision_impact": result.get("decision_impact", {}),
                    "investment": result.get("investment")
                }
        except Exception as e:
            print(f"[WARN] AI decision failed: {e}, falling back to rule-based")
        
        return self._rule_decision(situation, options, player_echo)
    
    def _rule_decision(self, situation: str, options: List[str], player_echo: Optional[str]) -> Dict:
        """规则决策"""
        from ..systems.mbti_traits import mbti_system
        
        # 计算MBTI特质影响
        current_state = {
            "happiness": self.person.attributes.happiness,
            "stress": self.person.attributes.stress,
            "trust": self.person.attributes.trust_level,
            "credits": self.person.attributes.credits
        }
        
        mbti_influence = mbti_system.calculate_decision_influence(
            self.person.attributes.mbti_type, current_state, situation
        )
        
        # 基础权重
        weights = [1.0] * len(options)
        
        # MBTI影响
        mbti = self.person.attributes.mbti_type.value
        for i, option in enumerate(options):
            # 思维型偏好理性选择
            if "T" in mbti and any(word in option for word in ["分析", "计算", "理性", "数据"]):
                weights[i] += 0.3 + mbti_influence * 0.2
            
            # 情感型偏好情感选择
            if "F" in mbti and any(word in option for word in ["感觉", "直觉", "情感", "帮助"]):
                weights[i] += 0.3 + mbti_influence * 0.2
            
            # 保守型人格避免高风险
            if mbti in ["ISTJ", "ISFJ"] and any(word in option for word in ["风险", "投机", "冒险"]):
                weights[i] -= 0.4
            
            # 企业家型偏好机会
            if mbti in ["ENTJ", "ENTP", "ESTP"] and any(word in option for word in ["机会", "投资", "创业"]):
                weights[i] += 0.4
        
        # 玩家影响
        if player_echo:
            trust_factor = self.person.attributes.trust_level / 100
            echo_lower = player_echo.lower()
            
            for i, option in enumerate(options):
                # 检查玩家建议是否与选项匹配
                option_words = set(option.lower().split())
                echo_words = set(echo_lower.split())
                
                # 计算词汇重叠度
                overlap = len(option_words & echo_words) / max(len(option_words), 1)
                if overlap > 0.2:  # 20%以上重叠认为相关
                    weights[i] += 0.5 * trust_factor * overlap
                
                # 明确的数字建议
                if f"选择{i+1}" in echo_lower or f"第{i+1}" in echo_lower:
                    weights[i] += 0.8 * trust_factor
        
        # 选择权重最高的选项
        chosen_idx = weights.index(max(weights))
        chosen_option = options[chosen_idx]
        
        # 生成思考过程
        thoughts = f"作为{mbti}类型，我倾向于选择这个方案。"
        if player_echo and self.person.attributes.trust_level > 50:
            thoughts += "你的建议对我的决策有一定影响。"
        elif player_echo and self.person.attributes.trust_level <= 30:
            thoughts += "虽然听到了你的建议，但我更相信自己的判断。"
        
        return {
            "chosen_option": chosen_option,
            "ai_thoughts": thoughts[:200]
        }
    
    def generate_situation(self, context: Dict) -> Optional[Dict]:
        """生成新的决策情况"""
        if deepseek_engine:
            try:
                return deepseek_engine.generate_situation(context)
            except Exception as e:
                print(f"[WARN] AI situation generation failed: {e}, using fallback")
        
        return self._fallback_situation_generation(context)
    
    def _fallback_situation_generation(self, context: Dict) -> Dict:
        """备用情况生成"""
        import random
        
        # 基于MBTI和当前状态生成情况
        mbti = self.person.attributes.mbti_type.value
        credits = self.person.attributes.credits
        
        situations = {
            "low_money": {
                "description": "你的资金有些紧张，需要寻找增收途径。朋友介绍了一个兼职机会，但需要投入一些时间和精力。",
                "choices": [
                    "接受兼职工作 - 每月额外收入3000-5000CP",
                    "寻找更高薪的全职工作 - 风险较大但收入可能翻倍",
                    "节约开支维持现状 - 减少不必要支出"
                ]
            },
            "medium_money": {
                "description": "你有了一定的积蓄，开始考虑如何让钱生钱。银行理财经理向你推荐了几种投资产品。",
                "choices": [
                    "购买稳健型理财产品 - 年化收益5-8%",
                    "投资股票基金 - 风险较高但收益可观",
                    "继续储蓄等待更好机会 - 保持资金流动性"
                ]
            },
            "high_money": {
                "description": "你的财务状况良好，朋友邀请你参与一个创业项目的天使投资，承诺高回报但风险不小。",
                "choices": [
                    "投资创业项目 - 投入50万CP，可能获得10倍回报",
                    "购买房产投资 - 稳健增值，年化8-12%",
                    "多元化投资组合 - 分散风险，稳步增长"
                ]
            }
        }
        
        # 根据资金状况选择情况类型
        if credits < 50000:
            situation_type = "low_money"
        elif credits < 200000:
            situation_type = "medium_money"
        else:
            situation_type = "high_money"
        
        base_situation = situations[situation_type]
        
        # 根据MBTI调整情况描述
        if "T" in mbti:  # 思维型
            base_situation["description"] += " 你需要理性分析各种选择的利弊。"
        elif "F" in mbti:  # 情感型
            base_situation["description"] += " 你考虑着这个决定对生活的影响。"
        
        return base_situation
    
    def update_trust_level(self, decision_outcome: str, player_suggestion_followed: bool):
        """更新信任度"""
        if not player_suggestion_followed:
            return
        
        # 根据决策结果调整信任度
        trust_change = 0
        if "成功" in decision_outcome or "收益" in decision_outcome:
            trust_change = random.randint(2, 5)
        elif "失败" in decision_outcome or "损失" in decision_outcome:
            trust_change = random.randint(-8, -3)
        else:
            trust_change = random.randint(-1, 2)
        
        self.person.update_attributes({"trust_level": trust_change})
        return trust_change
    
    def get_decision_summary(self) -> Dict:
        """获取决策摘要"""
        return {
            "total_decisions": len(self.thoughts),
            "recent_thoughts": self.thoughts[-3:] if self.thoughts else [],
            "decision_patterns": self.decision_patterns,
            "current_state": {
                "confidence_avg": sum(t.get("confidence", 0.5) for t in self.thoughts[-5:]) / min(5, len(self.thoughts)) if self.thoughts else 0.5,
                "stress_influenced_decisions": sum(1 for t in self.thoughts if "压力" in str(t.get("considerations", []))),
                "player_influenced_decisions": sum(1 for t in self.thoughts if "玩家建议" in str(t.get("considerations", [])))
            }
        }
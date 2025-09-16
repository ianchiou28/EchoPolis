"""
AI化身核心系统 - Echopolis核心模块
实现AI化身的属性、状态管理和决策逻辑
"""
import random
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ..systems.mbti_traits import MBTIType, mbti_system
from ..systems.fate_wheel import FateType, fate_wheel
from ..systems.asset_calculator import asset_calculator
# from ..ai.deepseek_engine import deepseek_engine  # 移除错误的全局导入

class LifeStage(Enum):
    """人生阶段"""
    STARTUP = "startup"      # 启航期 (18-22岁)
    EXPLORATION = "exploration"  # 探索期 (23-30岁)  
    STRUGGLE = "struggle"    # 奋斗期 (31-45岁)
    ACCUMULATION = "accumulation"  # 沉淀期 (46-60岁)
    RETIREMENT = "retirement"  # 黄昏期 (60岁以上)

@dataclass
class AvatarAttributes:
    """AI化身属性"""
    # 基本信息
    name: str
    age: int = 22
    mbti_type: MBTIType = MBTIType.INTP
    fate_type: FateType = FateType.MIDDLE_CLASS
    life_stage: LifeStage = LifeStage.STARTUP
    
    # 财务状况
    credits: int = 50000  # 信用点
    credit_score: int = 700  # 信用分
    long_term_investments: int = 0  # 长期投资
    locked_investments: list = None  # 锁定投资列表
    current_round: int = 1  # 当前回合数
    
    # 身心状态 (0-100)
    health: int = 100
    energy: int = 100
    happiness: int = 50
    stress: int = 0
    
    # 社交关系
    trust_level: int = 50  # 对玩家的信任度 (0-100)
    
    # 决策计数器
    decision_count: int = 0
    successful_decisions: int = 0
    
    # 游戏状态
    is_bankrupt: bool = False

class DecisionContext:
    """决策上下文"""
    def __init__(self, situation: str, options: List[str], context_type: str = "general"):
        self.situation = situation
        self.options = options
        self.context_type = context_type
        self.timestamp = None

class AIAvatar:
    """AI化身主类"""
    
    def __init__(self, name: str, mbti_type: MBTIType):
        self.attributes = AvatarAttributes(name=name, mbti_type=mbti_type)
        self.attributes.locked_investments = []
        self.decision_history: List[Dict] = []
        self.current_situation: Optional[DecisionContext] = None
        
        # 初始化命运
        self._initialize_fate()
    
    def _initialize_fate(self):
        """初始化命运轮盘结果"""
        fate_outcome = fate_wheel.spin_wheel()
        self.attributes.fate_type = fate_outcome.fate_type
        self.attributes.credits = fate_outcome.initial_credits
        
        # 应用初始属性
        for attr, value in fate_outcome.initial_attributes.items():
            if hasattr(self.attributes, attr):
                setattr(self.attributes, attr, value)
        
        # 记录命运背景
        self.fate_background = fate_outcome
    
    def get_status(self) -> Dict:
        """获取化身完整状态"""
        mbti_desc = mbti_system.get_personality_description(self.attributes.mbti_type)
        cash_flow = self._calculate_cash_flow()
        
        return {
            "basic_info": {
                "name": self.attributes.name,
                "age": self.attributes.age,
                "mbti": f"{self.attributes.mbti_type.value} - {mbti_desc}",
                "fate": f"{self.fate_background.name} - {self.fate_background.description}",
                "life_stage": self.attributes.life_stage.value,
                "status": "破产" if self.attributes.is_bankrupt else "正常"
            },
            "financial": {
                "credits": f"{self.attributes.credits:,} CP",
                "long_term_investments": f"{self.attributes.long_term_investments:,} CP",
                "cash_flow": f"{cash_flow:+,} CP",
                "credit_score": self.attributes.credit_score
            },
            "physical_mental": {
                "health": f"{self.attributes.health}/100",
                "energy": f"{self.attributes.energy}/100", 
                "happiness": f"{self.attributes.happiness}/100",
                "stress": f"{self.attributes.stress}/100"
            },
            "relationship": {
                "trust_level": f"{self.attributes.trust_level}/100",
                "trust_status": self._get_trust_status()
            },
            "performance": {
                "total_decisions": self.attributes.decision_count,
                "successful_rate": f"{self._get_success_rate():.1f}%"
            },
            "special_traits": self.fate_background.special_traits,
            "background_story": self.fate_background.background_story
        }
    
    def _get_trust_status(self) -> str:
        """获取信任状态描述"""
        trust = self.attributes.trust_level
        if trust >= 81:
            return "完全依赖 - AI会优先采纳你的建议"
        elif trust >= 51:
            return "高度信赖 - AI很重视你的意见"
        elif trust >= 21:
            return "普通关系 - AI会考虑你的建议"
        else:
            return "怀疑态度 - AI对你的建议持谨慎态度"
    
    def _get_success_rate(self) -> float:
        """计算决策成功率"""
        if self.attributes.decision_count == 0:
            return 0.0
        return (self.attributes.successful_decisions / self.attributes.decision_count) * 100
    
    def generate_situation(self, ai_engine=None) -> Optional[DecisionContext]:
        """生成决策情况"""
        # 使用传入的AI引擎生成情况
        if ai_engine:
            ai_situation = self._generate_ai_situation(ai_engine)
            if ai_situation:
                self.current_situation = ai_situation
                return self.current_situation
        
        # 如果没有AI引擎或AI生成失败，返回空
        return None
    
    def _generate_ai_situation(self, ai_engine) -> Optional[DecisionContext]:
        """使用AI生成情况"""
        context = {
            "name": self.attributes.name,
            "age": self.attributes.age,
            "mbti": self.attributes.mbti_type.value,
            "credits": self.attributes.credits,
            "health": self.attributes.health,
            "happiness": self.attributes.happiness,
            "stress": self.attributes.stress,
            "life_stage": self.attributes.life_stage.value,
            "background": self.fate_background.background_story,
            "traits": ", ".join(self.fate_background.special_traits),
            "decision_count": self.attributes.decision_count
        }
        
        return ai_engine.generate_situation(context)
    
    def make_decision(self, player_echo: Optional[str] = None) -> Dict:
        """AI做出决策"""
        if not self.current_situation:
            return {"error": "没有当前决策情况"}
        
        # 使用规则决策作为默认方法
        chosen_option, ai_thoughts = self._make_rule_decision(player_echo)
        
        # 计算资产影响
        result = asset_calculator.calculate_decision_impact(
            chosen_option, self.attributes.credits
        )
        if len(result) == 3:
            asset_change, asset_desc, investment_type = result
        else:
            asset_change, asset_desc = result
            investment_type = "short_term"
        
        old_credits = self.attributes.credits
        old_cash_flow = self._calculate_cash_flow()
        
        # 处理投资类型
        if investment_type == "long_term":
            self.attributes.long_term_investments += abs(asset_change)
        elif investment_type == "locked":
            # 提取锁定期限
            lock_months = self._extract_lock_period(chosen_option)
            self.attributes.locked_investments.append({
                'amount': abs(asset_change),
                'remaining_rounds': lock_months,
                'description': asset_desc
            })
        
        self.attributes.credits = max(0, self.attributes.credits + asset_change)
        new_cash_flow = self._calculate_cash_flow()
        cash_flow_change = new_cash_flow - old_cash_flow
        
        # 检查破产
        self._check_bankruptcy()
        
        # 通知央行监控交易
        from ..entities.god import central_bank
        central_bank.monitor_transaction(self, asset_change, "decision", chosen_option)
        
        # 更新状态
        trust_change = self._update_trust(player_echo, chosen_option)
        self._update_attributes_after_decision(chosen_option)
        
        # 记录决策历史
        decision_record = {
            "situation": self.current_situation.situation,
            "options": self.current_situation.options,
            "chosen": chosen_option,
            "player_echo": player_echo,
            "ai_thoughts": ai_thoughts,
            "trust_change": trust_change,
            "decision_count": self.attributes.decision_count
        }
        self.decision_history.append(decision_record)
        
        # 清除当前情况
        self.current_situation = None
        
        return {
            "chosen_option": chosen_option,
            "ai_thoughts": ai_thoughts,
            "trust_change": trust_change,
            "new_trust_level": self.attributes.trust_level,
            "asset_change": asset_change,
            "asset_desc": asset_desc,
            "old_credits": old_credits,
            "new_credits": self.attributes.credits,
            "cash_flow": new_cash_flow,
            "cash_flow_change": cash_flow_change,
            "is_bankrupt": self.attributes.is_bankrupt
        }
    
    def make_ai_decision(self, ai_engine, player_echo: Optional[str] = None) -> Dict:
        """使用DeepSeek AI做决策"""
        context = {
            "name": self.attributes.name,
            "age": self.attributes.age,
            "mbti": self.attributes.mbti_type.value,
            "credits": self.attributes.credits,
            "health": self.attributes.health,
            "happiness": self.attributes.happiness,
            "stress": self.attributes.stress,
            "trust": self.attributes.trust_level,
            "background": self.fate_background.background_story,
            "traits": ", ".join(self.fate_background.special_traits),
            "situation": self.current_situation.situation,
            "options": self.current_situation.options,
            "player_echo": player_echo
        }
        
        return ai_engine.make_decision(context)
    
    def _make_rule_decision(self, player_echo: Optional[str] = None) -> Tuple[str, str]:
        """使用规则做决策(备用方案)"""
        # 计算决策权重
        decision_weights = self._calculate_decision_weights(player_echo)
        
        # 选择最高权重的选项
        chosen_option_index = max(range(len(decision_weights)), key=decision_weights.__getitem__)
        chosen_option = self.current_situation.options[chosen_option_index]
        
        # 生成AI的内心想法
        ai_thoughts = self._generate_ai_thoughts(chosen_option, player_echo, decision_weights)
        
        return chosen_option, ai_thoughts
    
    def _calculate_decision_weights(self, player_echo: Optional[str]) -> List[float]:
        """计算每个选项的决策权重"""
        if not self.current_situation:
            return []
        
        num_options = len(self.current_situation.options)
        base_weights = [1.0] * num_options  # 基础权重
        
        # MBTI特质影响
        mbti_influence = mbti_system.calculate_decision_influence(
            self.attributes.mbti_type,
            self._get_current_state(),
            self.current_situation.context_type
        )
        
        # 命运特质影响
        fate_influence = fate_wheel.calculate_fate_influence(
            self.attributes.fate_type,
            self.current_situation.context_type
        )
        
        # 玩家回响影响
        player_influence = self._calculate_player_influence(player_echo)
        
        # 状态影响
        state_influence = self._calculate_state_influence()
        
        # 综合计算权重
        final_weights = []
        for i in range(num_options):
            weight = base_weights[i]
            weight += mbti_influence * 0.3
            weight += sum(fate_influence.values()) * 0.2
            weight += player_influence.get(i, 0) * (self.attributes.trust_level / 100) * 0.4
            weight += state_influence * 0.1
            weight += random.uniform(-0.1, 0.1)  # 随机因子
            final_weights.append(max(weight, 0.1))  # 确保权重不为负
        
        return final_weights
    
    def _get_current_state(self) -> Dict:
        """获取当前状态字典"""
        return {
            "happiness": self.attributes.happiness,
            "stress": self.attributes.stress,
            "trust": self.attributes.trust_level,
            "fq_level": 2,  # 简化的FQ等级
            "credits": self.attributes.credits
        }
    
    def _calculate_player_influence(self, player_echo: Optional[str]) -> Dict[int, float]:
        """计算玩家回响对各选项的影响"""
        if not player_echo:
            return {}
        
        influence = {}
        echo_lower = player_echo.lower()
        
        # 简单的关键词匹配逻辑
        for i, option in enumerate(self.current_situation.options):
            option_lower = option.lower()
            
            # 正面关键词匹配
            if any(keyword in echo_lower for keyword in ["建议", "推荐", "应该", "最好"]):
                if any(word in echo_lower for word in option_lower.split()):
                    influence[i] = 0.5
            
            # 负面关键词匹配
            if any(keyword in echo_lower for keyword in ["不要", "别", "不建议", "风险"]):
                if any(word in echo_lower for word in option_lower.split()):
                    influence[i] = -0.5
        
        return influence
    
    def _calculate_state_influence(self) -> float:
        """计算当前状态对决策的影响"""
        influence = 0.0
        
        # 压力影响
        if self.attributes.stress > 70:
            influence -= 0.2  # 高压力时倾向保守
        
        # 幸福感影响
        if self.attributes.happiness < 30:
            influence -= 0.1  # 低幸福感时可能做出情绪化决策
        
        # 健康影响
        if self.attributes.health < 50:
            influence -= 0.1  # 健康不佳时决策能力下降
        
        return influence
    
    def _generate_ai_thoughts(self, chosen_option: str, player_echo: Optional[str], weights: List[float]) -> str:
        """生成AI的内心想法"""
        thoughts = []
        
        # 基于选择的基本想法
        if "投资" in chosen_option:
            if "10万" in chosen_option:
                thoughts.append("我觉得这是个不错的机会，值得大胆尝试")
            elif "1万" in chosen_option:
                thoughts.append("小额试水比较稳妥，可以控制风险")
            else:
                thoughts.append("这个投资风险太大，我选择保守一些")
        
        # 基于MBTI特质的想法
        mbti_thoughts = {
            MBTIType.INTP: "我需要更多时间分析这个决策的各种可能性",
            MBTIType.ENTJ: "机会稍纵即逝，必须果断行动",
            MBTIType.ISTJ: "我更倾向于选择稳妥可靠的方案",
            MBTIType.ESFP: "我的直觉告诉我这样做"
        }
        
        if self.attributes.mbti_type in mbti_thoughts:
            thoughts.append(mbti_thoughts[self.attributes.mbti_type])
        
        # 基于玩家回响的想法
        if player_echo:
            trust_level = self.attributes.trust_level
            if trust_level > 70:
                thoughts.append(f"我很信任你的建议：'{player_echo}'")
            elif trust_level > 40:
                thoughts.append(f"我会考虑你的意见：'{player_echo}'")
            else:
                thoughts.append(f"虽然你建议'{player_echo}'，但我有自己的判断")
        
        # 基于当前状态的想法
        if self.attributes.stress > 60:
            thoughts.append("目前压力比较大，需要谨慎选择")
        if self.attributes.happiness < 40:
            thoughts.append("最近心情不太好，希望这个决策能改善情况")
        
        result = "，".join(thoughts)
        # 限制长度到150个字符内
        if len(result) > 150:
            result = result[:147] + "..."
        
        return result
    
    def _update_trust(self, player_echo: Optional[str], chosen_option: str) -> int:
        """更新信任度"""
        if not player_echo:
            return 0
        
        # 简化的信任度更新逻辑
        trust_change = 0
        echo_lower = player_echo.lower()
        option_lower = chosen_option.lower()
        
        # 如果AI采纳了玩家的建议
        if any(word in echo_lower for word in option_lower.split()):
            trust_change = random.randint(2, 5)
        else:
            # 如果AI没有采纳建议，信任度可能下降
            trust_change = random.randint(-2, 1)
        
        self.attributes.trust_level = max(0, min(100, self.attributes.trust_level + trust_change))
        return trust_change
    
    def _update_attributes_after_decision(self, chosen_option: str):
        """决策后更新属性"""
        self.attributes.decision_count += 1
        
        # 简化的属性更新逻辑
        if "投资" in chosen_option:
            self.attributes.stress += random.randint(1, 3)
        
        if "拒绝" in chosen_option:
            self.attributes.happiness -= random.randint(1, 2)
        
        # 确保属性在合理范围内
        self.attributes.stress = min(100, self.attributes.stress)
        self.attributes.happiness = max(0, self.attributes.happiness)
    
    def advance_round(self):
        """推进一回合（一个月）"""
        if self.attributes.is_bankrupt:
            return
        
        self.attributes.current_round += 1
        
        # 精力恢复
        self.attributes.energy = min(100, self.attributes.energy + 20)
        
        # 压力自然衰减
        self.attributes.stress = max(0, self.attributes.stress - 2)
        
        # 信任度缓慢衰减
        if self.attributes.trust_level > 50:
            self.attributes.trust_level = max(50, self.attributes.trust_level - 1)
        
        # 处理锁定投资
        self._process_locked_investments()
        
        # 长期投资收益
        if self.attributes.long_term_investments > 0:
            monthly_return = int(self.attributes.long_term_investments * 0.003)  # 0.3%月收益
            self.attributes.credits += monthly_return
        
        # 月度开支
        monthly_expense = random.randint(3000, 15000)
        self.attributes.credits -= monthly_expense
        
        # 检查破产
        self._check_bankruptcy()
        
        # 年龄增长 (每12回合增长1岁)
        if self.attributes.current_round % 12 == 0:
            self.attributes.age += 1
            self._update_life_stage()
    
    def _update_life_stage(self):
        """更新人生阶段"""
        age = self.attributes.age
        if age <= 22:
            self.attributes.life_stage = LifeStage.STARTUP
        elif age <= 30:
            self.attributes.life_stage = LifeStage.EXPLORATION
        elif age <= 45:
            self.attributes.life_stage = LifeStage.STRUGGLE
        elif age <= 60:
            self.attributes.life_stage = LifeStage.ACCUMULATION
        else:
            self.attributes.life_stage = LifeStage.RETIREMENT
    
    def save_state(self) -> Dict:
        """保存化身状态"""
        return {
            "attributes": asdict(self.attributes),
            "fate_background": asdict(self.fate_background),
            "decision_history": self.decision_history
        }
    
    def _calculate_cash_flow(self) -> int:
        """计算现金流 = 总资产 - 长期投资 - 锁定投资"""
        locked_amount = sum(inv['amount'] for inv in self.attributes.locked_investments)
        return self.attributes.credits - self.attributes.long_term_investments - locked_amount
    
    def _check_bankruptcy(self):
        """检查破产状态"""
        cash_flow = self._calculate_cash_flow()
        if cash_flow < 0:
            self.attributes.is_bankrupt = True
    
    def _extract_lock_period(self, option: str) -> int:
        """提取锁定期限（月数）"""
        import re
        # 查找数字+月或数字+个月
        months = re.findall(r'(\d+)(?:个)?月', option)
        if months:
            return int(months[0])
        # 查找数字+年
        years = re.findall(r'(\d+)年', option)
        if years:
            return int(years[0]) * 12
        return 12  # 默认1年
    
    def _process_locked_investments(self):
        """处理锁定投资的到期"""
        expired_investments = []
        for i, inv in enumerate(self.attributes.locked_investments):
            inv['remaining_rounds'] -= 1
            if inv['remaining_rounds'] <= 0:
                # 投资到期，返还本金和收益
                return_amount = int(inv['amount'] * random.uniform(1.1, 1.4))  # 10%-40%收益
                self.attributes.credits += return_amount
                expired_investments.append(i)
        
        # 移除已到期的投资
        for i in reversed(expired_investments):
            del self.attributes.locked_investments[i]
    
    def load_state(self, state_data: Dict):
        """加载化身状态"""
        if "attributes" in state_data:
            attr_data = state_data["attributes"]
            for key, value in attr_data.items():
                if hasattr(self.attributes, key):
                    setattr(self.attributes, key, value)
            # 确保 locked_investments 是列表
            if not hasattr(self.attributes, 'locked_investments') or self.attributes.locked_investments is None:
                self.attributes.locked_investments = []
        
        if "decision_history" in state_data:
            self.decision_history = state_data["decision_history"]
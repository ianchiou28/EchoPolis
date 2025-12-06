"""
AI化身核心系统 - FinAI核心模块
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
from ..systems.investment_system import investment_system
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
    
    def __init__(self, name: str, mbti_type: MBTIType, session_id: str = None):
        self.attributes = AvatarAttributes(name=name, mbti_type=mbti_type)
        self.attributes.locked_investments = []
        self.decision_history: List[Dict] = []
        self.current_situation: Optional[DecisionContext] = None
        self.session_id = session_id
        
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
        
        # 如果没有AI引擎或AI生成失败，使用预设情况
        fallback_situation = self._generate_fallback_situation()
        if fallback_situation:
            self.current_situation = fallback_situation
        return self.current_situation
    
    def _generate_ai_situation(self, ai_engine) -> Optional[DecisionContext]:
        """使用AI生成情况"""
        if not ai_engine or not hasattr(ai_engine, 'api_key') or not ai_engine.api_key:
            print(f"[WARN] AI引擎不可用，跳过AI情况生成")
            return None
        
        context = {
            "name": self.attributes.name,
            "age": self.attributes.age,
            "mbti": self.attributes.mbti_type.value if hasattr(self.attributes.mbti_type, 'value') else str(self.attributes.mbti_type),
            "cash": self.attributes.credits,
            "health": self.attributes.health,
            "happiness": self.attributes.happiness,
            "stress": self.attributes.stress,
            "energy": self.attributes.energy,
            "life_stage": self.attributes.life_stage.value,
            "background": self.fate_background.background_story,
            "traits": ", ".join(self.fate_background.special_traits),
            "decision_count": self.attributes.decision_count
        }
        
        # 添加用户标签和自动标签
        if hasattr(self, 'user_tags'):
            context["user_tags"] = self.user_tags
        if hasattr(self, 'auto_tags'):
            context["auto_tags"] = self.auto_tags
        
        # 添加行为画像数据（如果有）
        if hasattr(self, 'behavior_profile') and self.behavior_profile:
            context["behavior_profile"] = {
                "risk_preference": self.behavior_profile.get("risk_preference", "moderate"),
                "decision_style": self.behavior_profile.get("decision_style", "rational"),
                "avg_risk_score": self.behavior_profile.get("avg_risk_score", 0.5),
                "avg_rationality": self.behavior_profile.get("avg_rationality", 0.5),
                "action_count": self.behavior_profile.get("action_count", 0)
            }
            # 从行为画像获取自动标签
            if not context.get("auto_tags") and self.behavior_profile.get("auto_tags"):
                context["auto_tags"] = self.behavior_profile.get("auto_tags")
        
        # 添加职业状态数据（如果有）
        if hasattr(self, 'career_status') and self.career_status:
            current_job = self.career_status.get("current_job") or {}
            # 检查是否有有效的工作（title 不为 None）
            has_valid_job = current_job and current_job.get("title") is not None
            context["career"] = {
                "has_job": has_valid_job,
                "job_title": current_job.get("title", "无业") if has_valid_job else "无业",
                "company": current_job.get("company", "") if has_valid_job else "",
                "salary": current_job.get("salary", 0) if has_valid_job else 0,
                "months_employed": current_job.get("months", 0) if has_valid_job else 0,
                "skills": self.career_status.get("skills", []),
                "job_history_count": len(self.career_status.get("job_history", []))
            }
        else:
            # 默认无业状态
            context["career"] = {
                "has_job": False,
                "job_title": "无业",
                "company": "",
                "salary": 0,
                "months_employed": 0,
                "skills": [],
                "job_history_count": 0
            }
        
        try:
            print(f"[DEBUG] 调用AI情况生成，API Key可用: {ai_engine.api_key is not None}")
            print(f"[DEBUG] 用户标签: {context.get('user_tags', '无')}, 自动标签: {context.get('auto_tags', '无')}")
            ai_situation = ai_engine.generate_situation(context)
            if ai_situation:
                print(f"[DEBUG] AI生成情况成功")
                return DecisionContext(
                    situation=ai_situation["description"],
                    options=ai_situation["choices"],
                    context_type="ai_generated"
                )
        except Exception as e:
            print(f"[ERROR] AI情况生成失败: {e}")
        
        return None
    
    def set_user_tags(self, tags: str):
        """设置用户自选标签"""
        self.user_tags = tags
    
    def set_auto_tags(self, tags: str):
        """设置自动生成标签"""
        self.auto_tags = tags
    
    def set_behavior_profile(self, profile: dict):
        """设置行为画像数据"""
        self.behavior_profile = profile
    
    def set_career_status(self, career_info: dict):
        """设置职业状态数据"""
        self.career_status = career_info
    
    def make_decision(self, player_echo: Optional[str] = None, ai_engine=None) -> Dict:
        """AI做出决策"""
        if not self.current_situation:
            return {"error": "没有当前决策情况"}
        
        # 优先使用AI决策，如果失败则使用规则决策
        print(f"[DEBUG] AI引擎可用: {ai_engine is not None}")
        if ai_engine:
            print(f"[DEBUG] API Key可用: {hasattr(ai_engine, 'api_key') and ai_engine.api_key is not None}")
        
        if ai_engine and hasattr(ai_engine, 'api_key') and ai_engine.api_key:
            try:
                print(f"[DEBUG] 尝试AI决策...")
                ai_result = self.make_ai_decision(ai_engine, player_echo)
                print(f"[DEBUG] AI决策结果: {ai_result}")
                if "error" not in ai_result:
                    return self._process_ai_decision_result(ai_result, player_echo)
                else:
                    print(f"[WARN] AI决策返回错误: {ai_result.get('error')}")
            except Exception as e:
                print(f"[ERROR] AI决策异常: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[INFO] AI引擎不可用，使用规则决策")
        
        # 使用规则决策作为备用方案
        return self._process_rule_decision(player_echo)
    
    def _process_ai_decision_result(self, ai_result: Dict, player_echo: Optional[str]) -> Dict:
        """处理AI决策结果并应用到化身属性"""
        chosen_option = ai_result.get("chosen_option", "")
        ai_thoughts = ai_result.get("ai_thoughts", "AI没有提供想法")
        
        old_credits = self.attributes.credits
        old_cash_flow = self._calculate_cash_flow()
        
        # 应用AI决策的影响
        if "decision_impact" in ai_result:
            impact = ai_result["decision_impact"]
            
            # 应用财务变化
            cash_change = impact.get("cash_change", 0)
            invested_assets_change = impact.get("invested_assets_change", 0)
            
            # 现金变化
            self.attributes.credits += cash_change
            
            # 投资资产变化（AI已经计算好了）
            if invested_assets_change != 0:
                self.attributes.long_term_investments += invested_assets_change
            
            # 应用状态变化
            self.attributes.health += impact.get("health_change", 0)
            self.attributes.happiness += impact.get("happiness_change", 0)
            self.attributes.energy += impact.get("energy_change", 0)
            self.attributes.stress += impact.get("stress_change", 0)
            
            # 确保属性在合理范围内
            self.attributes.health = max(0, min(100, self.attributes.health))
            self.attributes.happiness = max(0, min(100, self.attributes.happiness))
            self.attributes.energy = max(0, min(100, self.attributes.energy))
            self.attributes.stress = max(0, min(100, self.attributes.stress))
            self.attributes.credits = max(0, self.attributes.credits)
            
            # 处理投资记录（只记录一次）
            investment_saved = False
            if "investment_item" in impact and impact["investment_item"] and not investment_saved:
                inv_data = impact["investment_item"]
                investment_name = inv_data.get("name", "AI投资项目")
                amount = inv_data.get("amount", abs(invested_assets_change))
                duration = inv_data.get("duration", 12)
                inv_type = inv_data.get("type", "MEDIUM_TERM")
                
                # 保存投资到数据库
                self._save_investment_to_db(investment_name, amount, inv_type, duration, 0, 0.1, ai_thoughts)
                investment_saved = True
            elif "investment" in impact and impact["investment"] and not investment_saved:
                # 兼容旧格式
                inv_data = impact["investment"]
                investment_name = inv_data.get("name", "AI投资项目")
                amount = inv_data.get("amount", abs(invested_assets_change))
                
                self._save_investment_to_db(investment_name, amount, "MEDIUM_TERM", 12, 0, 0.1, ai_thoughts)
                investment_saved = True
            
            # 处理交易记录
            if "transaction_name" in impact:
                from ..systems.investment_system import investment_system
                transaction_name = impact["transaction_name"]
                transaction_amount = cash_change
                investment_system.add_transaction(
                    self.attributes.current_round,
                    transaction_name,
                    transaction_amount
                )
                
                # 保存到数据库
                self._save_transaction_to_db(transaction_name, transaction_amount, ai_thoughts)
            else:
                # 如果没有明确的交易名称，根据现金变化推断
                if cash_change > 0:
                    self._save_transaction_to_db("工资收入", cash_change, ai_thoughts)
                elif cash_change < 0 and "investment" not in impact:
                    self._save_transaction_to_db("其他支出", cash_change, ai_thoughts)
            
            # 处理投资（避免重复）
            # if "investment" in ai_result and ai_result["investment"]:
            #     pass  # 已在上面处理过了
        
        new_cash_flow = self._calculate_cash_flow()
        cash_flow_change = new_cash_flow - old_cash_flow
        
        # 检查破产
        self._check_bankruptcy()
        
        # 更新信任度（结合AI决策中的trust_change和传统逻辑）
        ai_trust_change = 0
        if "decision_impact" in ai_result:
            ai_trust_change = ai_result["decision_impact"].get("trust_change", 0)
        
        traditional_trust_change = self._update_trust(player_echo, chosen_option)
        trust_change = ai_trust_change + traditional_trust_change
        
        # 确保信任度在合理范围内
        self.attributes.trust_level = max(0, min(100, self.attributes.trust_level))
        
        self._update_attributes_after_decision(chosen_option)
        
        # 记录决策历史
        decision_record = {
            "situation": self.current_situation.situation,
            "options": self.current_situation.options,
            "chosen": chosen_option,
            "player_echo": player_echo,
            "ai_thoughts": ai_thoughts,
            "trust_change": trust_change,
            "decision_count": self.attributes.decision_count,
            "ai_decision": True
        }
        self.decision_history.append(decision_record)
        
        # 推进一个月
        self.advance_round()
        
        # 清除当前情况
        self.current_situation = None
        
        return {
            "chosen_option": chosen_option,
            "ai_thoughts": ai_thoughts,
            "trust_change": trust_change,
            "new_trust_level": self.attributes.trust_level,
            "asset_change": ai_result.get("decision_impact", {}).get("cash_change", 0),
            "monthly_expense": self._calculate_monthly_expense(),
            "asset_desc": "AI决策影响",
            "old_credits": old_credits,
            "new_credits": self.attributes.credits,
            "cash_flow": new_cash_flow,
            "cash_flow_change": cash_flow_change,
            "is_bankrupt": self.attributes.is_bankrupt,
            "current_round": self.attributes.current_round
        }
    
    def _process_rule_decision(self, player_echo: Optional[str]) -> Dict:
        """处理规则决策"""
        chosen_option, ai_thoughts = self._make_rule_decision(player_echo)
        
        # 计算资产影响
        result = asset_calculator.calculate_decision_impact(
            chosen_option, self.attributes.credits, self.attributes.current_round
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
        
        # 通知央行监控交易（如果可用）
        try:
            from ..entities.god import central_bank
            central_bank.monitor_transaction(self, asset_change, "decision", chosen_option)
        except ImportError:
            pass  # 央行模块不可用时跳过
        
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
            "decision_count": self.attributes.decision_count,
            "ai_decision": False
        }
        self.decision_history.append(decision_record)
        
        # 记录其他交易（如果有现金变化但没有明确的交易记录）
        if asset_change > 0:
            self._save_transaction_to_db("工资收入", asset_change, ai_thoughts)
        elif asset_change < 0 and "investment" not in asset_desc.lower():
            self._save_transaction_to_db("其他支出", asset_change, ai_thoughts)
        
        # 记录月基础开支
        monthly_expense = self._calculate_monthly_expense()
        if monthly_expense > 0:
            self._save_transaction_to_db("月基础开支", -monthly_expense, ai_thoughts)
        
        # 处理月收益
        monthly_returns = asset_calculator.process_monthly_returns(self.attributes.current_round)
        if monthly_returns > 0:
            self.attributes.credits += monthly_returns
            # 保存月收益到数据库
            self._save_transaction_to_db("月收益", monthly_returns)
        
        # 推进一个月
        self.advance_round()
        
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
            "is_bankrupt": self.attributes.is_bankrupt,
            "current_round": self.attributes.current_round
        }
    
    def make_ai_decision(self, ai_engine, player_echo: Optional[str] = None) -> Dict:
        """使用DeepSeek AI做决策"""
        if not ai_engine or not hasattr(ai_engine, 'api_key') or not ai_engine.api_key:
            return {"error": "AI引擎不可用"}
        
        context = {
            "name": self.attributes.name,
            "age": self.attributes.age,
            "mbti": self.attributes.mbti_type.value if hasattr(self.attributes.mbti_type, 'value') else str(self.attributes.mbti_type),
            "cash": self.attributes.credits,
            "invested_assets": self.attributes.long_term_investments,
            "total_assets": self.attributes.credits + self.attributes.long_term_investments,
            "health": self.attributes.health,
            "happiness": self.attributes.happiness,
            "energy": self.attributes.energy,
            "stress": self.attributes.stress,
            "trust": self.attributes.trust_level,
            "background": self.fate_background.background_story,
            "traits": ", ".join(self.fate_background.special_traits),
            "situation": self.current_situation.situation,
            "options": self.current_situation.options,
            "player_echo": player_echo,
            "current_month": self.attributes.current_round
        }
        
        try:
            print(f"[DEBUG] 调用AI决策，API Key可用: {ai_engine.api_key is not None}")
            result = ai_engine.make_decision(context)
            print(f"[DEBUG] AI决策结果: {result.get('chosen_option', 'N/A')}")
            return result
        except Exception as e:
            print(f"[ERROR] AI决策调用失败: {e}")
            return {"error": str(e)}
    
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
    
    def _save_investment_to_db(self, name: str, amount: int, inv_type: str, duration: int, monthly_return: int, return_rate: float, ai_thoughts: str = None):
        """保存投资到数据库"""
        try:
            from ..database.database import db
            if self.session_id:
                db.save_investment(
                    self.session_id,  # 使用session_id作为username（账号）
                    self.session_id,
                    name,
                    amount,
                    inv_type,
                    duration,
                    monthly_return,
                    return_rate,
                    self.attributes.current_round,
                    ai_thoughts
                )
        except Exception as e:
            print(f"[WARN] 保存投资失败: {e}")
            pass  # 数据库不可用时跳过
    
    def _save_transaction_to_db(self, transaction_name: str, amount: int, ai_thoughts: str = None):
        """保存交易到数据库"""
        try:
            from ..database.database import db
            if self.session_id:
                db.save_transaction(
                    self.session_id,  # 使用session_id作为username（账号）
                    self.session_id,
                    self.attributes.current_round,
                    transaction_name,
                    amount,
                    ai_thoughts
                )
        except Exception as e:
            print(f"[WARN] 保存交易失败: {e}")
            pass  # 数据库不可用时跳过
    
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
        
        # 添加月工资收入
        monthly_salary = self._calculate_monthly_salary()
        if monthly_salary > 0:
            self.attributes.credits += monthly_salary
            self._save_transaction_to_db("月工资收入", monthly_salary)
            print(f"[DEBUG] Saved monthly salary: {monthly_salary}")
        
        # 信任度缓慢衰减
        if self.attributes.trust_level > 50:
            self.attributes.trust_level = max(50, self.attributes.trust_level - 1)
        
        # 处理锁定投资
        self._process_locked_investments()
        
        # 长期投资收益
        if self.attributes.long_term_investments > 0:
            monthly_return = int(self.attributes.long_term_investments * 0.003)  # 0.3%月收益
            self.attributes.credits += monthly_return
            # 记录投资收益交易
            if monthly_return > 0:
                self._save_transaction_to_db("长期投资收益", monthly_return)
                print(f"[DEBUG] Saved investment return: {monthly_return}")
        
        # 基于阶级的月度开支
        monthly_expense = self._calculate_monthly_expense()
        self.attributes.credits -= monthly_expense
        
        # 记录月基础开支交易
        if monthly_expense > 0:
            self._save_transaction_to_db("月基础开支", -monthly_expense)
            print(f"[DEBUG] Saved monthly expense: {-monthly_expense}")
        
        # 检查破产
        self._check_bankruptcy()
        
        # 年龄增长 (每12回合增长1岁)
        if self.attributes.current_round % 12 == 0:
            self.attributes.age += 1
            self._update_life_stage()
    
    def _calculate_monthly_expense(self) -> int:
        """根据命运阶级计算月度基础开支"""
        from ..systems.fate_wheel import FateType
        
        # 基于命运类型的月度开支
        expense_map = {
            FateType.BILLIONAIRE: random.randint(80000, 120000),      # 亿万富豪：8-12万/月
            FateType.SCHOLAR_FAMILY: random.randint(15000, 25000),    # 书香门第：1.5-2.5万/月
            FateType.MIDDLE_CLASS: random.randint(12000, 18000),      # 中产家庭：1.2-1.8万/月
            FateType.SELF_MADE: random.randint(8000, 12000),          # 白手起家：0.8-1.2万/月
            FateType.WORKING_CLASS: random.randint(6000, 10000),      # 工薪阶层：0.6-1万/月
            FateType.FALLEN_NOBLE: random.randint(10000, 15000),      # 家道中落：1-1.5万/月（维持体面）
            FateType.LOW_INCOME: random.randint(3000, 5000),          # 低收入户：0.3-0.5万/月
        }
        
        return expense_map.get(self.attributes.fate_type, random.randint(8000, 12000))
    
    def _calculate_monthly_salary(self) -> int:
        """根据命运阶级计算月工资"""
        from ..systems.fate_wheel import FateType
        
        # 基于命运类型的月工资
        salary_map = {
            FateType.BILLIONAIRE: random.randint(200000, 300000),      # 亿万富豪：20-30万/月
            FateType.SCHOLAR_FAMILY: random.randint(25000, 35000),     # 书香门第：2.5-3.5万/月
            FateType.MIDDLE_CLASS: random.randint(18000, 25000),       # 中产家庭：1.8-2.5万/月
            FateType.SELF_MADE: random.randint(12000, 18000),          # 白手起家：1.2-1.8万/月
            FateType.WORKING_CLASS: random.randint(8000, 12000),       # 工薪阶层：0.8-1.2万/月
            FateType.FALLEN_NOBLE: random.randint(15000, 20000),       # 家道中落：1.5-2万/月
            FateType.LOW_INCOME: random.randint(5000, 8000),           # 低收入户：0.5-0.8万/月
        }
        
        return salary_map.get(self.attributes.fate_type, random.randint(10000, 15000))
    
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
                # 记录投资到期收益交易
                self._save_transaction_to_db(f"{inv.get('description', '投资项目')}到期收益", return_amount)
                print(f"[DEBUG] Saved matured investment return: {return_amount}")
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
    
    def _generate_fallback_situation(self) -> Optional[DecisionContext]:
        """生成预设情况（当AI不可用时）"""
        import random
        
        situations = [
            {
                "situation": f"作为{self.attributes.mbti_type.value if hasattr(self.attributes.mbti_type, 'value') else str(self.attributes.mbti_type)}类型的{self.attributes.name}，你面临一个投资机会。银行经理向你推荐一个新的理财产品，年化收益率8%，但需要锁定资金2年。",
                "options": [
                    "投资50万元到该产品（锁定2年）",
                    "只投资10万元试水（锁定2年）",
                    "拒绝投资，寻找其他机会"
                ]
            },
            {
                "situation": f"作为{self.attributes.mbti_type.value if hasattr(self.attributes.mbti_type, 'value') else str(self.attributes.mbti_type)}类型的{self.attributes.name}，你在职场上面临选择。公司提供两个职位选择：高薪但压力大的管理岗，或稳定的技术岗。",
                "options": [
                    "选择管理岗位，追求高收入（月薪+5000，压力+20）",
                    "选择技术岗位，追求稳定（月薪+3000，幸福感+10）",
                    "继续寻找其他工作机会"
                ]
            },
            {
                "situation": f"作为{self.attributes.mbti_type.value if hasattr(self.attributes.mbti_type, 'value') else str(self.attributes.mbti_type)}类型的{self.attributes.name}，你的朋友邀请你投资他的创业项目。他声称这是下一个大机会，但需要投入30万元，成功率不确定。",
                "options": [
                    "全力支持朋友，投资30万（高风险高收益）",
                    "小额投资5万表示支持（低风险）",
                    "礼貌拒绝，保持友谊（保守选择）"
                ]
            }
        ]
        
        situation_data = random.choice(situations)
        self.current_situation = DecisionContext(
            situation=situation_data["situation"],
            options=situation_data["options"],
            context_type="fallback"
        )
        return self.current_situation
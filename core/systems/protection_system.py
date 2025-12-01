"""
防输保护机制 - EchoPolis
破产保护、杠杆限制、新手期、预警系统
"""
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class WarningLevel(Enum):
    """警告级别"""
    INFO = "提示"
    WARNING = "警告"
    DANGER = "危险"
    CRITICAL = "紧急"


@dataclass
class Warning:
    """警告信息"""
    level: WarningLevel
    title: str
    message: str
    suggestion: str


class ProtectionSystem:
    """防输保护系统"""
    
    # 新手保护期（月）
    NEWBIE_PERIOD = 6
    
    # 杠杆限制
    MAX_LEVERAGE_RATIO = 0.2  # 杠杆产品最多占总资产20%
    MAX_SINGLE_STOCK_RATIO = 0.3  # 单只股票最多30%
    
    # 破产保护
    BANKRUPTCY_THRESHOLD = -50000  # 负债超过5万触发破产
    REBIRTH_RETAIN_SKILL = 0.5  # 重生保留50%技能
    REBIRTH_SEED_MONEY = 10000  # 重生启动资金
    
    def __init__(self):
        self.bankruptcy_count: Dict[str, int] = {}
        self.warnings_history: Dict[str, List[Warning]] = {}
    
    def check_newbie_protection(self, current_month: int) -> Dict:
        """检查新手保护状态"""
        is_newbie = current_month <= self.NEWBIE_PERIOD
        
        if is_newbie:
            remaining = self.NEWBIE_PERIOD - current_month
            return {
                "is_protected": True,
                "remaining_months": remaining,
                "benefits": [
                    "市场波动减半",
                    "负面事件概率降低50%",
                    "首次亏损补偿20%"
                ]
            }
        return {"is_protected": False}
    
    def apply_newbie_modifier(self, value: float, current_month: int, 
                             is_negative: bool = False) -> float:
        """应用新手期修正"""
        if current_month > self.NEWBIE_PERIOD:
            return value
        
        if is_negative:
            return value * 0.5  # 负面影响减半
        return value
    
    def check_leverage_limit(self, session_id: str, total_assets: int,
                            leverage_holdings: int, new_amount: int) -> Tuple[bool, str]:
        """检查杠杆限制"""
        if total_assets <= 0:
            return False, "资产不足，无法使用杠杆产品"
        
        current_ratio = leverage_holdings / total_assets
        new_ratio = (leverage_holdings + new_amount) / total_assets
        
        if new_ratio > self.MAX_LEVERAGE_RATIO:
            max_allowed = int(total_assets * self.MAX_LEVERAGE_RATIO - leverage_holdings)
            return False, f"杠杆持仓已达上限(20%)，最多可再投入¥{max(0, max_allowed):,}"
        
        return True, "OK"
    
    def check_concentration_risk(self, session_id: str, total_assets: int,
                                 holdings: Dict[str, int]) -> List[Warning]:
        """检查集中度风险"""
        warnings = []
        
        for asset_name, amount in holdings.items():
            if total_assets <= 0:
                continue
            ratio = amount / total_assets
            
            if ratio > 0.5:
                warnings.append(Warning(
                    level=WarningLevel.DANGER,
                    title="持仓过度集中",
                    message=f"{asset_name}占比{ratio*100:.0f}%，超过50%",
                    suggestion="建议分散投资，降低单一资产风险"
                ))
            elif ratio > self.MAX_SINGLE_STOCK_RATIO:
                warnings.append(Warning(
                    level=WarningLevel.WARNING,
                    title="单一持仓偏高",
                    message=f"{asset_name}占比{ratio*100:.0f}%，超过30%",
                    suggestion="考虑适当减仓，分散风险"
                ))
        
        return warnings
    
    def check_cashflow_warning(self, cash: int, monthly_expense: int,
                              monthly_income: int) -> Optional[Warning]:
        """检查现金流预警"""
        months_runway = cash / monthly_expense if monthly_expense > 0 else 999
        net_flow = monthly_income - monthly_expense
        
        if cash < 0:
            return Warning(
                level=WarningLevel.CRITICAL,
                title="现金流断裂",
                message="现金为负，急需补充资金",
                suggestion="立即变现部分资产或申请贷款"
            )
        
        if months_runway < 1:
            return Warning(
                level=WarningLevel.DANGER,
                title="现金即将耗尽",
                message=f"现金仅够支撑{months_runway:.1f}个月",
                suggestion="减少支出或增加收入来源"
            )
        
        if months_runway < 3:
            return Warning(
                level=WarningLevel.WARNING,
                title="现金储备不足",
                message=f"建议保留3-6个月支出的现金储备",
                suggestion="暂缓新投资，优先补充现金"
            )
        
        if net_flow < 0 and months_runway < 6:
            return Warning(
                level=WarningLevel.INFO,
                title="现金流为负",
                message="支出大于收入，注意控制",
                suggestion="检查固定支出，寻找增收机会"
            )
        
        return None
    
    def check_bankruptcy(self, total_assets: int, total_debt: int) -> Tuple[bool, Dict]:
        """检查是否破产"""
        net_worth = total_assets - total_debt
        
        if net_worth < self.BANKRUPTCY_THRESHOLD:
            return True, {
                "net_worth": net_worth,
                "total_assets": total_assets,
                "total_debt": total_debt,
                "threshold": self.BANKRUPTCY_THRESHOLD
            }
        return False, {}
    
    def process_bankruptcy(self, session_id: str, skills: List[str]) -> Dict:
        """处理破产"""
        # 记录破产次数
        self.bankruptcy_count[session_id] = self.bankruptcy_count.get(session_id, 0) + 1
        count = self.bankruptcy_count[session_id]
        
        # 计算保留的技能
        retained_skills_count = int(len(skills) * self.REBIRTH_RETAIN_SKILL)
        retained_skills = skills[:retained_skills_count] if skills else []
        
        # 根据破产次数调整重生资金
        seed_money = self.REBIRTH_SEED_MONEY
        if count == 1:
            seed_money = 10000
        elif count == 2:
            seed_money = 5000
        else:
            seed_money = 3000
        
        return {
            "bankruptcy_count": count,
            "seed_money": seed_money,
            "retained_skills": retained_skills,
            "message": self._get_bankruptcy_message(count)
        }
    
    def _get_bankruptcy_message(self, count: int) -> str:
        """获取破产提示信息"""
        if count == 1:
            return "首次破产，系统给予最大支持。吸取教训，重新出发！"
        elif count == 2:
            return "再次破产，启动资金减少。请更谨慎地管理风险。"
        else:
            return "多次破产，请认真学习理财知识后再尝试。"
    
    def get_all_warnings(self, session_id: str, cash: int, total_assets: int,
                        monthly_income: int, monthly_expense: int,
                        holdings: Dict[str, int], leverage_holdings: int,
                        current_month: int) -> List[Dict]:
        """获取所有警告"""
        warnings = []
        
        # 现金流警告
        cf_warning = self.check_cashflow_warning(cash, monthly_expense, monthly_income)
        if cf_warning:
            warnings.append({
                "level": cf_warning.level.value,
                "title": cf_warning.title,
                "message": cf_warning.message,
                "suggestion": cf_warning.suggestion
            })
        
        # 集中度警告
        conc_warnings = self.check_concentration_risk(session_id, total_assets, holdings)
        for w in conc_warnings:
            warnings.append({
                "level": w.level.value,
                "title": w.title,
                "message": w.message,
                "suggestion": w.suggestion
            })
        
        # 杠杆警告
        if total_assets > 0:
            leverage_ratio = leverage_holdings / total_assets
            if leverage_ratio > 0.15:
                warnings.append({
                    "level": WarningLevel.WARNING.value,
                    "title": "杠杆使用较高",
                    "message": f"杠杆产品占比{leverage_ratio*100:.0f}%",
                    "suggestion": "杠杆放大收益的同时也放大风险"
                })
        
        # 新手期提示
        newbie = self.check_newbie_protection(current_month)
        if newbie["is_protected"]:
            warnings.append({
                "level": WarningLevel.INFO.value,
                "title": "新手保护期",
                "message": f"还剩{newbie['remaining_months']}个月保护期",
                "suggestion": "趁此期间多学习，风险已减半"
            })
        
        return warnings
    
    def get_risk_score(self, cash: int, total_assets: int, total_debt: int,
                      leverage_holdings: int, holdings: Dict[str, int]) -> Dict:
        """计算风险评分 (0-100, 越高风险越大)"""
        score = 0
        factors = []
        
        # 负债率
        if total_assets > 0:
            debt_ratio = total_debt / total_assets
            if debt_ratio > 0.8:
                score += 30
                factors.append("负债率过高")
            elif debt_ratio > 0.5:
                score += 15
                factors.append("负债率偏高")
        
        # 杠杆率
        if total_assets > 0:
            leverage_ratio = leverage_holdings / total_assets
            if leverage_ratio > 0.15:
                score += 20
                factors.append("杠杆使用较多")
        
        # 现金比例
        if total_assets > 0:
            cash_ratio = cash / total_assets
            if cash_ratio < 0.05:
                score += 20
                factors.append("现金储备不足")
            elif cash_ratio < 0.1:
                score += 10
                factors.append("现金比例偏低")
        
        # 集中度
        if total_assets > 0:
            for name, amount in holdings.items():
                if amount / total_assets > 0.4:
                    score += 15
                    factors.append(f"{name}持仓过度集中")
                    break
        
        # 限制在0-100
        score = min(100, max(0, score))
        
        if score < 30:
            level = "低风险"
            color = "green"
        elif score < 60:
            level = "中等风险"
            color = "orange"
        else:
            level = "高风险"
            color = "red"
        
        return {
            "score": score,
            "level": level,
            "color": color,
            "factors": factors
        }


# 全局实例
protection_system = ProtectionSystem()

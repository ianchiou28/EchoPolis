"""
资产计算系统 - 实时计算决策对资产的影响
"""
import re
import random
from typing import Dict, Tuple
from .investment_system import investment_system, InvestmentType

class AssetCalculator:
    """资产影响计算器"""
    
    @staticmethod
    def calculate_decision_impact(chosen_option: str, current_credits: int, current_round: int = 1) -> Tuple[int, str]:
        """计算决策对资产的影响
        
        Returns:
            Tuple[int, str]: (资产变化, 变化描述)
        """
        option_lower = chosen_option.lower()
        
        # 投资相关决策
        if any(keyword in chosen_option for keyword in ["投资", "投入", "试水", "孵化", "参与"]):
            change, desc, _ = AssetCalculator._calculate_investment_impact(chosen_option, current_credits, current_round)
            return change, desc
        
        # 购买相关决策
        if any(keyword in option_lower for keyword in ["购买", "买入", "花费", "购房", "首付", "80%"]):
            change, desc, _ = AssetCalculator._calculate_purchase_impact(chosen_option, current_credits)
            investment_system.add_transaction(current_round, desc, change)
            return change, desc
        
        # 储蓄相关决策
        if any(keyword in option_lower for keyword in ["储蓄", "存款", "定存"]):
            change, desc, _ = AssetCalculator._calculate_savings_impact(chosen_option, current_credits)
            investment_system.add_transaction(current_round, desc, change)
            return change, desc
        
        # 工作相关决策
        if any(keyword in option_lower for keyword in ["工作", "兼职", "加班"]):
            change, desc, _ = AssetCalculator._calculate_work_impact(chosen_option, current_credits)
            investment_system.add_transaction(current_round, desc, change)
            return change, desc
        
        # 默认小幅随机变化
        change = random.randint(-500, 1000)
        desc = "日常开支" if change < 0 else "意外收入"
        investment_system.add_transaction(current_round, desc, change)
        return change, desc
    
    @staticmethod
    def _calculate_investment_impact(option: str, credits: int, current_round: int = 1) -> Tuple[int, str, str]:
        """计算投资影响"""
        # 提取投资金额
        amounts = re.findall(r'(\d+)万', option)
        if amounts:
            amount = int(amounts[0]) * 10000
        else:
            # 根据选项内容估算
            if "大额" in option or "全部" in option:
                amount = int(credits * 0.3)
            elif "小额" in option or "试水" in option:
                amount = min(10000, int(credits * 0.1))
            else:
                amount = int(credits * 0.2)
        
        # 判断投资类型和期限
        if "基金" in option or "月收益" in option:
            inv_type = InvestmentType.MONTHLY
            duration = random.randint(12, 36)
            return_rate = random.uniform(0.06, 0.12)  # 年化6-12%
        elif "短期" in option or "3个月" in option:
            inv_type = InvestmentType.SHORT_TERM
            duration = random.randint(1, 3)
            return_rate = random.uniform(0.02, 0.08)
        elif "长期" in option or "年" in option:
            inv_type = InvestmentType.LONG_TERM
            duration = random.randint(12, 24)
            return_rate = random.uniform(0.08, 0.20)
        else:
            inv_type = InvestmentType.MEDIUM_TERM
            duration = random.randint(3, 12)
            return_rate = random.uniform(0.05, 0.15)
        
        # 生成投资名称
        if "股票" in option:
            name = "股票投资"
        elif "基金" in option:
            name = "投资基金"
        elif "债券" in option:
            name = "债券投资"
        elif "孵化" in option or "科技" in option:
            name = "科技孵化项目"
        else:
            name = "理财产品"
        
        # 创建投资记录
        investment_system.add_investment(name, amount, inv_type, duration, return_rate, current_round)
        
        # 记录投资交易
        investment_system.add_transaction(current_round, f"投资{name}", -amount)
        
        return -amount, f"投资{name}", "investment"
    
    @staticmethod
    def _calculate_purchase_impact(option: str, credits: int) -> Tuple[int, str, str]:
        """计算购买影响"""
        # 检查是否为购房决策
        if any(keyword in option for keyword in ["购房", "首付", "80%"]):
            # 购房：使用80%资金作为首付
            down_payment = int(credits * 0.8)
            change = -down_payment
            desc = f"购房首付 (80%资金)"
            return change, desc, "long_term"
        
        # 提取金额
        amounts = re.findall(r'(\d+)万', option)
        if amounts:
            change = -int(amounts[0]) * 10000
        else:
            # 根据物品类型估算
            if any(item in option for item in ["房", "车", "房产"]):
                change = -random.randint(50000, 200000)
            elif any(item in option for item in ["电脑", "手机", "设备"]):
                change = -random.randint(3000, 15000)
            else:
                change = -random.randint(500, 5000)
        
        desc = "购买支出"
        return change, desc, "short_term"
    
    @staticmethod
    def _calculate_savings_impact(option: str, credits: int) -> Tuple[int, str, str]:
        """计算储蓄影响"""
        # 储蓄通常是正收益
        if "定存" in option:
            change = int(credits * random.uniform(0.02, 0.05))
            desc = "定存利息"
        else:
            change = int(credits * random.uniform(0.01, 0.03))
            desc = "储蓄收益"
        
        return change, desc, "long_term"
    
    @staticmethod
    def _calculate_work_impact(option: str, credits: int) -> Tuple[int, str, str]:
        """计算工作影响"""
        if "加班" in option:
            change = random.randint(1000, 3000)
            desc = "加班收入"
        elif "兼职" in option:
            change = random.randint(2000, 8000)
            desc = "兼职收入"
        elif "跳槽" in option or "换工作" in option:
            change = random.randint(-5000, 15000)
            desc = "工作变动" if change > 0 else "跳槽成本"
        else:
            change = random.randint(3000, 8000)
            desc = "工作收入"
        
        return change, desc, "short_term"

    @staticmethod
    def process_monthly_returns(current_round: int) -> int:
        """处理月收益"""
        return investment_system.process_monthly_returns(current_round)
    
    @staticmethod
    def get_investment_summary() -> str:
        """获取投资摘要"""
        return investment_system.get_investment_summary()
    
    @staticmethod
    def get_transaction_summary(rounds: int = 5) -> str:
        """获取交易摘要"""
        return investment_system.get_transaction_summary(rounds)

# 全局实例
asset_calculator = AssetCalculator()
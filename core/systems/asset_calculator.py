"""
资产计算系统 - 实时计算决策对资产的影响
"""
import re
import random
from typing import Dict, Tuple

class AssetCalculator:
    """资产影响计算器"""
    
    @staticmethod
    def calculate_decision_impact(chosen_option: str, current_credits: int) -> Tuple[int, str]:
        """计算决策对资产的影响
        
        Returns:
            Tuple[int, str]: (资产变化, 变化描述)
        """
        option_lower = chosen_option.lower()
        
        # 投资相关决策
        if "投资" in chosen_option:
            return AssetCalculator._calculate_investment_impact(chosen_option, current_credits)
        
        # 购买相关决策
        if any(keyword in option_lower for keyword in ["购买", "买入", "花费", "购房", "首付", "80%"]):
            return AssetCalculator._calculate_purchase_impact(chosen_option, current_credits)
        
        # 储蓄相关决策
        if any(keyword in option_lower for keyword in ["储蓄", "存款", "定存"]):
            return AssetCalculator._calculate_savings_impact(chosen_option, current_credits)
        
        # 工作相关决策
        if any(keyword in option_lower for keyword in ["工作", "兼职", "加班"]):
            return AssetCalculator._calculate_work_impact(chosen_option, current_credits)
        
        # 默认小幅随机变化
        change = random.randint(-500, 1000)
        desc = "日常开支" if change < 0 else "意外收入"
        return change, desc
    
    @staticmethod
    def _calculate_investment_impact(option: str, credits: int) -> Tuple[int, str, str]:
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
        
        # 判断投资类型
        if any(keyword in option for keyword in ["锁定", "个月", "年"]) and any(char.isdigit() for char in option):
            investment_type = "locked"
        elif any(keyword in option for keyword in ["长期", "定投", "基金"]):
            investment_type = "long_term"
        else:
            investment_type = "short_term"
        
        # 投资成功率和收益率
        if "高风险" in option or "股票" in option:
            success_rate = 0.4
            return_rate = random.uniform(-0.3, 0.5)
        elif "稳健" in option or "债券" in option:
            success_rate = 0.8
            return_rate = random.uniform(-0.05, 0.15)
        else:
            success_rate = 0.6
            return_rate = random.uniform(-0.1, 0.25)
        
        if random.random() < success_rate:
            change = int(amount * return_rate)
            desc = f"投资收益 {return_rate*100:.1f}%"
        else:
            change = -int(amount * random.uniform(0.1, 0.3))
            desc = "投资亏损"
        
        return change, desc, investment_type
    
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

# 全局实例
asset_calculator = AssetCalculator()
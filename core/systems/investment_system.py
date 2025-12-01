"""
投资管理系统 - 管理投资、消费、收益记录和资产
"""
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from .market_sentiment_system import market_sentiment_system

class InvestmentType(Enum):
    """投资类型"""
    SHORT_TERM = "短期"    # 1-3个月
    MEDIUM_TERM = "中期"   # 3-12个月  
    LONG_TERM = "长期"     # 12个月以上
    MONTHLY = "月收益"     # 每月固定收益

@dataclass
class Investment:
    """投资记录"""
    name: str                    # 资产名称
    amount: int                  # 投资金额
    investment_type: InvestmentType  # 投资类型
    remaining_months: int        # 剩余月数
    monthly_return: int         # 月收益（固定收益型）
    total_return_rate: float    # 总收益率（一次性收益型）
    created_round: int          # 创建回合
    
@dataclass
class TransactionRecord:
    """交易记录"""
    round_num: int              # 回合数
    transaction_name: str       # 交易名称
    amount: int                 # 金额（正负数）
    timestamp: float           # 时间戳

class InvestmentSystem:
    """投资管理系统"""
    
    def __init__(self):
        self.investments: List[Investment] = []
        self.transaction_history: List[TransactionRecord] = []
    
    def add_investment(self, name: str, amount: int, investment_type: InvestmentType, 
                      duration_months: int, return_rate: float, current_round: int, session_id: str = None) -> Investment:
        """添加投资"""
        if investment_type == InvestmentType.MONTHLY:
            monthly_return = int(amount * return_rate / 12)  # 年化收益转月收益
            total_return_rate = 0
        else:
            monthly_return = 0
            total_return_rate = return_rate
            
        investment = Investment(
            name=name,
            amount=amount,
            investment_type=investment_type,
            remaining_months=duration_months,
            monthly_return=monthly_return,
            total_return_rate=total_return_rate,
            created_round=current_round
        )
        
        self.investments.append(investment)
        self.add_transaction(current_round, f"投资{name}", -amount, session_id)
        
        # 保存到数据库
        if session_id:
            try:
                from ..database import db
                db.save_investment(session_id, name, amount, investment_type.value, 
                                 duration_months, monthly_return, return_rate, current_round)
            except ImportError:
                pass
        
        return investment
    
    def add_transaction(self, round_num: int, transaction_name: str, amount: int, session_id: str = None):
        """添加交易记录"""
        record = TransactionRecord(
            round_num=round_num,
            transaction_name=transaction_name,
            amount=amount,
            timestamp=time.time()
        )
        self.transaction_history.append(record)
        
        # 保存到数据库
        if session_id:
            try:
                from ..database import db
                db.save_transaction(session_id, round_num, transaction_name, amount)
            except ImportError:
                pass
    
    def process_monthly_returns(self, current_round: int) -> int:
        """处理月收益，返回总收益"""
        total_return = 0
        
        # 获取市场情绪修正
        try:
            sentiment_modifier = market_sentiment_system.get_influence_modifier()
        except:
            sentiment_modifier = 0.0
            
        for investment in self.investments[:]:  # 使用切片避免修改列表时出错
            if investment.remaining_months <= 0:
                continue
                
            # 月收益型投资
            if investment.investment_type == InvestmentType.MONTHLY:
                # 应用市场情绪修正 (影响浮动收益部分，这里假设月收益受市场影响波动 +/- 20%)
                adjusted_return = int(investment.monthly_return * (1 + sentiment_modifier))
                total_return += adjusted_return
                self.add_transaction(current_round, f"{investment.name}月收益(市场修正:{sentiment_modifier:+.2%})", adjusted_return)
            
            # 减少剩余月数
            investment.remaining_months -= 1
            
            # 到期投资处理
            if investment.remaining_months <= 0:
                if investment.investment_type != InvestmentType.MONTHLY:
                    # 一次性收益
                    # 应用市场情绪修正到最终收益率
                    final_rate = investment.total_return_rate + sentiment_modifier
                    final_return = int(investment.amount * (1 + final_rate))
                    total_return += final_return
                    self.add_transaction(current_round, f"{investment.name}到期收益(市场修正:{sentiment_modifier:+.2%})", final_return)
                
                # 移除到期投资
                self.investments.remove(investment)
        
        return total_return
    
    def get_active_investments(self) -> List[Investment]:
        """获取活跃投资"""
        return [inv for inv in self.investments if inv.remaining_months > 0]
    
    def get_total_invested_amount(self) -> int:
        """获取总投资金额"""
        return sum(inv.amount for inv in self.get_active_investments())
    
    def get_monthly_income(self) -> int:
        """获取月收益总额"""
        return sum(inv.monthly_return for inv in self.get_active_investments() 
                  if inv.investment_type == InvestmentType.MONTHLY)
    
    def get_investment_summary(self) -> str:
        """获取投资摘要"""
        active_investments = self.get_active_investments()
        if not active_investments:
            return "📊 当前无投资"
        
        summary = "📊 当前投资:\n"
        for inv in active_investments:
            if inv.investment_type == InvestmentType.MONTHLY:
                summary += f"  💰 {inv.name}: {inv.amount:,}CP, +{inv.monthly_return:,}CP/月, 剩余{inv.remaining_months}月\n"
            else:
                summary += f"  📈 {inv.name}: {inv.amount:,}CP, {inv.investment_type.value}, 剩余{inv.remaining_months}月\n"
        
        summary += f"💼 总投资: {self.get_total_invested_amount():,}CP\n"
        summary += f"💵 月收益: {self.get_monthly_income():,}CP"
        return summary
    
    def get_recent_transactions(self, limit: int = 10) -> List[TransactionRecord]:
        """获取最近交易记录"""
        return sorted(self.transaction_history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_transaction_summary(self, rounds: int = 5) -> str:
        """获取交易摘要"""
        recent = [t for t in self.transaction_history if t.round_num >= max(1, max(t.round_num for t in self.transaction_history) - rounds + 1)] if self.transaction_history else []
        
        if not recent:
            return "📋 暂无交易记录"
        
        summary = f"📋 最近{rounds}回合交易:\n"
        for record in sorted(recent, key=lambda x: x.round_num, reverse=True):
            amount_str = f"+{record.amount:,}" if record.amount > 0 else f"{record.amount:,}"
            summary += f"  第{record.round_num}回合: {record.transaction_name} {amount_str}CP\n"
        
        return summary.rstrip()

# 全局实例
investment_system = InvestmentSystem()
"""
行为洞察系统
记录和分析玩家的金融决策行为，生成个人画像和群体洞察
支持 AI 驱动的个性化洞察生成
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import defaultdict
import json

class BehaviorInsightSystem:
    """行为洞察系统"""
    
    # 风险评分阈值
    RISK_THRESHOLDS = {
        'conservative': (0, 0.3),      # 保守型
        'moderate': (0.3, 0.6),        # 稳健型
        'aggressive': (0.6, 1.0)       # 激进型
    }
    
    # 决策风格特征
    DECISION_STYLES = {
        'rational': '理性规划型',
        'impulsive': '冲动跟风型',
        'passive': '被动随缘型',
        'adaptive': '灵活应变型'
    }
    
    def __init__(self, database, ai_engine=None):
        self.db = database
        self.ai_engine = ai_engine
    
    def set_ai_engine(self, ai_engine):
        """设置AI引擎"""
        self.ai_engine = ai_engine
    
    # ============ 行为记录 ============
    
    def log_action(self, session_id: str, month: int, action_type: str,
                  action_data: Dict, market_state: Dict) -> None:
        """
        记录玩家行为
        
        Args:
            session_id: 会话ID
            month: 游戏月份
            action_type: 行为类型（stock_buy, stock_sell, fund_buy, loan_apply等）
            action_data: 行为数据
            market_state: 市场状态
        """
        # 分类行为
        action_category = self._classify_action(action_type)
        
        # 计算风险评分
        risk_score = self._calculate_risk_score(action_type, action_data, market_state)
        
        # 计算理性度评分
        rationality_score = self._calculate_rationality_score(action_type, action_data, market_state)
        
        # 构建决策上下文
        decision_context = self._build_context(action_data, market_state)
        
        # 记录到数据库
        self.db.log_behavior(
            session_id=session_id,
            month=month,
            action_type=action_type,
            action_category=action_category,
            amount=action_data.get('amount') or action_data.get('price'),
            risk_score=risk_score,
            rationality_score=rationality_score,
            market_condition=market_state.get('economic_phase'),
            decision_context=decision_context
        )
    
    def _classify_action(self, action_type: str) -> str:
        """分类行为"""
        if 'stock' in action_type or 'fund' in action_type:
            return 'investment'
        elif 'loan' in action_type or 'debt' in action_type:
            return 'financing'
        elif 'house' in action_type or 'rent' in action_type:
            return 'housing'
        elif 'insurance' in action_type:
            return 'protection'
        elif 'lifestyle' in action_type:
            return 'consumption'
        return 'other'
    
    def _calculate_risk_score(self, action_type: str, action_data: Dict, market_state: Dict) -> float:
        """
        计算风险评分（0-1）
        基于：行为类型、金额、市场环境、杠杆使用等
        """
        risk_score = 0.5  # 基础分
        
        # 1. 行为固有风险
        inherent_risk = {
            'stock_buy': 0.7,
            'stock_sell': 0.3,
            'fund_buy': 0.5,
            'fund_sell': 0.3,
            'loan_apply': 0.8,
            'loan_repay': 0.2,
            'house_buy': 0.65,
            'house_sell': 0.3,
            'house_rent': 0.2,
            'insurance_buy': 0.15,
            'lifestyle_luxury': 0.6,
            'lifestyle_basic': 0.2,
            'side_business': 0.75
        }
        risk_score = inherent_risk.get(action_type, 0.5)
        
        # 2. 市场环境调整
        if market_state.get('economic_phase') == 'recession':
            if 'buy' in action_type:
                risk_score += 0.2  # 衰退期买入更冒险
        elif market_state.get('economic_phase') == 'boom':
            if 'sell' in action_type:
                risk_score -= 0.1  # 繁荣期卖出较保守
        
        # 3. 金额占比调整
        if 'amount' in action_data and 'cash' in action_data:
            ratio = action_data['amount'] / max(action_data['cash'], 1)
            if ratio > 0.8:
                risk_score += 0.15  # 大额投入
            elif ratio < 0.2:
                risk_score -= 0.1  # 小额试探
        
        # 4. 杠杆使用
        if action_data.get('use_loan') or 'loan' in action_type:
            risk_score += 0.2
        
        return np.clip(risk_score, 0, 1)
    
    def _calculate_rationality_score(self, action_type: str, action_data: Dict, market_state: Dict) -> float:
        """
        计算理性度评分（0-1）
        基于：时机选择、价格判断、风险控制等
        """
        rationality = 0.5
        
        # 1. 时机选择
        if market_state.get('economic_phase') == 'recession':
            if 'buy' in action_type and 'stock' in action_type:
                rationality += 0.2  # 低谷买入 - 理性
        elif market_state.get('economic_phase') == 'boom':
            if 'sell' in action_type:
                rationality += 0.15  # 高点卖出 - 理性
            elif 'buy' in action_type:
                rationality -= 0.15  # 高点追涨 - 不理性
        
        # 2. 分散投资
        if action_type in ['stock_buy', 'fund_buy']:
            if action_data.get('existing_holdings', 0) >= 3:
                rationality += 0.1  # 已有分散投资
        
        # 3. 现金储备
        if 'cash' in action_data and 'amount' in action_data:
            remaining_cash = action_data['cash'] - action_data['amount']
            monthly_expense = action_data.get('monthly_expense', 0)
            if monthly_expense > 0:
                reserve_months = remaining_cash / monthly_expense
                if reserve_months >= 6:
                    rationality += 0.15  # 保留足够应急金
                elif reserve_months < 3:
                    rationality -= 0.2  # 现金储备不足
        
        # 4. 止损策略
        if action_type == 'stock_sell':
            if action_data.get('reason') == 'stop_loss':
                rationality += 0.1  # 及时止损
        
        return np.clip(rationality, 0, 1)
    
    def _build_context(self, action_data: Dict, market_state: Dict) -> str:
        """构建决策上下文描述"""
        context_parts = []
        
        if market_state.get('economic_phase'):
            context_parts.append(f"经济阶段:{market_state['economic_phase']}")
        
        if 'amount' in action_data:
            context_parts.append(f"金额:{action_data['amount']}")
        
        if 'reason' in action_data:
            context_parts.append(f"原因:{action_data['reason']}")
        
        return "; ".join(context_parts)
    
    # ============ 行为分析 ============
    
    def analyze_profile(self, session_id: str, current_month: int) -> Dict:
        """
        分析玩家行为画像
        
        Returns:
            {
                'risk_preference': 'conservative|moderate|aggressive',
                'decision_style': 'rational|impulsive|passive|adaptive',
                'loss_aversion': 0-1,
                'overconfidence': 0-1,
                'herding_tendency': 0-1,
                'planning_ability': 0-1,
                'action_count': int,
                'avg_risk_score': float,
                'avg_rationality': float
            }
        """
        # 获取近期行为日志（最近12个月）
        logs = self.db.get_behavior_logs(session_id, months=12)
        
        if not logs or len(logs) < 5:
            # 数据不足，返回默认画像
            return {
                'risk_preference': 'moderate',
                'decision_style': 'passive',
                'loss_aversion': 0.5,
                'overconfidence': 0.5,
                'herding_tendency': 0.5,
                'planning_ability': 0.5,
                'action_count': len(logs),
                'avg_risk_score': 0.5,
                'avg_rationality': 0.5,
                'last_updated_month': current_month
            }
        
        # 计算基础指标
        risk_scores = [log['risk_score'] for log in logs if log['risk_score'] is not None]
        rationality_scores = [log['rationality_score'] for log in logs if log['rationality_score'] is not None]
        
        avg_risk = np.mean(risk_scores) if risk_scores else 0.5
        avg_rationality = np.mean(rationality_scores) if rationality_scores else 0.5
        
        # 判断风险偏好
        risk_preference = self._determine_risk_preference(avg_risk)
        
        # 判断决策风格
        decision_style = self._determine_decision_style(logs, avg_rationality)
        
        # 计算行为特征
        loss_aversion = self._calculate_loss_aversion(logs)
        overconfidence = self._calculate_overconfidence(logs, avg_risk)
        herding_tendency = self._calculate_herding_tendency(logs)
        planning_ability = self._calculate_planning_ability(logs, avg_rationality)
        
        profile = {
            'risk_preference': risk_preference,
            'decision_style': decision_style,
            'loss_aversion': loss_aversion,
            'overconfidence': overconfidence,
            'herding_tendency': herding_tendency,
            'planning_ability': planning_ability,
            'action_count': len(logs),
            'avg_risk_score': avg_risk,
            'avg_rationality': avg_rationality,
            'last_updated_month': current_month
        }
        
        # 保存到数据库
        self.db.update_behavior_profile(session_id, profile)
        
        return profile
    
    def _determine_risk_preference(self, avg_risk: float) -> str:
        """判断风险偏好"""
        for pref, (low, high) in self.RISK_THRESHOLDS.items():
            if low <= avg_risk < high:
                return pref
        return 'moderate'
    
    def _determine_decision_style(self, logs: List[Dict], avg_rationality: float) -> str:
        """判断决策风格"""
        if len(logs) < 5:
            return 'passive'
        
        # 行为频率
        action_frequency = len(logs) / 12  # 月均行为数
        
        if avg_rationality > 0.65 and action_frequency >= 2:
            return 'rational'  # 理性规划型：理性度高，行为频繁
        elif avg_rationality < 0.45 and action_frequency >= 2.5:
            return 'impulsive'  # 冲动跟风型：理性度低，行为频繁
        elif action_frequency < 1.5:
            return 'passive'  # 被动随缘型：行为稀少
        else:
            return 'adaptive'  # 灵活应变型：中等理性度和频率
    
    def _calculate_loss_aversion(self, logs: List[Dict]) -> float:
        """计算损失厌恶程度（0-1，越高越厌恶损失）"""
        sell_actions = [log for log in logs if 'sell' in log['action_type']]
        
        if not sell_actions:
            return 0.5
        
        # 统计止损行为占比
        stop_loss_count = sum(1 for log in sell_actions if 'stop_loss' in log.get('decision_context', ''))
        
        if sell_actions:
            loss_aversion = stop_loss_count / len(sell_actions)
            return np.clip(loss_aversion, 0, 1)
        
        return 0.5
    
    def _calculate_overconfidence(self, logs: List[Dict], avg_risk: float) -> float:
        """计算过度自信程度（0-1）"""
        # 如果高风险行为多且理性度低，说明可能过度自信
        high_risk_actions = [log for log in logs if log.get('risk_score', 0) > 0.7]
        
        if len(logs) > 0:
            high_risk_ratio = len(high_risk_actions) / len(logs)
            
            # 高风险比例高，但理性度不高 -> 过度自信
            low_rationality_actions = [log for log in high_risk_actions 
                                      if log.get('rationality_score', 1) < 0.5]
            
            if high_risk_actions:
                overconfidence = len(low_rationality_actions) / len(high_risk_actions)
                return np.clip(overconfidence, 0, 1)
        
        return 0.3  # 默认较低
    
    def _calculate_herding_tendency(self, logs: List[Dict]) -> float:
        """计算羊群效应倾向（0-1）"""
        # 统计在繁荣期追涨和衰退期恐慌抛售的行为
        herding_actions = 0
        total_market_actions = 0
        
        for log in logs:
            if log.get('market_condition') and log['action_type'] in ['stock_buy', 'stock_sell']:
                total_market_actions += 1
                
                # 繁荣期买入 = 追涨
                if log['market_condition'] == 'boom' and 'buy' in log['action_type']:
                    herding_actions += 1
                # 衰退期卖出 = 恐慌抛售
                elif log['market_condition'] == 'recession' and 'sell' in log['action_type']:
                    herding_actions += 1
        
        if total_market_actions > 0:
            herding = herding_actions / total_market_actions
            return np.clip(herding, 0, 1)
        
        return 0.4  # 默认中等
    
    def _calculate_planning_ability(self, logs: List[Dict], avg_rationality: float) -> float:
        """计算规划能力（0-1）"""
        # 基于理性度和行为多样性
        action_categories = set(log['action_category'] for log in logs)
        category_diversity = len(action_categories) / 5  # 最多5个类别
        
        # 综合理性度和多样性
        planning = (avg_rationality * 0.7 + category_diversity * 0.3)
        return np.clip(planning, 0, 1)
    
    # ============ 群体洞察 ============
    
    def generate_cohort_insights(self, current_month: int, sample_size: int = 50) -> List[Dict]:
        """
        生成Z世代群体洞察
        
        Returns:
            洞察列表，每条包含：
            - insight_type: 洞察类型（risk_profile, decision_pattern, behavioral_bias等）
            - title: 标题
            - description: 详细描述
            - data_source: 数据来源
            - confidence_level: 置信度
        """
        insights = []
        
        # TODO: 实际实现中需要收集多个玩家的数据
        # 这里先提供框架，后续可以基于真实数据生成洞察
        
        # 示例洞察1：风险偏好分布
        insights.append({
            'insight_type': 'risk_profile',
            'insight_category': 'investment',
            'title': 'Z世代投资者风险偏好呈两极分化',
            'description': '数据显示，45%的Z世代玩家表现出激进型投资风格，倾向高风险高回报；'
                          '35%为保守型，优先资金安全；仅20%为稳健型。这与传统投资者分布显著不同。',
            'data_source': 'behavior_profiles',
            'sample_size': sample_size,
            'confidence_level': 0.85,
            'tags': 'risk_preference,investment,generation_z',
            'generated_month': current_month
        })
        
        # 示例洞察2：决策模式
        insights.append({
            'insight_type': 'decision_pattern',
            'insight_category': 'behavior',
            'title': '冲动型决策在Z世代中占比30%',
            'description': 'Z世代玩家中，30%表现出冲动跟风型决策特征，易受市场情绪影响；'
                          '25%为理性规划型，善于分析和长期规划；其余为被动或灵活型。',
            'data_source': 'behavior_logs',
            'sample_size': sample_size,
            'confidence_level': 0.80,
            'tags': 'decision_style,behavioral_pattern',
            'generated_month': current_month
        })
        
        # 示例洞察3：行为偏差
        insights.append({
            'insight_type': 'behavioral_bias',
            'insight_category': 'psychology',
            'title': 'Z世代存在显著羊群效应，60%追涨杀跌',
            'description': '超过60%的Z世代玩家在市场繁荣期大量买入，衰退期恐慌抛售，'
                          '表现出明显的羊群行为。仅15%能逆势操作。',
            'data_source': 'behavior_logs',
            'sample_size': sample_size,
            'confidence_level': 0.88,
            'tags': 'herding_effect,market_timing,bias',
            'generated_month': current_month
        })
        
        # 保存洞察到数据库
        for insight in insights:
            self.db.save_cohort_insight(insight)
        
        return insights
    
    def get_peer_comparison(self, session_id: str) -> Dict:
        """
        获取与同龄人（所有玩家）的对比数据
        
        Returns:
            {
                'user_profile': 用户个人数据,
                'peer_average': 同龄人平均数据,
                'percentiles': 百分位排名,
                'comparisons': 各维度对比详情
            }
        """
        # 获取当前用户画像
        user_profile = self.db.get_behavior_profile(session_id)
        
        if not user_profile:
            return {
                'user_profile': None,
                'peer_average': None,
                'percentiles': {},
                'comparisons': []
            }
        
        # 获取所有用户画像（模拟群体数据）
        # TODO: 实际实现中应该查询所有用户的behavior_profiles
        # 这里使用模拟的群体平均值
        peer_average = self._get_simulated_peer_average()
        
        # 计算各维度对比
        comparisons = []
        
        # 风险偏好对比
        comparisons.append({
            'dimension': 'risk_score',
            'dimension_label': '风险承受',
            'user_value': user_profile.get('avg_risk_score', 0.5),
            'peer_value': peer_average['avg_risk_score'],
            'user_display': f"{user_profile.get('avg_risk_score', 0.5) * 100:.0f}%",
            'peer_display': f"{peer_average['avg_risk_score'] * 100:.0f}%",
            'verdict': self._get_comparison_verdict(
                user_profile.get('avg_risk_score', 0.5),
                peer_average['avg_risk_score'],
                'neutral'  # 风险无好坏，中性对比
            )
        })
        
        # 理性评分对比
        comparisons.append({
            'dimension': 'rationality',
            'dimension_label': '决策理性',
            'user_value': user_profile.get('avg_rationality', 0.5),
            'peer_value': peer_average['avg_rationality'],
            'user_display': f"{user_profile.get('avg_rationality', 0.5) * 100:.0f}%",
            'peer_display': f"{peer_average['avg_rationality'] * 100:.0f}%",
            'verdict': self._get_comparison_verdict(
                user_profile.get('avg_rationality', 0.5),
                peer_average['avg_rationality'],
                'higher_better'
            )
        })
        
        # 规划能力对比
        comparisons.append({
            'dimension': 'planning',
            'dimension_label': '规划能力',
            'user_value': user_profile.get('planning_ability', 0.5),
            'peer_value': peer_average['planning_ability'],
            'user_display': f"{user_profile.get('planning_ability', 0.5) * 100:.0f}%",
            'peer_display': f"{peer_average['planning_ability'] * 100:.0f}%",
            'verdict': self._get_comparison_verdict(
                user_profile.get('planning_ability', 0.5),
                peer_average['planning_ability'],
                'higher_better'
            )
        })
        
        # 羊群倾向对比
        comparisons.append({
            'dimension': 'herding',
            'dimension_label': '羊群倾向',
            'user_value': user_profile.get('herding_tendency', 0.5),
            'peer_value': peer_average['herding_tendency'],
            'user_display': f"{user_profile.get('herding_tendency', 0.5) * 100:.0f}%",
            'peer_display': f"{peer_average['herding_tendency'] * 100:.0f}%",
            'verdict': self._get_comparison_verdict(
                user_profile.get('herding_tendency', 0.5),
                peer_average['herding_tendency'],
                'lower_better'
            )
        })
        
        # 损失厌恶对比
        comparisons.append({
            'dimension': 'loss_aversion',
            'dimension_label': '损失厌恶',
            'user_value': user_profile.get('loss_aversion', 0.5),
            'peer_value': peer_average['loss_aversion'],
            'user_display': f"{user_profile.get('loss_aversion', 0.5) * 100:.0f}%",
            'peer_display': f"{peer_average['loss_aversion'] * 100:.0f}%",
            'verdict': self._get_comparison_verdict(
                user_profile.get('loss_aversion', 0.5),
                peer_average['loss_aversion'],
                'neutral'
            )
        })
        
        # 过度自信对比
        comparisons.append({
            'dimension': 'overconfidence',
            'dimension_label': '过度自信',
            'user_value': user_profile.get('overconfidence', 0.5),
            'peer_value': peer_average['overconfidence'],
            'user_display': f"{user_profile.get('overconfidence', 0.5) * 100:.0f}%",
            'peer_display': f"{peer_average['overconfidence'] * 100:.0f}%",
            'verdict': self._get_comparison_verdict(
                user_profile.get('overconfidence', 0.5),
                peer_average['overconfidence'],
                'lower_better'
            )
        })
        
        # 计算百分位排名（模拟）
        percentiles = self._calculate_percentiles(user_profile, peer_average)
        
        return {
            'user_profile': user_profile,
            'peer_average': peer_average,
            'percentiles': percentiles,
            'comparisons': comparisons
        }
    
    def _get_simulated_peer_average(self) -> Dict:
        """获取模拟的同龄人平均数据"""
        # 基于Z世代群体特征的模拟数据
        return {
            'avg_risk_score': 0.55,  # 较高风险偏好
            'avg_rationality': 0.52,  # 中等理性
            'planning_ability': 0.48,  # 规划能力偏低
            'herding_tendency': 0.58,  # 较高羊群倾向
            'loss_aversion': 0.52,  # 中等损失厌恶
            'overconfidence': 0.55,  # 较高过度自信
            'action_count': 45,
            'risk_preference': 'moderate',
            'decision_style': 'adaptive'
        }
    
    def _get_comparison_verdict(self, user_val: float, peer_val: float, direction: str) -> Dict:
        """生成对比结论
        
        Args:
            user_val: 用户值
            peer_val: 同龄人平均值
            direction: 'higher_better', 'lower_better', 'neutral'
        """
        diff = user_val - peer_val
        diff_percent = abs(diff) / max(peer_val, 0.01) * 100
        
        if abs(diff) < 0.05:
            return {
                'status': 'similar',
                'icon': '≈',
                'text': '与同龄人持平',
                'color': 'neutral'
            }
        
        is_higher = diff > 0
        
        if direction == 'neutral':
            return {
                'status': 'higher' if is_higher else 'lower',
                'icon': '↑' if is_higher else '↓',
                'text': f"比同龄人{'高' if is_higher else '低'}{diff_percent:.0f}%",
                'color': 'neutral'
            }
        elif direction == 'higher_better':
            return {
                'status': 'better' if is_higher else 'worse',
                'icon': '↑' if is_higher else '↓',
                'text': f"比同龄人{'高' if is_higher else '低'}{diff_percent:.0f}%",
                'color': 'positive' if is_higher else 'negative'
            }
        else:  # lower_better
            return {
                'status': 'better' if not is_higher else 'worse',
                'icon': '↓' if not is_higher else '↑',
                'text': f"比同龄人{'低' if not is_higher else '高'}{diff_percent:.0f}%",
                'color': 'positive' if not is_higher else 'negative'
            }
    
    def _calculate_percentiles(self, user_profile: Dict, peer_average: Dict) -> Dict:
        """计算百分位排名（模拟）"""
        percentiles = {}
        
        # 基于正态分布模拟百分位
        for key in ['avg_rationality', 'planning_ability']:
            user_val = user_profile.get(key, 0.5)
            peer_val = peer_average.get(key, 0.5)
            
            # 简化的百分位计算
            if user_val >= peer_val:
                percentile = 50 + min(45, (user_val - peer_val) * 200)
            else:
                percentile = 50 - min(45, (peer_val - user_val) * 200)
            
            percentiles[key] = round(percentile)
        
        # 羊群倾向和过度自信（越低越好）
        for key in ['herding_tendency', 'overconfidence']:
            user_val = user_profile.get(key, 0.5)
            peer_val = peer_average.get(key, 0.5)
            
            if user_val <= peer_val:
                percentile = 50 + min(45, (peer_val - user_val) * 200)
            else:
                percentile = 50 - min(45, (user_val - peer_val) * 200)
            
            percentiles[key] = round(percentile)
        
        # 综合排名
        percentiles['overall'] = round(np.mean(list(percentiles.values())))
        
        return percentiles

    # ============ 前端数据接口 ============
    
    def get_behavior_evolution(self, session_id: str) -> Dict:
        """
        获取行为演变趋势数据
        
        Returns:
            {
                'timeline': 按月份的行为指标变化,
                'milestones': 重要行为里程碑,
                'trend_summary': 趋势总结
            }
        """
        # 获取所有行为日志
        all_logs = self.db.get_behavior_logs(session_id, months=999)  # 获取所有
        
        if not all_logs:
            return {
                'timeline': [],
                'milestones': [],
                'trend_summary': None
            }
        
        # 按月份分组计算指标
        monthly_data = defaultdict(lambda: {
            'risk_scores': [],
            'rationality_scores': [],
            'action_count': 0,
            'categories': defaultdict(int)
        })
        
        for log in all_logs:
            month = log.get('game_month', 1)
            monthly_data[month]['risk_scores'].append(log.get('risk_score', 0.5))
            monthly_data[month]['rationality_scores'].append(log.get('rationality_score', 0.5))
            monthly_data[month]['action_count'] += 1
            monthly_data[month]['categories'][log.get('action_category', 'other')] += 1
        
        # 生成时间线数据
        timeline = []
        months = sorted(monthly_data.keys())
        
        prev_risk = None
        prev_rationality = None
        
        for month in months:
            data = monthly_data[month]
            avg_risk = np.mean(data['risk_scores']) if data['risk_scores'] else 0.5
            avg_rationality = np.mean(data['rationality_scores']) if data['rationality_scores'] else 0.5
            
            # 计算变化
            risk_change = None
            rationality_change = None
            
            if prev_risk is not None:
                risk_change = avg_risk - prev_risk
            if prev_rationality is not None:
                rationality_change = avg_rationality - prev_rationality
            
            timeline.append({
                'month': month,
                'avg_risk': round(avg_risk, 3),
                'avg_rationality': round(avg_rationality, 3),
                'action_count': data['action_count'],
                'top_category': max(data['categories'], key=data['categories'].get) if data['categories'] else None,
                'risk_change': round(risk_change, 3) if risk_change is not None else None,
                'rationality_change': round(rationality_change, 3) if rationality_change is not None else None
            })
            
            prev_risk = avg_risk
            prev_rationality = avg_rationality
        
        # 检测里程碑
        milestones = self._detect_behavior_milestones(timeline, all_logs)
        
        # 生成趋势总结
        trend_summary = self._generate_trend_summary(timeline)
        
        return {
            'timeline': timeline,
            'milestones': milestones,
            'trend_summary': trend_summary
        }
    
    def _detect_behavior_milestones(self, timeline: List[Dict], logs: List[Dict]) -> List[Dict]:
        """检测行为里程碑"""
        milestones = []
        
        if len(timeline) < 2:
            return milestones
        
        # 首次行为
        first_log = min(logs, key=lambda x: x.get('game_month', 999))
        milestones.append({
            'month': first_log.get('game_month', 1),
            'type': 'first_action',
            'icon': '🎯',
            'title': '首次金融决策',
            'description': f"开始了你的金融旅程：{self._translate_category(first_log.get('action_category', ''))}"
        })
        
        # 检测显著变化
        for i in range(1, len(timeline)):
            curr = timeline[i]
            prev = timeline[i-1]
            
            # 理性提升里程碑
            if curr.get('rationality_change') and curr['rationality_change'] > 0.15:
                milestones.append({
                    'month': curr['month'],
                    'type': 'rationality_up',
                    'icon': '📈',
                    'title': '理性决策能力提升',
                    'description': f"理性评分提升了{curr['rationality_change']*100:.0f}%"
                })
            
            # 风险控制里程碑
            if curr.get('risk_change') and curr['risk_change'] < -0.15:
                milestones.append({
                    'month': curr['month'],
                    'type': 'risk_down',
                    'icon': '🛡️',
                    'title': '风险控制改善',
                    'description': f"风险水平降低了{abs(curr['risk_change'])*100:.0f}%"
                })
            
            # 活跃度里程碑
            if curr['action_count'] >= 10 and prev['action_count'] < 10:
                milestones.append({
                    'month': curr['month'],
                    'type': 'active',
                    'icon': '🔥',
                    'title': '活跃投资者',
                    'description': '单月行为次数突破10次'
                })
        
        # 按月份排序
        milestones.sort(key=lambda x: x['month'])
        
        return milestones
    
    def _generate_trend_summary(self, timeline: List[Dict]) -> Dict:
        """生成趋势总结"""
        if len(timeline) < 2:
            return {
                'risk_trend': 'stable',
                'rationality_trend': 'stable',
                'overall': '数据不足，继续积累行为记录'
            }
        
        # 计算整体趋势
        first_half = timeline[:len(timeline)//2] if len(timeline) > 2 else [timeline[0]]
        second_half = timeline[len(timeline)//2:] if len(timeline) > 2 else [timeline[-1]]
        
        avg_risk_first = np.mean([t['avg_risk'] for t in first_half])
        avg_risk_second = np.mean([t['avg_risk'] for t in second_half])
        
        avg_rat_first = np.mean([t['avg_rationality'] for t in first_half])
        avg_rat_second = np.mean([t['avg_rationality'] for t in second_half])
        
        risk_trend = 'increasing' if avg_risk_second > avg_risk_first + 0.05 else \
                     'decreasing' if avg_risk_second < avg_risk_first - 0.05 else 'stable'
        
        rationality_trend = 'increasing' if avg_rat_second > avg_rat_first + 0.05 else \
                           'decreasing' if avg_rat_second < avg_rat_first - 0.05 else 'stable'
        
        # 生成文字总结
        trend_texts = {
            ('increasing', 'increasing'): '风险偏好和理性都在提升，你正在变得更加大胆且有策略',
            ('increasing', 'decreasing'): '⚠️ 风险增加但理性下降，需要警惕冲动决策',
            ('increasing', 'stable'): '风险偏好在增加，建议配合理性分析',
            ('decreasing', 'increasing'): '👍 理想状态：风险降低的同时理性提升',
            ('decreasing', 'decreasing'): '整体趋于保守，可以适当探索更多机会',
            ('decreasing', 'stable'): '风险控制良好，保持稳健风格',
            ('stable', 'increasing'): '理性决策能力在提升，继续保持',
            ('stable', 'decreasing'): '注意保持理性分析，避免情绪化决策',
            ('stable', 'stable'): '行为模式稳定，形成了自己的决策风格'
        }
        
        overall = trend_texts.get((risk_trend, rationality_trend), '继续积累数据以获得更准确的分析')
        
        return {
            'risk_trend': risk_trend,
            'rationality_trend': rationality_trend,
            'risk_change_pct': round((avg_risk_second - avg_risk_first) * 100, 1),
            'rationality_change_pct': round((avg_rat_second - avg_rat_first) * 100, 1),
            'overall': overall
        }

    def get_personal_insights(self, session_id: str) -> Dict:
        """
        获取个人洞察数据（用于前端展示）
        
        Returns:
            {
                'profile': 行为画像,
                'recent_actions': 近期行为统计,
                'recommendations': 行为建议
            }
        """
        # 获取行为画像
        profile = self.db.get_behavior_profile(session_id)
        
        if not profile:
            return {
                'profile': None,
                'recent_actions': [],
                'recommendations': []
            }
        
        # 获取近期行为统计
        logs = self.db.get_behavior_logs(session_id, months=3)
        recent_actions = self._summarize_recent_actions(logs)
        
        # 生成个性化建议
        recommendations = self._generate_recommendations(profile, logs)
        
        return {
            'profile': profile,
            'recent_actions': recent_actions,
            'recommendations': recommendations
        }
    
    def _summarize_recent_actions(self, logs: List[Dict]) -> Dict:
        """汇总近期行为"""
        if not logs:
            return {}
        
        categories = defaultdict(int)
        for log in logs:
            categories[log['action_category']] += 1
        
        return {
            'total_actions': len(logs),
            'by_category': dict(categories),
            'avg_risk': np.mean([log['risk_score'] for log in logs if log['risk_score']]),
            'avg_rationality': np.mean([log['rationality_score'] for log in logs if log['rationality_score']])
        }
    
    def _generate_recommendations(self, profile: Dict, logs: List[Dict]) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        risk_pref = profile['risk_preference']
        decision_style = profile['decision_style']
        
        # 基于风险偏好
        if risk_pref == 'aggressive' and profile['avg_rationality'] < 0.5:
            recommendations.append('您的投资风格较为激进，建议加强风险控制，保留更多应急资金。')
        elif risk_pref == 'conservative' and profile['planning_ability'] > 0.7:
            recommendations.append('您具备良好的规划能力，可以适当尝试中等风险的投资产品。')
        
        # 基于决策风格
        if decision_style == 'impulsive':
            recommendations.append('您的决策较为冲动，建议在重大投资前进行更多分析和思考。')
        elif decision_style == 'passive':
            recommendations.append('您的投资行为较少，建议更主动地学习和实践财务管理。')
        
        # 基于行为偏差
        if profile['herding_tendency'] > 0.6:
            recommendations.append('您容易受市场情绪影响，建议培养独立判断能力，避免盲目跟风。')
        
        if profile['overconfidence'] > 0.6:
            recommendations.append('注意控制过度自信心理，高风险投资前应充分评估潜在损失。')
        
        return recommendations[:3]  # 最多返回3条建议
    
    # ============ AI 洞察生成 ============
    
    async def generate_ai_insight(self, session_id: str, current_month: int) -> Optional[Dict]:
        """
        使用AI生成个性化行为洞察报告
        
        Returns:
            {
                'title': 洞察标题,
                'summary': 简短总结,
                'analysis': 详细分析,
                'suggestions': 建议列表,
                'risk_alert': 风险提醒（如果有）
            }
        """
        if not self.ai_engine:
            return None
        
        # 获取用户数据
        profile = self.db.get_behavior_profile(session_id)
        logs = self.db.get_behavior_logs(session_id, months=6)
        
        if not profile or not logs:
            return None
        
        # 构建分析上下文
        context = self._build_ai_context(profile, logs)
        
        # 调用AI生成洞察
        prompt = f"""你是一位专业的金融行为分析师，专注于Z世代（95后-00后）的投资行为研究。
请根据以下用户行为数据，生成一份简洁的个性化洞察报告。

用户行为画像：
- 风险偏好：{self._translate_risk(profile['risk_preference'])}
- 决策风格：{self.DECISION_STYLES.get(profile['decision_style'], profile['decision_style'])}
- 损失厌恶指数：{profile['loss_aversion']:.2f}
- 过度自信指数：{profile['overconfidence']:.2f}
- 羊群效应倾向：{profile['herding_tendency']:.2f}
- 规划能力指数：{profile['planning_ability']:.2f}
- 平均风险评分：{profile['avg_risk_score']:.2f}
- 平均理性评分：{profile['avg_rationality']:.2f}

近期行为统计（{len(logs)}条记录）：
{context}

请以JSON格式输出（不要包含markdown代码块标记），包含以下字段：
{{
  "title": "一句话概括用户的金融行为特征",
  "summary": "50字以内的简短总结",
  "analysis": "100-150字的详细分析，包括优点和潜在问题",
  "suggestions": ["建议1", "建议2", "建议3"],
  "risk_alert": "如果发现高风险行为模式，给出警告；否则为null"
}}"""

        try:
            response = await self.ai_engine.generate_response_async(prompt)
            if response:
                # 尝试解析JSON
                try:
                    # 清理可能的markdown代码块标记
                    clean_response = response.strip()
                    if clean_response.startswith('```'):
                        clean_response = clean_response.split('```')[1]
                        if clean_response.startswith('json'):
                            clean_response = clean_response[4:]
                    clean_response = clean_response.strip()
                    
                    insight = json.loads(clean_response)
                    insight['generated_by'] = 'ai'
                    insight['generated_month'] = current_month
                    return insight
                except json.JSONDecodeError:
                    # 如果JSON解析失败，返回原始文本
                    return {
                        'title': '行为分析报告',
                        'summary': response[:100],
                        'analysis': response,
                        'suggestions': [],
                        'risk_alert': None,
                        'generated_by': 'ai',
                        'generated_month': current_month
                    }
        except Exception as e:
            print(f"[BehaviorInsight] AI insight generation failed: {e}")
        
        return None
    
    def _build_ai_context(self, profile: Dict, logs: List[Dict]) -> str:
        """构建AI分析的上下文信息"""
        # 按类别统计
        categories = defaultdict(int)
        risk_by_category = defaultdict(list)
        
        for log in logs:
            cat = log['action_category']
            categories[cat] += 1
            if log['risk_score']:
                risk_by_category[cat].append(log['risk_score'])
        
        context_lines = []
        for cat, count in categories.items():
            cat_name = {
                'investment': '投资',
                'financing': '融资',
                'housing': '住房',
                'protection': '保障',
                'consumption': '消费'
            }.get(cat, cat)
            
            avg_risk = np.mean(risk_by_category[cat]) if risk_by_category[cat] else 0
            context_lines.append(f"- {cat_name}行为：{count}次，平均风险{avg_risk:.2f}")
        
        return '\n'.join(context_lines)
    
    def _translate_risk(self, risk_pref: str) -> str:
        """翻译风险偏好"""
        return {
            'conservative': '保守型',
            'moderate': '稳健型',
            'aggressive': '激进型'
        }.get(risk_pref, risk_pref)
    
    # ============ 行为统计接口 ============
    
    def get_behavior_statistics(self, session_id: str) -> Dict:
        """
        获取详细的行为统计数据（用于图表展示）
        
        Returns:
            {
                'monthly_activity': 月度行为数量趋势,
                'category_distribution': 行为类别分布,
                'risk_trend': 风险评分趋势,
                'rationality_trend': 理性度趋势,
                'behavior_radar': 行为特征雷达图数据
            }
        """
        logs = self.db.get_behavior_logs(session_id)
        profile = self.db.get_behavior_profile(session_id)
        
        if not logs:
            return {
                'monthly_activity': [],
                'category_distribution': [],
                'risk_trend': [],
                'rationality_trend': [],
                'behavior_radar': []
            }
        
        # 1. 月度行为数量趋势
        monthly_counts = defaultdict(int)
        for log in logs:
            monthly_counts[log['month']] += 1
        
        monthly_activity = [
            {'month': m, 'count': c}
            for m, c in sorted(monthly_counts.items())
        ]
        
        # 2. 行为类别分布
        category_counts = defaultdict(int)
        for log in logs:
            category_counts[log['action_category']] += 1
        
        category_distribution = [
            {'category': self._translate_category(cat), 'count': count, 'key': cat}
            for cat, count in category_counts.items()
        ]
        
        # 3. 风险/理性度趋势（按月平均）
        monthly_risk = defaultdict(list)
        monthly_rationality = defaultdict(list)
        
        for log in logs:
            if log['risk_score']:
                monthly_risk[log['month']].append(log['risk_score'])
            if log['rationality_score']:
                monthly_rationality[log['month']].append(log['rationality_score'])
        
        risk_trend = [
            {'month': m, 'value': np.mean(scores)}
            for m, scores in sorted(monthly_risk.items())
        ]
        
        rationality_trend = [
            {'month': m, 'value': np.mean(scores)}
            for m, scores in sorted(monthly_rationality.items())
        ]
        
        # 4. 行为特征雷达图数据
        behavior_radar = []
        if profile:
            behavior_radar = [
                {'axis': '风险承受', 'value': profile.get('avg_risk_score', 0.5)},
                {'axis': '理性程度', 'value': profile.get('avg_rationality', 0.5)},
                {'axis': '规划能力', 'value': profile.get('planning_ability', 0.5)},
                {'axis': '独立决策', 'value': 1 - profile.get('herding_tendency', 0.5)},
                {'axis': '风险意识', 'value': 1 - profile.get('overconfidence', 0.5)},
                {'axis': '损失管理', 'value': profile.get('loss_aversion', 0.5)}
            ]
        
        return {
            'monthly_activity': monthly_activity,
            'category_distribution': category_distribution,
            'risk_trend': risk_trend,
            'rationality_trend': rationality_trend,
            'behavior_radar': behavior_radar
        }
    
    def _translate_category(self, category: str) -> str:
        """翻译行为类别"""
        return {
            'investment': '投资',
            'financing': '融资',
            'housing': '住房',
            'protection': '保障',
            'consumption': '消费',
            'other': '其他'
        }.get(category, category)
    
    # ============ 行为预警系统 ============
    
    def check_behavior_alerts(self, session_id: str, current_month: int) -> List[Dict]:
        """
        检测高风险行为模式并生成预警
        
        Returns:
            预警列表，每条包含：
            - alert_type: 预警类型
            - severity: 严重程度 (low/medium/high/critical)
            - title: 预警标题
            - message: 预警详情
            - suggestion: 建议
        """
        alerts = []
        
        # 获取近期行为数据
        logs = self.db.get_behavior_logs(session_id, months=3)
        profile = self.db.get_behavior_profile(session_id)
        
        if not logs or len(logs) < 3:
            return alerts
        
        # 1. 检测连续高风险行为
        high_risk_streak = self._check_high_risk_streak(logs)
        if high_risk_streak:
            alerts.append(high_risk_streak)
        
        # 2. 检测过度交易
        overtrading = self._check_overtrading(logs, current_month)
        if overtrading:
            alerts.append(overtrading)
        
        # 3. 检测杠杆过度使用
        leverage_alert = self._check_leverage_abuse(logs)
        if leverage_alert:
            alerts.append(leverage_alert)
        
        # 4. 检测羊群行为
        if profile and profile.get('herding_tendency', 0) > 0.7:
            alerts.append({
                'alert_type': 'herding_behavior',
                'severity': 'medium',
                'title': '羊群效应倾向较高',
                'message': '您的投资决策容易受市场情绪影响，存在追涨杀跌的风险。',
                'suggestion': '建议制定明确的投资计划，避免在市场极端情绪时做出重大决策。'
            })
        
        # 5. 检测过度自信
        if profile and profile.get('overconfidence', 0) > 0.7:
            alerts.append({
                'alert_type': 'overconfidence',
                'severity': 'medium',
                'title': '过度自信风险',
                'message': '您的高风险投资比例较高，但理性度评分偏低。',
                'suggestion': '建议在高风险投资前进行更充分的分析，并设置止损点。'
            })
        
        # 6. 检测现金储备不足
        cash_alert = self._check_low_cash_reserve(logs)
        if cash_alert:
            alerts.append(cash_alert)
        
        return alerts
    
    def _check_high_risk_streak(self, logs: List[Dict]) -> Optional[Dict]:
        """检测连续高风险行为"""
        recent_logs = logs[:10]  # 最近10条
        high_risk_count = sum(1 for log in recent_logs if (log.get('risk_score') or 0) > 0.7)
        
        if high_risk_count >= 5:
            return {
                'alert_type': 'high_risk_streak',
                'severity': 'high',
                'title': '连续高风险操作警告',
                'message': f'您最近{len(recent_logs)}次操作中有{high_risk_count}次为高风险行为。',
                'suggestion': '建议暂停激进投资，重新评估您的风险承受能力和投资组合。'
            }
        return None
    
    def _check_overtrading(self, logs: List[Dict], current_month: int) -> Optional[Dict]:
        """检测过度交易"""
        # 统计最近一个月的交易次数
        recent_trades = [log for log in logs 
                        if log['month'] >= current_month - 1 
                        and log['action_category'] == 'investment']
        
        if len(recent_trades) > 15:
            return {
                'alert_type': 'overtrading',
                'severity': 'medium',
                'title': '交易频率过高',
                'message': f'您本月进行了{len(recent_trades)}次投资交易，频繁交易会增加手续费成本和决策失误风险。',
                'suggestion': '建议制定长期投资策略，减少短期频繁操作。'
            }
        return None
    
    def _check_leverage_abuse(self, logs: List[Dict]) -> Optional[Dict]:
        """检测杠杆过度使用"""
        loan_actions = [log for log in logs if 'loan' in log['action_type']]
        
        if len(loan_actions) >= 3:
            return {
                'alert_type': 'leverage_abuse',
                'severity': 'high',
                'title': '贷款使用频繁',
                'message': f'您近期申请了{len(loan_actions)}次贷款，过度使用杠杆会增加财务风险。',
                'suggestion': '建议控制负债率，确保每月还款不超过收入的30%。'
            }
        return None
    
    def _check_low_cash_reserve(self, logs: List[Dict]) -> Optional[Dict]:
        """检测现金储备不足"""
        # 检查是否有低现金储备的投资行为
        risky_investments = [log for log in logs 
                           if log['action_category'] == 'investment'
                           and (log.get('rationality_score') or 1) < 0.4]
        
        if len(risky_investments) >= 2:
            return {
                'alert_type': 'low_cash_reserve',
                'severity': 'high',
                'title': '现金储备不足风险',
                'message': '您在现金储备较低时进行了多次投资，可能影响应急资金。',
                'suggestion': '建议保持至少3-6个月生活费的现金储备作为应急基金。'
            }
        return None
    
    def get_warnings(self, session_id: str, game_state: Dict = None) -> List[Dict]:
        """
        获取行为预警（API 入口方法）
        
        Args:
            session_id: 会话ID
            game_state: 当前游戏状态（可选）
            
        Returns:
            预警列表
        """
        # 获取当前月份
        current_month = 0
        if game_state:
            current_month = game_state.get('current_month', 0)
        else:
            # 尝试从数据库获取
            try:
                current_month = self.db.get_session_month(session_id) or 0
            except:
                pass
        
        # 调用内部预警检测方法
        return self.check_behavior_alerts(session_id, current_month)
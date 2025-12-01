"""
回响交互系统 - FinAI核心模块
处理玩家与AI化身之间的"意识回响"交互
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class EchoType(Enum):
    """回响类型"""
    INSPIRATIONAL = "inspirational"    # 启发式
    ADVISORY = "advisory"             # 建议式  
    DIRECTIVE = "directive"           # 指令式
    EMOTIONAL = "emotional"           # 情感式

@dataclass
class EchoAnalysis:
    """回响分析结果"""
    echo_type: EchoType
    sentiment: str  # positive, negative, neutral
    confidence: float  # 0-1
    key_words: List[str]
    intent: str
    target_option: Optional[str] = None

class EchoSystem:
    """回响系统主类"""
    
    def __init__(self):
        self.intervention_points = 10  # 每日干预点数
        self.max_intervention_points = 10
        self.echo_history: List[Dict] = []
    
    def analyze_echo(self, echo_text: str, available_options: List[str]) -> EchoAnalysis:
        """分析玩家的回响内容"""
        echo_lower = echo_text.lower().strip()
        
        # 情感分析
        sentiment = self._analyze_sentiment(echo_lower)
        
        # 类型识别
        echo_type = self._identify_echo_type(echo_lower)
        
        # 关键词提取
        key_words = self._extract_keywords(echo_lower)
        
        # 意图识别
        intent = self._identify_intent(echo_lower, key_words)
        
        # 目标选项匹配
        target_option = self._match_target_option(echo_lower, available_options)
        
        # 置信度计算
        confidence = self._calculate_confidence(echo_lower, key_words, target_option)
        
        return EchoAnalysis(
            echo_type=echo_type,
            sentiment=sentiment,
            confidence=confidence,
            key_words=key_words,
            intent=intent,
            target_option=target_option
        )
    
    def _analyze_sentiment(self, text: str) -> str:
        """分析情感倾向"""
        positive_words = [
            "好", "棒", "赞", "支持", "同意", "推荐", "建议", "应该", "最好",
            "不错", "可以", "值得", "机会", "收益", "成功", "优秀", "聪明"
        ]
        
        negative_words = [
            "不", "别", "不要", "不行", "不好", "危险", "风险", "亏损", "失败",
            "错误", "问题", "担心", "害怕", "谨慎", "小心", "避免", "拒绝"
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _identify_echo_type(self, text: str) -> EchoType:
        """识别回响类型"""
        # 指令式关键词
        directive_patterns = [
            r"必须", r"一定要", r"立即", r"马上", r"现在就", r"直接",
            r"给我", r"帮我", r"去做", r"执行"
        ]
        
        # 建议式关键词
        advisory_patterns = [
            r"建议", r"推荐", r"最好", r"应该", r"可以考虑", r"不如",
            r"我觉得", r"我认为", r"或许", r"也许"
        ]
        
        # 启发式关键词
        inspirational_patterns = [
            r"想想", r"考虑", r"思考", r"分析", r"评估", r"权衡",
            r"如果", r"假设", r"可能", r"会不会"
        ]
        
        # 情感式关键词
        emotional_patterns = [
            r"担心", r"害怕", r"兴奋", r"开心", r"紧张", r"焦虑",
            r"希望", r"期待", r"失望", r"沮丧"
        ]
        
        # 按优先级检查
        if any(re.search(pattern, text) for pattern in directive_patterns):
            return EchoType.DIRECTIVE
        elif any(re.search(pattern, text) for pattern in advisory_patterns):
            return EchoType.ADVISORY
        elif any(re.search(pattern, text) for pattern in inspirational_patterns):
            return EchoType.INSPIRATIONAL
        elif any(re.search(pattern, text) for pattern in emotional_patterns):
            return EchoType.EMOTIONAL
        else:
            return EchoType.ADVISORY  # 默认为建议式
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 金融相关关键词
        financial_keywords = [
            "投资", "股票", "基金", "债券", "房产", "贷款", "存款", "理财",
            "风险", "收益", "利率", "通胀", "市场", "经济", "金融", "资产",
            "买入", "卖出", "持有", "止损", "加仓", "减仓", "套现", "融资"
        ]
        
        # 决策相关关键词
        decision_keywords = [
            "选择", "决定", "考虑", "分析", "评估", "比较", "权衡", "判断",
            "机会", "时机", "策略", "计划", "目标", "方案", "建议", "意见"
        ]
        
        # 情感相关关键词
        emotion_keywords = [
            "担心", "害怕", "紧张", "焦虑", "兴奋", "开心", "满意", "失望",
            "后悔", "遗憾", "希望", "期待", "信心", "怀疑", "犹豫", "坚定"
        ]
        
        all_keywords = financial_keywords + decision_keywords + emotion_keywords
        found_keywords = [keyword for keyword in all_keywords if keyword in text]
        
        return found_keywords
    
    def _identify_intent(self, text: str, keywords: List[str]) -> str:
        """识别意图"""
        if any(word in keywords for word in ["投资", "买入", "购买"]):
            if any(word in text for word in ["不要", "别", "不建议"]):
                return "discourage_investment"
            else:
                return "encourage_investment"
        
        elif any(word in keywords for word in ["卖出", "止损", "套现"]):
            return "suggest_sell"
        
        elif any(word in keywords for word in ["等待", "持有", "观望"]):
            return "suggest_wait"
        
        elif any(word in keywords for word in ["分析", "考虑", "评估"]):
            return "suggest_analysis"
        
        elif any(word in keywords for word in ["谨慎", "小心", "风险"]):
            return "warn_risk"
        
        else:
            return "general_advice"
    
    def _match_target_option(self, text: str, options: List[str]) -> Optional[str]:
        """匹配目标选项"""
        best_match = None
        max_score = 0
        
        for option in options:
            score = 0
            option_words = option.lower().split()
            
            # 计算匹配分数
            for word in option_words:
                if word in text:
                    score += 1
            
            # 特殊匹配规则
            if "投资" in option.lower():
                if any(keyword in text for keyword in ["投资", "买入", "购买"]):
                    score += 2
                if any(keyword in text for keyword in ["不要", "别", "拒绝"]):
                    score -= 2
            
            if "拒绝" in option.lower():
                if any(keyword in text for keyword in ["不要", "别", "拒绝", "不建议"]):
                    score += 2
            
            if score > max_score:
                max_score = score
                best_match = option
        
        return best_match if max_score > 0 else None
    
    def _calculate_confidence(self, text: str, keywords: List[str], target_option: Optional[str]) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度
        
        # 文本长度影响
        if len(text) > 10:
            confidence += 0.1
        if len(text) > 30:
            confidence += 0.1
        
        # 关键词数量影响
        confidence += min(len(keywords) * 0.05, 0.2)
        
        # 目标选项匹配影响
        if target_option:
            confidence += 0.2
        
        # 明确性指标
        if any(word in text for word in ["建议", "推荐", "应该", "最好"]):
            confidence += 0.1
        
        if any(word in text for word in ["不要", "别", "不建议", "拒绝"]):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def process_echo(self, echo_text: str, available_options: List[str], 
                    current_trust: int) -> Dict:
        """处理回响并返回影响结果"""
        if self.intervention_points <= 0:
            return {
                "success": False,
                "message": "今日干预点数已用完，请明天再试",
                "remaining_points": 0
            }
        
        # 分析回响
        analysis = self.analyze_echo(echo_text, available_options)
        
        # 消耗干预点数
        self.intervention_points -= 1
        
        # 计算影响权重
        influence_weight = self._calculate_influence_weight(analysis, current_trust)
        
        # 记录回响历史
        echo_record = {
            "text": echo_text,
            "analysis": analysis,
            "influence_weight": influence_weight,
            "remaining_points": self.intervention_points
        }
        self.echo_history.append(echo_record)
        
        return {
            "success": True,
            "analysis": analysis,
            "influence_weight": influence_weight,
            "remaining_points": self.intervention_points,
            "message": f"回响已发送，影响权重: {influence_weight:.2f}"
        }
    
    def _calculate_influence_weight(self, analysis: EchoAnalysis, trust_level: int) -> float:
        """计算回响的影响权重"""
        base_weight = 0.3  # 基础权重
        
        # 信任度影响 (最重要的因素)
        trust_multiplier = trust_level / 100.0
        
        # 置信度影响
        confidence_bonus = analysis.confidence * 0.2
        
        # 回响类型影响
        type_multipliers = {
            EchoType.DIRECTIVE: 0.8,      # 指令式影响最大
            EchoType.ADVISORY: 1.0,       # 建议式标准影响
            EchoType.INSPIRATIONAL: 0.6,  # 启发式影响较小
            EchoType.EMOTIONAL: 0.4       # 情感式影响最小
        }
        
        type_multiplier = type_multipliers.get(analysis.echo_type, 1.0)
        
        # 情感倾向影响
        sentiment_bonus = 0.1 if analysis.sentiment == "positive" else 0.0
        
        # 计算最终权重
        final_weight = (base_weight + confidence_bonus + sentiment_bonus) * trust_multiplier * type_multiplier
        
        return min(final_weight, 1.0)  # 最大权重为1.0
    
    def reset_daily_points(self):
        """重置每日干预点数"""
        self.intervention_points = self.max_intervention_points
    
    def get_echo_statistics(self) -> Dict:
        """获取回响统计信息"""
        if not self.echo_history:
            return {"total_echoes": 0}
        
        total_echoes = len(self.echo_history)
        avg_influence = sum(record["influence_weight"] for record in self.echo_history) / total_echoes
        
        type_counts = {}
        for record in self.echo_history:
            echo_type = record["analysis"].echo_type.value
            type_counts[echo_type] = type_counts.get(echo_type, 0) + 1
        
        return {
            "total_echoes": total_echoes,
            "average_influence": avg_influence,
            "type_distribution": type_counts,
            "remaining_points": self.intervention_points
        }

# 全局实例
echo_system = EchoSystem()
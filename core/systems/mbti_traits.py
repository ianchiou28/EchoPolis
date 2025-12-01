"""
MBTI人格特质系统 - FinAI核心模块
定义16种MBTI人格类型的决策特征和行为模式
"""
import random
from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass

class MBTIType(Enum):
    # 分析师 (NT)
    INTJ = "INTJ"  # 建筑师
    INTP = "INTP"  # 逻辑学家  
    ENTJ = "ENTJ"  # 指挥官
    ENTP = "ENTP"  # 辩论家
    
    # 外交官 (NF)
    INFJ = "INFJ"  # 提倡者
    INFP = "INFP"  # 调停者
    ENFJ = "ENFJ"  # 主人公
    ENFP = "ENFP"  # 竞选者
    
    # 守护者 (SJ)
    ISTJ = "ISTJ"  # 物流师
    ISFJ = "ISFJ"  # 守护者
    ESTJ = "ESTJ"  # 总经理
    ESFJ = "ESFJ"  # 执政官
    
    # 探险家 (SP)
    ISTP = "ISTP"  # 鉴赏家
    ISFP = "ISFP"  # 探险家
    ESTP = "ESTP"  # 企业家
    ESFP = "ESFP"  # 表演者

@dataclass
class MBTITrait:
    """MBTI特质定义"""
    name: str
    description: str
    decision_weight: float  # 决策权重 (-1.0 到 1.0)
    trigger_conditions: List[str]  # 触发条件
    behavioral_tendency: str  # 行为倾向描述

class MBTITraitsSystem:
    """MBTI特质系统"""
    
    def __init__(self):
        self.traits_map = self._initialize_traits()
    
    def _initialize_traits(self) -> Dict[MBTIType, List[MBTITrait]]:
        """初始化所有MBTI类型的特质"""
        return {
            MBTIType.INTJ: [
                MBTITrait("战略规划", "倾向于制定长期投资计划", 0.8, 
                         ["面临重大投资决策"], "优先考虑长期收益而非短期利润"),
                MBTITrait("独立决策", "不易受他人意见影响", -0.3,
                         ["信任度<50"], "更相信自己的分析而非他人建议"),
                MBTITrait("风险厌恶", "偏好稳健的投资策略", 0.6,
                         ["市场波动>20%"], "在市场不确定时选择保守策略")
            ],
            
            MBTIType.INTP: [
                MBTITrait("分析瘫痪", "过度分析导致决策延迟", -0.4,
                         ["面临多个选择", "FQ>=3"], "花费过多时间分析而错失机会"),
                MBTITrait("理论导向", "偏好基于数据的决策", 0.7,
                         ["有详细数据支持"], "更信任量化分析结果"),
                MBTITrait("创新投资", "愿意尝试新兴投资领域", 0.5,
                         ["出现新投资机会"], "对科技股和新兴市场感兴趣")
            ],
            
            MBTIType.ENTJ: [
                MBTITrait("果断执行", "快速做出投资决策", 0.8,
                         ["时间紧迫"], "不会因过度思考而错失机会"),
                MBTITrait("高风险偏好", "愿意承担更大风险获取收益", 0.6,
                         ["预期收益>15%"], "追求高收益投资机会"),
                MBTITrait("领导倾向", "容易被成功案例影响", 0.4,
                         ["看到成功投资案例"], "模仿成功投资者的策略")
            ],
            
            MBTIType.ENTP: [
                MBTITrait("机会主义", "善于发现投资机会", 0.7,
                         ["市场出现新趋势"], "快速识别并抓住新兴机会"),
                MBTITrait("多元化投资", "不愿意把鸡蛋放在一个篮子里", 0.5,
                         ["投资组合集中度>60%"], "主动分散投资风险"),
                MBTITrait("变化适应", "能够快速调整投资策略", 0.6,
                         ["市场环境变化"], "根据市场变化灵活调整")
            ],
            
            MBTIType.ESFP: [
                MBTITrait("情绪化决策", "容易受当前情绪影响", -0.5,
                         ["幸福感<30", "压力值>70"], "在情绪低落时做出冲动决策"),
                MBTITrait("社交影响", "容易受朋友建议影响", 0.4,
                         ["收到朋友投资建议"], "重视社交圈的投资意见"),
                MBTITrait("即时满足", "偏好短期收益", -0.3,
                         ["看到快速盈利机会"], "更关注短期回报而非长期价值")
            ],
            
            MBTIType.ISTJ: [
                MBTITrait("保守稳健", "偏好低风险投资", 0.8,
                         ["市场波动>15%"], "选择银行存款、国债等稳健产品"),
                MBTITrait("按部就班", "遵循既定投资计划", 0.6,
                         ["有明确投资计划"], "严格执行预设的投资策略"),
                MBTITrait("传统偏好", "偏好传统投资产品", 0.4,
                         ["面临新型投资产品"], "更信任传统的投资方式")
            ],
            
            MBTIType.ISFJ: [
                MBTITrait("谨慎保守", "优先考虑资金安全", 0.7,
                         ["面临高风险投资"], "倾向于选择保本型投资产品"),
                MBTITrait("家庭优先", "投资决策考虑家庭需求", 0.6,
                         ["家庭支出增加"], "为家庭稳定而牺牲投资收益"),
                MBTITrait("情感决策", "容易受情感因素影响", -0.3,
                         ["压力值>60"], "在压力下可能做出非理性决策")
            ],
            
            MBTIType.INFJ: [
                MBTITrait("长远眼光", "注重投资的长期价值", 0.8,
                         ["面临长期投资机会"], "愿意为未来收益等待"),
                MBTITrait("价值投资", "偏好有社会意义的投资", 0.5,
                         ["出现ESG投资机会"], "选择符合价值观的投资项目"),
                MBTITrait("直觉判断", "依赖直觉做投资决策", 0.4,
                         ["缺乏详细数据"], "相信内在直觉胜过外在分析")
            ],
            
            MBTIType.INFP: [
                MBTITrait("理想主义", "投资符合个人价值观的项目", 0.6,
                         ["出现理念相符投资"], "宁可收益低也要投资理念相符"),
                MBTITrait("风险规避", "避免可能造成重大损失的投资", 0.7,
                         ["面临高风险投资"], "更关注本金安全而非高收益"),
                MBTITrait("情绪波动", "投资决策受情绪状态影响", -0.4,
                         ["幸福感<40"], "情绪低落时容易做出消极决策")
            ],
            
            MBTIType.ENFJ: [
                MBTITrait("社会责任", "偏好对社会有益的投资", 0.5,
                         ["出现社会影响投资"], "选择能产生正面社会影响的项目"),
                MBTITrait("团队决策", "重视他人意见和建议", 0.6,
                         ["收到专业建议"], "容易被专家意见说服"),
                MBTITrait("乐观偏向", "倾向于高估投资收益", -0.3,
                         ["面临诱人投资机会"], "可能因过度乐观而忽视风险")
            ],
            
            MBTIType.ENFP: [
                MBTITrait("创新追求", "喜欢投资新兴和创新领域", 0.7,
                         ["出现创新投资机会"], "对新技术和新模式投资感兴趣"),
                MBTITrait("多样化偏好", "不喜欢单一投资策略", 0.5,
                         ["投资组合过于集中"], "主动寻求投资组合多样化"),
                MBTITrait("冲动决策", "容易被热门投资吸引", -0.4,
                         ["出现热门投资话题"], "可能因一时冲动而投资")
            ],
            
            MBTIType.ESTJ: [
                MBTITrait("目标导向", "制定明确的投资目标", 0.8,
                         ["需要制定投资计划"], "设定具体的收益目标和时间表"),
                MBTITrait("权威信任", "相信专业机构的投资建议", 0.6,
                         ["收到权威机构建议"], "倾向于跟随知名投资机构"),
                MBTITrait("效率优先", "偏好简单直接的投资方式", 0.4,
                         ["面临复杂投资产品"], "避免过于复杂的投资结构")
            ],
            
            MBTIType.ESFJ: [
                MBTITrait("安全第一", "优先考虑投资安全性", 0.8,
                         ["面临风险投资"], "宁可收益低也要保证本金安全"),
                MBTITrait("从众心理", "容易跟随大众投资趋势", 0.3,
                         ["出现投资热潮"], "倾向于跟随主流投资选择"),
                MBTITrait("关系影响", "重视亲友的投资建议", 0.5,
                         ["收到亲友建议"], "容易被信任的人影响投资决策")
            ],
            
            MBTIType.ISTP: [
                MBTITrait("实用主义", "关注投资的实际价值", 0.6,
                         ["评估投资实用性"], "更看重实际收益而非概念炒作"),
                MBTITrait("独立分析", "喜欢自己研究投资标的", 0.7,
                         ["需要投资决策"], "不轻信他人，坚持独立判断"),
                MBTITrait("灵活应变", "能够快速调整投资策略", 0.5,
                         ["市场环境变化"], "根据市场变化及时调整投资")
            ],
            
            MBTIType.ISFP: [
                MBTITrait("价值导向", "投资符合个人价值观的项目", 0.6,
                         ["出现价值观冲突"], "避免投资与价值观冲突的项目"),
                MBTITrait("低调保守", "偏好稳健的投资方式", 0.7,
                         ["面临激进投资"], "选择风险较低的投资策略"),
                MBTITrait("情感决策", "投资决策受个人情感影响", -0.3,
                         ["情绪波动较大"], "可能因情绪而做出非理性决策")
            ],
            
            MBTIType.ESTP: [
                MBTITrait("机会敏感", "善于发现短期投资机会", 0.7,
                         ["出现短期机会"], "快速抓住市场短期波动机会"),
                MBTITrait("风险偏好", "愿意承担较高投资风险", 0.6,
                         ["高收益投资机会"], "为了高收益愿意承担风险"),
                MBTITrait("行动导向", "倾向于快速做出投资决策", 0.5,
                         ["需要快速决策"], "不喜欢长时间犹豫和分析")
            ]
        }
    
    def get_traits(self, mbti_type: MBTIType) -> List[MBTITrait]:
        """获取指定MBTI类型的特质列表"""
        return self.traits_map.get(mbti_type, [])
    
    def calculate_decision_influence(self, mbti_type: MBTIType, 
                                   current_state: Dict, 
                                   decision_context: str) -> float:
        """计算MBTI特质对决策的影响权重"""
        traits = self.get_traits(mbti_type)
        total_influence = 0.0
        active_traits = 0
        
        for trait in traits:
            if self._check_trigger_conditions(trait.trigger_conditions, current_state, decision_context):
                total_influence += trait.decision_weight
                active_traits += 1
        
        # 返回平均影响权重
        return total_influence / max(active_traits, 1)
    
    def _check_trigger_conditions(self, conditions: List[str], 
                                current_state: Dict, 
                                context: str) -> bool:
        """检查特质触发条件是否满足"""
        for condition in conditions:
            if self._evaluate_condition(condition, current_state, context):
                return True
        return False
    
    def _evaluate_condition(self, condition: str, state: Dict, context: str) -> bool:
        """评估单个条件"""
        # 简化的条件评估逻辑
        if "幸福感<" in condition:
            threshold = int(condition.split("<")[1])
            return state.get("happiness", 50) < threshold
        elif "压力值>" in condition:
            threshold = int(condition.split(">")[1])
            return state.get("stress", 0) > threshold
        elif "信任度<" in condition:
            threshold = int(condition.split("<")[1])
            return state.get("trust", 50) < threshold
        elif "FQ>=" in condition:
            threshold = int(condition.split(">=")[1])
            return state.get("fq_level", 1) >= threshold
        elif "市场波动>" in condition:
            # 这里可以根据实际市场数据判断
            return "市场波动" in context
        elif condition in context:
            return True
        
        return False
    
    def get_personality_description(self, mbti_type: MBTIType) -> str:
        """获取MBTI类型的性格描述"""
        descriptions = {
            MBTIType.INTJ: "建筑师 - 富有想象力和战略性的思想家，一切皆在计划中",
            MBTIType.INTP: "逻辑学家 - 具有创造性的发明家，对知识有着止不住的渴望",
            MBTIType.ENTJ: "指挥官 - 大胆，富有想象力的强势领导者，总能找到或创造解决方法",
            MBTIType.ENTP: "辩论家 - 聪明好奇的思想家，不会放弃任何挑战",
            MBTIType.INFJ: "提倡者 - 安静而神秘，同时鼓舞他人的理想主义者",
            MBTIType.INFP: "调停者 - 诗意，善良的利他主义者，总是热心为正义而战",
            MBTIType.ENFJ: "主人公 - 魅力非凡的领导者，能够使听众着迷",
            MBTIType.ENFP: "竞选者 - 热情，有创造性的社交者，总能找到微笑的理由",
            MBTIType.ISTJ: "物流师 - 实用主义的现实主义者，可靠性无可置疑",
            MBTIType.ISFJ: "守护者 - 非常专注而温暖的守护者，时刻准备保护爱着的人们",
            MBTIType.ESTJ: "总经理 - 出色的管理者，在管理事物或人员方面无与伦比",
            MBTIType.ESFJ: "执政官 - 极有同情心，善于社交的人们，总是热心帮助他人",
            MBTIType.ISTP: "鉴赏家 - 大胆而实际的实验家，擅长使用各种工具",
            MBTIType.ISFP: "探险家 - 灵活，迷人的艺术家，时刻准备探索新的可能性",
            MBTIType.ESTP: "企业家 - 聪明，精力充沛的感知者，真正享受生活在边缘",
            MBTIType.ESFP: "表演者 - 自发的，精力充沛的娱乐者，生活在他们周围从不无聊"
        }
        return descriptions.get(mbti_type, "未知类型")

# 全局实例
mbti_system = MBTITraitsSystem()

class MBTITraits:
    """MBTI特质接口类 - 兼容性包装"""
    
    @staticmethod
    def get_all_types():
        """获取所有MBTI类型"""
        return MBTI_TYPES

# 导出MBTI类型字典供GUI使用
MBTI_TYPES = {
    'INTJ': {'description': '建筑师 - 富有想象力和战略性的思想家，一切皆在计划中'},
    'INTP': {'description': '逻辑学家 - 具有创造性的发明家，对知识有着止不住的渴望'},
    'ENTJ': {'description': '指挥官 - 大胆，富有想象力的强势领导者，总能找到或创造解决方法'},
    'ENTP': {'description': '辩论家 - 聪明好奇的思想家，不会放弃任何挑战'},
    'INFJ': {'description': '提倡者 - 安静而神秘，同时鼓舞他人的理想主义者'},
    'INFP': {'description': '调停者 - 诗意，善良的利他主义者，总是热心为正义而战'},
    'ENFJ': {'description': '主人公 - 魅力非凡的领导者，能够使听众着迷'},
    'ENFP': {'description': '竞选者 - 热情，有创造性的社交者，总能找到微笑的理由'},
    'ISTJ': {'description': '物流师 - 实用主义的现实主义者，可靠性无可置疑'},
    'ISFJ': {'description': '守护者 - 非常专注而温暖的守护者，时刻准备保护爱着的人们'},
    'ESTJ': {'description': '总经理 - 出色的管理者，在管理事物或人员方面无与伦比'},
    'ESFJ': {'description': '执政官 - 极有同情心，善于社交的人们，总是热心帮助他人'},
    'ISTP': {'description': '鉴赏家 - 大胆而实际的实验家，擅长使用各种工具'},
    'ISFP': {'description': '探险家 - 灵活，迷人的艺术家，时刻准备探索新的可能性'},
    'ESTP': {'description': '企业家 - 聪明，精力充沛的感知者，真正享受生活在边缘'},
    'ESFP': {'description': '表演者 - 自发的，精力充沛的娱乐者，生活在他们周围从不无聊'}
}
"""
简化的AI化身类 - 专门用于GUI版本
"""
from typing import Dict, Optional
from ..systems.mbti_traits import MBTI_TYPES
from ..systems.fate_wheel import FATE_WHEEL

class SimpleAvatar:
    """简化的AI化身类"""
    
    def __init__(self, name: str, mbti_type: str):
        self.name = name
        self.mbti_type = mbti_type
        
        # 基本属性
        self.assets = 50000
        self.health = 100
        self.energy = 100
        self.happiness = 50
        self.stress = 0
        self.trust_level = 50
        self.round_count = 1
        
        # MBTI描述
        self.mbti_description = MBTI_TYPES.get(mbti_type, {}).get('description', '未知类型')
        
        # 命运背景（稍后设置）
        self.fate_type = None
        self.fate_description = ""
    
    def set_fate(self, fate_key: str):
        """设置命运"""
        if fate_key in FATE_WHEEL:
            fate_data = FATE_WHEEL[fate_key]
            self.fate_type = fate_key
            self.fate_description = fate_data['description']
            self.assets = fate_data['initial_money']
    
    def get_status_dict(self) -> Dict:
        """获取状态字典"""
        return {
            'name': self.name,
            'mbti_type': self.mbti_type,
            'mbti_description': self.mbti_description,
            'assets': self.assets,
            'health': self.health,
            'energy': self.energy,
            'happiness': self.happiness,
            'stress': self.stress,
            'trust_level': self.trust_level,
            'round_count': self.round_count,
            'fate_type': self.fate_type,
            'fate_description': self.fate_description
        }
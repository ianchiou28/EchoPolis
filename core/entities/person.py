"""
Person实体 - 参考AIvilization的Person结构
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .brain import Brain
from .action import Action, ActionType
from ..systems.mbti_traits import MBTIType

class PersonState(Enum):
    """人物状态"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    RESTING = "resting"

@dataclass
class PersonAttributes:
    """人物属性"""
    name: str
    age: int = 22
    mbti_type: MBTIType = MBTIType.INTP
    credits: int = 50000
    health: int = 100
    energy: int = 100
    happiness: int = 50
    stress: int = 0
    trust_level: int = 50

class Person:
    """人物实体 - 类似AIvilization的Person"""
    
    def __init__(self, name: str, mbti_type: MBTIType):
        self.attributes = PersonAttributes(name=name, mbti_type=mbti_type)
        self.brain = Brain(self)
        self.state = PersonState.IDLE
        self.current_action: Optional[Action] = None
        self.action_history: List[Action] = []
        self.memory: Dict = {}
        
    def think(self, situation: str, options: List[str], player_echo: Optional[str] = None) -> Dict:
        """思考决策"""
        self.state = PersonState.THINKING
        result = self.brain.process_decision(situation, options, player_echo)
        return result
    
    def act(self, action_type: ActionType, target: str, context: Dict = None) -> Dict:
        """执行行动"""
        self.state = PersonState.ACTING
        action = Action(action_type, target, context or {})
        self.current_action = action
        
        result = action.execute(self)
        self.action_history.append(action)
        
        self.state = PersonState.IDLE
        self.current_action = None
        
        return result
    
    def update_attributes(self, changes: Dict):
        """更新属性"""
        for attr, value in changes.items():
            if hasattr(self.attributes, attr):
                current = getattr(self.attributes, attr)
                if isinstance(current, int):
                    new_value = max(0, min(100, current + value)) if attr != 'credits' else max(0, current + value)
                    setattr(self.attributes, attr, new_value)
    
    def get_state(self) -> Dict:
        """获取状态"""
        return {
            "name": self.attributes.name,
            "age": self.attributes.age,
            "mbti": self.attributes.mbti_type.value,
            "credits": self.attributes.credits,
            "health": self.attributes.health,
            "energy": self.attributes.energy,
            "happiness": self.attributes.happiness,
            "stress": self.attributes.stress,
            "trust_level": self.attributes.trust_level,
            "state": self.state.value,
            "current_action": self.current_action.action_type.value if self.current_action else None
        }
    
    def rest(self):
        """休息恢复"""
        self.state = PersonState.RESTING
        self.update_attributes({
            "energy": 20,
            "stress": -5,
            "health": 2
        })
        self.state = PersonState.IDLE
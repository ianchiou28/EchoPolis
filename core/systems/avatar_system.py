# -*- coding: utf-8 -*-
"""
头像系统 - 使用成就金币购买头像
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class AvatarRarity(Enum):
    """头像稀有度"""
    COMMON = "common"       # 普通
    RARE = "rare"           # 稀有
    EPIC = "epic"           # 史诗
    LEGENDARY = "legendary" # 传说

@dataclass
class Avatar:
    """头像定义"""
    id: str
    name: str
    description: str
    image: str              # 图片文件名或emoji
    rarity: AvatarRarity
    price: int              # 成就金币价格
    unlock_condition: str = ""  # 解锁条件描述（有些头像需要特定成就才能购买）
    required_achievement: str = ""  # 需要的成就ID（空表示无需成就）

# 所有可用头像
AVATARS: Dict[str, Avatar] = {
    # === 免费/默认头像 ===
    "default_orange": Avatar(
        id="default_orange",
        name="默认橙方",
        description="每位玩家的起点",
        image="😐",
        rarity=AvatarRarity.COMMON,
        price=0
    ),
    
    # === 普通头像 (100-500 金币) ===
    "happy_face": Avatar(
        id="happy_face",
        name="快乐方块",
        description="保持微笑，好运自来",
        image="😊",
        rarity=AvatarRarity.COMMON,
        price=100
    ),
    "cool_shades": Avatar(
        id="cool_shades",
        name="墨镜大佬",
        description="低调奢华有内涵",
        image="😎",
        rarity=AvatarRarity.COMMON,
        price=150
    ),
    "money_eyes": Avatar(
        id="money_eyes",
        name="财迷",
        description="眼里只有钱钱钱",
        image="🤑",
        rarity=AvatarRarity.COMMON,
        price=200
    ),
    "nerd_face": Avatar(
        id="nerd_face",
        name="学霸",
        description="知识就是力量",
        image="🤓",
        rarity=AvatarRarity.COMMON,
        price=200
    ),
    "thinking_face": Avatar(
        id="thinking_face",
        name="深思者",
        description="让我想想...",
        image="🤔",
        rarity=AvatarRarity.COMMON,
        price=150
    ),
    
    # === 稀有头像 (500-2000 金币) ===
    "star_eyes": Avatar(
        id="star_eyes",
        name="追星族",
        description="眼里有星辰大海",
        image="🤩",
        rarity=AvatarRarity.RARE,
        price=500
    ),
    "crown": Avatar(
        id="crown",
        name="小王子",
        description="每个人都是自己的国王",
        image="🤴",
        rarity=AvatarRarity.RARE,
        price=800
    ),
    "princess": Avatar(
        id="princess",
        name="小公主",
        description="优雅从容",
        image="👸",
        rarity=AvatarRarity.RARE,
        price=800
    ),
    "robot": Avatar(
        id="robot",
        name="机器人",
        description="高效理性的投资者",
        image="🤖",
        rarity=AvatarRarity.RARE,
        price=1000
    ),
    "alien": Avatar(
        id="alien",
        name="外星来客",
        description="用外星视角看金融",
        image="👽",
        rarity=AvatarRarity.RARE,
        price=1200
    ),
    "ninja": Avatar(
        id="ninja",
        name="忍者",
        description="低调潜伏，一击必中",
        image="🥷",
        rarity=AvatarRarity.RARE,
        price=1500
    ),
    
    # === 史诗头像 (2000-5000 金币) ===
    "diamond": Avatar(
        id="diamond",
        name="钻石恒久远",
        description="坚不可摧的意志",
        image="💎",
        rarity=AvatarRarity.EPIC,
        price=2500
    ),
    "rocket": Avatar(
        id="rocket",
        name="火箭升空",
        description="To the moon!",
        image="🚀",
        rarity=AvatarRarity.EPIC,
        price=3000
    ),
    "unicorn": Avatar(
        id="unicorn",
        name="独角兽",
        description="传说中的存在",
        image="🦄",
        rarity=AvatarRarity.EPIC,
        price=3500
    ),
    "dragon": Avatar(
        id="dragon",
        name="神龙",
        description="金融市场的王者",
        image="🐉",
        rarity=AvatarRarity.EPIC,
        price=4000
    ),
    "phoenix": Avatar(
        id="phoenix",
        name="凤凰涅槃",
        description="浴火重生",
        image="🔥",
        rarity=AvatarRarity.EPIC,
        price=4500,
        unlock_condition="需要解锁「绝地反击」成就",
        required_achievement="COMEBACK"
    ),
    
    # === 传说头像 (5000+ 金币) ===
    "whale": Avatar(
        id="whale",
        name="巨鲸",
        description="市场的主宰者",
        image="🐋",
        rarity=AvatarRarity.LEGENDARY,
        price=8000,
        unlock_condition="需要解锁「百万富翁」成就",
        required_achievement="W1M"
    ),
    "galaxy": Avatar(
        id="galaxy",
        name="银河系",
        description="财富如繁星般闪耀",
        image="🌌",
        rarity=AvatarRarity.LEGENDARY,
        price=10000
    ),
    "crown_diamond": Avatar(
        id="crown_diamond",
        name="钻石王冠",
        description="至高无上的荣耀",
        image="👑",
        rarity=AvatarRarity.LEGENDARY,
        price=15000,
        unlock_condition="需要解锁「财务自由」成就",
        required_achievement="W10M"
    ),
    "trophy": Avatar(
        id="trophy",
        name="冠军奖杯",
        description="真正的赢家",
        image="🏆",
        rarity=AvatarRarity.LEGENDARY,
        price=20000,
        unlock_condition="解锁10个成就",
        required_achievement=""  # 特殊条件，需要代码检查
    ),
}


# 头像对应的颜色
AVATAR_COLORS = {
    "default_orange": "#ff8c00",
    "happy_face": "#ffd700",
    "cool_shades": "#1a1a1a",
    "money_eyes": "#00aa00",
    "nerd_face": "#8b4513",
    "thinking_face": "#4a9eff",
    "star_eyes": "#ff69b4",
    "crown": "#daa520",
    "princess": "#ff69b4",
    "robot": "#708090",
    "alien": "#00ff7f",
    "ninja": "#2f2f2f",
    "diamond": "#b9f2ff",
    "rocket": "#ff4500",
    "unicorn": "#ee82ee",
    "dragon": "#dc143c",
    "phoenix": "#ff6600",
    "whale": "#1e90ff",
    "galaxy": "#4b0082",
    "crown_diamond": "#ffd700",
    "trophy": "#ffd700"
}


class AvatarSystem:
    """头像系统"""
    
    def __init__(self):
        self.avatars = AVATARS
    
    def get_all_avatars(self) -> List[Dict]:
        """获取所有头像"""
        return [
            {
                "id": avatar.id,
                "name": avatar.name,
                "description": avatar.description,
                "emoji": avatar.image,
                "color": AVATAR_COLORS.get(avatar.id, "#ff8c00"),
                "rarity": avatar.rarity.value,
                "price": avatar.price,
                "unlock_condition": avatar.unlock_condition,
                "required_achievement": avatar.required_achievement,
                "required_count": 10 if avatar.id == "trophy" else 0
            }
            for avatar in self.avatars.values()
        ]
    
    def get_avatar(self, avatar_id: str) -> Optional[Dict]:
        """获取单个头像信息"""
        if avatar_id in self.avatars:
            avatar = self.avatars[avatar_id]
            return {
                "id": avatar.id,
                "name": avatar.name,
                "description": avatar.description,
                "emoji": avatar.image,
                "color": AVATAR_COLORS.get(avatar.id, "#ff8c00"),
                "rarity": avatar.rarity.value,
                "price": avatar.price,
                "unlock_condition": avatar.unlock_condition,
                "required_achievement": avatar.required_achievement,
                "required_count": 10 if avatar.id == "trophy" else 0
            }
        return None
    
    def can_purchase(self, avatar_id: str, user_coins: int, user_achievements: List[str], achievement_count: int) -> tuple[bool, str]:
        """检查是否可以购买头像"""
        if avatar_id not in self.avatars:
            return False, "头像不存在"
        
        avatar = self.avatars[avatar_id]
        
        # 检查金币
        if user_coins < avatar.price:
            return False, f"金币不足，需要{avatar.price}金币"
        
        # 检查成就要求
        if avatar.required_achievement:
            if avatar.required_achievement not in user_achievements:
                return False, f"需要先解锁「{avatar.unlock_condition}」"
        
        # 特殊检查：奖杯需要10个成就
        if avatar_id == "trophy" and achievement_count < 10:
            return False, f"需要解锁10个成就（当前{achievement_count}个）"
        
        return True, "可以购买"
    
    def get_avatars_by_rarity(self, rarity: str) -> List[Dict]:
        """按稀有度获取头像"""
        return [
            self.get_avatar(avatar.id)
            for avatar in self.avatars.values()
            if avatar.rarity.value == rarity
        ]


# 全局实例
avatar_system = AvatarSystem()

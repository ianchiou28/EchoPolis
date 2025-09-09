"""
字体管理器 - 解决中文显示问题
"""
import pygame
import os
import sys

class FontManager:
    def __init__(self):
        # 初始化pygame字体系统
        if not pygame.get_init():
            pygame.init()
        pygame.font.init()
        
        self.fonts = {}
        self._load_fonts()
    
    def _load_fonts(self):
        """加载字体"""
        # 尝试加载系统中文字体
        chinese_fonts = [
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "C:/Windows/Fonts/simsun.ttc",    # 宋体
            "C:/Windows/Fonts/simkai.ttf",    # 楷体
        ]
        
        # 找到第一个可用的中文字体
        chinese_font_path = None
        for font_path in chinese_fonts:
            if os.path.exists(font_path):
                chinese_font_path = font_path
                break
        
        # 加载不同大小的字体
        sizes = [16, 20, 24, 32, 48]
        for size in sizes:
            try:
                if chinese_font_path:
                    self.fonts[f'chinese_{size}'] = pygame.font.Font(chinese_font_path, size)
                else:
                    # 如果没有找到中文字体，使用默认字体
                    self.fonts[f'default_{size}'] = pygame.font.Font(None, size)
            except:
                # 备用方案：使用pygame默认字体
                self.fonts[f'default_{size}'] = pygame.font.Font(None, size)
    
    def get_font(self, size=24):
        """获取字体"""
        # 优先返回中文字体
        if f'chinese_{size}' in self.fonts:
            return self.fonts[f'chinese_{size}']
        elif f'default_{size}' in self.fonts:
            return self.fonts[f'default_{size}']
        else:
            # 最后的备用方案
            return pygame.font.Font(None, size)
    
    def render_text(self, text, size=24, color=(255, 255, 255)):
        """渲染文本，自动处理中文"""
        font = self.get_font(size)
        try:
            return font.render(text, True, color)
        except:
            # 如果渲染失败，尝试用英文替代
            fallback_text = self._get_fallback_text(text)
            return font.render(fallback_text, True, color)
    
    def _get_fallback_text(self, text):
        """获取英文替代文本"""
        fallback_map = {
            "🌆 Echopolis": "Echopolis",
            "回声都市": "Echo City",
            "AI驱动的金融模拟器": "AI Financial Simulator",
            "🎮 开始游戏": "Start Game",
            "👥 多人模式": "Multiplayer",
            "⚙️ 设置": "Settings", 
            "❌ 退出": "Exit",
            "创建AI化身": "Create AI Avatar",
            "选择MBTI人格类型:": "Select MBTI Type:",
            "输入化身名字:": "Enter Avatar Name:",
            "🌐 多人模式已启用": "Multiplayer Enabled",
            "中央银行": "Central Bank",
            "金融中心": "Financial Center",
            "住宅区": "Residential",
            "交易市场": "Market",
            "商学院": "Business School",
        }
        
        for chinese, english in fallback_map.items():
            if chinese in text:
                return text.replace(chinese, english)
        
        # 如果没有找到映射，返回原文本
        return text

# 全局字体管理器实例
font_manager = FontManager()
"""
基础场景类
"""
import pygame
from abc import ABC, abstractmethod
from ..font_manager import font_manager

class BaseScene(ABC):
    def __init__(self, game_window):
        self.game_window = game_window
        self.font_manager = font_manager
    
    @abstractmethod
    def handle_event(self, event):
        pass
    
    @abstractmethod
    def update(self, dt):
        pass
    
    @abstractmethod
    def render(self, screen):
        pass
    
    def on_enter(self, **kwargs):
        """进入场景时调用"""
        pass
    
    def draw_text(self, screen, text, pos, color=(255, 255, 255), size=24):
        """绘制文本"""
        text_surface = self.font_manager.render_text(text, size, color)
        screen.blit(text_surface, pos)
        return text_surface.get_rect(topleft=pos)
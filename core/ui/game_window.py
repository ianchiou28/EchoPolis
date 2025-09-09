"""
游戏主窗口管理器
"""
import pygame
import sys
from typing import Dict, Any
from .scenes.main_scene import MainScene
from .scenes.avatar_creation_scene import AvatarCreationScene
from .scenes.game_scene import GameScene

class GameWindow:
    def __init__(self, width=1024, height=768):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("🌆 Echopolis - 回声都市")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 场景管理
        self.scenes = {
            'main': MainScene(self),
            'avatar_creation': AvatarCreationScene(self),
            'game': GameScene(self)
        }
        self.current_scene = 'main'
        
        # 游戏状态
        self.game_state = {
            'avatar': None,
            'multiplayer_ready': False,
            'players': []
        }
    
    def switch_scene(self, scene_name: str, **kwargs):
        """切换场景"""
        if scene_name in self.scenes:
            self.current_scene = scene_name
            self.scenes[scene_name].on_enter(**kwargs)
    
    def run(self):
        """主游戏循环"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scenes[self.current_scene].handle_event(event)
            
            # 更新
            self.scenes[self.current_scene].update(dt)
            
            # 渲染
            self.screen.fill((20, 25, 40))  # 深蓝色背景
            self.scenes[self.current_scene].render(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
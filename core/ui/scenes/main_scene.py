"""
主菜单场景
"""
import pygame
from .base_scene import BaseScene

class MainScene(BaseScene):
    def __init__(self, game_window):
        super().__init__(game_window)
        self.menu_items = [
            "🎮 开始游戏",
            "👥 多人模式", 
            "⚙️ 设置",
            "❌ 退出"
        ]
        self.selected_item = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                self._handle_menu_selection()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, item_rect in enumerate(self.menu_rects):
                if item_rect.collidepoint(mouse_pos):
                    self.selected_item = i
                    self._handle_menu_selection()
    
    def _handle_menu_selection(self):
        if self.selected_item == 0:  # 开始游戏
            self.game_window.switch_scene('avatar_creation')
        elif self.selected_item == 1:  # 多人模式
            self.game_window.game_state['multiplayer_ready'] = True
            self.game_window.switch_scene('avatar_creation')
        elif self.selected_item == 3:  # 退出
            self.game_window.running = False
    
    def update(self, dt):
        pass
    
    def render(self, screen):
        # 标题
        title_rect = self.draw_text(screen, "🌆 Echopolis", 
                                  (screen.get_width()//2 - 150, 100), 
                                  (100, 200, 255), 48)
        
        subtitle_rect = self.draw_text(screen, "回声都市 - AI驱动的金融模拟器", 
                                     (screen.get_width()//2 - 200, 160), 
                                     (150, 150, 150), 24)
        
        # 菜单项
        self.menu_rects = []
        start_y = 300
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 100) if i == self.selected_item else (200, 200, 200)
            rect = self.draw_text(screen, item, 
                                (screen.get_width()//2 - 100, start_y + i * 60), 
                                color, 24)
            self.menu_rects.append(rect)
        
        # 底部信息
        self.draw_text(screen, "使用 ↑↓ 键选择，回车确认", 
                      (screen.get_width()//2 - 150, screen.get_height() - 50), 
                      (100, 100, 100), 20)
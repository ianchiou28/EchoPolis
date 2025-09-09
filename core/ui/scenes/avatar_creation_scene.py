"""
AI化身创建场景
"""
import pygame
import random
from .base_scene import BaseScene
from ...systems.mbti_traits import MBTI_TYPES
from ...systems.fate_wheel import FATE_WHEEL
from ..simple_avatar import SimpleAvatar

class AvatarCreationScene(BaseScene):
    def __init__(self, game_window):
        super().__init__(game_window)
        self.mbti_types = list(MBTI_TYPES.keys())
        self.selected_mbti = 0
        self.avatar_name = ""
        self.input_active = False
        self.fate_result = None
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self._create_avatar()
                elif event.key == pygame.K_BACKSPACE:
                    self.avatar_name = self.avatar_name[:-1]
                elif event.unicode.isprintable():
                    self.avatar_name += event.unicode
            else:
                if event.key == pygame.K_LEFT:
                    self.selected_mbti = (self.selected_mbti - 1) % len(self.mbti_types)
                elif event.key == pygame.K_RIGHT:
                    self.selected_mbti = (self.selected_mbti + 1) % len(self.mbti_types)
                elif event.key == pygame.K_RETURN:
                    self.input_active = True
                elif event.key == pygame.K_ESCAPE:
                    self.game_window.switch_scene('main')
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # 检查MBTI选择区域点击
            if hasattr(self, 'mbti_rects'):
                for i, rect in enumerate(self.mbti_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_mbti = i
            
            # 检查输入框点击
            if hasattr(self, 'name_input_rect') and self.name_input_rect.collidepoint(mouse_pos):
                self.input_active = True
    
    def _create_avatar(self):
        if self.avatar_name.strip():
            try:
                # 创建简化AI化身
                mbti_type = self.mbti_types[self.selected_mbti]
                avatar = SimpleAvatar(self.avatar_name.strip(), mbti_type)
                
                # 命运轮盘
                self.fate_result = random.choice(list(FATE_WHEEL.keys()))
                avatar.set_fate(self.fate_result)
                
                self.game_window.game_state['avatar'] = avatar
                self.game_window.switch_scene('game')
            except Exception as e:
                print(f"Error creating avatar: {e}")
                # 如果创建失败，显示错误信息但不崩溃
                self.avatar_name = f"Error: {str(e)}"
    
    def update(self, dt):
        pass
    
    def render(self, screen):
        # 标题
        self.draw_text(screen, "创建AI化身", (50, 50), (255, 255, 255), 48)
        
        # MBTI选择
        self.draw_text(screen, "选择MBTI人格类型:", (50, 120), (200, 200, 200), 24)
        
        self.mbti_rects = []
        start_x, start_y = 50, 160
        cols = 4
        for i, mbti in enumerate(self.mbti_types):
            x = start_x + (i % cols) * 200
            y = start_y + (i // cols) * 80
            
            color = (255, 255, 100) if i == self.selected_mbti else (150, 150, 150)
            rect = self.draw_text(screen, mbti, (x, y), color, 24)
            
            # 显示人格描述
            if i == self.selected_mbti:
                desc = MBTI_TYPES[mbti]['description'][:50] + "..."
                self.draw_text(screen, desc, (x, y + 25), (100, 200, 100), 16)
            
            self.mbti_rects.append(rect)
        
        # 名字输入
        self.draw_text(screen, "输入化身名字:", (50, 400), (200, 200, 200), 24)
        
        # 输入框
        input_color = (255, 255, 255) if self.input_active else (150, 150, 150)
        self.name_input_rect = pygame.Rect(50, 440, 300, 30)
        pygame.draw.rect(screen, (50, 50, 50), self.name_input_rect)
        pygame.draw.rect(screen, input_color, self.name_input_rect, 2)
        
        display_name = self.avatar_name + ("|" if self.input_active else "")
        self.draw_text(screen, display_name, (55, 445), (255, 255, 255), 20)
        
        # 操作提示
        self.draw_text(screen, "← → 选择MBTI类型", (50, 500), (100, 100, 100), 16)
        self.draw_text(screen, "点击输入框输入名字，回车创建", (50, 530), (100, 100, 100), 16)
        self.draw_text(screen, "ESC 返回主菜单", (50, 560), (100, 100, 100), 16)
        
        # 多人模式提示
        if self.game_window.game_state.get('multiplayer_ready'):
            self.draw_text(screen, "🌐 多人模式已启用", (screen.get_width() - 200, 50), (100, 255, 100), 20)
        
        # 显示命运结果
        if self.fate_result:
            self.draw_text(screen, f"命运结果: {self.fate_result}", (50, 600), (255, 255, 100), 18)
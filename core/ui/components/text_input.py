"""
文本输入组件
"""
import pygame

class TextInput:
    def __init__(self, x, y, width, height, placeholder="", font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.font = font or pygame.font.Font(None, 24)
        self.is_active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable():
                self.text += event.unicode
    
    def update(self, dt):
        # 光标闪烁
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def render(self, screen):
        # 输入框背景
        color = (80, 80, 80) if self.is_active else (50, 50, 50)
        pygame.draw.rect(screen, color, self.rect)
        
        border_color = (150, 200, 255) if self.is_active else (100, 100, 100)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # 文本内容
        display_text = self.text if self.text else self.placeholder
        text_color = (255, 255, 255) if self.text else (150, 150, 150)
        
        if self.is_active and self.cursor_visible and self.text:
            display_text += "|"
        
        text_surface = self.font.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
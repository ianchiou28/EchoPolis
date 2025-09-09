"""
按钮组件
"""
import pygame

class Button:
    def __init__(self, x, y, width, height, text, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font or pygame.font.Font(None, 24)
        self.is_hovered = False
        self.is_pressed = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
        return False
    
    def render(self, screen):
        # 按钮背景
        if self.is_pressed:
            color = (100, 100, 150)
        elif self.is_hovered:
            color = (80, 80, 120)
        else:
            color = (60, 60, 100)
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        # 按钮文字
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
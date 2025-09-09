"""
面板组件
"""
import pygame

class Panel:
    def __init__(self, x, y, width, height, title="", alpha=180):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.alpha = alpha
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
    def render(self, screen):
        # 创建半透明表面
        panel_surface = pygame.Surface((self.rect.width, self.rect.height))
        panel_surface.set_alpha(self.alpha)
        panel_surface.fill((20, 25, 40))
        
        screen.blit(panel_surface, self.rect.topleft)
        
        # 边框
        pygame.draw.rect(screen, (100, 150, 200), self.rect, 2)
        
        # 标题
        if self.title:
            title_surface = self.title_font.render(self.title, True, (255, 255, 255))
            screen.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))
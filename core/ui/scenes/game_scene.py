"""
主游戏场景 - 包含地图和游戏界面
"""
import pygame
import math
from .base_scene import BaseScene

class GameScene(BaseScene):
    def __init__(self, game_window):
        super().__init__(game_window)
        self.camera_x = 0
        self.camera_y = 0
        self.map_width = 2000
        self.map_height = 1500
        
        # UI面板
        self.show_status = True
        self.show_chat = False
        self.chat_input = ""
        self.chat_active = False
        
        # 地图建筑
        self.buildings = [
            {'type': 'bank', 'pos': (400, 300), 'size': (80, 60), 'name': '中央银行'},
            {'type': 'office', 'pos': (600, 200), 'size': (100, 80), 'name': '金融中心'},
            {'type': 'house', 'pos': (200, 400), 'size': (60, 60), 'name': '住宅区'},
            {'type': 'market', 'pos': (800, 350), 'size': (120, 90), 'name': '交易市场'},
            {'type': 'school', 'pos': (300, 600), 'size': (90, 70), 'name': '商学院'},
        ]
        
        # 玩家位置
        self.player_pos = [500, 400]
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.chat_active:
                if event.key == pygame.K_RETURN:
                    self._send_echo()
                elif event.key == pygame.K_ESCAPE:
                    self.chat_active = False
                    self.chat_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]
                elif event.unicode.isprintable():
                    self.chat_input += event.unicode
            else:
                # 移动控制
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.player_pos[1] -= 20
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.player_pos[1] += 20
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.player_pos[0] -= 20
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.player_pos[0] += 20
                
                # UI控制
                elif event.key == pygame.K_TAB:
                    self.show_status = not self.show_status
                elif event.key == pygame.K_RETURN:
                    self.chat_active = True
                    self.show_chat = True
                elif event.key == pygame.K_SPACE:
                    self._interact_with_building()
                elif event.key == pygame.K_ESCAPE:
                    self.game_window.switch_scene('main')
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                mouse_pos = pygame.mouse.get_pos()
                # 检查建筑点击
                for building in self.buildings:
                    building_rect = pygame.Rect(
                        building['pos'][0] - self.camera_x,
                        building['pos'][1] - self.camera_y,
                        building['size'][0],
                        building['size'][1]
                    )
                    if building_rect.collidepoint(mouse_pos):
                        self._interact_with_building(building)
    
    def _send_echo(self):
        """发送回响给AI"""
        if self.chat_input.strip():
            avatar = self.game_window.game_state['avatar']
            if avatar:
                # 这里调用回响系统
                print(f"发送回响: {self.chat_input}")
                # TODO: 集成回响系统
            self.chat_input = ""
            self.chat_active = False
    
    def _interact_with_building(self, building=None):
        """与建筑互动"""
        if not building:
            # 检查玩家附近的建筑
            for b in self.buildings:
                distance = math.sqrt((self.player_pos[0] - b['pos'][0])**2 + 
                                   (self.player_pos[1] - b['pos'][1])**2)
                if distance < 100:
                    building = b
                    break
        
        if building:
            print(f"与 {building['name']} 互动")
            # TODO: 实现建筑功能
    
    def update(self, dt):
        # 更新摄像机位置（跟随玩家）
        target_camera_x = self.player_pos[0] - self.game_window.width // 2
        target_camera_y = self.player_pos[1] - self.game_window.height // 2
        
        self.camera_x += (target_camera_x - self.camera_x) * 0.1
        self.camera_y += (target_camera_y - self.camera_y) * 0.1
        
        # 限制摄像机范围
        self.camera_x = max(0, min(self.camera_x, self.map_width - self.game_window.width))
        self.camera_y = max(0, min(self.camera_y, self.map_height - self.game_window.height))
    
    def render(self, screen):
        # 绘制地图背景
        self._draw_map(screen)
        
        # 绘制建筑
        self._draw_buildings(screen)
        
        # 绘制玩家
        self._draw_player(screen)
        
        # 绘制UI
        if self.show_status:
            self._draw_status_panel(screen)
        
        if self.show_chat:
            self._draw_chat_panel(screen)
        
        # 绘制控制提示
        self._draw_controls(screen)
    
    def _draw_map(self, screen):
        """绘制地图背景"""
        # 简单的网格背景
        grid_size = 50
        for x in range(0, self.game_window.width + grid_size, grid_size):
            pygame.draw.line(screen, (30, 35, 50), 
                           (x - int(self.camera_x) % grid_size, 0), 
                           (x - int(self.camera_x) % grid_size, self.game_window.height))
        
        for y in range(0, self.game_window.height + grid_size, grid_size):
            pygame.draw.line(screen, (30, 35, 50), 
                           (0, y - int(self.camera_y) % grid_size), 
                           (self.game_window.width, y - int(self.camera_y) % grid_size))
    
    def _draw_buildings(self, screen):
        """绘制建筑"""
        colors = {
            'bank': (100, 150, 255),
            'office': (150, 150, 150),
            'house': (100, 255, 100),
            'market': (255, 150, 100),
            'school': (255, 255, 100)
        }
        
        for building in self.buildings:
            x = building['pos'][0] - self.camera_x
            y = building['pos'][1] - self.camera_y
            
            # 只绘制在屏幕内的建筑
            if -100 < x < self.game_window.width + 100 and -100 < y < self.game_window.height + 100:
                color = colors.get(building['type'], (100, 100, 100))
                pygame.draw.rect(screen, color, 
                               (x, y, building['size'][0], building['size'][1]))
                pygame.draw.rect(screen, (255, 255, 255), 
                               (x, y, building['size'][0], building['size'][1]), 2)
                
                # 建筑名称
                self.draw_text(screen, building['name'], (x, y - 20), (255, 255, 255), 16)
    
    def _draw_player(self, screen):
        """绘制玩家"""
        player_screen_x = self.player_pos[0] - self.camera_x
        player_screen_y = self.player_pos[1] - self.camera_y
        
        # 玩家角色（简单的圆形）
        pygame.draw.circle(screen, (255, 100, 100), 
                         (int(player_screen_x), int(player_screen_y)), 15)
        pygame.draw.circle(screen, (255, 255, 255), 
                         (int(player_screen_x), int(player_screen_y)), 15, 2)
        
        # 玩家名字
        avatar = self.game_window.game_state.get('avatar')
        if avatar:
            self.draw_text(screen, avatar.name, 
                         (player_screen_x - 20, player_screen_y - 35), 
                         (255, 255, 255), 16)
    
    def _draw_status_panel(self, screen):
        """绘制状态面板"""
        avatar = self.game_window.game_state.get('avatar')
        if not avatar:
            return
        
        panel_rect = pygame.Rect(10, 10, 300, 200)
        pygame.draw.rect(screen, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(screen, (100, 100, 100), panel_rect, 2)
        
        y_offset = 20
        self.draw_text(screen, f"🤖 {avatar.name} ({avatar.mbti_type})", (20, y_offset), (255, 255, 255), 18)
        y_offset += 25
        self.draw_text(screen, f"💰 资产: {avatar.assets:,} CP", (20, y_offset), (255, 255, 255), 16)
        y_offset += 25
        self.draw_text(screen, f"❤️ 健康: {avatar.health}/100", (20, y_offset), (255, 255, 255), 16)
        y_offset += 25
        self.draw_text(screen, f"⚡ 精力: {avatar.energy}/100", (20, y_offset), (255, 255, 255), 16)
        y_offset += 25
        self.draw_text(screen, f"😊 幸福: {avatar.happiness}/100", (20, y_offset), (255, 255, 255), 16)
        y_offset += 25
        self.draw_text(screen, f"📅 回合: {avatar.round_count}", (20, y_offset), (255, 255, 255), 16)
        y_offset += 25
        if avatar.fate_type:
            self.draw_text(screen, f"🎲 命运: {avatar.fate_type}", (20, y_offset), (255, 255, 100), 14)
    
    def _draw_chat_panel(self, screen):
        """绘制聊天面板"""
        if not self.chat_active:
            return
        
        panel_rect = pygame.Rect(50, self.game_window.height - 150, 
                               self.game_window.width - 100, 100)
        pygame.draw.rect(screen, (0, 0, 0, 200), panel_rect)
        pygame.draw.rect(screen, (100, 150, 255), panel_rect, 2)
        
        self.draw_text(screen, "💭 发送回响给AI:", (60, self.game_window.height - 140), (255, 255, 255), 18)
        
        # 输入框
        input_rect = pygame.Rect(60, self.game_window.height - 110, 
                               self.game_window.width - 140, 30)
        pygame.draw.rect(screen, (50, 50, 50), input_rect)
        pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)
        
        display_text = self.chat_input + "|"
        self.draw_text(screen, display_text, (65, self.game_window.height - 105), (255, 255, 255), 16)
        
        self.draw_text(screen, "回车发送，ESC取消", (60, self.game_window.height - 75), (150, 150, 150), 14)
    
    def _draw_controls(self, screen):
        """绘制控制提示"""
        controls = [
            "WASD/方向键: 移动",
            "空格: 互动",
            "回车: 发送回响",
            "TAB: 切换状态面板",
            "ESC: 返回菜单"
        ]
        
        for i, control in enumerate(controls):
            self.draw_text(screen, control, 
                         (self.game_window.width - 200, 10 + i * 20), 
                         (100, 100, 100), 14)
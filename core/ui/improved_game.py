"""
改进的游戏引擎 - 使用Arcade框架
"""
import arcade
import random
from typing import Dict, List, Optional
from ..systems.mbti_traits import MBTI_TYPES
from ..systems.fate_wheel import FATE_WHEEL
from .simple_avatar import SimpleAvatar

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "🌆 Echopolis - 回声都市"

class EchopolisGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        
        # 游戏状态
        self.current_scene = "menu"
        self.avatar = None
        self.selected_menu = 0
        self.selected_mbti = 0
        self.avatar_name = ""
        self.input_active = False
        
        # 菜单选项
        self.menu_items = ["🎮 开始游戏", "👥 多人模式", "⚙️ 设置", "❌ 退出"]
        self.mbti_types = list(MBTI_TYPES.keys())
        
        # 游戏世界
        self.player_x = 400
        self.player_y = 300
        self.buildings = [
            {"name": "中央银行", "x": 200, "y": 200, "width": 80, "height": 60},
            {"name": "金融中心", "x": 400, "y": 150, "width": 100, "height": 80},
            {"name": "住宅区", "x": 600, "y": 250, "width": 60, "height": 60},
        ]
    
    def on_draw(self):
        self.clear()
        
        if self.current_scene == "menu":
            self.draw_menu()
        elif self.current_scene == "create_avatar":
            self.draw_avatar_creation()
        elif self.current_scene == "game":
            self.draw_game()
    
    def draw_menu(self):
        # 标题
        arcade.draw_text("🌆 Echopolis", SCREEN_WIDTH//2 - 150, 500, 
                        arcade.color.CYAN, 48, anchor_x="left")
        arcade.draw_text("回声都市 - AI金融模拟器", SCREEN_WIDTH//2 - 200, 450, 
                        arcade.color.LIGHT_GRAY, 20, anchor_x="left")
        
        # 菜单项
        for i, item in enumerate(self.menu_items):
            color = arcade.color.YELLOW if i == self.selected_menu else arcade.color.WHITE
            arcade.draw_text(item, SCREEN_WIDTH//2 - 100, 350 - i*50, 
                           color, 24, anchor_x="left")
    
    def draw_avatar_creation(self):
        # 标题
        arcade.draw_text("创建AI化身", 50, 650, arcade.color.WHITE, 32)
        
        # MBTI选择
        arcade.draw_text("选择MBTI类型:", 50, 600, arcade.color.LIGHT_GRAY, 20)
        
        for i, mbti in enumerate(self.mbti_types[:8]):  # 只显示前8个
            x = 50 + (i % 4) * 200
            y = 550 - (i // 4) * 40
            color = arcade.color.YELLOW if i == self.selected_mbti else arcade.color.LIGHT_GRAY
            arcade.draw_text(mbti, x, y, color, 18)
        
        # 名字输入
        arcade.draw_text("输入名字:", 50, 400, arcade.color.LIGHT_GRAY, 20)
        arcade.draw_rectangle_outline(200, 370, 200, 30, arcade.color.WHITE)
        arcade.draw_text(self.avatar_name + ("|" if self.input_active else ""), 
                        110, 365, arcade.color.WHITE, 16)
        
        # 提示
        arcade.draw_text("方向键选择MBTI，点击输入框输入名字，回车创建", 
                        50, 300, arcade.color.GRAY, 14)
    
    def draw_game(self):
        if not self.avatar:
            return
            
        # 绘制地图网格
        for x in range(0, SCREEN_WIDTH, 50):
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.DARK_GRAY, 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.DARK_GRAY, 1)
        
        # 绘制建筑
        for building in self.buildings:
            arcade.draw_rectangle_filled(building["x"], building["y"], 
                                       building["width"], building["height"], 
                                       arcade.color.BLUE)
            arcade.draw_text(building["name"], building["x"] - 30, building["y"] + 40, 
                           arcade.color.WHITE, 12)
        
        # 绘制玩家
        arcade.draw_circle_filled(self.player_x, self.player_y, 15, arcade.color.RED)
        arcade.draw_text(self.avatar.name, self.player_x - 20, self.player_y + 25, 
                        arcade.color.WHITE, 12)
        
        # 状态面板
        self.draw_status_panel()
    
    def draw_status_panel(self):
        # 背景
        arcade.draw_rectangle_filled(150, SCREEN_HEIGHT - 100, 280, 180, 
                                   arcade.color.BLACK + (200,))
        arcade.draw_rectangle_outline(150, SCREEN_HEIGHT - 100, 280, 180, 
                                    arcade.color.WHITE, 2)
        
        # 状态信息
        y_start = SCREEN_HEIGHT - 40
        arcade.draw_text(f"🤖 {self.avatar.name} ({self.avatar.mbti_type})", 
                        20, y_start, arcade.color.WHITE, 14)
        arcade.draw_text(f"💰 资产: {self.avatar.assets:,} CP", 
                        20, y_start - 25, arcade.color.WHITE, 12)
        arcade.draw_text(f"❤️ 健康: {self.avatar.health}/100", 
                        20, y_start - 45, arcade.color.WHITE, 12)
        arcade.draw_text(f"⚡ 精力: {self.avatar.energy}/100", 
                        20, y_start - 65, arcade.color.WHITE, 12)
        arcade.draw_text(f"😊 幸福: {self.avatar.happiness}/100", 
                        20, y_start - 85, arcade.color.WHITE, 12)
        
        if self.avatar.fate_type:
            arcade.draw_text(f"🎲 {self.avatar.fate_type}", 
                            20, y_start - 105, arcade.color.YELLOW, 10)
    
    def on_key_press(self, key, modifiers):
        if self.current_scene == "menu":
            if key == arcade.key.UP:
                self.selected_menu = (self.selected_menu - 1) % len(self.menu_items)
            elif key == arcade.key.DOWN:
                self.selected_menu = (self.selected_menu + 1) % len(self.menu_items)
            elif key == arcade.key.ENTER:
                if self.selected_menu == 0:  # 开始游戏
                    self.current_scene = "create_avatar"
                elif self.selected_menu == 3:  # 退出
                    self.close()
        
        elif self.current_scene == "create_avatar":
            if self.input_active:
                if key == arcade.key.ENTER:
                    self.create_avatar()
                elif key == arcade.key.BACKSPACE:
                    self.avatar_name = self.avatar_name[:-1]
                elif key == arcade.key.ESCAPE:
                    self.input_active = False
            else:
                if key == arcade.key.LEFT:
                    self.selected_mbti = (self.selected_mbti - 1) % len(self.mbti_types)
                elif key == arcade.key.RIGHT:
                    self.selected_mbti = (self.selected_mbti + 1) % len(self.mbti_types)
                elif key == arcade.key.ENTER:
                    self.input_active = True
                elif key == arcade.key.ESCAPE:
                    self.current_scene = "menu"
        
        elif self.current_scene == "game":
            if key == arcade.key.W:
                self.player_y = min(SCREEN_HEIGHT - 20, self.player_y + 20)
            elif key == arcade.key.S:
                self.player_y = max(20, self.player_y - 20)
            elif key == arcade.key.A:
                self.player_x = max(20, self.player_x - 20)
            elif key == arcade.key.D:
                self.player_x = min(SCREEN_WIDTH - 20, self.player_x + 20)
            elif key == arcade.key.ESCAPE:
                self.current_scene = "menu"
    
    def on_key_release(self, key, modifiers):
        pass
    
    def on_text(self, text):
        if self.current_scene == "create_avatar" and self.input_active:
            if text.isprintable() and len(self.avatar_name) < 20:
                self.avatar_name += text
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.current_scene == "create_avatar":
            # 检查输入框点击
            if 100 < x < 300 and 355 < y < 385:
                self.input_active = True
    
    def create_avatar(self):
        if self.avatar_name.strip():
            try:
                mbti_type = self.mbti_types[self.selected_mbti]
                self.avatar = SimpleAvatar(self.avatar_name.strip(), mbti_type)
                
                # 随机命运
                fate_key = random.choice(list(FATE_WHEEL.keys()))
                self.avatar.set_fate(fate_key)
                
                self.current_scene = "game"
                print(f"Created avatar: {self.avatar.name} ({mbti_type}) - {fate_key}")
            except Exception as e:
                print(f"Error creating avatar: {e}")

def main():
    game = EchopolisGame()
    arcade.run()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
简化的GUI启动器 - 用于测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("Starting Echopolis GUI...")
    
    try:
        from core.ui.game_window import GameWindow
        print("GUI modules loaded successfully")
        
        # 创建游戏窗口
        game = GameWindow(1024, 768)
        print("Game window created")
        
        # 启动游戏循环
        print("Starting game loop...")
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
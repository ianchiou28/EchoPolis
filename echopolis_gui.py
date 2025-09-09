#!/usr/bin/env python3
"""
Echopolis GUI版本启动器
像素风格的AI驱动金融模拟游戏
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动游戏"""
    print("Starting Echopolis GUI...")
    print("Pixel-style AI Financial Simulator")
    print("=" * 50)
    
    # 检查可用的游戏引擎
    print("\nAvailable game engines:")
    print("1. Pygame (current) - Basic 2D graphics")
    print("2. Arcade (improved) - Better performance and features")
    
    choice = input("\nSelect engine (1/2, default=1): ").strip() or "1"
    
    try:
        if choice == "2":
            try:
                import arcade
                from core.ui.improved_game import main as arcade_main
                print("Starting Arcade version...")
                arcade_main()
            except ImportError:
                print("Arcade not installed. Install with: pip install arcade")
                print("Falling back to Pygame version...")
                start_pygame_version()
        else:
            start_pygame_version()
    except KeyboardInterrupt:
        print("\nGame exited")
    except Exception as e:
        print(f"Game startup failed: {e}")
        import traceback
        traceback.print_exc()

def start_pygame_version():
    """启动Pygame版本"""
    try:
        from core.ui.game_window import GameWindow
        game = GameWindow(1024, 768)
        game.run()
    except Exception as e:
        print(f"Pygame version failed: {e}")
        raise

if __name__ == "__main__":
    main()
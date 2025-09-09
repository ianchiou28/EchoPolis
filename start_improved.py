#!/usr/bin/env python3
"""
改进版Echopolis启动器 - 使用Arcade引擎
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("Echopolis - Improved Version")
    print("Using Arcade Game Engine")
    print("=" * 40)
    
    try:
        import arcade
        print("[OK] Arcade engine loaded")
        
        from core.ui.improved_game import main as game_main
        game_main()
        
    except ImportError:
        print("[ERROR] Arcade not installed")
        print("Install with: pip install arcade")
        print("Or run: pip install -r requirements_improved.txt")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
GUI系统测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_import():
    """测试GUI模块导入"""
    try:
        from core.ui.game_window import GameWindow
        from core.ui.scenes.main_scene import MainScene
        from core.ui.scenes.avatar_creation_scene import AvatarCreationScene
        from core.ui.scenes.game_scene import GameScene
        print("[OK] GUI modules imported successfully")
        return True
    except Exception as e:
        print(f"[ERROR] GUI module import failed: {e}")
        return False

def test_pygame():
    """测试pygame"""
    try:
        import pygame
        pygame.init()
        print("[OK] Pygame initialized successfully")
        pygame.quit()
        return True
    except Exception as e:
        print(f"[ERROR] Pygame test failed: {e}")
        return False

def main():
    print("Echopolis GUI System Test")
    print("=" * 40)
    
    tests = [
        ("Pygame Test", test_pygame),
        ("GUI Module Import Test", test_gui_import),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n[TEST] {name}...")
        if test_func():
            passed += 1
    
    print(f"\n[RESULT] Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("[SUCCESS] All tests passed! You can start the GUI version")
        print("Run command: python echopolis_gui.py")
    else:
        print("[WARNING] Some tests failed, please check dependencies")

if __name__ == "__main__":
    main()
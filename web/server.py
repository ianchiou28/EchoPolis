#!/usr/bin/env python3
"""
Echopolis Web服务器 - 提供AI后端服务
"""
import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.avatar.ai_avatar import AIAvatar
    from core.systems.mbti_traits import MBTIType
    ai_avatar_available = True
except ImportError:
    print("Warning: AI Avatar system not available, using mock responses")
    ai_avatar_available = False

class EchopolisHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="web", **kwargs)
    
    def do_POST(self):
        if self.path == '/api/generate_situation':
            self.handle_generate_situation()
        elif self.path == '/api/make_decision':
            self.handle_make_decision()
        else:
            self.send_error(404)
    
    def handle_generate_situation(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        if ai_avatar_available:
            try:
                # 创建临时AI化身来生成情况
                mbti_str = data.get('mbti', 'INTP')
                mbti_type = getattr(MBTIType, mbti_str, MBTIType.INTP)
                temp_avatar = AIAvatar(data.get('name', '化身'), mbti_type)
                
                # 设置化身状态
                temp_avatar.attributes.credits = data.get('assets', 50000)
                temp_avatar.attributes.health = data.get('health', 100)
                temp_avatar.attributes.happiness = data.get('happiness', 50)
                temp_avatar.attributes.stress = data.get('stress', 0)
                
                # 生成AI情况
                situation_context = temp_avatar.generate_situation()
                if situation_context:
                    result = {
                        "success": True,
                        "situation": situation_context.situation,
                        "options": situation_context.options,
                        "context_type": situation_context.context_type
                    }
                else:
                    result = self._get_mock_situation(data)
            except Exception as e:
                print(f"AI generation failed: {e}")
                result = self._get_mock_situation(data)
        else:
            result = self._get_mock_situation(data)
        
        self.send_json_response(result)
    
    def handle_make_decision(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        if ai_avatar_available:
            try:
                avatar_context = data.get('avatar_context', {})
                mbti_str = avatar_context.get('mbti', 'INTP')
                mbti_type = getattr(MBTIType, mbti_str, MBTIType.INTP)
                temp_avatar = AIAvatar(avatar_context.get('name', '化身'), mbti_type)
                
                situation_data = data.get('situation', {})
                from core.avatar.ai_avatar import DecisionContext
                temp_avatar.current_situation = DecisionContext(
                    situation_data.get('situation', ''),
                    situation_data.get('options', []),
                    situation_data.get('context_type', 'general')
                )
                
                temp_avatar.attributes.credits = avatar_context.get('assets', 50000)
                temp_avatar.attributes.trust_level = avatar_context.get('trust', 50)
                
                decision_result = temp_avatar.make_decision(data.get('player_echo'))
                
                result = {
                    "success": True,
                    "chosen_option": decision_result.get('chosen_option', ''),
                    "ai_thoughts": decision_result.get('ai_thoughts', ''),
                    "trust_change": decision_result.get('trust_change', 0)
                }
            except Exception as e:
                print(f"AI decision failed: {e}")
                result = self._get_mock_decision(data)
        else:
            result = self._get_mock_decision(data)
        
        self.send_json_response(result)
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _get_mock_situation(self, data):
        context_type = data.get('contextType', 'general')
        situations = {
            'banking': {
                "situation": f"作为{data.get('mbti', 'INTP')}类型的{data.get('name', '化身')}，银行经理向你推荐了一款新的理财产品...",
                "options": ["购买50万CP理财产品", "申请贷款扩大投资", "仅咨询不购买"]
            },
            'investment': {
                "situation": f"在金融中心，{data.get('name', '化身')}发现了一个热门的AI科技股...",
                "options": ["投资100万CP到AI科技股", "购买混合基金分散风险", "观望市场走势"]
            },
            'general': {
                "situation": f"{data.get('name', '化身')}，你的朋友邀请你参与一个创业项目...",
                "options": ["投资80万CP支持朋友", "小额投资20万CP试水", "礼貌拒绝"]
            }
        }
        
        situation_data = situations.get(context_type, situations['general'])
        return {
            "success": True,
            "situation": situation_data["situation"],
            "options": situation_data["options"],
            "context_type": context_type
        }
    
    def _get_mock_decision(self, data):
        options = data.get('situation', {}).get('options', ['选项1', '选项2', '选项3'])
        chosen = options[0] if options else "默认选择"
        return {
            "success": True,
            "chosen_option": chosen,
            "ai_thoughts": f"我选择了{chosen}，这是基于当前情况的最佳决策。",
            "trust_change": 2
        }

def start_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, EchopolisHandler)
    print(f"🌐 Echopolis Web服务器启动")
    print(f"📍 访问地址: http://localhost:{port}")
    print(f"🎮 游戏地址: http://localhost:{port}/index.html")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.shutdown()

if __name__ == "__main__":
    start_server()
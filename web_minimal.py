"""
Echopolis Web API服务器
集成核心游戏系统和AI引擎
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import random

# 尝试导入核心游戏系统
try:
    from core.avatar.ai_avatar import AIAvatar
    from core.systems.mbti_traits import MBTITraits
    from core.systems.fate_wheel import FateWheel
    from core.systems.echo_system import EchoSystem
    from core.ai.deepseek_engine import DeepSeekEngine
    AI_AVAILABLE = True
    print("[OK] AI modules loaded successfully")
except ImportError as e:
    print(f"[WARN] AI modules not available: {e}")
    AI_AVAILABLE = False

app = FastAPI(title="Echopolis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 游戏会话存储
game_sessions = {}

# 初始化AI引擎
ai_engine = None
try:
    # 尝试从config.json读取API key
    import json
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('deepseek_api_key')
            if api_key and api_key != 'sk-your-api-key-here':
                ai_engine = DeepSeekEngine(api_key)
                AI_AVAILABLE = True
                print("[OK] AI Engine initialized with API key")
            else:
                print("[WARN] No valid API key found in config.json")
                AI_AVAILABLE = False
    except FileNotFoundError:
        print("[WARN] config.json not found")
        AI_AVAILABLE = False
except Exception as e:
    print(f"[ERROR] AI Engine failed to initialize: {e}")
    AI_AVAILABLE = False
    ai_engine = None

class CreateAvatarRequest(BaseModel):
    name: str
    mbti: str
    session_id: str

class GenerateSituationRequest(BaseModel):
    session_id: str
    context: str = ""

class EchoRequest(BaseModel):
    session_id: str
    echo_text: str

class AutoDecisionRequest(BaseModel):
    session_id: str

@app.get("/")
async def root():
    return {"message": "🌆 Echopolis API Server", "version": "1.0.0", "ai_available": AI_AVAILABLE}

@app.get("/api/mbti-types")
async def get_mbti_types():
    if AI_AVAILABLE:
        return MBTITraits.get_all_types()
    else:
        return {
            "INTP": {"description": "逻辑学家 - 创新的发明家"},
            "ENTJ": {"description": "指挥官 - 大胆的领导者"},
            "ISFJ": {"description": "守护者 - 温暖的保护者"},
            "ESFP": {"description": "表演者 - 自发的娱乐者"}
        }

@app.post("/api/create-avatar")
async def create_avatar(request: CreateAvatarRequest):
    try:
        fates = ['💰 亿万富豪', '📚 书香门第', '💔 家道中落', '💰 低收入户']
        fate_name = random.choice(fates)
        credits_map = {'💰 亿万富豪': 100000000, '📚 书香门第': 1000000, '💔 家道中落': 10000, '💰 低收入户': 25000}
        initial_cash = credits_map[fate_name]
        
        avatar_data = {
            "name": request.name,
            "mbti": request.mbti,
            "fate": fate_name,
            "cash": initial_cash,
            "invested_assets": 0,
            "total_assets": initial_cash,
            "current_month": 0,
            "active_investments": [],
            "background_story": f"你是{request.name}，{request.mbti}类型。",
            "special_traits": ["智慧", "勇气", "坚持"],
            "health": 100,
            "energy": 100,
            "happiness": 100,
            "stress": 0,
            "trust_level": 50,
            "intervention_points": 10
        }
        
        game_sessions[request.session_id] = {"avatar_data": avatar_data}
        
        return {
            "success": True,
            "avatar": avatar_data
        }
    except Exception as e:
        print(f"创建化身错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/generate-situation")
async def generate_situation(request: GenerateSituationRequest):
    if request.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not (ai_engine and AI_AVAILABLE):
        raise HTTPException(status_code=503, detail="AI engine is not available. Please check API key and backend logs.")

    session = game_sessions[request.session_id]
    avatar_data = session["avatar_data"]
    
    try:
        situation_context = {
            "name": avatar_data["name"],
            "mbti": avatar_data["mbti"],
            "age": 25,
            "cash": avatar_data["cash"],
            "other_assets": avatar_data.get("other_assets", 0),
            "total_assets": avatar_data.get("total_assets", avatar_data["cash"]),
            "health": avatar_data["health"],
            "happiness": avatar_data["happiness"],
            "stress": avatar_data["stress"],
            "background": avatar_data["background_story"],
            "traits": ", ".join(avatar_data["special_traits"]),
            "life_stage": "exploration",
            "decision_count": session.get("decision_count", 0)
        }
        
        print(f"[AI] Generating situation for {avatar_data['name']} ({avatar_data['mbti']})")
        ai_situation = ai_engine.generate_situation(situation_context)
        
        if ai_situation and isinstance(ai_situation, dict) and 'description' in ai_situation and 'choices' in ai_situation:
            situation_data = {
                "situation": ai_situation['description'],
                "options": ai_situation['choices'],
                "ai_generated": True
            }
            session["current_situation"] = situation_data
            print(f"[OK] AI situation generated: {ai_situation['description'][:50]}...")
            return situation_data
        else:
            error_message = f"AI returned an invalid or empty situation format: {ai_situation}"
            print(f"[ERROR] {error_message}")
            raise HTTPException(status_code=500, detail=error_message)
            
    except Exception as e:
        error_detail = f"An unexpected error occurred during AI situation generation: {str(e)}"
        print(f"[ERROR] {error_detail}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)

def _process_monthly_events(session):
    """处理每个月开始时发生的事件，例如投资到期"""
    avatar_data = session["avatar_data"]
    avatar_data["current_month"] += 1
    
    events_log = []
    mature_investments = []
    
    # 检查到期投资
    for investment in avatar_data.get("active_investments", []):
        if avatar_data["current_month"] >= investment["maturity_month"]:
            # 计算回报 (简单起见，我们用一个随机范围)
            # 短期: -5% to 15%, 中期: -10% to 30%, 长期: -20% to 60%
            duration = investment["duration"]
            if duration == 3:
                return_rate = random.uniform(-0.05, 0.15)
            elif duration == 6:
                return_rate = random.uniform(-0.10, 0.30)
            else: # 12 months
                return_rate = random.uniform(-0.20, 0.60)
            
            return_amount = investment["amount"] * (1 + return_rate)
            profit = return_amount - investment["amount"]
            
            # 更新财务状况
            avatar_data["cash"] += return_amount
            avatar_data["invested_assets"] -= investment["amount"]
            avatar_data["total_assets"] += profit
            
            log_message = f"第{avatar_data['current_month']}月：你于第{investment['start_month']}月投资的{investment['amount']:,}CP（{duration}个月）已到期，回报为{profit:,.0f}CP！"
            events_log.append(log_message)
            mature_investments.append(investment)

    # 移除已到期的投资
    if mature_investments:
        avatar_data["active_investments"] = [inv for inv in avatar_data["active_investments"] if inv not in mature_investments]
        
    return events_log

def process_decision(session, decision_context):
    avatar_data = session["avatar_data"]
    game_over = False

    ai_decision = ai_engine.make_decision(decision_context)
    
    if not (ai_decision and "chosen_option" in ai_decision and "financial_impact" in ai_decision):
        print(f"[WARN] AI decision returned abnormal result: {ai_decision}")
        return {
            "decision": { "ai_thoughts": "AI决策异常，系统自动执行了安全操作。" },
            "avatar": avatar_data,
            "game_over": False,
            "monthly_events": []
        }

    impact = ai_decision.get("decision_impact", {})

    # 1. 处理新的投资
    investment = impact.get("investment")
    if investment and isinstance(investment, dict):
        amount = int(investment.get("amount", 0))
        duration = int(investment.get("duration", 0))
        if amount > 0 and duration in [3, 6, 12] and avatar_data["cash"] >= amount:
            # This is an investment, cash moves to invested_assets
            avatar_data["cash"] -= amount
            avatar_data["invested_assets"] = avatar_data.get("invested_assets", 0) + amount
            
            new_investment = {
                "amount": amount,
                "duration": duration,
                "start_month": avatar_data["current_month"],
                "maturity_month": avatar_data["current_month"] + duration
            }
            avatar_data.get("active_investments", []).append(new_investment)

    # 2. 处理所有由AI计算的即时变化
    avatar_data["cash"] += int(impact.get("cash_change", 0))
    avatar_data["invested_assets"] += int(impact.get("invested_assets_change", 0))
    avatar_data["health"] = max(0, min(100, avatar_data["health"] + int(impact.get("health_change", 0))))
    avatar_data["happiness"] = max(0, min(100, avatar_data["happiness"] + int(impact.get("happiness_change", 0))))
    avatar_data["stress"] = max(0, min(100, avatar_data["stress"] + int(impact.get("stress_change", 0))))
    avatar_data["trust_level"] = max(0, min(100, avatar_data["trust_level"] + int(impact.get("trust_change", 0))))

    # 3. 重新计算总资产并检查破产
    avatar_data["total_assets"] = avatar_data["cash"] + avatar_data["invested_assets"]
    
    if avatar_data["cash"] < 0:
        game_over = True

    print(f"[OK] AI decision made: {ai_decision['chosen_option'][:30]}...")
    
    return {
        "decision": {
            "chosen_option": ai_decision["chosen_option"],
            "ai_thoughts": ai_decision.get("ai_thoughts", "AI未提供想法。"),
            "decision_impact": impact, # Pass the whole impact object to frontend
            "ai_powered": True,
        },
        "avatar": avatar_data,
        "game_over": game_over
    }

@app.post("/api/echo")
async def send_echo(request: EchoRequest):
    if request.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = game_sessions[request.session_id]
    
    # 1. 处理本月事件
    monthly_events = _process_monthly_events(session)

    # 2. 执行玩家决策
    avatar_data = session["avatar_data"]
    current_situation = session.get("current_situation", {})
    
    if not current_situation:
        raise HTTPException(status_code=400, detail="No current situation to respond to")
    
    if not (ai_engine and AI_AVAILABLE):
        raise HTTPException(status_code=503, detail="AI engine is not available.")

    try:
        decision_context = {
            "name": avatar_data["name"], "mbti": avatar_data["mbti"], "age": 25,
            "cash": avatar_data["cash"],
            "invested_assets": avatar_data.get("invested_assets", 0),
            "total_assets": avatar_data.get("total_assets", avatar_data["cash"]),
            "current_month": avatar_data.get("current_month", 0),
            "health": avatar_data["health"], "happiness": avatar_data["happiness"], "stress": avatar_data["stress"],
            "trust": avatar_data["trust_level"], "background": avatar_data["background_story"],
            "traits": ", ".join(avatar_data["special_traits"]),
            "situation": current_situation.get("situation", "面临决策"),
            "options": current_situation.get("options", []),
            "player_echo": request.echo_text
        }
        
        result = process_decision(session, decision_context)
        result["monthly_events"] = monthly_events
        return result

    except Exception as e:
        print(f"[ERROR] AI echo decision failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during AI decision: {e}")


@app.post("/api/auto-decision")
async def auto_decision(request: AutoDecisionRequest):
    if request.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = game_sessions[request.session_id]

    # 1. 处理本月事件
    monthly_events = _process_monthly_events(session)

    # 2. 执行AI自主决策
    avatar_data = session["avatar_data"]
    current_situation = session.get("current_situation", {})
    
    if not current_situation:
        raise HTTPException(status_code=400, detail="No current situation")
        
    if not (ai_engine and AI_AVAILABLE):
        raise HTTPException(status_code=503, detail="AI engine is not available.")

    try:
        decision_context = {
            "name": avatar_data["name"], "mbti": avatar_data["mbti"], "age": 25,
            "cash": avatar_data["cash"],
            "invested_assets": avatar_data.get("invested_assets", 0),
            "total_assets": avatar_data.get("total_assets", avatar_data["cash"]),
            "current_month": avatar_data.get("current_month", 0),
            "health": avatar_data["health"], "happiness": avatar_data["happiness"], "stress": avatar_data["stress"],
            "trust": avatar_data["trust_level"], "background": avatar_data["background_story"],
            "traits": ", ".join(avatar_data["special_traits"]),
            "situation": current_situation.get("situation", "面临决策"),
            "options": current_situation.get("options", []),
            "player_echo": "无玩家建议，请自主决策"
        }
        
        result = process_decision(session, decision_context)
        result["monthly_events"] = monthly_events
        return result

    except Exception as e:
        print(f"[ERROR] AI auto decision failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during AI auto decision: {e}")


@app.post("/api/generate-situation")
async def generate_situation(request: GenerateSituationRequest):
    if request.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not (ai_engine and AI_AVAILABLE):
        raise HTTPException(status_code=503, detail="AI engine is not available. Please check API key and backend logs.")

    session = game_sessions[request.session_id]
    avatar_data = session["avatar_data"]
    
    try:
        situation_context = {
            "name": avatar_data["name"],
            "mbti": avatar_data["mbti"],
            "age": 25,
            "cash": avatar_data["cash"],
            "health": avatar_data["health"],
            "happiness": avatar_data["happiness"],
            "stress": avatar_data["stress"],
            "background": avatar_data["background_story"],
            "traits": ", ".join(avatar_data["special_traits"]),
            "life_stage": "exploration",
            "decision_count": session.get("decision_count", 0)
        }
        
        print(f"[AI] Generating situation for {avatar_data['name']} ({avatar_data['mbti']})")
        ai_situation = ai_engine.generate_situation(situation_context)
        
        if ai_situation and isinstance(ai_situation, dict) and 'description' in ai_situation and 'choices' in ai_situation:
            situation_data = {
                "situation": ai_situation['description'],
                "options": ai_situation['choices'],
                "ai_generated": True
            }
            session["current_situation"] = situation_data
            print(f"[OK] AI situation generated: {ai_situation['description'][:50]}...")
            return situation_data
        else:
            error_message = f"AI returned an invalid or empty situation format: {ai_situation}"
            print(f"[ERROR] {error_message}")
            raise HTTPException(status_code=500, detail=error_message)
            
    except Exception as e:
        # Catch any exception, including HTTPExceptions from deeper calls, and format it
        error_detail = f"An unexpected error occurred during AI situation generation: {str(e)}"
        print(f"[ERROR] {error_detail}")
        import traceback
        traceback.print_exc()
        # Re-raise as a 500 error to ensure the client gets a proper server error response
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/echo")
async def send_echo(request: EchoRequest):
    if request.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = game_sessions[request.session_id]
    avatar_data = session["avatar_data"]
    current_situation = session.get("current_situation", {})
    
    if not current_situation:
        raise HTTPException(status_code=400, detail="No current situation to respond to")
    
    game_over = False
    
    # 使用AI决策
    if ai_engine and AI_AVAILABLE:
        try:
            decision_context = {
                "name": avatar_data["name"],
                "mbti": avatar_data["mbti"],
                "age": 25,
                "cash": avatar_data["cash"],
                "health": avatar_data["health"],
                "happiness": avatar_data["happiness"],
                "stress": avatar_data["stress"],
                "trust": avatar_data["trust_level"],
                "background": avatar_data["background_story"],
                "traits": ", ".join(avatar_data["special_traits"]),
                "situation": current_situation.get("situation", "面临决策"),
                "options": current_situation.get("options", []),
                "player_echo": request.echo_text
            }
            
            print(f"[AI] Making decision - Player suggestion: {request.echo_text[:30]}...")
            ai_decision = ai_engine.make_decision(decision_context)
            
            if ai_decision and "chosen_option" in ai_decision and "error" not in ai_decision:
                cash_change = random.randint(-80000, 30000) # More realistic change
                avatar_data["cash"] += cash_change
                
                session["decision_count"] = session.get("decision_count", 0) + 1
                
                if avatar_data["cash"] < 0:
                    game_over = True

                print(f"[OK] AI decision made: {ai_decision['chosen_option'][:30]}...")
                print(f"[AI] Thoughts: {ai_decision.get('ai_thoughts', '')[:50]}...")
                
                return {
                    "echo_analysis": {"type": "advisory", "confidence": 0.9, "ai_powered": True},
                    "decision": {
                        "chosen_option": ai_decision["chosen_option"],
                        "ai_thoughts": ai_decision.get("ai_thoughts", "让我仔细考虑一下..."),
                        "new_cash": avatar_data["cash"],
                        "trust_change": random.randint(1, 5),
                        "cash_change": cash_change
                    },
                    "avatar": avatar_data,
                    "game_over": game_over
                }
            else:
                print(f"[WARN] AI decision returned abnormal result: {ai_decision}")
        except Exception as e:
            print(f"[ERROR] AI decision failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Fallback simplified logic
    options = current_situation.get("options", ["选择第一个选项"])
    chosen = random.choice(options)
    cash_change = random.randint(-50000, 100000)
    avatar_data["cash"] += cash_change
    
    if avatar_data["cash"] < 0:
        game_over = True

    ai_thoughts = f"考虑了你的建议'{request.echo_text}'，我觉得{chosen}比较合适。"
    
    return {
        "echo_analysis": {"type": "advisory", "confidence": 0.8, "ai_powered": False},
        "decision": {
            "chosen_option": chosen,
            "ai_thoughts": ai_thoughts,
            "new_cash": avatar_data["cash"],
            "trust_change": random.randint(-2, 5),
            "cash_change": cash_change
        },
        "avatar": avatar_data,
        "game_over": game_over
    }

@app.post("/api/auto-decision")
async def auto_decision(request: AutoDecisionRequest):
    if request.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = game_sessions[request.session_id]
    avatar_data = session["avatar_data"]
    current_situation = session.get("current_situation", {})
    
    if not current_situation:
        raise HTTPException(status_code=400, detail="No current situation")
        
    game_over = False

    # 使用AI自主决策
    if ai_engine and AI_AVAILABLE:
        try:
            decision_context = {
                "name": avatar_data["name"],
                "mbti": avatar_data["mbti"],
                "age": 25,
                "cash": avatar_data["cash"],
                "health": avatar_data["health"],
                "happiness": avatar_data["happiness"],
                "stress": avatar_data["stress"],
                "trust": avatar_data["trust_level"],
                "background": avatar_data["background_story"],
                "traits": ", ".join(avatar_data["special_traits"]),
                "situation": current_situation.get("situation", "面临决策"),
                "options": current_situation.get("options", []),
                "player_echo": "无玩家建议，请自主决策"
            }
            
            print(f"[AI] Auto decision in progress...")
            ai_decision = ai_engine.make_decision(decision_context)
            
            if ai_decision and "chosen_option" in ai_decision and "error" not in ai_decision:
                cash_change = random.randint(-80000, 20000) # AI is more conservative
                avatar_data["cash"] += cash_change
                
                if avatar_data["cash"] < 0:
                    game_over = True

                session["decision_count"] = session.get("decision_count", 0) + 1
                
                print(f"[OK] AI auto decision made: {ai_decision['chosen_option'][:30]}...")
                
                return {
                    "decision": {
                        "chosen_option": ai_decision["chosen_option"],
                        "ai_thoughts": ai_decision.get("ai_thoughts", "经过深思熟虑..."),
                        "new_cash": avatar_data["cash"],
                        "trust_change": 0,
                        "cash_change": cash_change,
                        "ai_powered": True
                    },
                    "avatar": avatar_data,
                    "game_over": game_over
                }
        except Exception as e:
            print(f"[ERROR] AI auto decision failed: {e}")

    # Fallback simplified logic
    options = current_situation.get("options", ["选择第一个选项"])
    chosen = random.choice(options)
    cash_change = random.randint(-30000, 80000)
    avatar_data["cash"] += cash_change
    
    if avatar_data["cash"] < 0:
        game_over = True
        
    print(f"[DEFAULT] Default auto decision: {chosen[:30]}...")
    
    return {
        "decision": {
            "chosen_option": chosen,
            "ai_thoughts": f"作为{avatar_data['mbti']}类型，经过深思熟虑，我选择了{chosen}。",
            "new_cash": avatar_data["cash"],
            "trust_change": 0,
            "cash_change": cash_change,
            "ai_powered": False
        },
        "avatar": avatar_data,
        "game_over": game_over
    }

if __name__ == "__main__":
    print("[START] Starting Echopolis server...")
    print("[INFO] Service URL: http://localhost:8008")
    print("[INFO] API Docs: http://localhost:8008/docs")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8008)
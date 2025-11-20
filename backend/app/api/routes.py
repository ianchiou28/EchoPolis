"""
API路由定义
"""
from fastapi import APIRouter, HTTPException
from app.models.requests import (
    CreateAvatarRequest,
    GenerateSituationRequest,
    EchoRequest,
    AutoDecisionRequest,
    SessionStartRequest,
    SessionAdvanceRequest,
    SessionFinishRequest,
    AIChatRequest,
)
from app.models.auth import LoginRequest, RegisterRequest, AuthResponse
from app.services.game_service import GameService
import sys
import os
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from core.systems.asset_manager import AssetManager

router = APIRouter()
game_service = GameService()
asset_manager = AssetManager()

@router.get("/mbti-types")
async def get_mbti_types():
    return game_service.get_mbti_types()

@router.get("/fate-wheel")
async def get_fate_wheel():
    return game_service.get_fate_wheel()

@router.post("/create-avatar")
async def create_avatar(request: CreateAvatarRequest):
    try:
        print(f"Creating avatar: name={request.name}, mbti={request.mbti}, session_id={request.session_id}")
        result = await game_service.create_avatar(request.name, request.mbti, request.session_id)
        print(f"Avatar created successfully: {result}")
        return {"success": True, "avatar": result}
    except Exception as e:
        print(f"Error creating avatar: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-situation")
async def generate_situation(request: GenerateSituationRequest):
    try:
        return await game_service.generate_situation(request.session_id, request.context or "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/echo")
async def send_echo(request: EchoRequest):
    try:
        return await game_service.send_echo(request.session_id, request.echo_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auto-decision")
async def auto_decision(request: AutoDecisionRequest):
    try:
        return await game_service.auto_decision(request.session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(request: LoginRequest):
    try:
        success = game_service.verify_account(request.username, request.password)
        if success:
            return AuthResponse(success=True, message="登录成功", username=request.username)
        else:
            return AuthResponse(success=False, message="用户名或密码错误")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register")
async def register(request: RegisterRequest):
    try:
        print(f"[注册] 用户名: {request.username}")
        if not game_service.db:
            print("[错误] 数据库未初始化")
            return AuthResponse(success=False, message="数据库未初始化")
        
        success = game_service.create_account(request.username, request.password)
        print(f"[注册] 结果: {success}")
        
        if success:
            return AuthResponse(success=True, message="注册成功", username=request.username)
        else:
            return AuthResponse(success=False, message="用户名已存在")
    except Exception as e:
        print(f"[注册错误] {e}")
        import traceback
        traceback.print_exc()
        return AuthResponse(success=False, message=f"注册失败: {str(e)}")

@router.get("/investments/{username}")
async def get_investments(username: str):
    try:
        return game_service.get_user_investments(username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/{username}")
async def get_transactions(username: str, limit: int = 10):
    try:
        return game_service.get_user_transactions(username, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{username}")
async def get_user_info(username: str):
    try:
        user_info = game_service.get_user_info(username)
        if user_info:
            return user_info
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
        print(f"Error getting user info: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/avatar/status")
async def get_avatar_status(session_id: str = None):
    try:
        print(f"[Avatar Status] 收到session_id: {session_id}")
        
        if not session_id:
            print("[Avatar Status] session_id为空，返回默认数据")
            return {
                "name": "未选择角色",
                "mbti_type": "INTJ",
                "total_assets": 0,
                "cash": 0,
                "trust_level": 50,
                "current_month": 0
            }
        
        if not game_service.db:
            raise Exception("数据库未初始化")
        
        # 从数据库获取角色数据
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, mbti, credits, username FROM users WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            print(f"[Avatar Status] 数据库查询结果: {row}")
            
            if not row:
                # 尝试用id查询
                cursor.execute('''
                    SELECT name, mbti, credits, username FROM users WHERE id = ?
                ''', (session_id,))
                row = cursor.fetchone()
                print(f"[Avatar Status] 用id查询结果: {row}")
            
            if not row:
                raise Exception(f"角色不存在: {session_id}")
            
            cash = row[2]
            username = row[3]
            
            # 计算投资资产
            cursor.execute('''
                SELECT SUM(amount) FROM investments 
                WHERE username = ? AND remaining_months > 0
            ''', (username,))
            invested = cursor.fetchone()[0] or 0
            
            total_assets = cash + invested
            
            result = {
                "name": row[0],
                "mbti_type": row[1],
                "total_assets": total_assets,
                "cash": cash,
                "invested_assets": invested,
                "trust_level": 50,
                "current_month": 0
            }
            print(f"[Avatar Status] 返回数据: {result}")
            return result
    except Exception as e:
        print(f"[Avatar Status] 错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/investments")
async def get_investments(session_id: str = None):
    try:
        print(f"[投资列表] session_id: {session_id}")
        
        if not session_id or not game_service.db:
            return []
        
        # 从数据库获取投资
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username FROM users WHERE session_id = ?
            ''', (session_id,))
            user_row = cursor.fetchone()
            
            if not user_row:
                return []
            
            username = user_row[0]
            cursor.execute('''
                SELECT id, name, amount, investment_type, remaining_months, monthly_return, return_rate
                FROM investments 
                WHERE username = ?
                ORDER BY created_at DESC
            ''', (username,))
            
            investments = []
            for row in cursor.fetchall():
                term = 'short' if '短期' in row[3] else ('medium' if '中期' in row[3] else 'long')
                # 计算预期收益
                if row[5] > 0:  # 月收益型
                    profit = row[5] * row[4]
                else:  # 一次性收益型
                    profit = int(row[2] * row[6])  # amount * return_rate
                
                investments.append({
                    "id": row[0],
                    "name": row[1],
                    "term": term,
                    "amount": row[2],
                    "profit": profit,
                    "duration": row[4],
                    "monthly_return": row[5] or 0,
                    "is_active": row[4] > 0
                })
            
            print(f"[投资列表] 返回{len(investments)}条数据")
            return investments
    except Exception as e:
        print(f"[投资列表] 错误: {e}")
        import traceback
        traceback.print_exc()
        return []

@router.post("/ai/chat")
async def ai_chat(request: AIChatRequest):
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="message required")
        return await game_service.ai_chat(request.message, session_id=request.session_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/characters/{username}")
async def get_characters(username: str):
    try:
        if not game_service.db:
            return []
        
        # 从数据库获取用户的所有角色
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id, name, mbti, credits FROM users WHERE username = ?
            ''', (username,))
            
            characters = []
            for row in cursor.fetchall():
                characters.append({
                    "id": row[0],  # session_id作为id返回
                    "name": row[1],
                    "mbti": row[2],
                    "assets": row[3]
                })
            return characters
    except Exception as e:
        print(f"获取角色列表错误: {e}")
        import traceback
        traceback.print_exc()
        return []

@router.post("/characters/create")
async def create_character(data: dict):
    try:
        username = data.get("username")
        name = data.get("name")
        mbti = data.get("mbti")
        fate = data.get("fate")
        
        if not game_service.db:
            raise Exception("数据库未初始化")
        
        print(f"创建角色: {username} - {name} ({mbti}) - {fate['name']}")
        
        # 生成session_id
        import uuid
        session_id = f"{username}_{uuid.uuid4().hex[:8]}"
        
        # 保存到数据库
        game_service.db.save_user(
            username=username,
            session_id=session_id,
            name=name,
            mbti=mbti,
            fate=fate['name'],
            credits=fate['initial_money']
        )
        
        return {
            "success": True,
            "character": {
                "id": session_id,
                "name": name,
                "mbti": mbti,
                "assets": fate['initial_money']
            }
        }
    except Exception as e:
        print(f"创建角色错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

async def make_ai_decision(session_id: str, name: str, mbti: str, cash: int, situation: str, options: list, api_key: str):
    """让AI做出决策（可能包含投资）"""
    try:
        from core.ai.deepseek_engine import DeepSeekEngine
        engine = DeepSeekEngine(api_key)
        
        context = {
            "name": name,
            "mbti": mbti,
            "age": 25,
            "cash": cash,
            "invested_assets": 0,
            "total_assets": cash,
            "health": 80,
            "happiness": 70,
            "energy": 75,
            "stress": 30,
            "trust": 50,
            "current_month": 1,
            "situation": situation,
            "options": options,
            "player_echo": None
        }
        
        result = engine.make_decision(context)
        print(f"[AI决策] 结果: {result}")
        return result
    except Exception as e:
        print(f"[AI决策] 失败: {e}")
        return None

@router.post("/time/advance")
async def advance_time(data: dict):
    try:
        from core.ai.deepseek_engine import DeepSeekEngine
        import json
        import os
        
        session_id = data.get('session_id')
        name = data.get('name', '用户')
        mbti = data.get('mbti', 'INTJ')
        cash = data.get('cash', 0)
        total_assets = data.get('total_assets', 0)
        
        print(f"[时间推进] 角色: {name} ({mbti}), 现金: {cash}, 总资产: {total_assets}")
        
        # 加载API key
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('deepseek_api_key')
        
        # 计算月收入（简化版）
        monthly_income = int(total_assets * 0.005)  # 假设0.5%月收益
        
        # 生成新情况，传递角色信息
        prompt = f"""你是一个金融模拟游戏的情况生成器。

角色信息：
- 姓名：{name}
- MBTI人格：{mbti}
- 现金：¥{cash:,}
- 总资产：¥{total_assets:,}
- 月收入：¥{monthly_income:,}

请根据该角色的{mbti}人格特点和财务状况，生成一个合适的财务决策情况：
1. 情况描述（50-100字）
2. 3个选择方案

格式：
情况：[描述]
选项1：[选择1]
选项2：[选择2]
选项3：[选择3]"""
        
        print(f"[时间推进] 传递给AI: 现金={cash:,}, 总资产={total_assets:,}, 月收入={monthly_income:,}")
        
        print(f"[时间推进] 调用DeepSeek API...")
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 300
            },
            timeout=30
        )
        print(f"[时间推进] API响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"]
            
            # 解析情况
            lines = ai_text.split('\n')
            situation = ""
            options = []
            
            for line in lines:
                if '情况：' in line or '情况:' in line:
                    situation = line.split('：', 1)[-1].split(':', 1)[-1].strip()
                elif '选项1：' in line or '选项1:' in line:
                    options.append(line.split('：', 1)[-1].split(':', 1)[-1].strip())
                elif '选项2：' in line or '选项2:' in line:
                    options.append(line.split('：', 1)[-1].split(':', 1)[-1].strip())
                elif '选项3：' in line or '选项3:' in line:
                    options.append(line.split('：', 1)[-1].split(':', 1)[-1].strip())
            
            # 更新数据库中的资产（添加月收入）
            new_cash = cash + monthly_income
            if game_service.db and session_id:
                import sqlite3
                with sqlite3.connect(game_service.db.db_path) as conn:
                    cursor = conn.cursor()
                    # 更新现金
                    cursor.execute('''
                        UPDATE users SET credits = ? WHERE id = ?
                    ''', (new_cash, session_id))
                    
                    # 更新投资的剩余月数
                    cursor.execute('''
                        UPDATE investments 
                        SET remaining_months = remaining_months - 1
                        WHERE session_id = ? AND remaining_months > 0
                    ''', (session_id,))
                    
                    # 处理到期投资（将收益加到现金）
                    cursor.execute('''
                        SELECT id, name, amount, return_rate, monthly_return
                        FROM investments
                        WHERE session_id = ? AND remaining_months = 0
                    ''', (session_id,))
                    
                    matured_investments = cursor.fetchall()
                    total_matured_return = 0
                    
                    for inv in matured_investments:
                        inv_id, inv_name, inv_amount, return_rate, monthly_ret = inv
                        # 计算收益
                        if monthly_ret > 0:
                            # 月收益型，返还本金
                            total_return = inv_amount
                        else:
                            # 一次性收益型
                            total_return = int(inv_amount * (1 + return_rate))
                        
                        total_matured_return += total_return
                        print(f"[投资到期] {inv_name}: 本金{inv_amount}, 收益{total_return}")
                    
                    # 将到期收益加到现金
                    if total_matured_return > 0:
                        new_cash += total_matured_return
                        cursor.execute('''
                            UPDATE users SET credits = ? WHERE id = ?
                        ''', (new_cash, session_id))
                    
                    conn.commit()
                    print(f"[时间推进] 月收入: {monthly_income}, 到期收益: {total_matured_return}, 新现金: {new_cash}")
            
            return {
                "success": True,
                "new_cash": new_cash,
                "total_assets": new_cash,
                "monthly_income": monthly_income,
                "situation": situation or "新的一个月开始了，你需要做出新的决策。",
                "options": options if len(options) == 3 else [
                    "继续当前策略",
                    "调整投资组合",
                    "寻找新机会"
                ]
            }
        else:
            # Fallback情况
            print(f"[时间推进] API调用失败，使用fallback")
            new_cash = cash + monthly_income
            
            return {
                "success": True,
                "new_cash": new_cash,
                "total_assets": new_cash,
                "monthly_income": monthly_income,
                "situation": "新的一个月开始了。你的投资组合产生了收益，现在需要考虑下一步的财务规划。",
                "options": [
                    "继续持有当前投资",
                    "增加新的投资项目",
                    "提取部分收益改善生活"
                ]
            }
    except Exception as e:
        print(f"时间推进错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ai/invest")
async def ai_invest(data: dict):
    """AI自主投资决策"""
    try:
        from core.ai.deepseek_engine import DeepSeekEngine
        import json
        import os
        
        session_id = data.get('session_id')
        name = data.get('name', '用户')
        mbti = data.get('mbti', 'INTJ')
        cash = data.get('cash', 0)
        
        # 加载API key
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('deepseek_api_key')
        
        engine = DeepSeekEngine(api_key)
        
        # 构建投资情况
        situation = f"你现在有{cash:,}CP现金，考虑进行一些投资来增加收益。"
        options = [
            "投资20%资金到短期理财产品（3个月，5-8%年化收益）",
            "投资30%资金到中期基金（6个月，8-12%年化收益）",
            "保守策略，不进行新投资"
        ]
        
        context = {
            "name": name,
            "mbti": mbti,
            "age": 25,
            "cash": cash,
            "invested_assets": 0,
            "total_assets": cash,
            "health": 80,
            "happiness": 70,
            "energy": 75,
            "stress": 30,
            "trust": 50,
            "current_month": 1,
            "situation": situation,
            "options": options,
            "player_echo": None
        }
        
        result = engine.make_decision(context)
        print(f"[AI投资] 决策结果: {result}")
        
        # 如果有投资，保存到数据库
        if result.get('investment'):
            inv = result['investment']
            import sqlite3
            with sqlite3.connect(game_service.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT username FROM users WHERE id = ?', (session_id,))
                user_row = cursor.fetchone()
                
                if user_row:
                    username = user_row[0]
                    type_map = {'SHORT_TERM': '短期', 'MEDIUM_TERM': '中期', 'LONG_TERM': '长期'}
                    inv_type = type_map.get(inv.get('type', 'SHORT_TERM'), '短期')
                    
                    game_service.db.save_investment(
                        username=username,
                        session_id=session_id,
                        name=inv.get('name', '投资项目'),
                        amount=inv.get('amount', 0),
                        investment_type=inv_type,
                        remaining_months=inv.get('duration', 3),
                        monthly_return=inv.get('monthly_return', 0),
                        return_rate=inv.get('return_rate', 0.05),
                        created_round=1,
                        ai_thoughts=result.get('ai_thoughts', '')
                    )
                    
                    # 更新现金
                    new_cash = cash - inv.get('amount', 0)
                    cursor.execute('UPDATE users SET credits = ? WHERE id = ?', (new_cash, session_id))
                    conn.commit()
                    
                    print(f"[投资记录] 已保存: {inv.get('name')} - {inv.get('amount')}CP")
                    
                    return {
                        "success": True,
                        "investment": inv,
                        "ai_thoughts": result.get('ai_thoughts', ''),
                        "new_cash": new_cash
                    }
        
        return {
            "success": False,
            "message": "AI决定不进行投资",
            "ai_thoughts": result.get('ai_thoughts', '')
        }
    except Exception as e:
        print(f"AI投资决策错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/world/action")
async def world_action(action: dict):
    try:
        action_name = action.get("action_name")
        price = action.get("price", 0)
        building = action.get("building", "")
        session_id = action.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required")
        
        # 从数据库获取现金
        import sqlite3
        conn = sqlite3.connect(game_service.db.db_path, timeout=10.0)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT credits, username FROM users WHERE id = ?', (session_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
            
            current_cash = row[0]
            username = row[1]
        finally:
            conn.close()
        
        # 检查现金
        if price > current_cash:
            return {
                "success": False,
                "message": f"🚫 现金不足，无法执行此操作",
                "ai_advice": f"💰 需要￥{price:,}，但你只有￥{current_cash:,}\n💡 建议：先积累资金或考虑银行贷款"
            }
        
        # AI审查
        ai_message = ""
        if building == "realestate" and price > current_cash * 0.8:
            return {
                "success": False,
                "message": "🚫 风险过高",
                "ai_advice": "🛡️ 建议保留至少30%现金作为应急储备"
            }
        elif building == "business" and price > 100000:
            ai_message = "⚠️ 创业风险较高，请谨慎考虑"
        elif building == "stock" and price > current_cash * 0.5:
            ai_message = "⚠️ 股市波动大，注意风险"
        
        # 执行操作
        new_cash = current_cash - price
        
        conn = sqlite3.connect(game_service.db.db_path, timeout=10.0)
        try:
            cursor = conn.cursor()
            # 更新现金
            cursor.execute('UPDATE users SET credits = ? WHERE id = ?', (new_cash, session_id))
            
            # 保存投资
            if building in ["stock", "bank"]:
                type_map = {"stock": "短期", "bank": "中期"}
                duration = 3 if building == "stock" else 6
                return_rate = 0.08 if building == "stock" else 0.06
                
                cursor.execute('''
                    INSERT INTO investments 
                    (username, session_id, name, amount, investment_type, remaining_months, 
                     monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, action_name, price, type_map.get(building, "短期"),
                      duration, 0, return_rate, 1, f"在{building}执行: {action_name}"))
            
            conn.commit()
            
            # 计算总资产
            cursor.execute('SELECT SUM(amount) FROM investments WHERE username = ? AND remaining_months > 0', (username,))
            invested = cursor.fetchone()[0] or 0
        finally:
            conn.close()
        
        total_assets = new_cash + invested
        
        return {
            "success": True,
            "message": f"成功执行: {action_name}",
            "new_balance": new_cash,
            "total_assets": total_assets,
            "ai_comment": ai_message if ai_message else "这是个合理的决策，符合你的财务状况"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/start")
async def session_start(req: SessionStartRequest):
    """统一的会话启动接口：创建角色+会话+首月快照"""
    try:
      return game_service.start_session(req.username, req.name, req.mbti)
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))

@router.get("/session/state")
async def session_state(session_id: str):
    try:
      return game_service.get_session_state(session_id)
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/advance")
async def session_advance(req: SessionAdvanceRequest):
    try:
      return game_service.advance_session(req.session_id, req.echo_text)
    except Exception as e:
      print(f"[session_advance] error: {e}")
      raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/finish")
async def session_finish(req: SessionFinishRequest):
    try:
      return game_service.finish_session(req.session_id)
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))

@router.get("/session/timeline")
async def session_timeline(session_id: str, limit: int = 36):
    try:
      if not game_service.db:
        raise Exception("数据库未初始化")
      return game_service.db.get_session_timeline(session_id, limit)
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))

@router.get('/city/state')
async def city_state(session_id: str):
    try:
        return game_service.get_city_snapshot(session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/city/district/{district_id}')
async def city_district_event(district_id: str, payload: dict):
    session_id = payload.get('session_id')
    if not session_id:
        raise HTTPException(status_code=400, detail='session_id required')
    try:
        return game_service.generate_district_event(session_id, district_id, payload.get('context'))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/macro/indicators")
async def get_macro_indicators():
    try:
        return game_service.get_macro_indicators()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

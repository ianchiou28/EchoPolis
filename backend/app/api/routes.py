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
            # 检查列是否存在
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            has_stats = 'happiness' in columns
            
            if has_stats:
                cursor.execute('''
                    SELECT name, mbti, credits, username, happiness, energy, health FROM users WHERE session_id = ?
                ''', (session_id,))
            else:
                cursor.execute('''
                    SELECT name, mbti, credits, username FROM users WHERE session_id = ?
                ''', (session_id,))
            
            row = cursor.fetchone()
            print(f"[Avatar Status] 数据库查询结果: {row}")
            
            if not row:
                # 尝试用id查询
                if has_stats:
                    cursor.execute('''
                        SELECT name, mbti, credits, username, happiness, energy, health FROM users WHERE id = ?
                    ''', (session_id,))
                else:
                    cursor.execute('''
                        SELECT name, mbti, credits, username FROM users WHERE id = ?
                    ''', (session_id,))
                row = cursor.fetchone()
                print(f"[Avatar Status] 用id查询结果: {row}")
            
            if not row:
                raise Exception(f"角色不存在: {session_id}")
            
            cash = row[2]
            username = row[3]
            happiness = row[4] if has_stats and len(row) > 4 else 70
            energy = row[5] if has_stats and len(row) > 5 else 75
            health = row[6] if has_stats and len(row) > 6 else 80
            
            # 计算投资资产
            cursor.execute('''
                SELECT SUM(amount) FROM investments 
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            invested = cursor.fetchone()[0] or 0
            
            total_assets = cash + invested
            
            result = {
                "name": row[0],
                "mbti_type": row[1],
                "total_assets": total_assets,
                "cash": cash,
                "invested_assets": invested,
                "trust_level": 50,
                "current_month": 0,
                "happiness": happiness,
                "energy": energy,
                "health": health
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
                WHERE session_id = ?
                ORDER BY created_at DESC
            ''', (session_id,))
            
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
        tags = data.get("tags", [])  # 获取用户选择的预设标签
        custom_tags = data.get("customTags", [])  # 获取用户自定义标签
        
        if not game_service.db:
            raise Exception("数据库未初始化")
        
        print(f"创建角色: {username} - {name} ({mbti}) - {fate['name']} - tags: {tags}, customTags: {custom_tags}")
        
        # 生成session_id
        import uuid
        session_id = f"{username}_{uuid.uuid4().hex[:8]}"
        
        # 将预设标签和自定义标签合并
        # 预设标签使用 id，自定义标签添加 custom: 前缀
        all_tags = tags.copy() if tags else []
        for ct in custom_tags:
            all_tags.append(f"custom:{ct}")
        
        tags_str = ",".join(all_tags) if all_tags else ""
        
        # 保存到数据库
        game_service.db.save_user(
            username=username,
            session_id=session_id,
            name=name,
            mbti=mbti,
            fate=fate['name'],
            credits=fate['initial_money'],
            tags=tags_str
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

@router.delete("/characters/session/{session_id}")
async def delete_character(session_id: str):
    try:
        print(f"Deleting character: {session_id}")
        success = game_service.delete_character(session_id)
        if success:
            return {"success": True, "message": "角色删除成功"}
        else:
            raise HTTPException(status_code=404, detail="角色不存在或删除失败")
    except Exception as e:
        print(f"Error deleting character: {e}")
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
        action_type = action.get("action")
        price = action.get("price", 0)
        building = action.get("building", "") # districtId
        session_id = action.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required")
        
        # 从数据库获取用户信息
        import sqlite3
        conn = sqlite3.connect(game_service.db.db_path, timeout=10.0)
        try:
            cursor = conn.cursor()
            # 检查列是否存在
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            has_stats = 'happiness' in columns
            
            if has_stats:
                cursor.execute('SELECT credits, username, happiness, energy, health FROM users WHERE id = ?', (session_id,))
            else:
                cursor.execute('SELECT credits, username FROM users WHERE id = ?', (session_id,))
            
            row = cursor.fetchone()
            
            if not row:
                # Try session_id as string match
                if has_stats:
                    cursor.execute('SELECT credits, username, happiness, energy, health FROM users WHERE session_id = ?', (session_id,))
                else:
                    cursor.execute('SELECT credits, username FROM users WHERE session_id = ?', (session_id,))
                row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="User not found")
            
            current_cash = row[0]
            username = row[1]
            happiness = row[2] if has_stats and len(row) > 2 else 70
            energy = row[3] if has_stats and len(row) > 3 else 75
            health = row[4] if has_stats and len(row) > 4 else 80
        finally:
            conn.close()
        
        # 检查现金 (贷款除外)
        if action_type != 'loan' and price > current_cash:
            return {
                "success": False,
                "message": f"🚫 现金不足，无法执行此操作",
                "ai_advice": f"💰 需要￥{price:,}，但你只有￥{current_cash:,}\n💡 建议：先积累资金或考虑银行贷款"
            }
        
        # 执行操作逻辑
        new_cash = current_cash
        ai_message = ""
        message = f"成功执行: {action_name}"
        
        conn = sqlite3.connect(game_service.db.db_path, timeout=10.0)
        try:
            cursor = conn.cursor()
            
            # --- 金融区 ---
            if action_type == 'deposit':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "定期存款", price, "短期", 6, 0, 0.04, 1, "稳健理财"))
                ai_message = "定期存款是安全的资产配置。"
                
            elif action_type == 'loan':
                new_cash += price
                # 记录负债 (这里简化为只加钱，实际应该记录负债)
                ai_message = "贷款已到账，请注意按时还款。"
                
            elif action_type == 'credit_check':
                # 不扣钱
                message = f"当前信用评分: 750 (优秀)"
                ai_message = "你的信用状况良好。"

            # --- 交易所 ---
            elif action_type == 'stock_trade':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "股票投资", price, "短期", 3, 0, 0.15, 1, "股市有风险，投资需谨慎"))
                ai_message = "已买入股票，注意市场波动。"
                
            elif action_type == 'fund_invest':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "基金定投", price, "中期", 6, 0, 0.10, 1, "基金适合长期持有"))
                ai_message = "基金申购成功。"
                
            elif action_type == 'futures':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "期货合约", price, "短期", 1, 0, 0.50, 1, "高风险高收益"))
                ai_message = "期货交易风险极高，请密切关注。"

            # --- 房产中心 ---
            elif action_type == 'buy_house':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "房产购置", price, "长期", 24, 0, 0.20, 1, "房产是抗通胀的优质资产"))
                ai_message = "恭喜成为业主！"
                
            elif action_type == 'rent':
                new_cash -= price
                happiness = min(100, happiness + 2)
                ai_message = "支付房租，获得居住权。"
                
            elif action_type == 'property_manage':
                message = "当前持有房产市值稳定。"
                ai_message = "建议定期维护房产。"

            # --- 教育区 ---
            elif action_type == 'skill_course':
                new_cash -= price
                # 提升能力
                ai_message = "投资自己永远是最好的投资。"
                
            elif action_type == 'finance_course':
                new_cash -= price
                ai_message = "财商提升了，有助于做出更好的投资决策。"
                
            elif action_type == 'certificate':
                new_cash -= price
                ai_message = "获得证书，职业竞争力提升。"

            # --- 文娱区 ---
            elif action_type == 'entertainment':
                new_cash -= price
                energy = min(100, energy + 10)
                happiness = min(100, happiness + 5)
                ai_message = "适当放松有助于恢复精力。"
                
            elif action_type == 'social':
                new_cash -= price
                happiness = min(100, happiness + 8)
                ai_message = "拓展人脉对未来发展有益。"
                
            elif action_type == 'luxury':
                new_cash -= price
                happiness = min(100, happiness + 15)
                ai_message = "享受生活，但也要理性消费。"
            
            elif action_type == 'start_business':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "创业项目", price, "长期", 12, 0, 0.25, 1, "创业维艰，但也充满希望"))
                ai_message = "创业项目已启动，期待回报。"

            # --- 能源区 ---
            elif action_type == 'green_invest':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "绿色基金", price, "长期", 12, 0, 0.08, 1, "支持环保事业"))
                ai_message = "绿色投资符合未来趋势。"
                
            elif action_type == 'energy_stock':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "新能源股票", price, "中期", 6, 0, 0.12, 1, "新能源板块潜力巨大"))
                ai_message = "已布局新能源赛道。"
                
            elif action_type == 'carbon_trade':
                new_cash -= price
                cursor.execute('''
                    INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, session_id, "碳权交易", price, "短期", 3, 0, 0.10, 1, "碳交易市场活跃"))
                ai_message = "参与碳交易，助力碳中和。"
            
            # 更新用户状态
            if has_stats:
                cursor.execute('''
                    UPDATE users SET credits = ?, happiness = ?, energy = ?, health = ? WHERE username = ? AND session_id = ?
                ''', (new_cash, happiness, energy, health, username, session_id))
            else:
                cursor.execute('UPDATE users SET credits = ? WHERE username = ? AND session_id = ?', (new_cash, username, session_id))
            
            conn.commit()
            
            # 计算总资产
            cursor.execute('SELECT SUM(amount) FROM investments WHERE username = ? AND remaining_months > 0', (username,))
            invested = cursor.fetchone()[0] or 0
            
        finally:
            conn.close()
        
        total_assets = new_cash + invested
        
        return {
            "success": True,
            "message": message,
            "new_balance": new_cash,
            "total_assets": total_assets,
            "ai_comment": ai_message if ai_message else "操作已完成"
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
      print(f"[API] session_advance called for {req.session_id}")
      result = game_service.advance_session(req.session_id, req.echo_text)
      print(f"[API] session_advance success: month={result.get('new_month')}")
      return result
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

@router.post("/decide")
async def make_decision(request: dict):
    try:
        session_id = request.get("session_id")
        option_index = request.get("option_index")
        option_text = request.get("option_text", "")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required")
            
        print(f"[API] make_decision: {session_id}, index={option_index}, text='{option_text}'")
        
        # 调用服务层处理决策
        result = game_service.process_decision(session_id, option_index, option_text)
        return result
    except Exception as e:
        print(f"[API] make_decision error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/session/transactions")
async def get_session_transactions(session_id: str, limit: int = 20):
    try:
        return game_service.get_session_transactions(session_id, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 股票市场 API ============

def _aggregate_kline_weekly(daily_data: list) -> list:
    """将日K数据聚合为周K"""
    from datetime import datetime
    if not daily_data:
        return []
    
    weekly = []
    week_data = []
    current_week = None
    
    for d in daily_data:
        date_str = d.get("date", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            week_num = date.isocalendar()[1]
            year = date.year
            week_key = f"{year}-{week_num}"
        except:
            continue
        
        if current_week is None:
            current_week = week_key
        
        if week_key != current_week:
            # 新的一周，聚合上一周的数据
            if week_data:
                weekly.append({
                    "date": week_data[0]["date"],
                    "open": week_data[0]["open"],
                    "high": max(x["high"] for x in week_data),
                    "low": min(x["low"] for x in week_data),
                    "close": week_data[-1]["close"],
                    "volume": sum(x["volume"] for x in week_data)
                })
            week_data = [d]
            current_week = week_key
        else:
            week_data.append(d)
    
    # 处理最后一周
    if week_data:
        weekly.append({
            "date": week_data[0]["date"],
            "open": week_data[0]["open"],
            "high": max(x["high"] for x in week_data),
            "low": min(x["low"] for x in week_data),
            "close": week_data[-1]["close"],
            "volume": sum(x["volume"] for x in week_data)
        })
    
    return weekly

def _aggregate_kline_monthly(daily_data: list) -> list:
    """将日K数据聚合为月K"""
    if not daily_data:
        return []
    
    monthly = []
    month_data = []
    current_month = None
    
    for d in daily_data:
        date_str = d.get("date", "")
        month_key = date_str[:7] if len(date_str) >= 7 else None
        
        if not month_key:
            continue
        
        if current_month is None:
            current_month = month_key
        
        if month_key != current_month:
            # 新的一月，聚合上一月的数据
            if month_data:
                monthly.append({
                    "date": month_data[0]["date"],
                    "open": month_data[0]["open"],
                    "high": max(x["high"] for x in month_data),
                    "low": min(x["low"] for x in month_data),
                    "close": month_data[-1]["close"],
                    "volume": sum(x["volume"] for x in month_data)
                })
            month_data = [d]
            current_month = month_key
        else:
            month_data.append(d)
    
    # 处理最后一月
    if month_data:
        monthly.append({
            "date": month_data[0]["date"],
            "open": month_data[0]["open"],
            "high": max(x["high"] for x in month_data),
            "low": min(x["low"] for x in month_data),
            "close": month_data[-1]["close"],
            "volume": sum(x["volume"] for x in month_data)
        })
    
    return monthly


@router.get("/market/stocks")
async def get_market_stocks():
    """获取所有股票列表及当前价格 - 从数据库获取真实数据"""
    try:
        from core.systems.longbridge_client import longbridge_client, STOCK_MAPPING
        from core.systems.market_engine import market_engine
        
        stocks = []
        for game_code, mapping in STOCK_MAPPING.items():
            real_symbol = mapping[0]
            real_name = mapping[3] if len(mapping) > 3 else real_symbol
            
            # 从数据库获取最新K线数据来计算价格
            kline = longbridge_client.get_kline_from_db(game_code, 2)
            
            if kline and len(kline) > 0:
                latest = kline[-1]
                prev = kline[-2] if len(kline) > 1 else latest
                price = latest.get("close", 0)
                change_pct = ((price - prev.get("close", price)) / prev.get("close", price) * 100) if prev.get("close", 0) > 0 else 0
            else:
                # 如果没有数据库数据，使用 market_engine 的数据
                quote = market_engine.get_stock_quote(game_code)
                if quote:
                    price = quote.get("price", 0)
                    change_pct = quote.get("change_pct", 0)
                else:
                    continue
            
            # 获取股票基础信息
            stock_info = market_engine.stocks.get(game_code)
            
            stocks.append({
                "code": game_code,
                "name": stock_info.name if stock_info else game_code,
                "real_name": real_name,
                "real_symbol": real_symbol,
                "sector": stock_info.sector.value if stock_info else "其他",
                "price": round(price, 2),
                "change_pct": round(change_pct, 2),
                "pe_ratio": stock_info.pe_ratio if stock_info else 0,
                "dividend_yield": stock_info.dividend_yield * 100 if stock_info else 0,
                "description": stock_info.description if stock_info else ""
            })
        
        return {"success": True, "stocks": stocks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/market/stock/{stock_id}")
async def get_stock_detail(stock_id: str, days: int = 30):
    """获取单只股票详情和K线数据"""
    try:
        from core.systems.market_engine import market_engine
        stock = market_engine.get_stock_quote(stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail="股票不存在")
        klines = market_engine.get_stock_kline(stock_id, days)
        return {"success": True, "stock": stock, "klines": klines}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/market/state")
async def get_market_state():
    """获取市场整体状态"""
    try:
        from core.systems.market_engine import market_engine
        state = market_engine.get_market_overview()
        return {"success": True, "state": state}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/market/kline/{stock_id}")
async def get_stock_kline(stock_id: str, period: str = "day"):
    """获取股票K线数据 - 从 stock.db 数据库读取真实数据"""
    try:
        from core.systems.market_engine import market_engine
        from core.systems.longbridge_client import longbridge_client
        
        # 获取当前股票信息
        stock = market_engine.get_stock_quote(stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        # 从数据库获取K线数据
        days = 60 if period == "day" else (52 if period == "week" else 24)
        kline_data = longbridge_client.get_kline_from_db(stock_id, days * 5)  # 获取更多数据用于周K/月K聚合
        
        if not kline_data or len(kline_data) == 0:
            # 如果数据库没有数据，尝试从 API 获取
            kline_data = longbridge_client.get_game_stock_kline(stock_id, days, force_refresh=True)
        
        if not kline_data:
            raise HTTPException(status_code=404, detail="K线数据不存在")
        
        # 根据周期聚合数据
        if period == "week":
            kline_data = _aggregate_kline_weekly(kline_data)
        elif period == "month":
            kline_data = _aggregate_kline_monthly(kline_data)
        
        # 格式化日期显示
        formatted_kline = []
        for k in kline_data[-days:]:  # 只取最近的数据
            date_str = k.get("date", "")
            if period == "day":
                # 日K: 显示 MM/DD
                if len(date_str) >= 10:
                    formatted_date = f"{date_str[5:7]}/{date_str[8:10]}"
                else:
                    formatted_date = date_str
            elif period == "week":
                # 周K: 显示 MM/DD
                if len(date_str) >= 10:
                    formatted_date = f"{date_str[5:7]}/{date_str[8:10]}"
                else:
                    formatted_date = date_str
            else:
                # 月K: 显示 YYYY/MM
                if len(date_str) >= 7:
                    formatted_date = f"{date_str[0:4]}/{date_str[5:7]}"
                else:
                    formatted_date = date_str
            
            formatted_kline.append({
                "date": formatted_date,
                "open": round(k.get("open", 0), 2),
                "close": round(k.get("close", 0), 2),
                "high": round(k.get("high", 0), 2),
                "low": round(k.get("low", 0), 2),
                "volume": int(k.get("volume", 0))
            })
        
        return {"success": True, "kline": formatted_kline}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/market/simulate")
async def simulate_market_day():
    """模拟一天的市场变化（供测试用）"""
    try:
        from core.systems.market_engine import market_engine
        market_engine.simulate_day()
        return {"success": True, "message": "市场已模拟一天"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stock/buy")
async def buy_stock(data: dict):
    """买入股票"""
    try:
        from core.systems.market_engine import market_engine
        session_id = data.get("session_id")
        stock_id = data.get("stock_id")
        shares = data.get("shares", 0)
        
        if not session_id or not stock_id or shares <= 0:
            raise HTTPException(status_code=400, detail="参数错误")
        
        # 获取股票信息
        stock = market_engine.get_stock_quote(stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        price = stock["price"]
        total_cost = int(price * shares)
        
        # 检查现金
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT credits, username FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            cash, username = row
            if cash < total_cost:
                return {"success": False, "message": f"现金不足，需要¥{total_cost:,}"}
            
            # 扣除现金
            new_cash = cash - total_cost
            cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            
            # 更新持仓
            cursor.execute('''
                SELECT shares, avg_cost FROM stock_holdings 
                WHERE session_id = ? AND stock_id = ?
            ''', (session_id, stock_id))
            existing = cursor.fetchone()
            
            if existing:
                old_shares, old_cost = existing
                new_shares = old_shares + shares
                new_avg_cost = (old_shares * old_cost + shares * price) / new_shares
                cursor.execute('''
                    UPDATE stock_holdings SET shares = ?, avg_cost = ?
                    WHERE session_id = ? AND stock_id = ?
                ''', (new_shares, new_avg_cost, session_id, stock_id))
            else:
                current_month = game_service.db.get_session_month(session_id)
                cursor.execute('''
                    INSERT INTO stock_holdings (session_id, stock_id, stock_name, shares, avg_cost, buy_month)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, stock_id, stock["name"], shares, price, current_month))
            
            # 记录交易
            current_month = game_service.db.get_session_month(session_id)
            cursor.execute('''
                INSERT INTO stock_transactions 
                (session_id, stock_id, stock_name, action, shares, price, total_amount, month)
                VALUES (?, ?, ?, 'buy', ?, ?, ?, ?)
            ''', (session_id, stock_id, stock["name"], shares, price, total_cost, current_month))
            
            # 添加到主交易记录表
            cursor.execute('''
                INSERT INTO transactions (username, session_id, round_num, transaction_name, amount, ai_thoughts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, session_id, current_month, f'买入{stock["name"]}', -total_cost, f'买入{stock["name"]} {shares}股，价格¥{price:.2f}'))
            
            conn.commit()
        
        # 记录行为日志
        try:
            if game_service.behavior_system:
                from core.systems.macro_economy import macro_economy
                market_state = {
                    'economic_phase': macro_economy.current_phase,
                }
                action_data = {
                    'amount': total_cost,
                    'cash': cash,
                    'monthly_expense': 3000,  # 可以从数据库获取
                }
                game_service.behavior_system.log_action(
                    session_id, current_month, 'stock_buy', action_data, market_state
                )
        except Exception as e:
            print(f"[BehaviorLog] Failed to log stock buy: {e}")
        
        # 检查成就解锁（首次买股票）
        unlocked_achievements = []
        try:
            from core.systems.achievement_system import achievement_system
            
            # 获取已解锁成就
            with sqlite3.connect(game_service.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT achievement_id, unlocked_month FROM achievements_unlocked WHERE session_id = ?', (session_id,))
                unlocked_rows = cursor.fetchall()
                unlocked_list = [{"achievement_id": r[0], "unlocked_month": r[1]} for r in unlocked_rows]
            
            # 加载已解锁成就到系统
            achievement_system.load_unlocked_from_list(unlocked_list)
            
            # 检查首次买股票成就
            first_stock_result = achievement_system.record_first_action("stock_buy", current_month)
            if first_stock_result:
                ach = first_stock_result["achievement"]
                rewards = first_stock_result["rewards"]
                game_service.db.save_achievement_unlock(session_id, {
                    "achievement_id": ach["id"],
                    "achievement_name": ach["name"],
                    "rarity": ach["rarity"],
                    "reward_coins": rewards["coins"],
                    "reward_exp": rewards["exp"],
                    "reward_title": rewards.get("title"),
                    "unlocked_month": current_month
                })
                unlocked_achievements.append(first_stock_result)
                
            # 如果是第一个月投资，还有早起鸟儿成就
            if current_month <= 1:
                early_bird_result = achievement_system.record_special_event("early_invest", current_month)
                if early_bird_result:
                    ach = early_bird_result["achievement"]
                    rewards = early_bird_result["rewards"]
                    game_service.db.save_achievement_unlock(session_id, {
                        "achievement_id": ach["id"],
                        "achievement_name": ach["name"],
                        "rarity": ach["rarity"],
                        "reward_coins": rewards["coins"],
                        "reward_exp": rewards["exp"],
                        "reward_title": rewards.get("title"),
                        "unlocked_month": current_month
                    })
                    unlocked_achievements.append(early_bird_result)
        except Exception as e:
            print(f"[Achievement] Failed to check achievements: {e}")
        
        return {
            "success": True,
            "message": f"成功买入 {stock['name']} {shares}股",
            "price": price,
            "total_cost": total_cost,
            "new_cash": new_cash,
            "unlocked_achievements": unlocked_achievements
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stock/sell")
async def sell_stock(data: dict):
    """卖出股票"""
    try:
        from core.systems.market_engine import market_engine
        session_id = data.get("session_id")
        stock_id = data.get("stock_id")
        shares = data.get("shares", 0)
        
        if not session_id or not stock_id or shares <= 0:
            raise HTTPException(status_code=400, detail="参数错误")
        
        stock = market_engine.get_stock_quote(stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        price = stock["price"]
        
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查持仓
            cursor.execute('''
                SELECT shares, avg_cost FROM stock_holdings 
                WHERE session_id = ? AND stock_id = ?
            ''', (session_id, stock_id))
            holding = cursor.fetchone()
            
            if not holding or holding[0] < shares:
                return {"success": False, "message": "持仓不足"}
            
            old_shares, avg_cost = holding
            total_revenue = int(price * shares)
            profit = int((price - avg_cost) * shares)
            
            # 更新持仓
            new_shares = old_shares - shares
            if new_shares > 0:
                cursor.execute('''
                    UPDATE stock_holdings SET shares = ?
                    WHERE session_id = ? AND stock_id = ?
                ''', (new_shares, session_id, stock_id))
            else:
                cursor.execute('''
                    DELETE FROM stock_holdings WHERE session_id = ? AND stock_id = ?
                ''', (session_id, stock_id))
            
            # 增加现金
            cursor.execute('SELECT credits, username FROM users WHERE session_id = ?', (session_id,))
            user_row = cursor.fetchone()
            cash, username = user_row[0], user_row[1]
            new_cash = cash + total_revenue
            cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            
            # 记录交易
            current_month = game_service.db.get_session_month(session_id)
            cursor.execute('''
                INSERT INTO stock_transactions 
                (session_id, stock_id, stock_name, action, shares, price, total_amount, month, profit)
                VALUES (?, ?, ?, 'sell', ?, ?, ?, ?, ?)
            ''', (session_id, stock_id, stock["name"], shares, price, total_revenue, current_month, profit))
            
            # 添加到主交易记录表
            profit_text = f'，盈亏¥{profit:+,}' if profit != 0 else ''
            cursor.execute('''
                INSERT INTO transactions (username, session_id, round_num, transaction_name, amount, ai_thoughts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, session_id, current_month, f'卖出{stock["name"]}', total_revenue, f'卖出{stock["name"]} {shares}股，价格¥{price:.2f}{profit_text}'))
            
            conn.commit()
        
        # 记录行为日志
        try:
            if game_service.behavior_system:
                from core.systems.macro_economy import macro_economy
                market_state = {
                    'economic_phase': macro_economy.current_phase,
                }
                action_data = {
                    'amount': total_revenue,
                    'cash': cash,
                    'reason': 'stop_loss' if profit < 0 else 'take_profit'
                }
                game_service.behavior_system.log_action(
                    session_id, current_month, 'stock_sell', action_data, market_state
                )
        except Exception as e:
            print(f"[BehaviorLog] Failed to log stock sell: {e}")
        
        return {
            "success": True,
            "message": f"成功卖出 {stock['name']} {shares}股",
            "price": price,
            "total_revenue": total_revenue,
            "profit": profit,
            "new_cash": new_cash
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/holdings")
async def get_stock_holdings(session_id: str):
    """获取股票持仓"""
    try:
        from core.systems.market_engine import market_engine
        holdings = game_service.db.get_stock_holdings(session_id)
        
        # 添加当前价格和盈亏
        for h in holdings:
            stock = market_engine.get_stock_quote(h["stock_id"])
            if stock:
                h["current_price"] = stock["price"]
                h["market_value"] = int(stock["price"] * h["shares"])
                h["profit"] = int((stock["price"] - h["avg_cost"]) * h["shares"])
                h["profit_rate"] = (stock["price"] - h["avg_cost"]) / h["avg_cost"] if h["avg_cost"] > 0 else 0
        
        return {"success": True, "holdings": holdings}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/transactions")
async def get_stock_transactions(session_id: str, limit: int = 50):
    """获取股票交易历史"""
    try:
        transactions = game_service.db.get_stock_transactions(session_id, limit)
        return {"success": True, "transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 金融产品 API ============

@router.get("/products/list")
async def get_financial_products():
    """获取所有金融产品"""
    try:
        from core.systems.financial_products import product_library
        products = product_library.get_all_products_info()
        return {"success": True, "products": products}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/products/category/{category}")
async def get_products_by_category(category: str):
    """按类别获取金融产品"""
    try:
        from core.systems.financial_products import product_library, ProductCategory
        cat_map = {
            "deposit": ProductCategory.DEPOSIT,
            "bond": ProductCategory.BOND,
            "fund": ProductCategory.FUND,
            "derivative": ProductCategory.DERIVATIVE,
            "realestate": ProductCategory.REAL_ESTATE,
            "alternative": ProductCategory.ALTERNATIVE
        }
        cat = cat_map.get(category.lower())
        if not cat:
            raise HTTPException(status_code=400, detail="无效的产品类别")
        
        products = product_library.get_products_by_category(cat)
        return {"success": True, "products": [p.__dict__ for p in products]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 贷款系统 API ============

@router.get("/loans/products")
async def get_loan_products():
    """获取所有贷款产品"""
    try:
        from core.systems.debt_system import debt_system
        products = debt_system.get_loan_products()
        return {"success": True, "products": products}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/loans/apply")
async def apply_loan(data: dict):
    """申请贷款"""
    try:
        from core.systems.debt_system import debt_system
        session_id = data.get("session_id")
        product_id = data.get("product_id")
        amount = data.get("amount", 0)
        term_months = data.get("term_months", 12)
        
        if not session_id or not product_id or amount <= 0:
            raise HTTPException(status_code=400, detail="参数错误")
        
        # 获取信用分
        credit_score = game_service.db.get_latest_credit_score(session_id)
        current_month = game_service.db.get_session_month(session_id)
        
        success, result = debt_system.apply_loan(product_id, amount, term_months, credit_score, current_month)
        
        if success:
            loan = result
            # 保存贷款到数据库
            game_service.db.save_loan(session_id, {
                "loan_id": loan.id,
                "loan_type": loan.loan_type.value,
                "product_name": loan.product_name,
                "principal": loan.principal,
                "remaining_principal": loan.remaining_principal,
                "annual_rate": loan.annual_rate,
                "term_months": loan.term_months,
                "remaining_months": loan.remaining_months,
                "monthly_payment": loan.monthly_payment,
                "repayment_method": loan.repayment_method.value,
                "start_month": loan.start_month
            })
            
            # 增加现金
            import sqlite3
            with sqlite3.connect(game_service.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT credits FROM users WHERE session_id = ?', (session_id,))
                cash = cursor.fetchone()[0]
                new_cash = cash + amount
                cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
                conn.commit()
            
            # 记录行为日志
            try:
                if game_service.behavior_system:
                    from core.systems.macro_economy import macro_economy
                    market_state = {'economic_phase': macro_economy.current_phase}
                    action_data = {
                        'amount': amount,
                        'cash': cash,
                        'use_loan': True,
                        'term_months': term_months
                    }
                    game_service.behavior_system.log_action(
                        session_id, current_month, 'loan_apply', action_data, market_state
                    )
            except Exception as e:
                print(f"[BehaviorLog] Failed to log loan apply: {e}")
            
            # 检查成就解锁（首次贷款）
            unlocked_achievements = []
            try:
                from core.systems.achievement_system import achievement_system
                
                # 获取已解锁成就
                with sqlite3.connect(game_service.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT achievement_id, unlocked_month FROM achievements_unlocked WHERE session_id = ?', (session_id,))
                    unlocked_rows = cursor.fetchall()
                    unlocked_list = [{"achievement_id": r[0], "unlocked_month": r[1]} for r in unlocked_rows]
                
                # 加载已解锁成就到系统
                achievement_system.load_unlocked_from_list(unlocked_list)
                
                # 检查首次贷款成就
                first_loan_result = achievement_system.record_first_action("loan", current_month)
                if first_loan_result:
                    ach = first_loan_result["achievement"]
                    rewards = first_loan_result["rewards"]
                    game_service.db.save_achievement_unlock(session_id, {
                        "achievement_id": ach["id"],
                        "achievement_name": ach["name"],
                        "rarity": ach["rarity"],
                        "reward_coins": rewards["coins"],
                        "reward_exp": rewards["exp"],
                        "reward_title": rewards.get("title"),
                        "unlocked_month": current_month
                    })
                    unlocked_achievements.append(first_loan_result)
            except Exception as e:
                print(f"[Achievement] Failed to check achievements: {e}")
            
            return {
                "success": True,
                "message": f"贷款审批通过，¥{amount:,}已到账",
                "loan": {
                    "id": loan.id,
                    "monthly_payment": loan.monthly_payment,
                    "total_interest": loan.monthly_payment * loan.term_months - loan.principal
                },
                "new_cash": new_cash,
                "unlocked_achievements": unlocked_achievements
            }
        else:
            return {"success": False, "message": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/loans/active")
async def get_active_loans(session_id: str):
    """获取活跃贷款列表"""
    try:
        loans = game_service.db.get_loans(session_id, active_only=True)
        return {"success": True, "loans": loans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/credit/score")
async def get_credit_score(session_id: str):
    """获取信用分"""
    try:
        score = game_service.db.get_latest_credit_score(session_id)
        history = game_service.db.get_credit_history(session_id, 12)
        return {"success": True, "score": score, "history": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 保险系统 API ============

@router.get("/insurance/products")
async def get_insurance_products():
    """获取所有保险产品"""
    try:
        from core.systems.insurance_system import insurance_system
        products = insurance_system.get_available_products()
        return {"success": True, "products": [
            {
                "id": p.id,
                "name": p.name,
                "type": p.insurance_type.value,
                "monthly_premium": p.monthly_premium,
                "coverage_amount": p.coverage_amount,
                "deductible": p.deductible,
                "coverage_ratio": p.coverage_ratio,
                "description": p.description,
                "covers": p.covers
            }
            for p in products
        ]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/insurance/purchase")
async def purchase_insurance(data: dict):
    """购买保险"""
    try:
        from core.systems.insurance_system import insurance_system
        session_id = data.get("session_id")
        product_id = data.get("product_id")
        term_months = data.get("term_months", -1)
        
        if not session_id or not product_id:
            raise HTTPException(status_code=400, detail="参数错误")
        
        current_month = game_service.db.get_session_month(session_id)
        insurance_system.current_month = current_month
        
        success, result = insurance_system.purchase_insurance(product_id, term_months)
        
        if success:
            policy = result
            # 保存保单到数据库
            game_service.db.save_insurance_policy(session_id, {
                "policy_id": policy.id,
                "product_id": policy.product_id,
                "product_name": policy.product_name,
                "insurance_type": policy.insurance_type.value,
                "monthly_premium": policy.monthly_premium,
                "coverage_amount": policy.coverage_amount,
                "deductible": policy.deductible,
                "coverage_ratio": policy.coverage_ratio,
                "start_month": policy.start_month,
                "remaining_months": policy.remaining_months,
                "max_claims": policy.max_claims
            })
            
            # 记录行为日志
            try:
                if game_service.behavior_system:
                    from core.systems.macro_economy import macro_economy
                    market_state = {'economic_phase': macro_economy.current_phase}
                    action_data = {
                        'amount': policy.monthly_premium,
                        'coverage': policy.coverage_amount,
                        'insurance_type': policy.insurance_type.value
                    }
                    game_service.behavior_system.log_action(
                        session_id, current_month, 'insurance_buy', action_data, market_state
                    )
            except Exception as e:
                print(f"[BehaviorLog] Failed to log insurance buy: {e}")
            
            # 检查成就解锁（首次购买保险）
            unlocked_achievements = []
            try:
                from core.systems.achievement_system import achievement_system
                import sqlite3
                
                # 获取已解锁成就
                with sqlite3.connect(game_service.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT achievement_id, unlocked_month FROM achievements_unlocked WHERE session_id = ?', (session_id,))
                    unlocked_rows = cursor.fetchall()
                    unlocked_list = [{"achievement_id": r[0], "unlocked_month": r[1]} for r in unlocked_rows]
                
                # 加载已解锁成就到系统
                achievement_system.load_unlocked_from_list(unlocked_list)
                
                # 检查首次保险成就
                first_insurance_result = achievement_system.record_first_action("insurance", current_month)
                if first_insurance_result:
                    ach = first_insurance_result["achievement"]
                    rewards = first_insurance_result["rewards"]
                    game_service.db.save_achievement_unlock(session_id, {
                        "achievement_id": ach["id"],
                        "achievement_name": ach["name"],
                        "rarity": ach["rarity"],
                        "reward_coins": rewards["coins"],
                        "reward_exp": rewards["exp"],
                        "reward_title": rewards.get("title"),
                        "unlocked_month": current_month
                    })
                    unlocked_achievements.append(first_insurance_result)
            except Exception as e:
                print(f"[Achievement] Failed to check achievements: {e}")
            
            return {
                "success": True,
                "message": f"成功购买{policy.product_name}",
                "policy": {
                    "id": policy.id,
                    "name": policy.product_name,
                    "monthly_premium": policy.monthly_premium,
                    "coverage": policy.coverage_amount
                },
                "unlocked_achievements": unlocked_achievements
            }
        else:
            return {"success": False, "message": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/insurance/policies")
async def get_insurance_policies(session_id: str):
    """获取保险保单列表"""
    try:
        policies = game_service.db.get_insurance_policies(session_id)
        return {"success": True, "policies": policies}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 成就系统 API ============

@router.get("/achievements/all")
async def get_all_achievements():
    """获取所有成就定义"""
    try:
        from core.systems.achievement_system import ACHIEVEMENTS
        return {"success": True, "achievements": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "category": a.category.value,
                "rarity": a.rarity.value,
                "icon": a.icon,
                "condition": a.condition_desc,
                "reward_coins": a.reward_coins,
                "reward_exp": a.reward_exp,
                "reward_title": a.reward_title,
                "hidden": a.hidden
            }
            for a in ACHIEVEMENTS if not a.hidden
        ]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/achievements/unlocked")
async def get_unlocked_achievements(session_id: str):
    """获取已解锁成就"""
    try:
        achievements = game_service.db.get_unlocked_achievements(session_id)
        stats = game_service.db.get_achievement_stats(session_id)
        return {"success": True, "achievements": achievements, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/achievements/check")
async def check_achievements(data: dict):
    """检查并解锁成就"""
    try:
        from core.systems.achievement_system import achievement_system
        session_id = data.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required")
        
        # 获取玩家状态
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT credits FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="用户不存在")
            cash = row[0]
            
            # 计算总资产
            cursor.execute('SELECT SUM(amount) FROM investments WHERE session_id = ? AND remaining_months > 0', (session_id,))
            invested = cursor.fetchone()[0] or 0
            total_assets = cash + invested
            
            # 获取该用户已解锁的成就，避免重复解锁
            cursor.execute('SELECT achievement_id, unlocked_month FROM achievements_unlocked WHERE session_id = ?', (session_id,))
            unlocked_rows = cursor.fetchall()
            unlocked_list = [{"achievement_id": r[0], "unlocked_month": r[1]} for r in unlocked_rows]
        
        # 加载已解锁成就到系统内存
        achievement_system.load_unlocked_from_list(unlocked_list)
        
        current_month = game_service.db.get_session_month(session_id)
        
        # 检查财富成就
        unlocked = achievement_system.check_wealth_achievements(total_assets, current_month)
        
        # 保存解锁的成就
        for unlock in unlocked:
            ach = unlock["achievement"]
            rewards = unlock["rewards"]
            game_service.db.save_achievement_unlock(session_id, {
                "achievement_id": ach["id"],
                "achievement_name": ach["name"],
                "rarity": ach["rarity"],
                "reward_coins": rewards["coins"],
                "reward_exp": rewards["exp"],
                "reward_title": rewards.get("title"),
                "unlocked_month": current_month
            })
        
        return {"success": True, "unlocked": unlocked}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 现金流 API ============

@router.get("/cashflow/summary")
async def get_cashflow_summary(session_id: str):
    """获取现金流汇总"""
    try:
        history = game_service.db.get_cashflow_history(session_id, 12)
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 宏观经济 API ============

@router.get("/economy/state")
async def get_economy_state():
    """获取当前经济状态"""
    try:
        from core.systems.macro_economy import macro_economy
        state = macro_economy.get_current_state()
        return {
            "success": True,
            "state": {
                "gdp_growth": state.gdp_growth,
                "inflation": state.inflation,
                "interest_rate": state.interest_rate,
                "unemployment": state.unemployment,
                "cpi_index": state.cpi_index,
                "house_price_index": state.house_price_index,
                "stock_index": state.stock_index,
                "phase": state.phase.value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/economy/advice")
async def get_economy_advice():
    """获取投资建议"""
    try:
        from core.systems.macro_economy import macro_economy
        advice = macro_economy.get_investment_advice()
        sectors = macro_economy.get_sector_outlook()
        return {"success": True, "advice": advice, "sectors": sectors}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 职业系统路由 ====================

@router.get("/career/jobs")
async def get_available_jobs():
    """获取所有可用职位"""
    from core.systems.career_system import career_system
    return career_system.get_available_jobs()

@router.get("/career/current/{session_id}")
async def get_current_career(session_id: str):
    """获取玩家当前职业状态"""
    from core.systems.career_system import career_system
    career_info = career_system.get_career_status(session_id)
    return {"success": True, "career": career_info}

@router.post("/career/apply")
async def apply_for_job(request: dict):
    """申请职位"""
    from core.systems.career_system import career_system
    session_id = request.get("session_id")
    job_id = request.get("job_id")
    player_skills = request.get("skills", {})
    
    result = career_system.apply_for_job(session_id, job_id, player_skills)
    return result

@router.post("/career/resign")
async def resign_job(request: dict):
    """辞职"""
    from core.systems.career_system import career_system
    session_id = request.get("session_id")
    result = career_system.resign(session_id)
    return result

@router.get("/career/skills")
async def get_all_skills():
    """获取所有可学习技能"""
    from core.systems.career_system import career_system
    return career_system.get_all_skills()

@router.post("/career/learn-skill")
async def learn_skill(request: dict):
    """学习技能"""
    from core.systems.career_system import career_system
    session_id = request.get("session_id")
    skill_id = request.get("skill_id")
    result = career_system.learn_skill(session_id, skill_id)
    return result

@router.get("/career/side-businesses")
async def get_side_businesses():
    """获取可用的副业"""
    from core.systems.career_system import career_system
    return career_system.get_available_side_businesses()

@router.post("/career/start-side-business")
async def start_side_business(request: dict):
    """开始副业"""
    from core.systems.career_system import career_system
    session_id = request.get("session_id")
    business_id = request.get("business_id")
    result = career_system.start_side_business(session_id, business_id)
    return result

@router.get("/career/salary/{session_id}")
async def calculate_salary(session_id: str):
    """计算当前薪资"""
    from core.systems.career_system import career_system
    salary = career_system.calculate_monthly_salary(session_id)
    return {"success": True, "salary": salary}


# ==================== 事件系统路由 ====================

@router.post("/events/generate")
async def generate_events(request: dict):
    """生成随机事件"""
    try:
        from core.systems.event_system import event_system
        session_id = request.get("session_id")
        player_state = request.get("player_state", {})
        count = request.get("count", 1)
        
        events = event_system.get_random_events(session_id, player_state, count)
        # 转换为可序列化的格式
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "category": event.category.value,
                "options": [
                    {
                        "id": opt.id,
                        "text": opt.text,
                        "success_rate": opt.success_rate,
                        "impacts": [
                            {
                                "type": imp.impact_type.value,
                                "value": imp.value,
                                "duration": imp.duration,
                                "description": imp.description
                            } for imp in opt.impacts
                        ]
                    } for opt in event.options
                ]
            })
        return {"success": True, "events": events_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/events/respond")
async def respond_to_event(request: dict):
    """响应事件选择"""
    try:
        from core.systems.event_system import event_system
        session_id = request.get("session_id")
        event_id = request.get("event_id")
        option_id = request.get("option_id")
        player_state = request.get("player_state", {})
        
        result = event_system.apply_event_choice(session_id, event_id, option_id, player_state)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/events/history/{session_id}")
async def get_event_history(session_id: str):
    """获取事件历史"""
    try:
        from core.systems.event_system import event_system
        history = event_system.get_event_history(session_id)
        return {"success": True, "history": history}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/events/active-effects/{session_id}")
async def get_active_effects(session_id: str):
    """获取当前活跃的持续效果"""
    try:
        from core.systems.event_system import event_system
        effects = event_system.get_active_effects(session_id)
        return {"success": True, "effects": effects}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/events/update-effects")
async def update_effects(request: dict):
    """更新活跃效果（时间推进时调用）"""
    try:
        from core.systems.event_system import event_system
        session_id = request.get("session_id")
        active_effects = event_system.update_active_effects(session_id)
        return {"success": True, "active_effects": active_effects}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 银行系统路由 ====================

@router.get("/banking/deposits/{session_id}")
async def get_deposits(session_id: str):
    """获取存款信息"""
    try:
        import sqlite3
        # 直接从数据库查询存款信息
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, product_id, product_name, amount, buy_price, current_value, 
                       buy_month, maturity_month
                FROM financial_holdings
                WHERE session_id = ? AND product_type = 'deposit' AND is_active = 1
            ''', (session_id,))
            rows = cursor.fetchall()
        
        deposits = []
        total = 0
        monthly_interest = 0
        for r in rows:
            rate = r[4] or 0.0035  # buy_price 存储的是利率
            deposit = {
                'id': r[0],
                'product_id': r[1], 
                'product_name': r[2] or '活期存款',
                'amount': r[3], 
                'rate': rate,
                'value': r[5] or r[3],
                'buy_month': r[6], 
                'maturity_month': r[7]
            }
            deposits.append(deposit)
            total += r[3]  # amount
            monthly_interest += int(r[3] * rate / 12)
        
        return {
            "success": True, 
            "deposits": deposits,
            "total": total,
            "monthly_interest": monthly_interest
        }
    except Exception as e:
        print(f"[Banking] Get deposits error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": True, "deposits": [], "total": 0, "monthly_interest": 0}

@router.post("/banking/deposit")
async def make_deposit(request: dict):
    """存款"""
    try:
        import sqlite3
        session_id = request.get("session_id")
        amount = request.get("amount", 0)
        deposit_type = request.get("type", "demand")
        
        if not session_id or amount <= 0:
            return {"success": False, "error": "参数错误"}
        
        # 获取当前月份
        current_month = game_service.db.get_session_month(session_id) if hasattr(game_service.db, 'get_session_month') else 1
        
        # 直接从数据库获取现金
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT credits, username FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "用户不存在"}
            
            cash, username = row[0], row[1]
            if cash < amount:
                return {"success": False, "error": "现金不足"}
            
            # 扣除现金
            new_cash = cash - amount
            cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            
            # 获取当前月份
            cursor.execute('SELECT current_month FROM sessions WHERE session_id = ?', (session_id,))
            month_row = cursor.fetchone()
            current_month = month_row[0] if month_row else 1
            
            # 添加交易记录到 transactions 表
            deposit_names = {'demand': '活期存款', 'fixed_3m': '3个月定期', 'fixed_1y': '1年定期', 'fixed_3y': '3年定期'}
            deposit_name = deposit_names.get(deposit_type, '存款')
            cursor.execute('''
                INSERT INTO transactions (username, session_id, round_num, transaction_name, amount, ai_thoughts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, session_id, current_month, f'存入{deposit_name}', -amount, f'存入银行{deposit_name}，金额¥{amount:,}'))
            
            conn.commit()
        
        # 添加存款记录
        rate_map = {'demand': 0.0035, 'fixed_3m': 0.015, 'fixed_1y': 0.025, 'fixed_3y': 0.035}
        rate = rate_map.get(deposit_type, 0.0035)
        
        # 调用数据库方法保存存款
        game_service.db.add_deposit(session_id, amount, deposit_type, rate, current_month)
        
        # 记录行为日志
        try:
            if game_service.behavior_system:
                from core.systems.macro_economy import macro_economy
                market_state = {'economic_phase': macro_economy.current_phase}
                action_data = {
                    'amount': amount,
                    'cash': cash,
                    'deposit_type': deposit_type,
                    'rate': rate
                }
                game_service.behavior_system.log_action(
                    session_id, current_month, 'bank_deposit', action_data, market_state
                )
        except Exception as e:
            print(f"[BehaviorLog] Failed to log deposit: {e}")
        
        # 检查成就解锁（首次存款）
        unlocked_achievements = []
        try:
            from core.systems.achievement_system import achievement_system
            import sqlite3
            
            # 获取已解锁成就
            with sqlite3.connect(game_service.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT achievement_id, unlocked_month FROM achievements_unlocked WHERE session_id = ?', (session_id,))
                unlocked_rows = cursor.fetchall()
                unlocked_list = [{"achievement_id": r[0], "unlocked_month": r[1]} for r in unlocked_rows]
            
            # 加载已解锁成就到系统
            achievement_system.load_unlocked_from_list(unlocked_list)
            
            # 检查首次存款成就
            first_deposit_result = achievement_system.record_first_action("deposit", current_month)
            if first_deposit_result:
                ach = first_deposit_result["achievement"]
                rewards = first_deposit_result["rewards"]
                game_service.db.save_achievement_unlock(session_id, {
                    "achievement_id": ach["id"],
                    "achievement_name": ach["name"],
                    "rarity": ach["rarity"],
                    "reward_coins": rewards["coins"],
                    "reward_exp": rewards["exp"],
                    "reward_title": rewards.get("title"),
                    "unlocked_month": current_month
                })
                unlocked_achievements.append(first_deposit_result)
        except Exception as e:
            print(f"[Achievement] Failed to check achievements: {e}")
        
        return {"success": True, "message": f"成功存入 ¥{amount}", "unlocked_achievements": unlocked_achievements}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@router.get("/banking/loans/{session_id}")
async def get_user_loans(session_id: str):
    """获取用户贷款列表"""
    try:
        loans = game_service.db.get_loans(session_id) if hasattr(game_service.db, 'get_loans') else []
        formatted_loans = []
        for loan in loans:
            formatted_loans.append({
                "id": loan.get("loan_id"),
                "loan_type": loan.get("loan_type", "personal"),
                "product_name": loan.get("product_name", "消费贷"),
                "principal": loan.get("principal", 0),
                "remaining_principal": loan.get("remaining_principal", 0),
                "annual_rate": loan.get("annual_rate", 0.08),
                "monthly_payment": loan.get("monthly_payment", 0),
                "remaining_months": loan.get("remaining_months", 0),
                "term_months": loan.get("term_months", 12),
                "start_month": loan.get("start_month", 1),
                "status": "active",
                "statusText": "还款中"
            })
        return {"success": True, "loans": formatted_loans}
    except Exception as e:
        return {"success": True, "loans": []}

@router.post("/banking/loan")
async def apply_bank_loan(request: dict):
    """申请银行贷款"""
    try:
        import sqlite3
        import uuid
        
        session_id = request.get("session_id")
        amount = request.get("amount", 0)
        loan_type = request.get("type", "personal")
        term_months = request.get("term_months", 12)
        
        if not session_id or amount <= 0:
            return {"success": False, "error": "参数错误"}
        
        # 贷款产品配置
        loan_products = {
            "personal": {"name": "个人消费贷", "rate": 0.08, "max_amount": 50000, "min_credit": 600},
            "business": {"name": "创业贷款", "rate": 0.06, "max_amount": 200000, "min_credit": 700},
            "mortgage": {"name": "房屋贷款", "rate": 0.045, "max_amount": 1000000, "min_credit": 650},
            "emergency": {"name": "应急借款", "rate": 0.15, "max_amount": 10000, "min_credit": 0}
        }
        
        product = loan_products.get(loan_type)
        if not product:
            return {"success": False, "error": f"贷款产品不存在: {loan_type}"}
        
        if amount > product["max_amount"]:
            return {"success": False, "error": f"超过最大贷款额度 ¥{product['max_amount']:,}"}
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取当前现金和用户名
            cursor.execute('SELECT credits, username FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "用户不存在"}
            
            current_cash, username = row[0], row[1]
            
            # 简化信用评估：基于资产
            credit_score = 650 + min(current_cash // 10000, 200)
            
            if credit_score < product["min_credit"]:
                return {"success": False, "error": f"信用分不足，需要 {product['min_credit']} 分，当前 {credit_score} 分"}
            
            # 获取当前月份
            cursor.execute('SELECT current_month FROM sessions WHERE session_id = ?', (session_id,))
            month_row = cursor.fetchone()
            current_month = month_row[0] if month_row else 1
            
            # 计算月供 (等额本息)
            monthly_rate = product["rate"] / 12
            if monthly_rate > 0:
                monthly_payment = int(amount * monthly_rate * ((1 + monthly_rate) ** term_months) / (((1 + monthly_rate) ** term_months) - 1))
            else:
                monthly_payment = amount // term_months
            
            loan_id = f"loan_{str(uuid.uuid4())[:8]}"
            
            # 保存贷款
            cursor.execute('''
                INSERT INTO loans 
                (session_id, loan_id, loan_type, product_name, principal, remaining_principal, 
                 annual_rate, term_months, remaining_months, monthly_payment, repayment_method, start_month)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, loan_id, loan_type, product["name"],
                amount, amount, product["rate"], term_months, term_months,
                monthly_payment, "等额本息", current_month
            ))
            
            # 增加现金
            new_cash = current_cash + amount
            cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            
            # 添加交易记录到 transactions 表
            cursor.execute('''
                INSERT INTO transactions (username, session_id, round_num, transaction_name, amount, ai_thoughts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, session_id, current_month, f'申请{product["name"]}', amount, f'贷款批准，本金¥{amount:,}，月供¥{monthly_payment:,}，期限{term_months}个月'))
            
            conn.commit()
        
        # 检查成就解锁（首次贷款）
        unlocked_achievements = []
        try:
            from core.systems.achievement_system import achievement_system
            import sqlite3
            
            # 获取已解锁成就
            with sqlite3.connect(game_service.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT achievement_id, unlocked_month FROM achievements_unlocked WHERE session_id = ?', (session_id,))
                unlocked_rows = cursor.fetchall()
                unlocked_list = [{"achievement_id": r[0], "unlocked_month": r[1]} for r in unlocked_rows]
            
            # 加载已解锁成就到系统
            achievement_system.load_unlocked_from_list(unlocked_list)
            
            # 检查首次贷款成就
            first_loan_result = achievement_system.record_first_action("loan", current_month)
            if first_loan_result:
                ach = first_loan_result["achievement"]
                rewards = first_loan_result["rewards"]
                game_service.db.save_achievement_unlock(session_id, {
                    "achievement_id": ach["id"],
                    "achievement_name": ach["name"],
                    "rarity": ach["rarity"],
                    "reward_coins": rewards["coins"],
                    "reward_exp": rewards["exp"],
                    "reward_title": rewards.get("title"),
                    "unlocked_month": current_month
                })
                unlocked_achievements.append(first_loan_result)
        except Exception as e:
            print(f"[Achievement] Failed to check achievements: {e}")
            
        return {
            "success": True,
            "message": f"贷款批准，¥{amount:,} 已到账",
            "loan": {
                "id": loan_id,
                "monthly_payment": monthly_payment,
                "total_interest": monthly_payment * term_months - amount
            },
            "new_cash": new_cash,
            "unlocked_achievements": unlocked_achievements
        }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@router.get("/banking/credit/{session_id}")
async def get_credit_score_api(session_id: str):
    """获取信用评分"""
    try:
        import sqlite3
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取用户资产
            cursor.execute('SELECT credits FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": True, "score": 650}
            
            cash = row[0]
            
            # 获取投资资产
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM investments 
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            invested = cursor.fetchone()[0] or 0
            
            # 简化信用评估
            total_assets = cash + invested
            credit_score = 650 + min(total_assets // 10000 * 5, 200)
            credit_score = max(300, min(850, credit_score))
            
            return {"success": True, "score": credit_score}
    except Exception as e:
        return {"success": True, "score": 650}


# ==================== 保护系统路由 ====================

@router.get("/protection/status/{session_id}")
async def get_protection_status(session_id: str):
    """获取玩家保护状态"""
    from core.systems.protection_system import protection_system
    status = protection_system.get_protection_status(session_id)
    return {"success": True, "status": status}

@router.post("/protection/check-trade")
async def check_trade_allowed(request: dict):
    """检查交易是否被允许"""
    from core.systems.protection_system import protection_system
    session_id = request.get("session_id")
    trade_type = request.get("trade_type")
    amount = request.get("amount", 0)
    leverage = request.get("leverage", 1)
    
    result = protection_system.check_trade_allowed(session_id, trade_type, amount, leverage)
    return result

@router.post("/protection/declare-bankruptcy")
async def declare_bankruptcy(request: dict):
    """宣布破产"""
    from core.systems.protection_system import protection_system
    session_id = request.get("session_id")
    current_skills = request.get("skills", {})
    
    result = protection_system.declare_bankruptcy(session_id, current_skills)
    return result

@router.get("/protection/warnings/{session_id}")
async def get_warnings(session_id: str):
    """获取风险警告"""
    from core.systems.protection_system import protection_system
    player_state = {}  # 可从数据库获取
    warnings = protection_system.generate_warnings(session_id, player_state)
    return {"success": True, "warnings": warnings}

@router.get("/protection/suggestions/{session_id}")
async def get_suggestions(session_id: str):
    """获取投资建议"""
    from core.systems.protection_system import protection_system
    portfolio = {}  # 可从数据库获取
    suggestions = protection_system.get_diversification_suggestions(session_id, portfolio)
    return {"success": True, "suggestions": suggestions}


# ==================== 排行榜路由 ====================

@router.get("/leaderboard/assets")
async def get_asset_leaderboard(limit: int = 50):
    """获取资产排行榜"""
    try:
        from core.systems.leaderboard_system import leaderboard_system
        if not leaderboard_system.db and game_service.db:
            leaderboard_system.set_db(game_service.db)
        leaderboard = leaderboard_system.get_total_assets_leaderboard(limit)
        return {"success": True, "leaderboard": leaderboard}
    except Exception as e:
        print(f"[Leaderboard] Error: {e}")
        return {"success": True, "leaderboard": []}

@router.get("/leaderboard/growth")
async def get_growth_leaderboard(limit: int = 50):
    """获取增长率排行榜"""
    try:
        from core.systems.leaderboard_system import leaderboard_system
        if not leaderboard_system.db and game_service.db:
            leaderboard_system.set_db(game_service.db)
        leaderboard = leaderboard_system.get_growth_leaderboard(limit)
        return {"success": True, "leaderboard": leaderboard}
    except Exception as e:
        print(f"[Leaderboard] Error: {e}")
        return {"success": True, "leaderboard": []}

@router.get("/leaderboard/roi")
async def get_roi_leaderboard(limit: int = 50):
    """获取投资回报率排行榜"""
    try:
        from core.systems.leaderboard_system import leaderboard_system
        if not leaderboard_system.db and game_service.db:
            leaderboard_system.set_db(game_service.db)
        leaderboard = leaderboard_system.get_investment_return_leaderboard(limit)
        return {"success": True, "leaderboard": leaderboard}
    except Exception as e:
        print(f"[Leaderboard] Error: {e}")
        return {"success": True, "leaderboard": []}

@router.get("/leaderboard/achievements")
async def get_achievement_leaderboard(limit: int = 50):
    """获取成就排行榜"""
    try:
        from core.systems.leaderboard_system import leaderboard_system
        if not leaderboard_system.db and game_service.db:
            leaderboard_system.set_db(game_service.db)
        leaderboard = leaderboard_system.get_achievement_leaderboard(limit)
        return {"success": True, "leaderboard": leaderboard}
    except Exception as e:
        print(f"[Leaderboard] Error: {e}")
        return {"success": True, "leaderboard": []}

@router.get("/leaderboard/player/{session_id}")
async def get_player_ranking(session_id: str):
    """获取玩家自己的排名"""
    try:
        from core.systems.leaderboard_system import leaderboard_system, LeaderboardType
        if not leaderboard_system.db and game_service.db:
            leaderboard_system.set_db(game_service.db)
        
        # 获取玩家在各个榜单的排名
        ranking = {
            "assets_rank": None,
            "growth_rank": None,
            "roi_rank": None,
            "achievements_rank": None,
            "name": None,
            "total_assets": 0
        }
        
        try:
            assets_rank = leaderboard_system.get_player_rank(session_id, LeaderboardType.TOTAL_ASSETS)
            if assets_rank:
                ranking["assets_rank"] = assets_rank.get("rank")
                ranking["name"] = assets_rank.get("name")
                ranking["total_assets"] = assets_rank.get("total_assets")
        except Exception:
            pass
        
        try:
            growth_rank = leaderboard_system.get_player_rank(session_id, LeaderboardType.NET_WORTH_GROWTH)
            if growth_rank:
                ranking["growth_rank"] = growth_rank.get("rank")
                ranking["growth_rate"] = growth_rank.get("growth_rate")
        except Exception:
            pass
        
        try:
            roi_rank = leaderboard_system.get_player_rank(session_id, LeaderboardType.INVESTMENT_RETURN)
            if roi_rank:
                ranking["roi_rank"] = roi_rank.get("rank")
                ranking["roi"] = roi_rank.get("total_profit")
        except Exception:
            pass
        
        try:
            achievements_rank = leaderboard_system.get_player_rank(session_id, LeaderboardType.ACHIEVEMENT_COUNT)
            if achievements_rank:
                ranking["achievements_rank"] = achievements_rank.get("rank")
                ranking["achievement_count"] = achievements_rank.get("achievement_count")
        except Exception:
            pass
        
        return {"success": True, "ranking": ranking}
    except Exception as e:
        print(f"[Leaderboard] Error getting player ranking: {e}")
        return {"success": True, "ranking": {"assets_rank": None, "name": None}}

@router.post("/leaderboard/update")
async def update_player_stats(request: dict):
    """更新玩家统计数据"""
    from core.systems.leaderboard_system import leaderboard_system
    session_id = request.get("session_id")
    player_name = request.get("player_name", "匿名玩家")
    total_assets = request.get("total_assets", 0)
    achievement_count = request.get("achievement_count", 0)
    
    leaderboard_system.update_player_stats(
        session_id, player_name, total_assets, achievement_count
    )
    return {"success": True, "message": "Stats updated"}

@router.post("/leaderboard/record-trade")
async def record_trade(request: dict):
    """记录交易以计算ROI"""
    from core.systems.leaderboard_system import leaderboard_system
    session_id = request.get("session_id")
    invested = request.get("invested", 0)
    returned = request.get("returned", 0)
    
    leaderboard_system.record_trade(session_id, invested, returned)
    return {"success": True, "message": "Trade recorded"}


# ==================== 头像系统路由 ====================

@router.get("/avatar/shop")
async def get_avatar_shop():
    """获取头像商店列表"""
    try:
        from core.systems.avatar_system import avatar_system
        avatars = avatar_system.get_all_avatars()
        return {"success": True, "avatars": avatars}
    except Exception as e:
        print(f"[Avatar] Error getting shop: {e}")
        return {"success": False, "error": str(e)}

@router.get("/avatar/user/{session_id}")
async def get_user_avatar_info(session_id: str):
    """获取用户头像信息"""
    try:
        from core.systems.avatar_system import avatar_system
        import sqlite3
        
        # 直接查询成就金币用于调试
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT achievement_id, reward_coins FROM achievements_unlocked WHERE session_id = ?', (session_id,))
            raw_achievements = cursor.fetchall()
            print(f"[Avatar Debug] session_id: {session_id}")
            print(f"[Avatar Debug] Raw achievements: {raw_achievements}")
        
        # 获取用户金币
        coins = game_service.db.get_user_avatar_coins(session_id)
        print(f"[Avatar Debug] Calculated coins: {coins}")
        
        # 获取拥有的头像
        owned = game_service.db.get_user_avatars(session_id)
        
        # 获取当前装备的头像
        current = game_service.db.get_current_avatar(session_id)
        current_info = avatar_system.get_avatar(current)
        
        # 获取成就统计
        stats = game_service.db.get_achievement_stats(session_id)
        unlocked_achievements = game_service.db.get_unlocked_achievements(session_id)
        achievement_ids = [a['achievement_id'] for a in unlocked_achievements]
        
        return {
            "success": True,
            "coins": coins,
            "owned_avatars": owned,
            "current_avatar": current,
            "current_avatar_info": current_info,
            "achievement_count": stats['unlocked_count'],
            "achievement_ids": achievement_ids,
            "debug_achievements": raw_achievements  # 调试用
        }
    except Exception as e:
        print(f"[Avatar] Error getting user info: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e), "coins": 0, "owned_avatars": ["default_orange"], "current_avatar": "default_orange"}

@router.post("/avatar/purchase")
async def purchase_avatar(request: dict):
    """购买头像"""
    try:
        from core.systems.avatar_system import avatar_system
        
        session_id = request.get("session_id")
        avatar_id = request.get("avatar_id")
        
        if not session_id or not avatar_id:
            return {"success": False, "error": "缺少参数"}
        
        # 获取头像信息
        avatar_info = avatar_system.get_avatar(avatar_id)
        if not avatar_info:
            return {"success": False, "error": "头像不存在"}
        
        # 检查是否已拥有
        owned = game_service.db.get_user_avatars(session_id)
        if avatar_id in owned:
            return {"success": False, "error": "已拥有该头像"}
        
        # 获取用户金币和成就
        coins = game_service.db.get_user_avatar_coins(session_id)
        stats = game_service.db.get_achievement_stats(session_id)
        unlocked = game_service.db.get_unlocked_achievements(session_id)
        achievement_ids = [a['achievement_id'] for a in unlocked]
        
        # 检查是否可以购买
        can_buy, message = avatar_system.can_purchase(
            avatar_id, coins, achievement_ids, stats['unlocked_count']
        )
        
        if not can_buy:
            return {"success": False, "error": message}
        
        # 执行购买
        result = game_service.db.purchase_avatar(session_id, avatar_id, avatar_info['price'])
        if result:
            new_coins = game_service.db.get_user_avatar_coins(session_id)
            return {
                "success": True, 
                "message": f"成功购买「{avatar_info['name']}」！",
                "new_coins": new_coins
            }
        else:
            return {"success": False, "error": "购买失败"}
    except Exception as e:
        print(f"[Avatar] Error purchasing: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@router.post("/avatar/equip")
async def equip_avatar(request: dict):
    """装备头像"""
    try:
        session_id = request.get("session_id")
        avatar_id = request.get("avatar_id")
        
        if not session_id or not avatar_id:
            return {"success": False, "error": "缺少参数"}
        
        result = game_service.db.equip_avatar(session_id, avatar_id)
        if result:
            from core.systems.avatar_system import avatar_system
            avatar_info = avatar_system.get_avatar(avatar_id)
            return {
                "success": True, 
                "message": f"已装备「{avatar_info['name'] if avatar_info else avatar_id}」",
                "current_avatar": avatar_id
            }
        else:
            return {"success": False, "error": "装备失败，请确保已拥有该头像"}
    except Exception as e:
        print(f"[Avatar] Error equipping: {e}")
        return {"success": False, "error": str(e)}


# ==================== 房产系统路由 ====================

@router.get("/housing/properties/{session_id}")
async def get_user_properties(session_id: str):
    """获取用户房产列表"""
    try:
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, property_type, purchase_price, current_value, 
                       monthly_rent, is_rented, is_self_living, buy_month
                FROM properties WHERE session_id = ?
            ''', (session_id,))
            properties = []
            for r in cursor.fetchall():
                properties.append({
                    'id': r[0], 'name': r[1], 'type': r[2],
                    'purchasePrice': r[3], 'currentValue': r[4],
                    'monthlyRent': r[5], 'isRented': bool(r[6]),
                    'isSelfLiving': bool(r[7]), 'buyMonth': r[8],
                    'icon': '🏠' if r[2] == 'house' else '🏢' if r[2] == 'apartment' else '🏡'
                })
        return {"success": True, "properties": properties}
    except Exception as e:
        return {"success": True, "properties": []}

@router.get("/housing/status/{session_id}")
async def get_housing_status(session_id: str):
    """获取居住状态"""
    try:
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT living_type, property_name, monthly_cost, happiness_effect
                FROM living_status WHERE session_id = ?
            ''', (session_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "success": True,
                    "status": {
                        "type": row[0],
                        "propertyName": row[1],
                        "monthlyCost": row[2],
                        "happinessEffect": row[3]
                    }
                }
        return {"success": True, "status": {"type": "租房", "propertyName": "城中村单间", "monthlyCost": 800, "happinessEffect": -5}}
    except Exception as e:
        return {"success": True, "status": {"type": "租房", "propertyName": "城中村单间", "monthlyCost": 800, "happinessEffect": -5}}

@router.post("/housing/buy")
async def buy_property(request: dict):
    """购买房产"""
    try:
        import sqlite3
        session_id = request.get("session_id")
        property_id = request.get("property_id")
        payment_method = request.get("payment_method", "full")
        mortgage_term = request.get("mortgage_term", 360)
        
        # 房产信息映射
        property_info = {
            'apt1': {'name': '城郊小公寓', 'type': 'apartment', 'price': 500000, 'area': 45, 'expectedRent': 1500},
            'apt2': {'name': '市区精装公寓', 'type': 'apartment', 'price': 1200000, 'area': 70, 'expectedRent': 3500},
            'house1': {'name': '花园洋房', 'type': 'house', 'price': 2500000, 'area': 120, 'expectedRent': 6000},
            'house2': {'name': '学区房', 'type': 'house', 'price': 4000000, 'area': 90, 'expectedRent': 8000},
            'villa1': {'name': '郊外别墅', 'type': 'villa', 'price': 8000000, 'area': 300, 'expectedRent': 15000}
        }
        
        prop = property_info.get(property_id)
        if not prop:
            return {"success": False, "error": "房产不存在"}
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT credits FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "用户不存在"}
            
            cash = row[0]
            price = prop['price']
            
            if payment_method == 'full':
                if cash < price:
                    return {"success": False, "error": "现金不足"}
                new_cash = cash - price
            else:
                down_payment = int(price * 0.3)
                if cash < down_payment:
                    return {"success": False, "error": "首付不足"}
                new_cash = cash - down_payment
                loan_amount = int(price * 0.7)
                
                # 计算月供
                monthly_rate = 0.045 / 12
                n = mortgage_term
                monthly_payment = int((loan_amount * monthly_rate * pow(1 + monthly_rate, n)) / (pow(1 + monthly_rate, n) - 1))
                
                # 创建房贷记录
                import uuid
                loan_id = f"mortgage_{uuid.uuid4().hex[:8]}"
                cursor.execute('''
                    INSERT INTO loans (session_id, loan_id, loan_type, product_name, principal,
                        remaining_principal, annual_rate, term_months, remaining_months,
                        monthly_payment, repayment_method, start_month)
                    VALUES (?, ?, 'mortgage', ?, ?, ?, 0.045, ?, ?, ?, 'equal_payment', ?)
                ''', (session_id, loan_id, f"{prop['name']}房贷", loan_amount, loan_amount,
                      mortgage_term, mortgage_term, monthly_payment,
                      game_service.db.get_session_month(session_id)))
            
            # 确保properties表存在
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    property_type TEXT NOT NULL,
                    purchase_price INTEGER NOT NULL,
                    current_value INTEGER NOT NULL,
                    monthly_rent INTEGER DEFAULT 0,
                    is_rented INTEGER DEFAULT 0,
                    is_self_living INTEGER DEFAULT 0,
                    buy_month INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建房产记录
            cursor.execute('''
                INSERT INTO properties (session_id, name, property_type, purchase_price,
                    current_value, monthly_rent, buy_month)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, prop['name'], prop['type'], price, price,
                  prop['expectedRent'], game_service.db.get_session_month(session_id)))
            
            # 更新现金
            cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            conn.commit()
        
        # 记录行为日志
        try:
            if game_service.behavior_system:
                from core.systems.macro_economy import macro_economy
                market_state = {'economic_phase': macro_economy.current_phase}
                action_data = {
                    'amount': price,
                    'cash': cash,
                    'use_loan': payment_method != 'full',
                    'property_type': prop['type']
                }
                current_month = game_service.db.get_session_month(session_id)
                game_service.behavior_system.log_action(
                    session_id, current_month, 'house_buy', action_data, market_state
                )
        except Exception as e:
            print(f"[BehaviorLog] Failed to log house buy: {e}")
        
        return {"success": True, "message": f"成功购买{prop['name']}！", "new_cash": new_cash}
    except Exception as e:
        print(f"[Housing] Buy error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@router.post("/housing/rent")
async def rent_house(request: dict):
    """租房"""
    try:
        import sqlite3
        session_id = request.get("session_id")
        rental_id = request.get("rental_id")
        
        rental_info = {
            'basic': {'name': '城中村单间', 'monthly': 800, 'happiness': -5},
            'shared': {'name': '合租公寓', 'monthly': 1500, 'happiness': 0},
            'studio': {'name': '独立公寓', 'monthly': 3000, 'happiness': 5},
            'premium': {'name': '高档公寓', 'monthly': 6000, 'happiness': 15}
        }
        
        rental = rental_info.get(rental_id)
        if not rental:
            return {"success": False, "error": "租房选项不存在"}
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            # 确保living_status表存在
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS living_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    living_type TEXT NOT NULL,
                    property_name TEXT NOT NULL,
                    monthly_cost INTEGER NOT NULL,
                    happiness_effect INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                INSERT INTO living_status (session_id, living_type, property_name, monthly_cost, happiness_effect)
                VALUES (?, '租房', ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    property_name = excluded.property_name,
                    monthly_cost = excluded.monthly_cost,
                    happiness_effect = excluded.happiness_effect,
                    updated_at = CURRENT_TIMESTAMP
            ''', (session_id, rental['name'], rental['monthly'], rental['happiness']))
            conn.commit()
        
        # 记录行为日志
        try:
            if game_service.behavior_system:
                from core.systems.macro_economy import macro_economy
                market_state = {'economic_phase': macro_economy.current_phase}
                action_data = {
                    'amount': rental['monthly'],
                    'happiness_effect': rental['happiness'],
                    'rental_type': rental_id
                }
                current_month = game_service.db.get_session_month(session_id)
                game_service.behavior_system.log_action(
                    session_id, current_month, 'house_rent', action_data, market_state
                )
        except Exception as e:
            print(f"[BehaviorLog] Failed to log house rent: {e}")
        
        return {"success": True, "message": f"已租住{rental['name']}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/housing/mortgages/{session_id}")
async def get_mortgages(session_id: str):
    """获取房贷列表"""
    try:
        loans = game_service.db.get_loans(session_id, active_only=True)
        mortgages = [l for l in loans if l.get('loan_type') == 'mortgage']
        return {"success": True, "mortgages": mortgages}
    except Exception as e:
        return {"success": True, "mortgages": []}

@router.post("/housing/sell")
async def sell_property(request: dict):
    """出售房产"""
    try:
        import sqlite3
        session_id = request.get("session_id")
        property_id = request.get("property_id")
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取房产信息
            cursor.execute('''
                SELECT id, name, current_value, is_rented FROM properties
                WHERE id = ? AND session_id = ?
            ''', (property_id, session_id))
            prop = cursor.fetchone()
            
            if not prop:
                return {"success": False, "error": "房产不存在"}
            
            prop_id, prop_name, current_value, is_rented = prop
            
            if is_rented:
                return {"success": False, "error": "该房产正在出租中，请先解除租约"}
            
            # 售价为当前估值的95%（扣除交易费用）
            sale_price = int(current_value * 0.95)
            
            # 获取当前现金
            cursor.execute('SELECT credits FROM users WHERE session_id = ?', (session_id,))
            cash = cursor.fetchone()[0] or 0
            new_cash = cash + sale_price
            
            # 更新现金
            cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            
            # 删除房产记录
            cursor.execute('DELETE FROM properties WHERE id = ?', (prop_id,))
            
            # 检查是否有对应房贷，如果有则结清
            cursor.execute('''
                SELECT id, remaining_amount FROM loans 
                WHERE session_id = ? AND loan_type = 'mortgage' AND property_name = ?
            ''', (session_id, prop_name))
            mortgage = cursor.fetchone()
            
            if mortgage:
                mortgage_id, remaining = mortgage
                if new_cash >= remaining:
                    new_cash -= remaining
                    cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
                    cursor.execute('UPDATE loans SET is_active = 0 WHERE id = ?', (mortgage_id,))
                    sale_price -= remaining  # 实际到手
            
            conn.commit()
            
        return {"success": True, "message": f"成功出售{prop_name}！", "sale_price": sale_price}
    except Exception as e:
        print(f"[Housing] Sell error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@router.post("/housing/rentout")
async def rent_out_property(request: dict):
    """将房产出租"""
    try:
        import sqlite3
        session_id = request.get("session_id")
        property_id = request.get("property_id")
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取房产信息
            cursor.execute('''
                SELECT id, name, monthly_rent, is_rented, is_self_living FROM properties
                WHERE id = ? AND session_id = ?
            ''', (property_id, session_id))
            prop = cursor.fetchone()
            
            if not prop:
                return {"success": False, "error": "房产不存在"}
            
            prop_id, prop_name, monthly_rent, is_rented, is_self_living = prop
            
            if is_rented:
                return {"success": False, "error": "该房产已在出租中"}
            
            if is_self_living:
                return {"success": False, "error": "您正在居住该房产，无法出租"}
            
            # 更新为出租状态
            cursor.execute('''
                UPDATE properties SET is_rented = 1 WHERE id = ?
            ''', (prop_id,))
            conn.commit()
            
        return {"success": True, "message": f"{prop_name}已出租", "monthly_rent": monthly_rent or 0}
    except Exception as e:
        print(f"[Housing] Rent out error: {e}")
        return {"success": False, "error": str(e)}


# ==================== 生活方式系统路由 ====================

@router.get("/lifestyle/status/{session_id}")
async def get_lifestyle_status(session_id: str):
    """获取生活状态"""
    try:
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'happiness' in columns:
                cursor.execute('''
                    SELECT happiness, energy, health FROM users WHERE session_id = ?
                ''', (session_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        "success": True,
                        "status": {
                            "happiness": row[0] or 60,
                            "energy": row[1] or 75,
                            "health": row[2] or 80,
                            "social": 50  # 默认值，可以扩展
                        }
                    }
        return {"success": True, "status": {"happiness": 60, "energy": 75, "health": 80, "social": 50}}
    except Exception as e:
        return {"success": True, "status": {"happiness": 60, "energy": 75, "health": 80, "social": 50}}

@router.post("/lifestyle/activity")
async def do_lifestyle_activity(request: dict):
    """执行生活活动"""
    try:
        import sqlite3
        session_id = request.get("session_id")
        activity_id = request.get("activity_id")
        cost = request.get("cost", 0)
        effects = request.get("effects", {})
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取当前状态
            cursor.execute('SELECT credits, happiness, energy, health FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "用户不存在"}
            
            cash, happiness, energy, health = row
            happiness = happiness or 60
            energy = energy or 75
            health = health or 80
            
            if cash < cost:
                return {"success": False, "error": "现金不足"}
            
            # 应用效果
            new_cash = cash - cost
            new_happiness = max(0, min(100, happiness + effects.get('happiness', 0)))
            new_energy = max(0, min(100, energy + effects.get('energy', 0)))
            new_health = max(0, min(100, health + effects.get('health', 0)))
            
            cursor.execute('''
                UPDATE users SET credits = ?, happiness = ?, energy = ?, health = ?
                WHERE session_id = ?
            ''', (new_cash, new_happiness, new_energy, new_health, session_id))
            
            # 记录活动
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lifestyle_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    activity_id TEXT NOT NULL,
                    cost INTEGER NOT NULL,
                    effects TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            import json
            cursor.execute('''
                INSERT INTO lifestyle_activities (session_id, activity_id, cost, effects)
                VALUES (?, ?, ?, ?)
            ''', (session_id, activity_id, cost, json.dumps(effects)))
            
            # 记录现金流
            game_service.db.save_cashflow_record(
                session_id, game_service.db.get_session_month(session_id),
                'lifestyle', 'entertainment', activity_id, cost, False
            )
            
            conn.commit()
        
        # 记录行为日志
        try:
            if game_service.behavior_system:
                from core.systems.macro_economy import macro_economy
                market_state = {'economic_phase': macro_economy.current_phase}
                action_data = {
                    'amount': cost,
                    'cash': cash,
                    'activity_type': activity_id,
                    'happiness_effect': effects.get('happiness', 0)
                }
                current_month = game_service.db.get_session_month(session_id)
                action_type = 'lifestyle_luxury' if cost > 1000 else 'lifestyle_basic'
                game_service.behavior_system.log_action(
                    session_id, current_month, action_type, action_data, market_state
                )
        except Exception as e:
            print(f"[BehaviorLog] Failed to log lifestyle activity: {e}")
        
        return {
            "success": True,
            "message": "活动完成",
            "new_status": {
                "cash": new_cash,
                "happiness": new_happiness,
                "energy": new_energy,
                "health": new_health
            }
        }
    except Exception as e:
        print(f"[Lifestyle] Activity error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/lifestyle/business")
async def start_side_business(request: dict):
    """启动副业项目"""
    try:
        import sqlite3
        session_id = request.get("session_id")
        business_id = request.get("business_id")
        investment = request.get("investment", 0)
        
        business_info = {
            'shop': {'name': '网店经营', 'expectedReturn': 2000, 'risk': 0.2},
            'content': {'name': '自媒体创业', 'expectedReturn': 3000, 'risk': 0.3},
            'restaurant': {'name': '餐饮加盟', 'expectedReturn': 15000, 'risk': 0.4},
            'tech': {'name': '科技初创', 'expectedReturn': 50000, 'risk': 0.6}
        }
        
        biz = business_info.get(business_id)
        if not biz:
            return {"success": False, "error": "项目不存在"}
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT credits FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row or row[0] < investment:
                return {"success": False, "error": "资金不足"}
            
            new_cash = row[0] - investment
            
            # 创建副业表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS side_businesses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    business_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    investment INTEGER NOT NULL,
                    expected_return INTEGER NOT NULL,
                    risk_rate REAL NOT NULL,
                    status TEXT DEFAULT 'running',
                    start_month INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, business_id)
                )
            ''')
            
            cursor.execute('''
                INSERT INTO side_businesses (session_id, business_id, name, investment, expected_return, risk_rate, start_month)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, business_id) DO UPDATE SET status = 'running'
            ''', (session_id, business_id, biz['name'], investment, biz['expectedReturn'],
                  biz['risk'], game_service.db.get_session_month(session_id)))
            
            cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            conn.commit()
        
        return {"success": True, "message": f"{biz['name']}启动成功！", "new_cash": new_cash}
    except Exception as e:
        print(f"[Lifestyle] Business error: {e}")
        return {"success": False, "error": str(e)}

@router.get("/lifestyle/businesses/{session_id}")
async def get_side_businesses(session_id: str):
    """获取副业列表"""
    try:
        import sqlite3
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT business_id, name, investment, expected_return, status, start_month
                FROM side_businesses WHERE session_id = ? AND status = 'running'
            ''', (session_id,))
            businesses = []
            for r in cursor.fetchall():
                businesses.append({
                    'id': r[0], 'name': r[1], 'investment': r[2],
                    'expectedReturn': r[3], 'status': r[4], 'startMonth': r[5]
                })
        return {"success": True, "businesses": businesses}
    except Exception as e:
        return {"success": True, "businesses": []}

# ============ 行为洞察API ============

def resolve_session_id(session_id_or_user_id: str) -> str:
    """
    解析 session_id：如果传入的是数字用户ID，则从数据库查询对应的 session_id
    """
    # 如果是纯数字，认为是用户ID，需要查询对应的session_id
    if session_id_or_user_id.isdigit():
        try:
            import sqlite3
            with sqlite3.connect(game_service.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT session_id FROM users WHERE id = ?', (int(session_id_or_user_id),))
                result = cursor.fetchone()
                if result:
                    return result[0]
        except Exception as e:
            print(f"[Insights] Failed to resolve session_id: {e}")
    return session_id_or_user_id

@router.get("/insights/personal/{session_id}")
async def get_personal_insights(session_id: str):
    """获取个人行为洞察"""
    try:
        if not game_service.behavior_system:
            return {"success": False, "error": "行为洞察系统未初始化"}
        
        # 解析 session_id
        resolved_id = resolve_session_id(session_id)
        insights = game_service.behavior_system.get_personal_insights(resolved_id)
        
        # 获取用户自选标签
        import sqlite3
        user_tags = ""
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT tags FROM users WHERE session_id = ?', (resolved_id,))
            row = cursor.fetchone()
            if row and row[0]:
                user_tags = row[0]
        
        # 合并用户标签和自动标签
        if insights and insights.get('profile'):
            insights['profile']['user_tags'] = user_tags
        
        return {
            "success": True,
            "data": insights
        }
    except Exception as e:
        print(f"[Insights] Personal insights error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/cohort")
async def get_cohort_insights(insight_type: str = None, limit: int = 20):
    """获取群体洞察"""
    try:
        if not game_service.db:
            return {"success": False, "error": "数据库未初始化"}
        
        insights = game_service.db.get_cohort_insights(insight_type, limit)
        return {
            "success": True,
            "data": insights
        }
    except Exception as e:
        print(f"[Insights] Cohort insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/statistics/{session_id}")
async def get_behavior_statistics(session_id: str):
    """获取行为统计数据（用于图表）"""
    try:
        if not game_service.behavior_system:
            return {"success": False, "error": "行为洞察系统未初始化"}
        
        resolved_id = resolve_session_id(session_id)
        stats = game_service.behavior_system.get_behavior_statistics(resolved_id)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        print(f"[Insights] Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/ai/{session_id}")
async def get_ai_insight(session_id: str):
    """获取AI生成的个性化洞察"""
    try:
        if not game_service.behavior_system:
            return {"success": False, "error": "行为洞察系统未初始化"}
        
        resolved_id = resolve_session_id(session_id)
        
        # 设置AI引擎
        if game_service.ai_engine and not game_service.behavior_system.ai_engine:
            game_service.behavior_system.set_ai_engine(game_service.ai_engine)
        
        current_month = game_service.db.get_session_month(resolved_id)
        insight = await game_service.behavior_system.generate_ai_insight(resolved_id, current_month)
        
        if insight:
            return {"success": True, "data": insight}
        else:
            return {"success": False, "error": "无法生成AI洞察，请确保有足够的行为数据"}
    except Exception as e:
        print(f"[Insights] AI insight error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ========== 行为预警 API ==========
@router.get("/insights/warnings/{session_id}")
async def get_behavior_warnings(session_id: str):
    """获取行为预警信息"""
    try:
        if not game_service.behavior_system:
            return {"success": False, "error": "行为洞察系统未初始化"}
        
        resolved_id = resolve_session_id(session_id)
        
        # 获取当前月份作为游戏状态
        current_month = game_service.db.get_session_month(resolved_id) if game_service.db else 0
        state = {'current_month': current_month or 0}
        
        # 获取预警
        warnings = game_service.behavior_system.get_warnings(resolved_id, state)
        
        # 按严重程度排序
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        warnings.sort(key=lambda w: severity_order.get(w.get('severity', 'low'), 4))
        
        # 统计
        stats = {
            'total': len(warnings),
            'critical': len([w for w in warnings if w.get('severity') == 'critical']),
            'high': len([w for w in warnings if w.get('severity') == 'high']),
            'medium': len([w for w in warnings if w.get('severity') == 'medium']),
            'low': len([w for w in warnings if w.get('severity') == 'low'])
        }
        
        return {
            "success": True,
            "warnings": warnings,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Warnings] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ========== 同龄人对比 API ==========
@router.get("/insights/peer-comparison/{session_id}")
async def get_peer_comparison(session_id: str):
    """获取与同龄人的行为对比"""
    try:
        if not game_service.behavior_system:
            return {"success": False, "error": "行为洞察系统未初始化"}
        
        resolved_id = resolve_session_id(session_id)
        
        # 获取对比数据
        comparison_data = game_service.behavior_system.get_peer_comparison(resolved_id)
        
        return {
            "success": True,
            "data": comparison_data
        }
        
    except Exception as e:
        print(f"[PeerComparison] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ========== 行为演变趋势 API ==========
@router.get("/insights/evolution/{session_id}")
async def get_behavior_evolution(session_id: str):
    """获取行为演变趋势数据"""
    try:
        if not game_service.behavior_system:
            return {"success": False, "error": "行为洞察系统未初始化"}
        
        resolved_id = resolve_session_id(session_id)
        evolution_data = game_service.behavior_system.get_behavior_evolution(resolved_id)
        
        return {
            "success": True,
            "data": evolution_data
        }
        
    except Exception as e:
        print(f"[Evolution] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ========== 行为日志列表 API ==========
@router.get("/behavior-logs/{session_id}")
async def get_behavior_logs_list(session_id: str, limit: int = 50):
    """获取行为日志列表（用于时间线展示）"""
    try:
        if not game_service.db:
            return {"success": False, "error": "数据库未初始化"}
        
        logs = game_service.db.get_behavior_logs(session_id, months=999)  # 获取所有
        
        # 只返回最近的记录
        recent_logs = logs[:limit] if logs else []
        
        return {
            "success": True,
            "data": recent_logs,
            "total": len(logs) if logs else 0
        }
        
    except Exception as e:
        print(f"[BehaviorLogs] Error: {e}")
        return {
            "success": True,
            "data": [],
            "total": 0
        }


# ============ 统一时间线 API ============

@router.get("/timeline/{session_id}")
async def get_unified_timeline(session_id: str, limit: int = 100):
    """获取统一时间线 - 整合所有事件类型"""
    try:
        import sqlite3
        
        timeline_items = []
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. 获取交易记录
            cursor.execute('''
                SELECT round_num, transaction_name, amount, ai_thoughts, created_at
                FROM transactions
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            for row in cursor.fetchall():
                timeline_items.append({
                    "type": "transaction",
                    "category": "cash_flow",
                    "month": row[0],
                    "title": row[1],
                    "amount": row[2],
                    "ai_thoughts": row[3],
                    "timestamp": row[4],
                    "icon": "💰" if row[2] > 0 else "💸"
                })
            
            # 2. 获取城市事件
            cursor.execute('''
                SELECT district_id, title, description, type, created_at
                FROM city_events
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            for row in cursor.fetchall():
                timeline_items.append({
                    "type": "event",
                    "category": "environment",
                    "district_id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "event_type": row[3],
                    "timestamp": row[4],
                    "icon": "🌍"
                })
            
            # 3. 获取行为日志
            cursor.execute('''
                SELECT month, action_type, action_category, amount, risk_score, 
                       rationality_score, market_condition, decision_context, created_at
                FROM behavior_logs
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            for row in cursor.fetchall():
                timeline_items.append({
                    "type": "behavior",
                    "category": "subject",
                    "month": row[0],
                    "action_type": row[1],
                    "action_category": row[2],
                    "amount": row[3],
                    "risk_score": row[4],
                    "rationality_score": row[5],
                    "market_condition": row[6],
                    "decision_context": row[7],
                    "timestamp": row[8],
                    "icon": "🧠"
                })
            
            # 4. 获取存款记录
            cursor.execute('''
                SELECT product_name, amount, buy_price, buy_month, created_at
                FROM financial_holdings
                WHERE session_id = ? AND product_type = 'deposit'
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            for row in cursor.fetchall():
                timeline_items.append({
                    "type": "deposit",
                    "category": "cash_flow",
                    "title": f"存入{row[0]}",
                    "amount": -row[1],  # 存款是现金流出
                    "rate": row[2],
                    "month": row[3],
                    "timestamp": row[4],
                    "icon": "🏦"
                })
            
            # 5. 获取贷款记录
            cursor.execute('''
                SELECT product_name, principal, annual_rate, term_months, start_month, created_at
                FROM loans
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            for row in cursor.fetchall():
                timeline_items.append({
                    "type": "loan",
                    "category": "cash_flow",
                    "title": f"申请{row[0]}",
                    "amount": row[1],  # 贷款是现金流入
                    "rate": row[2],
                    "term_months": row[3],
                    "month": row[4],
                    "timestamp": row[5],
                    "icon": "💳"
                })
            
            # 6. 获取投资记录
            cursor.execute('''
                SELECT name, amount, investment_type, return_rate, created_round, ai_thoughts, created_at
                FROM investments
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            for row in cursor.fetchall():
                timeline_items.append({
                    "type": "investment",
                    "category": "asset_change",
                    "title": f"投资{row[0]}",
                    "amount": -row[1],
                    "investment_type": row[2],
                    "return_rate": row[3],
                    "month": row[4],
                    "ai_thoughts": row[5],
                    "timestamp": row[6],
                    "icon": "📈"
                })
            
            # 7. 获取股票交易记录
            cursor.execute('''
                SELECT stock_name, action, shares, price, total_amount, month, profit, created_at
                FROM stock_transactions
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            for row in cursor.fetchall():
                action = row[1]
                amount = row[4] if action == 'sell' else -row[4]
                profit = row[6] or 0
                timeline_items.append({
                    "type": "stock",
                    "category": "asset_change" if action == 'buy' else "cash_flow",
                    "title": f"{'买入' if action == 'buy' else '卖出'}{row[0]} {row[2]}股",
                    "amount": amount,
                    "price": row[3],
                    "shares": row[2],
                    "profit": profit if action == 'sell' else None,
                    "month": row[5],
                    "timestamp": row[7],
                    "icon": "📈" if action == 'buy' else "📉"
                })
            
            # 8. 获取月度快照（资产变化）
            cursor.execute('''
                SELECT month, total_assets, cash, invested_assets, happiness, stress, created_at
                FROM monthly_snapshots
                WHERE session_id = ?
                ORDER BY month DESC
                LIMIT ?
            ''', (session_id, limit))
            snapshots = cursor.fetchall()
            for i, row in enumerate(snapshots):
                # 计算资产变化
                prev_assets = snapshots[i+1][1] if i+1 < len(snapshots) else row[1]
                change = row[1] - prev_assets
                if change != 0:
                    timeline_items.append({
                        "type": "snapshot",
                        "category": "asset_change",
                        "month": row[0],
                        "title": f"第{row[0]}月资产{'增加' if change > 0 else '减少'}",
                        "total_assets": row[1],
                        "cash": row[2],
                        "invested_assets": row[3],
                        "change": change,
                        "happiness": row[4],
                        "stress": row[5],
                        "timestamp": row[6],
                        "icon": "📊"
                    })
        
        # 按时间排序
        timeline_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "success": True,
            "items": timeline_items[:limit],
            "total": len(timeline_items)
        }
        
    except Exception as e:
        print(f"[Timeline] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e), "items": []}


# ============ 档案库 API（按类别分组）============

@router.get("/archives/{session_id}")
async def get_archives(session_id: str):
    """获取档案库 - 按标签分类"""
    try:
        import sqlite3
        
        archives = {
            "ai_thoughts": [],      # AI想法
            "environment": [],       # 环境变化
            "subject": [],           # 主体变化
            "cash_flow": [],         # 现金流
            "asset_change": []       # 资产变化
        }
        
        with sqlite3.connect(game_service.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. AI想法 - 从交易记录和投资记录中提取
            cursor.execute('''
                SELECT round_num, transaction_name, ai_thoughts, created_at
                FROM transactions
                WHERE session_id = ? AND ai_thoughts IS NOT NULL AND ai_thoughts != ''
                ORDER BY created_at DESC
                LIMIT 50
            ''', (session_id,))
            for row in cursor.fetchall():
                archives["ai_thoughts"].append({
                    "month": row[0],
                    "title": row[1],
                    "content": row[2],
                    "timestamp": row[3]
                })
            
            cursor.execute('''
                SELECT created_round, name, ai_thoughts, created_at
                FROM investments
                WHERE session_id = ? AND ai_thoughts IS NOT NULL AND ai_thoughts != ''
                ORDER BY created_at DESC
                LIMIT 50
            ''', (session_id,))
            for row in cursor.fetchall():
                archives["ai_thoughts"].append({
                    "month": row[0],
                    "title": f"投资{row[1]}",
                    "content": row[2],
                    "timestamp": row[3]
                })
            
            # 2. 环境变化 - 城市事件和宏观经济
            cursor.execute('''
                SELECT district_id, title, description, type, created_at
                FROM city_events
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            ''', (session_id,))
            for row in cursor.fetchall():
                archives["environment"].append({
                    "district": row[0],
                    "title": row[1],
                    "description": row[2],
                    "event_type": row[3],
                    "timestamp": row[4]
                })
            
            # 3. 主体变化 - 行为日志
            cursor.execute('''
                SELECT month, action_type, action_category, risk_score, rationality_score, decision_context, created_at
                FROM behavior_logs
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            ''', (session_id,))
            for row in cursor.fetchall():
                archives["subject"].append({
                    "month": row[0],
                    "action_type": row[1],
                    "category": row[2],
                    "risk_score": row[3],
                    "rationality_score": row[4],
                    "context": row[5],
                    "timestamp": row[6]
                })
            
            # 4. 现金流 - 交易记录
            cursor.execute('''
                SELECT round_num, transaction_name, amount, created_at
                FROM transactions
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            ''', (session_id,))
            for row in cursor.fetchall():
                archives["cash_flow"].append({
                    "month": row[0],
                    "title": row[1],
                    "amount": row[2],
                    "timestamp": row[3]
                })
            
            # 5. 资产变化 - 月度快照
            cursor.execute('''
                SELECT month, total_assets, cash, invested_assets, happiness, stress, created_at
                FROM monthly_snapshots
                WHERE session_id = ?
                ORDER BY month DESC
                LIMIT 50
            ''', (session_id,))
            snapshots = cursor.fetchall()
            for i, row in enumerate(snapshots):
                prev_assets = snapshots[i+1][1] if i+1 < len(snapshots) else row[1]
                archives["asset_change"].append({
                    "month": row[0],
                    "total_assets": row[1],
                    "cash": row[2],
                    "invested_assets": row[3],
                    "change": row[1] - prev_assets,
                    "happiness": row[4],
                    "stress": row[5],
                    "timestamp": row[6]
                })
        
        # 按时间排序各分类
        for key in archives:
            archives[key].sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "success": True,
            "archives": archives
        }
        
    except Exception as e:
        print(f"[Archives] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e), "archives": {}}


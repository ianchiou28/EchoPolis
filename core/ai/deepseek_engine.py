# -*- coding: utf-8 -*-
"""
DeepSeek AI引擎 - Echopolis AI决策模块
"""
import requests
import json
from typing import Dict, List, Optional

class DeepSeekEngine:
    def __init__(self, api_key: str = None):
        # 尝试从配置文件读取API key
        if api_key is None:
            try:
                import json
                import os
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        api_key = config.get('deepseek_api_key')
            except:
                pass
        
        if not api_key:
            print("[WARN] DeepSeek API key not found. Using fallback mode.")
            self.api_key = None
        else:
            self.api_key = api_key
            print(f"[INFO] DeepSeek API key loaded: {api_key[:10]}...")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            self.headers = {}
    
    def make_decision(self, context: Dict) -> Dict:
        """强制使用DeepSeek AI做决策"""
        if not self.api_key:
            raise Exception("DeepSeek API key is required for decision making")
        
        prompt = self._build_decision_prompt(context)
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 250
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
        
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]
        parsed_result = self._parse_ai_response(ai_response, context["options"])
        print(f"[DEBUG] Parsed AI decision result: {parsed_result}")
        return parsed_result
    
    def _build_decision_prompt(self, context: Dict) -> str:
        """构建决策提示词 V3，要求AI计算所有变化"""
        mbti_profiles = {
            "ISTJ": "稽查者 - 像一座花岗岩堡垒般可靠，账本精确到小数点后两位",
            "ISFJ": "守护者 - 指尖带着温热的牛奶香，总记得你过敏的药材名",
            "INFJ": "劝告者 - 看见火焰在众人眼中熄灭，用隐喻缝补破碎的灵魂",
            "INTJ": "战略家 - 棋盘延伸到十年之后，卒子过河即成女王",
            "ISTP": "巧匠 - 摩托车引擎倒悬如心脏，扳手旋转出黄金比例",
            "ISFP": "艺术家 - 颜料在帆布上长出静脉，耳后别着野蕨的春天",
            "INFP": "调停者 - 捧着水晶般易碎的理想，在现实荆棘中采血验玫瑰",
            "INTP": "逻辑学家 - 在脑内搭建巴别图书馆，用公式翻译上帝呓语",
            "ESTP": "践行者 - 闯红灯的瞬间大笑不止，风险是活着的盐粒",
            "ESFP": "表演者 - 把每间客厅变成舞台，笑声如彩纸屑旋转飘落",
            "ENFP": "倡导者 - 思维是永不停歇的烟花厂，拉着陌生人畅想火星幼儿园",
            "ENTP": "辩论家 - 用悖论编织投石器，击碎所有庄严的玻璃窗",
            "ESTJ": "监督者 - 怀表链拴着整个组织体系，用效率浇筑社会骨架",
            "ESFJ": "执政官 - 记得所有成员的过敏原，社区花名册是圣典",
            "ENFJ": "教育家 - 在瞳孔深处点燃星火，话语长出牵引的羽翼",
            "ENTJ": "指挥官 - 将混沌锻造成进度图表，目光扫过之处升起脚手架"
        }
        mbti_profile = mbti_profiles.get(context["mbti"], "理性决策者")
        
        prompt = f"""你是一个{context['mbti']}人格类型的人（{mbti_profile}），名叫{context['name']}，{context['age']}岁。

# 游戏核心规则
1. 你的每一个决策都将让时间前进一个月。
2. 你的最终目标是实现财务自由，同时保持身心健康。
3. 现金是你生存的关键，现金低于0意味着直接破产。

# 投资规则
投资分为三类：短期(3个月), 中期(6个月), 长期(12个月)。投资时，现金立刻减少，等额资金进入“投资中资产”。到期后，本金和收益/亏损会自动结算到现金中。

你的当前财务状况(第{context.get('current_month', 0)}个月)：
- 现金：{context.get('cash', 0):,} CP
- 投资中资产：{context.get('invested_assets', 0):,} CP
- 总资产：{context.get('total_assets', 0):,} CP

你的其它状态：
- 健康：{context['health']}/100, 幸福感：{context['happiness']}/100, 精力：{context.get('energy', 100)}/100, 对玩家信任度：{context['trust']}/100

现在面临情况：{context['situation']}

可选行动：
{chr(10).join(f"{i+1}. {opt}" for i, opt in enumerate(context['options']))}

玩家建议：{context.get('player_echo', '无')}

# 你的任务
作为这个角色进行决策。你的回复必须严格遵循以下两行格式。在“想法”的末尾，必须附带一个包含所有决策影响的完整JSON。所有数值变化都必须由你根据情况和人格来计算。
选择：[数字]
想法：[你的内心独白...][决策影响JSON: {{"cash_change": <number>, "invested_assets_change": <number>, "health_change": <number>, "happiness_change": <number>, "energy_change": <number>, "trust_change": <number>, "investment_item": {{"name": "<投资项目名称>", "amount": <number>, "duration": <1,3,6,12>, "type": "SHORT_TERM|MEDIUM_TERM|LONG_TERM"}} or null}}]

## 重要：财务计算规则
- 花费金钱时cash_change必须为负数（如花费5000CP，则cash_change: -5000）
- 投资时设置investment_item对象并减少现金（如投资5000CP到理财产品3个月，则cash_change: -5000, investment_item: {{"name": "理财产品", "amount": 5000, "duration": 3, "type": "SHORT_TERM"}}）
- 投资类型：1-3个月=SHORT_TERM, 4-8个月=MEDIUM_TERM, 9个月以上=LONG_TERM
- 根据选择内容准确计算所有数值变化"""
        
        return prompt

    def _parse_ai_response(self, response: str, options: List[str]) -> Dict:
        """解析AI响应，提取决策和统一的decision_impact JSON"""
        print(f"[DEBUG] Raw AI response: {response}")
        
        # 默认值
        chosen_option = options[0] if options else "默认选择"
        thoughts = "AI没有提供明确想法。"
        decision_impact = {}
        investment = None
        financial_impact = {'cash_change': 0, 'other_assets_change': 0}
        
        try:
            # 解析选择
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('选择：'):
                    try:
                        choice_num = int(line.split('：')[1].strip())
                        if 1 <= choice_num <= len(options):
                            chosen_option = options[choice_num - 1]
                    except (ValueError, IndexError):
                        pass
                    break
            
            # 解析想法和JSON
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('想法：'):
                    idea_content = line.split('：', 1)[1] if '：' in line else line
                    
                    # 查找JSON标记
                    json_marker = '[决策影响JSON:'
                    if json_marker in idea_content:
                        thoughts_part, json_part = idea_content.rsplit(json_marker, 1)
                        thoughts = thoughts_part.strip()
                        
                        # 解析JSON
                        try:
                            json_str = json_part.strip().rstrip(']')
                            parsed_json = json.loads(json_str)
                            
                            decision_impact = parsed_json
                            
                            # 提取投资信息
                            if 'investment_item' in parsed_json and parsed_json['investment_item']:
                                investment = parsed_json['investment_item']
                            elif 'investment' in parsed_json and parsed_json['investment']:
                                investment = parsed_json['investment']
                            
                            # 构建financial_impact
                            financial_impact = {
                                'cash_change': parsed_json.get('cash_change', 0),
                                'other_assets_change': parsed_json.get('invested_assets_change', 0)
                            }
                            
                        except json.JSONDecodeError as e:
                            print(f"[WARN] JSON parsing failed: {e}. Raw: {json_part}")
                            thoughts = idea_content.strip()
                    else:
                        thoughts = idea_content.strip()
                    break
            
            result = {
                "chosen_option": chosen_option,
                "ai_thoughts": thoughts,
                "financial_impact": financial_impact,
                "investment": investment,
                "decision_impact": decision_impact,
                "raw_response": response
            }
            
            print(f"[DEBUG] Parsed result: {result}")
            return result
            
        except Exception as e:
            print(f"[ERROR] Parsing AI response failed: {e}")
            return {
                "chosen_option": chosen_option,
                "ai_thoughts": "解析AI响应时出现意外错误。",
                "financial_impact": financial_impact,
                "investment": None,
                "decision_impact": {},
                "raw_response": response
            }
    
    def generate_situation(self, context: Dict):
        """使用DeepSeek AI生成情况"""
        if not self.api_key:
            raise Exception("DeepSeek API key is required for situation generation")
        
        prompt = self._build_situation_prompt(context)
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 400
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            return self._parse_situation_response(ai_response)
        else:
            raise Exception(f"DeepSeek situation API error: {response.status_code} - {response.text}")
    
    def _build_situation_prompt(self, context: Dict) -> str:
        """构建情况生成提示词"""
        life_stage_desc = {
            "startup": "启航期，刚毕业不久",
            "exploration": "探索期，职场初期",
            "struggle": "奋斗期，事业家庭双重压力",
            "accumulation": "沉淀期，财富积累阶段",
            "retirement": "黄昏期，退休阶段"
        }.get(context["life_stage"], "成年期")
        
        mbti_profiles = {
            "ISTJ": "稽查者 - 像一座花岗岩堡垒般可靠，账本精确到小数点后两位",
            "ISFJ": "守护者 - 指尖带着温热的牛奶香，总记得你过敏的药材名",
            "INFJ": "劝告者 - 看见火焰在众人眼中熄灭，用隐喻缝补破碎的灵魂",
            "INTJ": "战略家 - 棋盘延伸到十年之后，卒子过河即成女王",
            "ISTP": "巧匠 - 摩托车引擎倒悬如心脏，扳手旋转出黄金比例",
            "ISFP": "艺术家 - 颜料在帆布上长出静脉，耳后别着野蕨的春天",
            "INFP": "调停者 - 捧着水晶般易碎的理想，在现实荆棘中采血验玫瑰",
            "INTP": "逻辑学家 - 在脑内搭建巴别图书馆，用公式翻译上帝呓语",
            "ESTP": "践行者 - 闯红灯的瞬间大笑不止，风险是活着的盐粒",
            "ESFP": "表演者 - 把每间客厅变成舞台，笑声如彩纸屑旋转飘落",
            "ENFP": "倡导者 - 思维是永不停歇的烟花厂，拉着陌生人畅想火星幼儿园",
            "ENTP": "辩论家 - 用悖论编织投石器，击碎所有庄严的玻璃窗",
            "ESTJ": "监督者 - 怀表链拴着整个组织体系，用效率浇筑社会骨架",
            "ESFJ": "执政官 - 记得所有成员的过敏原，社区花名册是圣典",
            "ENFJ": "教育家 - 在瞳孔深处点燃星火，话语长出牵引的羽翼",
            "ENTJ": "指挥官 - 将混沌锻造成进度图表，目光扫过之处升起脚手架"
        }
        
        mbti_profile = mbti_profiles.get(context["mbti"], "理性决策者")
        
        prompt = f"""你是一个金融游戏的情况生成器。请为以下角色生成一个适合的决策情况：

角色信息：
- 姓名：{context['name']}
- 年龄：{context['age']}岁
- 人生阶段：{life_stage_desc}
- MBTI类型：{context['mbti']} ({mbti_profile})
- 现金：{context['cash']:,} CP
- 健康：{context['health']}/100
- 幸福感：{context['happiness']}/100
- 精力：{context.get('energy', 100)}/100
- 背景：{context['background']}
- 特质：{context['traits']}
- 已做决策数：{context['decision_count']}

请生成一个符合以下要求的情况：
1. 与角色的年龄、背景和当前状态相符
2. 具有金融或生活决策的性质
3. 提供3个不同的选择方案

请严格按照以下格式回复：
情况：[详细描述当前面临的情况]
选项1：[第一个选择]
选项2：[第二个选择]
选项3：[第三个选择]"""
        return prompt
    
    def _parse_situation_response(self, response: str) -> Optional[Dict]:
        """解析情况生成响应"""
        try:
            lines = response.strip().split('\n')
            data = {}
            for line in lines:
                if '：' in line:
                    key, value = line.split('：', 1)
                    data[key.strip()] = value.strip()
            
            situation = data.get('情况')
            options = [
                data.get('选项1'),
                data.get('选项2'),
                data.get('选项3')
            ]
            
            if situation and all(options):
                return {
                    "description": situation,
                    "choices": options
                }
            else:
                print(f"[WARN] Parsing situation failed, missing fields. Data: {data}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Parsing situation response failed: {e}")
            return None
    
    def make_autonomous_decision(self, avatar, situation):
        """AI自主决策"""
        context = {
            "name": avatar.name,
            "mbti": avatar.mbti,
            "age": getattr(avatar, 'age', 25),
            "cash": avatar.credits,
            "other_assets": 0,
            "total_assets": avatar.credits,
            "health": avatar.health,
            "happiness": avatar.happiness,
            "stress": avatar.stress,
            "trust": avatar.trust_level,
            "background": avatar.background_story,
            "traits": avatar.special_traits,
            "situation": situation.get("description", situation.get("situation", "")),
            "options": situation.get("choices", situation.get("options", [])),
            "player_echo": ""
        }
        
        return self.make_decision(context)


    def _fallback_decision(self, context: Dict) -> Dict:
        """备用决策系统"""
        import random
        options = context.get("options", [])
        if not options:
            return {"error": "No options available"}
        
        chosen_option = random.choice(options)
        
        # 生成简单的决策影响
        cash_change = random.randint(-50000, 30000)
        invested_change = 0
        if "投资" in chosen_option:
            cash_change = random.randint(-120000, -10000)
            invested_change = abs(cash_change)
        
        return {
            "chosen_option": chosen_option,
            "ai_thoughts": f"经过考虑，我选择了{chosen_option}。",
            "decision_impact": {
                "cash_change": cash_change,
                "invested_assets_change": invested_change,
                "health_change": random.randint(-2, 5),
                "happiness_change": random.randint(-3, 8),
                "energy_change": random.randint(-5, 5),
                "trust_change": random.randint(-2, 3)
            }
        }
    
    def _fallback_situation(self, context: Dict):
        """备用情况生成"""
        import random
        
        situations = [
            {
                "description": "你刚入职一家科技公司，拿到第一笔年终奖金50,000 CP。同事邀请你加入一个“青年创投俱乐部”，入会费20,000 CP可参与优质初创项目投资。",
                "choices": [
                    "加入创投俱乐部 - 支付20,000 CP会费参与天使投资",
                    "购置黄金ETF - 用30,000 CP购买黄金ETF保值",
                    "升级生活体验 - 投入15,000 CP办理高端健身年卡"
                ]
            },
            {
                "description": "你的大学好友团队正在筹备一个智能健身镜创业项目，希望你能以天使投资人身份投入12万CP换取15%股权。",
                "choices": [
                    "投入12万CP参与创业项目 - 可能获得百倍回报",
                    "租赁高端公寓提升生活品质 - 月租2.4万CP",
                    "采纳父母建议进行稳健配置 - 80%资金定期理财"
                ]
            }
        ]
        
        return random.choice(situations)

def initialize_deepseek(api_key: str = None):
    """初始化DeepSeek引擎"""
    return DeepSeekEngine(api_key)

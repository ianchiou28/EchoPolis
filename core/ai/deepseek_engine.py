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
                config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        api_key = config.get('deepseek_api_key')
            except:
                pass
        
        if not api_key:
            raise ValueError("DeepSeek API key not found. Please set it in config.json")
            
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def make_decision(self, context: Dict) -> Dict:
        """使用DeepSeek AI做决策"""
        prompt = self._build_decision_prompt(context)
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 250
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                return self._parse_ai_response(ai_response, context["options"])
            else:
                return {"error": f"API错误: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def _build_decision_prompt(self, context: Dict) -> str:
        """构建决策提示词"""
        mbti_profiles = {
            "ISTJ": "稽查者 - 像一座花岗岩堡垒般可靠，账本精确到小数点后两位，遵循着祖辈传下的日程表，用事实与经验浇筑世界秩序",
            "ISFJ": "守护者 - 指尖带着温热的牛奶香，总记得你过敏的药材名，相册按年份编码存放，用绒布擦拭每段回忆",
            "INFJ": "劝告者 - 看见火焰在众人眼中熄灭，用隐喻缝补破碎的灵魂，深夜书房亮着椭圆光斑，先知在稿纸上承受刺痛",
            "INTJ": "战略家 - 棋盘延伸到十年之后，卒子过河即成女王，图书馆穹顶投下冷光，将万物纳入思维矩阵",
            "ISTP": "巧匠 - 摩托车引擎倒悬如心脏，扳手旋转出黄金比例，对说明书嗤之以鼻，用直觉拆解时空密码",
            "ISFP": "艺术家 - 颜料在帆布上长出静脉，耳后别着野蕨的春天，拒绝所有标签式拥抱，用沉默捍卫敏感内核",
            "INFP": "调停者 - 捧着水晶般易碎的理想，在现实荆棘中采血验玫瑰，日记本里压着三叶虫化石，与十九世纪诗人共用一副灵魂",
            "INTP": "逻辑学家 - 在脑内搭建巴别图书馆，用公式翻译上帝呓语，咖啡杯沿印着群论推导，突然停顿的交谈间隙",
            "ESTP": "践行者 - 闯红灯的瞬间大笑不止，风险是活着的盐粒，即兴扑克牌局赌注——整条街道的日落权",
            "ESFP": "表演者 - 把每间客厅变成舞台，笑声如彩纸屑旋转飘落，记住所有邻居的宠物名，用肢体语言翻译快乐",
            "ENFP": "倡导者 - 思维是永不停歇的烟花厂，拉着陌生人畅想火星幼儿园，背包里装着未实现的奇迹，眼泪与灵感同等珍贵",
            "ENTP": "辩论家 - 用悖论编织投石器，击碎所有庄严的玻璃窗，魔鬼辩护席空置太久，正好练习反向哲学体操",
            "ESTJ": "监督者 - 怀表链拴着整个组织体系，用效率浇筑社会骨架，名单勾选框必须直角，延迟是原罪的一种形式",
            "ESFJ": "执政官 - 记得所有成员的过敏原，社区花名册是圣典，用烘焙饼干化解纠纷，门廊灯为晚归者多亮一刻",
            "ENFJ": "教育家 - 在瞳孔深处点燃星火，话语长出牵引的羽翼，发现每个灵魂的密钥，却把自己的锁孔藏在雾中",
            "ENTJ": "指挥官 - 将混沌锻造成进度图表，目光扫过之处升起脚手架，战略蓝图铺满黎明——用咖啡渍标注滩头阵地"
        }
        
        mbti_profile = mbti_profiles.get(context["mbti"], "理性决策者")
        
        prompt = f"""你是一个{context['mbti']}人格类型的人（{mbti_profile}），名叫{context['name']}，{context['age']}岁。

你的当前财务状况：
- 现金：{context['cash']:,} CP (注意：若现金低于0，你将破产)
- 其它资产：{context['other_assets']:,} CP
- 总资产：{context['total_assets']:,} CP

你的其它状态：
- 健康：{context['health']}/100
- 幸福感：{context['happiness']}/100  
- 压力：{context['stress']}/100
- 对玩家信任度：{context['trust']}/100

你的背景：{context['background']}
特殊特质：{context['traits']}

现在面临情况：{context['situation']}

可选行动：
{chr(10).join(f"{i+1}. {opt}" for i, opt in enumerate(context['options']))}

玩家建议：{context.get('player_echo', '无')}

请作为这个人格类型的人，真实地表达你的内心想法和决策过程。请包括：
1. 你对这个情况的第一反应
2. 你考虑的因素(如现金、资产、风险、个人状态等)
3. 对玩家建议的看法(如果有)
4. 你的最终决定和原因

必须严格遵循以下格式，你的回复只能包含“选择”和“想法”两行：
选择：[这里只写一个数字，代表你选择的选项编号]
想法：[你的详细内心独白...][财务影响JSON: {{"cash_change": <数字>, "other_assets_change": <数字>}}]"""        
        return prompt
    
    def _parse_ai_response(self, response: str, options: List[str]) -> Dict:
        """解析AI响应，包含财务影响"""
        try:
            # 提取选择
            choice_line = next((line for line in response.split('\n') if line.startswith('选择：')), None)
            choice_num = int(choice_line.split('：')[1].strip()) if choice_line else 1
            chosen_option = options[choice_num - 1] if 1 <= choice_num <= len(options) else options[0]

            # 提取想法和财务JSON
            thoughts = ""
            financial_impact = {"cash_change": 0, "other_assets_change": 0}
            
            idea_line = next((line for line in response.split('\n') if line.startswith('想法：')), None)
            if idea_line:
                idea_content = idea_line.split('：', 1)[1]
                json_marker = '[财务影响JSON:'
                if json_marker in idea_content:
                    thoughts_part, json_part = idea_content.rsplit(json_marker, 1)
                    thoughts = thoughts_part.strip()
                    try:
                        # 提取并解析JSON
                        json_str = json_part.strip()
                        if json_str.endswith(']'):
                            json_str = json_str[:-1]
                        financial_impact = json.loads(json_str)
                    except json.JSONDecodeError:
                        print(f"[WARN] AI response JSON parsing failed. Raw: {json_part}")
                else:
                    thoughts = idea_content.strip()

            return {
                "chosen_option": chosen_option,
                "ai_thoughts": thoughts or "AI没有提供明确想法。",
                "financial_impact": financial_impact,
                "raw_response": response
            }
            
        except Exception as e:
            print(f"[ERROR] Parsing AI response failed: {e}. Raw: {response}")
            return {
                "chosen_option": options[0],
                "ai_thoughts": "解析AI响应时出现意外错误。",
                "financial_impact": {"cash_change": 0, "other_assets_change": 0},
                "raw_response": response
            }
    
    def generate_situation(self, context: Dict):
        """使用DeepSeek AI生成情况"""
        prompt = self._build_situation_prompt(context)
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 400
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                return self._parse_situation_response(ai_response)
            else:
                return None
                
        except Exception as e:
            return None
    
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
- 压力：{context['stress']}/100
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


def initialize_deepseek(api_key: str = None):
    """初始化DeepSeek引擎"""
    try:
        return DeepSeekEngine(api_key)
    except ValueError as e:
        print(f"DeepSeek初始化失败: {e}")
        return None
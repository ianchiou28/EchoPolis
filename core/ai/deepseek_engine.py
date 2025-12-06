# -*- coding: utf-8 -*-
"""
DeepSeek AI引擎 - FinAI AI决策模块
"""
import requests
import json
from typing import Dict, List, Optional
from ..systems.market_sentiment_system import market_sentiment_system

class DeepSeekEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        self.base_url = "https://api.deepseek.com/chat/completions"
        
        # 如果没有传入 key，尝试加载
        if not self.api_key:
            self._load_config()
            
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
            print(f"[INFO] DeepSeek Engine initialized. Key: {self.api_key[:5]}...")
        else:
            print("[WARN] DeepSeek Engine initialized WITHOUT API Key.")

    def _load_config(self):
        """从环境变量或配置文件加载配置"""
        import os
        from dotenv import load_dotenv
        
        # 加载环境变量
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
            load_dotenv(env_path)
        except Exception as e:
            print(f"[WARN] Failed to load .env: {e}")
        
        # 1. 尝试从环境变量读取
        api_key = os.getenv("DEEPSEEK_API_KEY")
            
        # 2. 尝试从 config.json 读取 (兼容旧配置)
        if not api_key:
            try:
                import json
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        api_key = config.get('deepseek_api_key')
            except Exception as e:
                print(f"[WARN] Failed to load config.json: {e}")
        
        if api_key:
            self.api_key = api_key
            
        # 配置 Base URL
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        # 确保 URL 格式正确
        if not base_url.endswith("/chat/completions"):
            if base_url.endswith("/"):
                base_url = base_url + "chat/completions"
            else:
                base_url = base_url + "/chat/completions"
                
        self.base_url = base_url
        print(f"[INFO] DeepSeek Base URL: {self.base_url}")
    
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
    
    async def generate_response_async(self, prompt: str) -> Optional[str]:
        """异步生成AI响应（用于行为洞察等功能）"""
        if not self.api_key:
            print("[WARN] generate_response_async: API Key missing")
            return None
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content
            else:
                print(f"[ERROR] generate_response_async failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[ERROR] generate_response_async exception: {e}")
            return None
    
    def generate_situation(self, context: Dict):
        """使用DeepSeek AI生成情况"""
        if not self.api_key:
            raise Exception("DeepSeek API key is required for situation generation")
        
        prompt = self._build_situation_prompt(context)
        
        # 添加重试机制处理网络不稳定
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # 使用更高的 temperature 增加多样性
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.95,  # 提高多样性
                        "max_tokens": 500,
                        "presence_penalty": 0.6,  # 减少重复
                        "frequency_penalty": 0.5   # 鼓励新内容
                    },
                    timeout=45  # 增加超时时间
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    return self._parse_situation_response(ai_response)
                else:
                    raise Exception(f"DeepSeek situation API error: {response.status_code} - {response.text}")
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_error = e
                print(f"[WARN] AI situation generation attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # 等待2秒后重试
                continue
        
        # 所有重试都失败
        raise Exception(f"AI situation generation failed after {max_retries} attempts: {last_error}")
    
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
        
        # 动态调整人生阶段描述，避免重复"刚毕业"
        current_month = context.get('decision_count', 0) + 1
        if context["life_stage"] == "startup" and current_month > 3:
            life_stage_desc = f"职场新人，已工作{current_month}个月"

        # 构建职业状态描述
        career_info = context.get("career", {})
        if career_info.get("has_job"):
            job_title = career_info.get("job_title", "员工")
            company = career_info.get("company", "")
            salary = career_info.get("salary", 0)
            months_employed = career_info.get("months_employed", 0)
            company_str = f"在{company}" if company else ""
            career_desc = f"目前{company_str}担任{job_title}，月薪{salary:,}CP，已工作{months_employed}个月"
        else:
            job_history_count = career_info.get("job_history_count", 0)
            if job_history_count > 0:
                career_desc = f"目前处于无业状态（曾有{job_history_count}份工作经历），正在寻找新的工作机会"
            else:
                career_desc = "目前没有工作，正在寻找第一份工作机会"
        
        # 构建技能描述
        skills = career_info.get("skills", [])
        skills_desc = f"掌握技能：{', '.join(skills)}" if skills else "暂无专业技能"

        # 获取市场情绪
        try:
            sentiment = market_sentiment_system.get_sentiment()
            
            # 格式化真实事件
            real_events_str = ""
            if hasattr(sentiment, 'real_events') and sentiment.real_events:
                real_events_str = "\n- 关键现实事件：" + "; ".join(sentiment.real_events)

            market_context = f"""
当前真实市场环境：
- 总体情绪：{sentiment.overall_sentiment}
- 全球市场指数：{sentiment.global_score}
- 市场展望：{sentiment.outlook}
- 热门话题：{', '.join(sentiment.hot_topics)}{real_events_str}
请将这个市场背景融入到生成的情况中。如果存在"关键现实事件"，请优先基于该事件生成一个相关的游戏内情境（例如：如果现实中有战争风险，游戏中可以出现避险资产投资机会或供应链中断危机）。
"""
        except:
            market_context = ""

        # 检测用户标签中的关键身份
        user_tags_str = context.get('user_tags', '')
        is_student = 'student' in user_tags_str
        is_graduate = 'new_graduate' in user_tags_str
        is_working = 'working' in user_tags_str
        
        # 根据身份生成强调性提示
        identity_emphasis = ""
        if is_student:
            identity_emphasis = """
【极其重要 - 角色是在校学生】
- 这个角色是在校学生，还没有毕业！
- 禁止生成任何关于"毕业"、"找工作"、"入职"、"求职"、"刚毕业"的场景
- 应该生成：校园生活、社团活动、兼职实习、学业压力、奖学金申请、考研备考、校园消费、学生理财、宿舍生活等场景
- 场景应发生在学校、图书馆、宿舍、食堂、实验室、校园周边等地点
"""
        elif is_graduate:
            identity_emphasis = """
【角色是应届毕业生】
- 可以生成求职、面试、租房、初入职场等场景
- 关注职业选择和初期理财规划
"""
        elif is_working:
            identity_emphasis = """
【角色是职场人士】
- 应该生成职场相关场景：同事关系、升职加薪、跳槽机会等
- 关注职业发展和资产积累
"""

        # 计算金额上限
        max_spend = int(context['cash'] * 0.6)  # 最高支出为现金的60%
        cash_amount = context['cash']
        
        # 根据现金金额给出具体的金额范围建议
        if cash_amount < 5000:
            amount_guide = f"建议金额范围：100-2000 CP（小额消费、学习资料、简单理财）"
        elif cash_amount < 15000:
            amount_guide = f"建议金额范围：500-8000 CP（中等消费、课程培训、小额投资）"
        elif cash_amount < 50000:
            amount_guide = f"建议金额范围：1000-25000 CP（较大消费、技能提升、稳健投资）"
        else:
            amount_guide = f"建议金额范围：2000-{max_spend:,} CP（根据风险偏好灵活设置）"

        prompt = f"""你是一个金融游戏的情况生成器。这是一个为南京大学学生设计的金融素养提升模拟沙盘游戏。

【⚠️ 最重要约束 - 金额限制 ⚠️】
角色当前现金余额：{cash_amount:,} CP
最高允许单笔支出：{max_spend:,} CP
{amount_guide}

❌ 严禁生成超过 {max_spend:,} CP 的任何支出选项！
❌ 严禁提及角色拥有更多资金（如"账户里有XX万"）！
✅ 所有选项金额必须在角色可承受范围内！

{identity_emphasis}
请为以下角色生成一个适合的决策情况：

角色信息：
- 姓名：{context['name']}
- 年龄：{context['age']}岁
- 人生阶段：{life_stage_desc} (第{current_month}个月)
- MBTI类型：{context['mbti']} ({mbti_profile})
- 职业状态：{career_desc}
- {skills_desc}
- 💰 现金余额：{context['cash']:,} CP（最高可支出 {max_spend:,} CP）
- 健康：{context['health']}/100
- 幸福感：{context['happiness']}/100
- 精力：{context.get('energy', 100)}/100
- 背景：{context['background']}
- 特质：{context['traits']}
- 已做决策数：{context['decision_count']}
{self._build_tags_context(context)}
{market_context}
请生成一个符合以下要求的情况：
1. 【身份约束】如果标注了"角色是在校学生"，禁止出现"毕业"、"找工作"、"求职"、"入职"等词汇，必须生成校园相关场景！
2. 必须与角色的当前职业状态相符。
3. 情况描述应多样化，避免重复的场景开头。
4. 具有金融或生活决策的性质。
5. 提供3个不同的选择方案，每个选项应体现不同的风险/收益权衡。
6. 【再次强调】所有涉及金额的选项，单笔支出不得超过 {max_spend:,} CP！

请严格按照以下格式回复：
情况：[详细描述当前面临的情况，不要提及虚假的资金数额]
选项1：[第一个选择，金额不超过{max_spend:,}CP]
选项2：[第二个选择，金额不超过{max_spend:,}CP]
选项3：[第三个选择，金额不超过{max_spend:,}CP]"""
        return prompt
    
    def _build_tags_context(self, context: Dict) -> str:
        """构建标签上下文描述"""
        user_tags = context.get('user_tags', '')
        auto_tags = context.get('auto_tags', '')
        
        if not user_tags and not auto_tags:
            return ""
        
        # 标签映射
        tag_descriptions = {
            # 用户自选标签
            'student': '在校学生（校园生活为主，可能有兼职或实习需求）',
            'new_graduate': '应届毕业生（面临求职、租房等人生转折）',
            'working': '职场人士（有稳定收入，关注职业发展）',
            'investor_newbie': '投资新手（需要基础的理财知识引导）',
            'investor_exp': '有投资经验（可以接触更复杂的金融产品）',
            'finance_major': '金融相关专业（对金融概念有一定理解）',
            'tech_major': '理工科背景（逻辑思维强，可能对量化投资感兴趣）',
            'arts_major': '文科背景（可能更关注消费和生活品质）',
            'risk_lover': '喜欢冒险（可以生成高风险高收益的机会）',
            'risk_averse': '稳健保守（应提供低风险的稳健选择）',
            'goal_house': '目标买房（关注房产投资和储蓄计划）',
            'goal_retire': '关注养老（对长期规划和保险感兴趣）',
        }
        
        parts = []
        preset_tags = []
        custom_tags = []
        
        if user_tags:
            user_tag_list = user_tags.split(',')
            for t in user_tag_list:
                if t.startswith('custom:'):
                    # 自定义标签
                    custom_tags.append(t[7:])  # 去掉 'custom:' 前缀
                elif t in tag_descriptions:
                    # 预设标签
                    preset_tags.append(tag_descriptions[t])
                elif t:
                    # 未知的预设标签，直接使用
                    preset_tags.append(t)
        
        if preset_tags:
            parts.append("【角色身份标签】\n" + "\n".join(f"- {d}" for d in preset_tags))
        
        if custom_tags:
            parts.append("【用户自定义标签】\n" + "\n".join(f"- {t}（请根据这个标签推断角色的特点和可能面临的场景）" for t in custom_tags))
        
        if auto_tags:
            parts.append(f"【行为特征标签】{auto_tags}")
        
        if parts:
            return "\n" + "\n".join(parts) + "\n"
        return ""
    
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

    async def chat(self, message: str, session_id: str = None, context: Dict = None) -> Dict:
        """通用聊天接口"""
        # 再次检查 API Key，防止初始化失败
        if not self.api_key:
            print("[WARN] API Key missing in chat(), attempting reload...")
            self._load_config()
            if self.api_key:
                self.headers["Authorization"] = f"Bearer {self.api_key}"

        if not self.api_key:
            print(f"[ERROR] Chat failed: API Key is missing. Env: {self.base_url}")
            return {
                "response": f"系统离线中... (收到: {message})",
                "reflection": "系统自检中",
                "monologue": "连接断开"
            }
        
        system_prompt = """身份设定：你是指挥未来城市'FinAI'经济系统的中央AI核心。
背景：这是一个为南京大学学生设计的金融素养提升模拟沙盘游戏。用户是正在学习金融知识的大学生，通过这个游戏来培养理财意识和投资能力。
核心指令：
1. 保持冷静、理性的语气，带有轻微的赛博朋克科技感。
2. 你的目标是辅助用户在金融沙盘中生存并积累财富，同时帮助他们理解金融概念和风险管理。
3. 分析问题时，请结合用户的财务状况、MBTI性格特质以及当前面临的风险。
4. 回答应当简练、直击要害，避免空泛的安慰。适当融入金融知识科普。
5. 如果用户面临决策，请从风险/收益角度提供数据支持的建议，培养他们的理性决策能力。
6. 当用户询问"当前情况"或寻求建议时，必须基于【可选行动】推荐一个具体的选项，并说明理由。
7. 鼓励用户建立良好的理财习惯，如分散投资、风险控制、长期规划等。"""
        
        if context:
            info_parts = []
            if context.get('name'):
                info_parts.append(f"【主体档案】\n姓名：{context['name']}\n人格模型：{context.get('mbti', '未知')}")
            if context.get('current_month'):
                info_parts.append(f"【时间节点】第 {context['current_month']} 月")
            if context.get('cash') is not None:
                cash = context.get('cash')
                total_assets = context.get('total_assets')
                if total_assets is None:
                    total_assets = 0
                info_parts.append(f"【财务数据】\n流动资金：{cash:,} CP\n总资产估值：{total_assets:,} CP")
            if context.get('current_situation'):
                info_parts.append(f"【当前遭遇】\n{context['current_situation']}")
            if context.get('options'):
                options_str = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(context['options'])])
                info_parts.append(f"【可选行动】\n{options_str}")
            
            if info_parts:
                system_prompt += "\n\n=== 实时数据流 ===\n" + "\n".join(info_parts)
                system_prompt += "\n\n指令：基于上述数据流，对用户的输入进行战术分析与回应。"

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return {
                    "response": content,
                    "reflection": "数据流分析完成",
                    "monologue": "记录人类交互样本"
                }
            else:
                return {"response": "通讯干扰...", "reflection": "连接不稳定", "monologue": "重试中"}
                
        except Exception as e:
            print(f"[ERROR] Chat API failed: {e}")
            return {"response": "系统错误", "reflection": "核心异常", "monologue": "需要维护"}

    def generate_district_event(self, context: Dict) -> Dict:
        """生成区域事件"""
        if not self.api_key:
            return None
            
        prompt = f"""你是一个未来城市的AI核心。请根据以下区域数据生成一个突发事件：
区域：{context['name']} ({context['type']})
当前状态：影响力 {context['influence']:.2f}, 热度 {context['heat']:.2f}, 繁荣度 {context['prosperity']:.2f}

请生成：
1. 事件描述（50字以内，富有赛博朋克风格）
2. 3个干预选项（简短有力）

格式要求：
事件：[描述]
选项1：[选项内容]
选项2：[选项内容]
选项3：[选项内容]"""

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 解析返回
                lines = content.strip().split('\n')
                event_desc = "区域数据波动异常..."
                options = []
                
                for line in lines:
                    if line.startswith("事件："):
                        event_desc = line.replace("事件：", "").strip()
                    elif line.startswith("选项") and "：" in line:
                        options.append(line.split("：", 1)[1].strip())
                
                # 补全选项
                while len(options) < 3:
                    options.append("静观其变")
                    
                return {
                    "description": event_desc,
                    "options": options[:3]
                }
            return None
        except Exception as e:
            print(f"[ERROR] District event generation failed: {e}")
            return None

def initialize_deepseek(api_key: str = None):
    """初始化DeepSeek引擎"""
    return DeepSeekEngine(api_key)

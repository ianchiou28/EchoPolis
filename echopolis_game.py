"""
Echopolis 主游戏系统
整合所有核心模块，提供完整的游戏体验
"""
import os
import json
from typing import Dict, Optional
from datetime import datetime

from core.avatar.ai_avatar import AIAvatar
from core.systems.mbti_traits import MBTIType
from core.systems.echo_system import echo_system
from core.ai.deepseek_engine import initialize_deepseek

class EchopolisGame:
    """Echopolis 游戏主类"""
    
    def __init__(self):
        self.current_avatar: Optional[AIAvatar] = None
        self.game_started = False
        self.ai_enabled = False
        self.ai_engine = None
        self.save_file = "echopolis_save.json"
        # 自动尝试设置AI
        self.setup_ai()
        
    def display_welcome(self):
        """显示欢迎界面"""
        print("=" * 60)
        print("🌆 欢迎来到 ECHOPOLIS (回声都市) 🌆")
        print("=" * 60)
        print("在这个AI驱动的金融模拟世界中，")
        print("你将通过'意识回响'引导你的AI化身，")
        print("在复杂的金融世界中做出决策，")
        print("体验每一个选择的深远影响。")
        print()
        print("🎮 可用指令:")
        print("  create <MBTI> <姓名>  - 创建AI化身 (如: create INTP Alex)")
        if not self.ai_enabled:
            print("  💡 当前使用规则决策，如需AI决策请配置API Key")
        print("  status               - 查看化身状态")
        print("  situation            - 生成新的决策情况")
        print("  echo <内容>          - 发送意识回响")
        print("  decide               - AI自主决策")
        print("  day                  - 推进一天")
        print("  save                 - 保存游戏")
        print("  load                 - 加载游戏")
        print("  help                 - 显示帮助")
        print("  quit                 - 退出游戏")
        print("=" * 60)
    
    def display_mbti_options(self):
        """显示MBTI选项"""
        print("\n📋 选择你的人格类型:")
        
        mbti_profiles = {
            "ISTJ": {
                "title": "稽查者",
                "portrait": "像一座花岗岩堡垒般可靠\n账本精确到小数点后两位\n遵循着祖辈传下的日程表\n用事实与经验浇筑世界秩序"
            },
            "ISFJ": {
                "title": "守护者", 
                "portrait": "指尖带着温热的牛奶香\n总记得你过敏的药材名\n相册按年份编码存放\n用绒布擦拭每段回忆"
            },
            "INFJ": {
                "title": "劝告者",
                "portrait": "看见火焰在众人眼中熄灭\n用隐喻缝补破碎的灵魂\n深夜书房亮着椭圆光斑\n先知在稿纸上承受刺痛"
            },
            "INTJ": {
                "title": "战略家",
                "portrait": "棋盘延伸到十年之后\n卒子过河即成女王\n图书馆穹顶投下冷光\n将万物纳入思维矩阵"
            },
            "ISTP": {
                "title": "巧匠",
                "portrait": "摩托车引擎倒悬如心脏\n扳手旋转出黄金比例\n对说明书嗤之以鼻\n用直觉拆解时空密码"
            },
            "ISFP": {
                "title": "艺术家",
                "portrait": "颜料在帆布上长出静脉\n耳后别着野蕨的春天\n拒绝所有标签式拥抱\n用沉默捍卫敏感内核"
            },
            "INFP": {
                "title": "调停者",
                "portrait": "捧着水晶般易碎的理想\n在现实荆棘中采血验玫瑰\n日记本里压着三叶虫化石\n与十九世纪诗人共用一副灵魂"
            },
            "INTP": {
                "title": "逻辑学家",
                "portrait": "在脑内搭建巴别图书馆\n用公式翻译上帝呓语\n咖啡杯沿印着群论推导\n突然停顿的交谈间隙"
            },
            "ESTP": {
                "title": "践行者",
                "portrait": "闯红灯的瞬间大笑不止\n风险是活着的盐粒\n即兴扑克牌局赌注\n——整条街道的日落权"
            },
            "ESFP": {
                "title": "表演者",
                "portrait": "把每间客厅变成舞台\n笑声如彩纸屑旋转飘落\n记住所有邻居的宠物名\n用肢体语言翻译快乐"
            },
            "ENFP": {
                "title": "倡导者",
                "portrait": "思维是永不停歇的烟花厂\n拉着陌生人畅想火星幼儿园\n背包里装着未实现的奇迹\n眼泪与灵感同等珍贵"
            },
            "ENTP": {
                "title": "辩论家",
                "portrait": "用悖论编织投石器\n击碎所有庄严的玻璃窗\n魔鬼辩护席空置太久\n正好练习反向哲学体操"
            },
            "ESTJ": {
                "title": "监督者",
                "portrait": "怀表链拴着整个组织体系\n用效率浇筑社会骨架\n名单勾选框必须直角\n延迟是原罪的一种形式"
            },
            "ESFJ": {
                "title": "执政官",
                "portrait": "记得所有成员的过敏原\n社区花名册是圣典\n用烘焙饼干化解纠纷\n门廊灯为晚归者多亮一刻"
            },
            "ENFJ": {
                "title": "教育家",
                "portrait": "在瞳孔深处点燃星火\n话语长出牵引的羽翼\n发现每个灵魂的密钥\n却把自己的锁孔藏在雾中"
            },
            "ENTJ": {
                "title": "指挥官",
                "portrait": "将混沌锻造成进度图表\n目光扫过之处升起脚手架\n战略蓝图铺满黎明\n——用咖啡渍标注滩头阵地"
            }
        }
        
        for mbti, profile in mbti_profiles.items():
            print(f"\n🎭 {mbti} - {profile['title']}")
            print(f"   {profile['portrait']}")
        print()
    
    def create_avatar(self, mbti_str: str, name: str) -> bool:
        """创建AI化身"""
        try:
            mbti_type = MBTIType(mbti_str.upper())
            
            # 显示选中的MBTI画像
            self._display_selected_mbti_profile(mbti_str.upper())
            
            self.current_avatar = AIAvatar(name, mbti_type)
            self.game_started = True
            
            print(f"\n🎉 成功创建AI化身: {name} ({mbti_str.upper()})")
            print(f"🎲 命运轮盘结果: {self.current_avatar.fate_background.name}")
            print(f"💰 初始资金: {self.current_avatar.attributes.credits:,} CP")
            print(f"🤖 AI模式: {'DeepSeek AI决策' if self.ai_enabled else '规则决策'}")
            print(f"📖 背景故事: {self.current_avatar.fate_background.background_story}")
            print(f"✨ 特殊特质: {', '.join(self.current_avatar.fate_background.special_traits)}")
            
            return True
        except ValueError:
            print(f"❌ 无效的MBTI类型: {mbti_str}")
            print("请使用有效的MBTI类型，如: INTP, ENTJ, ISFJ 等")
            return False
    
    def _display_selected_mbti_profile(self, mbti: str):
        """显示选中的MBTI画像"""
        mbti_profiles = {
            "ISTJ": {
                "title": "稽查者",
                "portrait": "像一座花岗岩堡垒般可靠\n账本精确到小数点后两位\n遵循着祖辈传下的日程表\n用事实与经验浇筑世界秩序"
            },
            "ISFJ": {
                "title": "守护者", 
                "portrait": "指尖带着温热的牛奶香\n总记得你过敏的药材名\n相册按年份编码存放\n用绒布擦拭每段回忆"
            },
            "INFJ": {
                "title": "劝告者",
                "portrait": "看见火焰在众人眼中熄灭\n用隐喻缝补破碎的灵魂\n深夜书房亮着椭圆光斑\n先知在稿纸上承受刺痛"
            },
            "INTJ": {
                "title": "战略家",
                "portrait": "棋盘延伸到十年之后\n卒子过河即成女王\n图书馆穹顶投下冷光\n将万物纳入思维矩阵"
            },
            "ISTP": {
                "title": "巧匠",
                "portrait": "摩托车引擎倒悬如心脏\n扳手旋转出黄金比例\n对说明书嗤之以鼻\n用直觉拆解时空密码"
            },
            "ISFP": {
                "title": "艺术家",
                "portrait": "颜料在帆布上长出静脉\n耳后别着野蕨的春天\n拒绝所有标签式拥抱\n用沉默捍卫敏感内核"
            },
            "INFP": {
                "title": "调停者",
                "portrait": "捧着水晶般易碎的理想\n在现实荆棘中采血验玫瑰\n日记本里压着三叶虫化石\n与十九世纪诗人共用一副灵魂"
            },
            "INTP": {
                "title": "逻辑学家",
                "portrait": "在脑内搭建巴别图书馆\n用公式翻译上帝呓语\n咖啡杯沿印着群论推导\n突然停顿的交谈间隙"
            },
            "ESTP": {
                "title": "践行者",
                "portrait": "闯红灯的瞬间大笑不止\n风险是活着的盐粒\n即兴扑克牌局赌注\n——整条街道的日落权"
            },
            "ESFP": {
                "title": "表演者",
                "portrait": "把每间客厅变成舞台\n笑声如彩纸屑旋转飘落\n记住所有邻居的宠物名\n用肢体语言翻译快乐"
            },
            "ENFP": {
                "title": "倡导者",
                "portrait": "思维是永不停歇的烟花厂\n拉着陌生人畅想火星幼儿园\n背包里装着未实现的奇迹\n眼泪与灵感同等珍贵"
            },
            "ENTP": {
                "title": "辩论家",
                "portrait": "用悖论编织投石器\n击碎所有庄严的玻璃窗\n魔鬼辩护席空置太久\n正好练习反向哲学体操"
            },
            "ESTJ": {
                "title": "监督者",
                "portrait": "怀表链拴着整个组织体系\n用效率浇筑社会骨架\n名单勾选框必须直角\n延迟是原罪的一种形式"
            },
            "ESFJ": {
                "title": "执政官",
                "portrait": "记得所有成员的过敏原\n社区花名册是圣典\n用烘焙饼干化解纠纷\n门廊灯为晚归者多亮一刻"
            },
            "ENFJ": {
                "title": "教育家",
                "portrait": "在瞳孔深处点燃星火\n话语长出牵引的羽翼\n发现每个灵魂的密钥\n却把自己的锁孔藏在雾中"
            },
            "ENTJ": {
                "title": "指挥官",
                "portrait": "将混沌锻造成进度图表\n目光扫过之处升起脚手架\n战略蓝图铺满黎明\n——用咖啡渍标注滩头阵地"
            }
        }
        
        profile = mbti_profiles.get(mbti)
        if profile:
            print(f"\n🎭 你选择了: {mbti} - {profile['title']}")
            print(f"\n📜 你的人格画像:")
            print(f"   {profile['portrait']}")
            print("\n🤖 AI将根据这个画像为你生成个性化的情况和决策...")
    
    def show_status(self):
        """显示化身状态"""
        if not self.current_avatar:
            print("❌ 请先创建AI化身")
            return
        
        status = self.current_avatar.get_status()
        
        print("\n" + "=" * 50)
        print(f"📊 {status['basic_info']['name']} 的状态报告")
        print("=" * 50)
        
        print(f"👤 基本信息:")
        print(f"   年龄: {status['basic_info']['age']}岁")
        print(f"   人格: {status['basic_info']['mbti']}")
        print(f"   出身: {status['basic_info']['fate']}")
        print(f"   阶段: {status['basic_info']['life_stage']}")
        
        print(f"\n💰 财务状况:")
        print(f"   资金: {status['financial']['credits']}")
        print(f"   信用分: {status['financial']['credit_score']}")
        
        print(f"\n🏥 身心状态:")
        print(f"   健康: {status['physical_mental']['health']}")
        print(f"   精力: {status['physical_mental']['energy']}")
        print(f"   幸福感: {status['physical_mental']['happiness']}")
        print(f"   压力: {status['physical_mental']['stress']}")
        
        print(f"\n🤝 关系状态:")
        print(f"   信任度: {status['relationship']['trust_level']}")
        print(f"   关系: {status['relationship']['trust_status']}")
        
        print(f"\n📈 决策表现:")
        print(f"   总决策数: {status['performance']['total_decisions']}")
        print(f"   成功率: {status['performance']['successful_rate']}")
        
        print(f"\n✨ 特殊特质: {', '.join(status['special_traits'])}")
        print(f"\n📖 背景故事: {status['background_story']}")
        
        # 显示干预点数和AI状态
        print(f"\n🎯 今日剩余干预点数: {echo_system.intervention_points}/10")
        print(f"🤖 AI状态: {'DeepSeek AI决策' if self.ai_enabled else '规则决策'}")
    
    def generate_situation(self):
        """生成新的决策情况"""
        if not self.current_avatar:
            print("❌ 请先创建AI化身")
            return
        
        situation = self.current_avatar.generate_situation(self.ai_engine)
        
        if not situation:
            print("❌ 无法生成情况，请稍后重试")
            return
        
        print("\n" + "🔔" * 20)
        print("📋 新情况出现!")
        print("🔔" * 20)
        print(f"📝 情况描述: {situation.situation}")
        print(f"\n🔀 可选择的行动:")
        for i, option in enumerate(situation.options, 1):
            print(f"   {i}. {option}")
        
        print(f"\n💡 提示: 使用 'echo <你的建议>' 来影响AI的决策")
        print(f"       或使用 'decide' 让AI自主决策")
    
    def send_echo(self, echo_text: str):
        """发送意识回响"""
        if not self.current_avatar:
            print("❌ 请先创建AI化身")
            return
        
        if not self.current_avatar.current_situation:
            print("❌ 当前没有需要决策的情况，请先使用 'situation' 生成情况")
            return
        
        # 处理回响
        result = echo_system.process_echo(
            echo_text, 
            self.current_avatar.current_situation.options,
            self.current_avatar.attributes.trust_level
        )
        
        if not result["success"]:
            print(f"❌ {result['message']}")
            return
        
        print(f"\n💭 你的回响: '{echo_text}'")
        print(f"📊 回响分析: {result['analysis'].echo_type.value} | 置信度: {result['analysis'].confidence:.2f}")
        print(f"🎯 影响权重: {result['influence_weight']:.2f}")
        print(f"⚡ 剩余干预点数: {result['remaining_points']}")
        
        # AI做出决策
        decision_result = self.current_avatar.make_decision(echo_text, self.ai_engine)
        
        # 首先显示决策结果
        print(f"\n🤖 AI决策: {decision_result['chosen_option']}")
        print(f"📈 信任度变化: {decision_result['trust_change']:+d} (当前: {decision_result['new_trust_level']})")
        
        # 显示资产变化和总量
        if 'asset_change' in decision_result:
            asset_change = decision_result['asset_change']
            cash_flow_change = decision_result.get('cash_flow_change', 0)
            print(f"💰 资产变化: {asset_change:+,} CP ({decision_result['asset_desc']})")
            print(f"💵 现金流变化: {cash_flow_change:+,} CP")
            print(f"💳 资产总量: {decision_result['new_credits']:,} CP")
            print(f"💵 现金流: {decision_result['cash_flow']:+,} CP")
            
            if decision_result['is_bankrupt']:
                print("💥 破产警告: 现金流为负，游戏失败！")
                return
        
        # 然后显示内心独白
        print(f"\n💡 AI内心独白: {decision_result['ai_thoughts']}")
        
        # 记录AI想法
        self._log_ai_thoughts(decision_result)
    
    def ai_decide(self):
        """AI自主决策"""
        if not self.current_avatar:
            print("❌ 请先创建AI化身")
            return
        
        if not self.current_avatar.current_situation:
            print("❌ 当前没有需要决策的情况，请先使用 'situation' 生成情况")
            return
        
        decision_result = self.current_avatar.make_decision(None, self.ai_engine)
        
        # 首先显示决策结果
        print(f"\n🤖 AI自主决策: {decision_result['chosen_option']}")
        
        # 显示资产变化和总量
        if 'asset_change' in decision_result:
            asset_change = decision_result['asset_change']
            cash_flow_change = decision_result.get('cash_flow_change', 0)
            print(f"💰 资产变化: {asset_change:+,} CP ({decision_result['asset_desc']})")
            print(f"💵 现金流变化: {cash_flow_change:+,} CP")
            print(f"💳 资产总量: {decision_result['new_credits']:,} CP")
            print(f"💵 现金流: {decision_result['cash_flow']:+,} CP")
            
            if decision_result['is_bankrupt']:
                print("💥 破产警告: 现金流为负，游戏失败！")
                return
        
        # 然后显示内心独白
        print(f"💡 AI内心独白: {decision_result['ai_thoughts']}")
        
        # 记录AI想法
        self._log_ai_thoughts(decision_result)
    
    def advance_round(self):
        """推进一回合（一个月）"""
        if not self.current_avatar:
            print("❌ 请先创建AI化身")
            return
        
        self.current_avatar.advance_round()
        echo_system.reset_daily_points()
        
        print(f"\n📅 第{self.current_avatar.attributes.current_round}回合开始!")
        print(f"⚡ 精力恢复: {self.current_avatar.attributes.energy}/100")
        print(f"😌 压力缓解: {self.current_avatar.attributes.stress}/100")
        print(f"🎯 干预点数重置: {echo_system.intervention_points}/10")
        
        # 显示锁定投资状态
        if self.current_avatar.attributes.locked_investments:
            print(f"🔒 锁定投资: {len(self.current_avatar.attributes.locked_investments)}项")
        
        if self.current_avatar.attributes.current_round % 12 == 0:
            print(f"🎂 {self.current_avatar.attributes.name} 又长大了一岁! 现在 {self.current_avatar.attributes.age} 岁")
    
    def save_game(self):
        """保存游戏"""
        if not self.current_avatar:
            print("❌ 没有可保存的游戏数据")
            return
        
        try:
            save_data = {
                "avatar_state": self.current_avatar.save_state(),
                "echo_history": echo_system.echo_history,
                "intervention_points": echo_system.intervention_points,
                "save_time": datetime.now().isoformat()
            }
            
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 游戏已保存到 {self.save_file}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def load_game(self):
        """加载游戏"""
        if not os.path.exists(self.save_file):
            print("❌ 没有找到存档文件")
            return
        
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 重建化身
            avatar_data = save_data["avatar_state"]
            mbti_type = MBTIType(avatar_data["attributes"]["mbti_type"])
            name = avatar_data["attributes"]["name"]
            
            self.current_avatar = AIAvatar(name, mbti_type)
            self.current_avatar.load_state(avatar_data)
            
            # 恢复回响系统状态
            echo_system.echo_history = save_data.get("echo_history", [])
            echo_system.intervention_points = save_data.get("intervention_points", 10)
            
            self.game_started = True
            
            save_time = save_data.get("save_time", "未知时间")
            print(f"📂 游戏加载成功! (保存时间: {save_time})")
            print(f"👤 欢迎回来, {self.current_avatar.attributes.name}!")
            
        except Exception as e:
            print(f"❌ 加载失败: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📖 Echopolis 游戏指南")
        print("=" * 40)
        print("🎯 游戏目标:")
        print("   通过'意识回响'影响你的AI化身，")
        print("   在金融世界中做出明智决策，")
        print("   体验选择与后果的深度关联。")
        print()
        print("🎮 基本流程:")
        print("   1. 创建AI化身 (create)")
        print("   2. 生成决策情况 (situation)")
        print("   3. 发送回响影响 (echo)")
        print("   4. 观察AI决策结果")
        print("   5. 推进时间 (day)")
        print()
        print("💡 游戏技巧:")
        print("   • 建立信任关系很重要")
        print("   • 每日干预点数有限，谨慎使用")
        print("   • 不同MBTI类型有不同决策倾向")
        print("   • 化身的状态会影响决策质量")
        print("   • 长期规划比短期收益更重要")
    
    def run(self):
        """运行游戏主循环"""
        self.display_welcome()
        
        while True:
            try:
                command = input("\n🎮 请输入指令: ").strip()
                
                if not command:
                    continue
                
                parts = command.split(' ', 2)
                cmd = parts[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    print("👋 感谢游玩 Echopolis! 再见!")
                    break
                
                elif cmd == "help":
                    self.show_help()
                
                elif cmd == "create":
                    if len(parts) < 3:
                        print("❌ 用法: create <MBTI> <姓名>")
                        print("例如: create INTP Alex")
                        self.display_mbti_options()
                    else:
                        self.create_avatar(parts[1], parts[2])
                
                elif cmd == "status":
                    self.show_status()
                
                elif cmd == "situation":
                    self.generate_situation()
                
                elif cmd == "echo":
                    if len(parts) < 2:
                        print("❌ 用法: echo <你的建议>")
                        print("例如: echo 我建议你小额试水，风险太大")
                    else:
                        echo_text = ' '.join(parts[1:])
                        self.send_echo(echo_text)
                
                elif cmd == "decide":
                    self.ai_decide()
                
                elif cmd == "round" or cmd == "next":
                    self.advance_round()
                
                elif cmd == "save":
                    self.save_game()
                
                elif cmd == "load":
                    self.load_game()
                
                else:
                    print(f"❌ 未知指令: {cmd}")
                    print("输入 'help' 查看可用指令")
            
            except KeyboardInterrupt:
                print("\n👋 游戏被中断，再见!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                print("请重试或输入 'help' 查看帮助")
    
    def setup_ai(self):
        """设置DeepSeek AI"""
        # 从环境变量或配置文件读取API key
        api_key = self._get_api_key()
        
        if not api_key:
            return False
        
        try:
            self.ai_engine = initialize_deepseek(api_key)
            if self.ai_engine:
                self.ai_enabled = True
                return True
            return False
        except Exception as e:
            return False
    
    def _get_api_key(self) -> str:
        """获取API Key"""
        # 1. 从环境变量读取
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if api_key:
            return api_key
        
        # 2. 从配置文件读取
        config_file = 'config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get('deepseek_api_key', '')
                    if api_key and api_key != 'sk-your-deepseek-api-key-here':
                        return api_key
            except Exception:
                pass
        
        # 3. 创建默认配置文件
        self._create_default_config()
        return ''
    
    def _create_default_config(self):
        """创建默认配置文件"""
        config_file = 'config.json'
        if not os.path.exists(config_file):
            default_config = {
                "deepseek_api_key": "sk-your-deepseek-api-key-here",
                "game_settings": {
                    "auto_save": True,
                    "difficulty": "normal"
                }
            }
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
    
    def _log_ai_thoughts(self, decision_result: Dict):
        """记录AI想法到文件"""
        if not self.current_avatar:
            return
        
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "avatar_name": self.current_avatar.attributes.name,
                "mbti_type": self.current_avatar.attributes.mbti_type.value,
                "age": self.current_avatar.attributes.age,
                "decision_count": self.current_avatar.attributes.decision_count,
                "chosen_option": decision_result['chosen_option'],
                "ai_thoughts": decision_result['ai_thoughts'],
                "trust_level": decision_result['new_trust_level'],
                "trust_change": decision_result['trust_change']
            }
            
            log_file = f"ai_thoughts_{self.current_avatar.attributes.name}.json"
            
            # 读取现有记录
            thoughts_log = []
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    thoughts_log = json.load(f)
            
            # 添加新记录
            thoughts_log.append(log_entry)
            
            # 保持最近100条记录
            if len(thoughts_log) > 100:
                thoughts_log = thoughts_log[-100:]
            
            # 写入文件
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(thoughts_log, f, ensure_ascii=False, indent=2)
                
        except Exception:
            pass  # 静默失败，不影响游戏体验

def main():
    """主函数"""
    game = EchopolisGame()
    game.run()

if __name__ == "__main__":
    main()
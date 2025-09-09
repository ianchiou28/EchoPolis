// Echopolis Web版本主游戏逻辑
class EchopolisGame {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.currentScene = 'main-menu';
        this.avatar = null;
        this.selectedMBTI = 0;
        
        // MBTI类型数据
        this.mbtiTypes = {
            'INTJ': '建筑师 - 富有想象力和战略性的思想家，一切皆在计划中',
            'INTP': '逻辑学家 - 具有创造性的发明家，对知识有着止不住的渴望',
            'ENTJ': '指挥官 - 大胆，富有想象力的强势领导者，总能找到或创造解决方法',
            'ENTP': '辩论家 - 聪明好奇的思想家，不会放弃任何挑战',
            'INFJ': '提倡者 - 安静而神秘，同时鼓舞他人的理想主义者',
            'INFP': '调停者 - 诗意，善良的利他主义者，总是热心为正义而战',
            'ENFJ': '主人公 - 魅力非凡的领导者，能够使听众着迷',
            'ENFP': '竞选者 - 热情，有创造性的社交者，总能找到微笑的理由',
            'ISTJ': '物流师 - 实用主义的现实主义者，可靠性无可置疑',
            'ISFJ': '守护者 - 非常专注而温暖的守护者，时刻准备保护爱着的人们',
            'ESTJ': '总经理 - 出色的管理者，在管理事物或人员方面无与伦比',
            'ESFJ': '执政官 - 极有同情心，善于社交的人们，总是热心帮助他人',
            'ISTP': '鉴赏家 - 大胆而实际的实验家，擅长使用各种工具',
            'ISFP': '探险家 - 灵活，迷人的艺术家，时刻准备探索新的可能性',
            'ESTP': '企业家 - 聪明，精力充沛的感知者，真正享受生活在边缘',
            'ESFP': '表演者 - 自发的，精力充沛的娱乐者，生活在他们周围从不无聊'
        };
        
        // 命运轮盘数据
        this.fateWheel = {
            '🏆 亿万富豪': { money: 100000000, desc: '含着金汤匙出生，家族企业遍布全球' },
            '📚 书香门第': { money: 1000000, desc: '知识分子家庭，重视教育和文化传承' },
            '💔 家道中落': { money: 10000, desc: '曾经辉煌的家族如今衰落，但保留着贵族的品味' },
            '💪 白手起家': { money: 50000, desc: '普通家庭出身，凭借自己的努力奋斗' },
            '🏠 中产家庭': { money: 200000, desc: '标准的中产阶级家庭，生活稳定舒适' },
            '🔧 工薪阶层': { money: 30000, desc: '蓝领工人家庭，勤劳朴实' },
            '👤 单亲家庭': { money: 25000, desc: '在单亲家庭中长大，更加独立坚强' }
        };
        
        // 游戏世界
        this.player = { x: 400, y: 300 };
        this.buildings = [
            { name: '中央银行', x: 200, y: 200, width: 80, height: 60, color: '#4a90e2' },
            { name: '金融中心', x: 400, y: 150, width: 100, height: 80, color: '#666' },
            { name: '住宅区', x: 600, y: 250, width: 60, height: 60, color: '#4caf50' }
        ];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupMBTIGrid();
        this.gameLoop();
    }
    
    setupEventListeners() {
        // 菜单按钮
        document.querySelectorAll('.menu-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                if (action === 'start') {
                    this.switchScene('avatar-creation');
                } else if (action === 'multiplayer') {
                    alert('多人模式开发中...');
                }
            });
        });
        
        // 创建化身按钮
        document.getElementById('create-avatar-btn').addEventListener('click', () => {
            this.createAvatar();
        });
        
        document.getElementById('back-to-menu-btn').addEventListener('click', () => {
            this.switchScene('main-menu');
        });
        
        // 键盘控制
        document.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
        
        // 聊天功能
        document.getElementById('send-echo-btn').addEventListener('click', () => {
            this.sendEcho();
        });
        
        document.getElementById('chat-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.sendEcho();
            }
        });
    }
    
    setupMBTIGrid() {
        const grid = document.getElementById('mbti-grid');
        const types = Object.keys(this.mbtiTypes);
        
        types.forEach((type, index) => {
            const btn = document.createElement('button');
            btn.className = 'mbti-btn';
            btn.textContent = type;
            btn.addEventListener('click', () => {
                this.selectMBTI(index);
            });
            grid.appendChild(btn);
        });
        
        this.selectMBTI(0); // 默认选择第一个
    }
    
    selectMBTI(index) {
        this.selectedMBTI = index;
        const types = Object.keys(this.mbtiTypes);
        const selectedType = types[index];
        
        // 更新按钮样式
        document.querySelectorAll('.mbti-btn').forEach((btn, i) => {
            btn.classList.toggle('selected', i === index);
        });
        
        // 更新描述
        document.getElementById('mbti-description').textContent = this.mbtiTypes[selectedType];
    }
    
    createAvatar() {
        const name = document.getElementById('avatar-name').value.trim();
        if (!name) {
            alert('请输入化身名字！');
            return;
        }
        
        const types = Object.keys(this.mbtiTypes);
        const mbtiType = types[this.selectedMBTI];
        
        // 随机命运
        const fateKeys = Object.keys(this.fateWheel);
        const fateKey = fateKeys[Math.floor(Math.random() * fateKeys.length)];
        const fate = this.fateWheel[fateKey];
        
        // 创建化身
        this.avatar = {
            name: name,
            mbtiType: mbtiType,
            assets: fate.money,
            health: 100,
            energy: 100,
            happiness: 50,
            stress: 0,
            trustLevel: 50,
            roundCount: 1,
            fateType: fateKey,
            fateDesc: fate.desc
        };
        
        // 显示命运结果
        const fateResult = document.getElementById('fate-result');
        fateResult.innerHTML = `
            <h4>🎲 命运轮盘结果</h4>
            <p><strong>${fateKey}</strong></p>
            <p>${fate.desc}</p>
            <p>初始资金: ${fate.money.toLocaleString()} CP</p>
        `;
        fateResult.style.display = 'block';
        
        setTimeout(() => {
            this.switchScene('game-scene');
            this.updateStatusPanel();
        }, 2000);
    }
    
    switchScene(sceneName) {
        document.querySelectorAll('.scene').forEach(scene => {
            scene.classList.remove('active');
        });
        document.getElementById(sceneName).classList.add('active');
        this.currentScene = sceneName;
    }
    
    handleKeyDown(e) {
        if (this.currentScene !== 'game-scene') return;
        
        const speed = 20;
        switch(e.key.toLowerCase()) {
            case 'w':
                this.player.y = Math.max(20, this.player.y - speed);
                break;
            case 's':
                this.player.y = Math.min(this.canvas.height - 20, this.player.y + speed);
                break;
            case 'a':
                this.player.x = Math.max(20, this.player.x - speed);
                break;
            case 'd':
                this.player.x = Math.min(this.canvas.width - 20, this.player.x + speed);
                break;
            case 'enter':
                this.toggleChat();
                break;
            case 'tab':
                e.preventDefault();
                this.toggleStatusPanel();
                break;
            case ' ':
                this.interact();
                break;
        }
    }
    
    toggleChat() {
        const chatPanel = document.getElementById('chat-panel');
        chatPanel.classList.toggle('hidden');
        if (!chatPanel.classList.contains('hidden')) {
            document.getElementById('chat-input').focus();
        }
    }
    
    toggleStatusPanel() {
        const statusPanel = document.getElementById('status-panel');
        statusPanel.style.display = statusPanel.style.display === 'none' ? 'block' : 'none';
    }
    
    sendEcho() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (message) {
            console.log('发送回响:', message);
            // 触发带有玩家建议的情况生成
            this.generateSituationWithEcho(message);
            input.value = '';
            this.toggleChat();
        }
    }
    
    async generateSituationWithEcho(playerEcho) {
        // 生成情况并包含玩家的回响
        await this.generateSituation('general');
        // 存储玩家回响用于后续决策
        this.currentPlayerEcho = playerEcho;
    }
    
    interact() {
        // 检查玩家附近的建筑
        for (let building of this.buildings) {
            const distance = Math.sqrt(
                Math.pow(this.player.x - (building.x + building.width/2), 2) +
                Math.pow(this.player.y - (building.y + building.height/2), 2)
            );
            if (distance < 80) {
                this.triggerBuildingEvent(building);
                break;
            }
        }
    }
    
    triggerBuildingEvent(building) {
        switch(building.name) {
            case '中央银行':
                this.generateSituation('banking');
                break;
            case '金融中心':
                this.generateSituation('investment');
                break;
            case '住宅区':
                this.generateSituation('lifestyle');
                break;
            default:
                this.generateSituation('general');
        }
    }
    
    async generateSituation(contextType = 'general') {
        if (!this.avatar) return;
        
        const avatarContext = {
            name: this.avatar.name,
            mbti: this.avatar.mbtiType,
            assets: this.avatar.assets,
            health: this.avatar.health,
            happiness: this.avatar.happiness,
            stress: this.avatar.stress,
            roundCount: this.avatar.roundCount,
            contextType: contextType
        };
        
        try {
            const response = await fetch('/api/generate_situation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(avatarContext)
            });
            
            const situation = await response.json();
            this.showSituationDialog(situation);
        } catch (error) {
            console.error('生成情况失败:', error);
            this.showMockSituation(contextType);
        }
    }
    
    showSituationDialog(situation) {
        const dialog = document.createElement('div');
        dialog.className = 'situation-dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h3>📋 新情况出现！</h3>
                <p class="situation-text">${situation.situation}</p>
                <div class="options">
                    ${situation.options.map((option, index) => 
                        `<button class="option-btn" data-index="${index}">${index + 1}. ${option}</button>`
                    ).join('')}
                </div>
                <div class="dialog-actions">
                    <button id="ai-decide-btn">AI自主决策</button>
                    <button id="close-dialog-btn">关闭</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        // 绑定事件
        dialog.querySelectorAll('.option-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const optionIndex = parseInt(e.target.dataset.index);
                this.makeDecision(situation, optionIndex);
                document.body.removeChild(dialog);
            });
        });
        
        dialog.querySelector('#ai-decide-btn').addEventListener('click', () => {
            this.makeAIDecision(situation);
            document.body.removeChild(dialog);
        });
        
        dialog.querySelector('#close-dialog-btn').addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
    }
    
    showMockSituation(contextType) {
        const situations = {
            banking: {
                situation: `${this.avatar.name}，银行经理向你推荐了一款新的理财产品...`,
                options: ['购买50万CP理财产品', '申请贷款扩大投资', '仅咨询不购买']
            },
            investment: {
                situation: `在金融中心，你发现了一个热门的投资机会...`,
                options: ['投资100万CP到股市', '购买基金分散风险', '观望市场走势']
            },
            lifestyle: {
                situation: `在住宅区，你考虑是否要改善居住环境...`,
                options: ['购买豪华公寓', '装修现有住房', '维持现状']
            },
            general: {
                situation: `${this.avatar.name}，你遇到了一个重要的人生选择...`,
                options: ['积极行动', '谨慎考虑', '寻求建议']
            }
        };
        
        const situation = situations[contextType] || situations.general;
        this.showSituationDialog(situation);
    }
    
    async makeDecision(situation, optionIndex) {
        const chosenOption = situation.options[optionIndex];
        console.log('玩家选择:', chosenOption);
        
        // 应用决策结果
        this.applyDecisionResult(chosenOption);
        this.showDecisionResult(chosenOption, '你做出了明智的选择！');
    }
    
    async makeAIDecision(situation) {
        const decisionData = {
            avatar_context: {
                name: this.avatar.name,
                mbti: this.avatar.mbtiType,
                assets: this.avatar.assets,
                trust: this.avatar.trustLevel
            },
            situation: situation,
            player_echo: null
        };
        
        try {
            const response = await fetch('/api/make_decision', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(decisionData)
            });
            
            const result = await response.json();
            this.applyDecisionResult(result.chosen_option);
            this.showDecisionResult(result.chosen_option, result.ai_thoughts);
        } catch (error) {
            console.error('AI决策失败:', error);
            const randomChoice = situation.options[Math.floor(Math.random() * situation.options.length)];
            this.applyDecisionResult(randomChoice);
            this.showDecisionResult(randomChoice, 'AI做出了决策');
        }
    }
    
    applyDecisionResult(chosenOption) {
        // 根据选择应用游戏效果
        let assetChange = 0;
        let healthChange = 0;
        let happinessChange = 0;
        
        if (chosenOption.includes('投资') || chosenOption.includes('购买')) {
            const amount = this.extractAmount(chosenOption);
            assetChange = -amount + Math.random() * amount * 0.3; // 可能盈亏
            this.avatar.stress += 5;
        } else if (chosenOption.includes('观望') || chosenOption.includes('谨慎')) {
            happinessChange = -2;
            this.avatar.stress -= 3;
        }
        
        this.avatar.assets += assetChange;
        this.avatar.health += healthChange;
        this.avatar.happiness += happinessChange;
        this.avatar.roundCount += 1;
        
        // 确保数值在合理范围内
        this.avatar.assets = Math.max(0, this.avatar.assets);
        this.avatar.health = Math.max(0, Math.min(100, this.avatar.health));
        this.avatar.happiness = Math.max(0, Math.min(100, this.avatar.happiness));
        this.avatar.stress = Math.max(0, Math.min(100, this.avatar.stress));
        
        this.updateStatusPanel();
    }
    
    extractAmount(text) {
        const match = text.match(/(\d+)万/);
        return match ? parseInt(match[1]) * 10000 : 10000;
    }
    
    showDecisionResult(choice, thoughts) {
        const result = document.createElement('div');
        result.className = 'decision-result';
        result.innerHTML = `
            <div class="result-content">
                <h3>✅ 决策完成</h3>
                <p><strong>选择:</strong> ${choice}</p>
                <p><strong>想法:</strong> ${thoughts}</p>
                <button id="continue-btn">继续游戏</button>
            </div>
        `;
        
        document.body.appendChild(result);
        
        result.querySelector('#continue-btn').addEventListener('click', () => {
            document.body.removeChild(result);
        });
        
        // 3秒后自动关闭
        setTimeout(() => {
            if (document.body.contains(result)) {
                document.body.removeChild(result);
            }
        }, 3000);
    }
    
    updateStatusPanel() {
        if (!this.avatar) return;
        
        const statusDiv = document.getElementById('avatar-status');
        statusDiv.innerHTML = `
            <p><strong>🤖 ${this.avatar.name} (${this.avatar.mbtiType})</strong></p>
            <p>💰 资产: ${this.avatar.assets.toLocaleString()} CP</p>
            <p>❤️ 健康: ${this.avatar.health}/100</p>
            <p>⚡ 精力: ${this.avatar.energy}/100</p>
            <p>😊 幸福: ${this.avatar.happiness}/100</p>
            <p>📅 回合: ${this.avatar.roundCount}</p>
            <p>🎲 命运: ${this.avatar.fateType}</p>
        `;
    }
    
    gameLoop() {
        this.render();
        requestAnimationFrame(() => this.gameLoop());
    }
    
    render() {
        if (this.currentScene !== 'game-scene') return;
        
        // 清空画布
        this.ctx.fillStyle = '#0a0f1c';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制网格
        this.drawGrid();
        
        // 绘制建筑
        this.drawBuildings();
        
        // 绘制玩家
        this.drawPlayer();
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#1a2332';
        this.ctx.lineWidth = 1;
        
        for (let x = 0; x < this.canvas.width; x += 50) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        for (let y = 0; y < this.canvas.height; y += 50) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }
    
    drawBuildings() {
        this.buildings.forEach(building => {
            // 绘制建筑
            this.ctx.fillStyle = building.color;
            this.ctx.fillRect(building.x, building.y, building.width, building.height);
            
            // 绘制边框
            this.ctx.strokeStyle = '#fff';
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(building.x, building.y, building.width, building.height);
            
            // 绘制名称
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '14px Microsoft YaHei';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(building.name, 
                building.x + building.width/2, 
                building.y - 10);
        });
    }
    
    drawPlayer() {
        // 绘制玩家角色
        this.ctx.fillStyle = '#ff6b6b';
        this.ctx.beginPath();
        this.ctx.arc(this.player.x, this.player.y, 15, 0, Math.PI * 2);
        this.ctx.fill();
        
        // 绘制边框
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // 绘制名字
        if (this.avatar) {
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '12px Microsoft YaHei';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(this.avatar.name, this.player.x, this.player.y - 25);
        }
    }
}

// 启动游戏
window.addEventListener('DOMContentLoaded', () => {
    new EchopolisGame();
});
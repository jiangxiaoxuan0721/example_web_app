// 主页功能卡片组件
class FunctionCards {
    constructor() {
        this.cards = [
            {
                id: 'n1-analysis',
                title: 'N-1分析',
                description: '电力系统N-1安全分析，评估系统在单个元件故障时的稳定性和可靠性。',
                icon: '⚡',
                status: 'available',
                statusText: '可用',
                className: '',
                action: () => this.handleN1Analysis()
            },
            {
                id: 'test-card-1',
                title: '潮流计算',
                description: '电力系统潮流计算分析，计算系统中的功率分布和电压状态。',
                icon: '📊',
                status: 'development',
                statusText: '开发中',
                className: '',
                action: () => this.handleTestCard(1)
            },
            {
                id: 'test-card-2',
                title: '短路计算',
                description: '电力系统短路电流计算，分析系统故障时的短路电流水平。',
                icon: '🔧',
                status: 'development',
                statusText: '开发中',
                className: '',
                action: () => this.handleTestCard(2)
            },
            {
                id: 'test-card-3',
                title: '暂态稳定',
                description: '电力系统暂态稳定性分析，评估系统在大扰动下的动态响应。',
                icon: '🌊',
                status: 'development',
                statusText: '开发中',
                className: '',
                action: () => this.handleTestCard(3)
            },
            {
                id: 'test-card-4',
                title: '电压稳定',
                description: '电力系统电压稳定性分析，评估系统的电压崩溃风险。',
                icon: '⚡',
                status: 'coming-soon',
                statusText: '即将推出',
                className: '',
                action: () => this.handleTestCard(4)
            },
            {
                id: 'test-card-5',
                title: '优化调度',
                description: '电力系统优化调度，实现经济运行和资源优化配置。',
                icon: '🎯',
                status: 'coming-soon',
                statusText: '即将推出',
                className: '',
                action: () => this.handleTestCard(5)
            }
        ];
    }

    init() {
        this.renderCards();
    }

    renderCards() {
        const container = document.getElementById('cardsContainer');
        if (!container) return;

        container.innerHTML = '';

        this.cards.forEach(card => {
            const cardElement = this.createCardElement(card);
            container.appendChild(cardElement);
        });
    }

    createCardElement(card) {
        const cardDiv = document.createElement('div');
        cardDiv.className = `function-card ${card.className}`;
        cardDiv.innerHTML = `
            <div class="card-icon">${card.icon}</div>
            <h3 class="card-title">${card.title}</h3>
            <p class="card-description">${card.description}</p>
            <span class="card-status status-${card.status}">${card.statusText}</span>
        `;

        cardDiv.addEventListener('click', () => {
            if (card.status === 'available') {
                card.action();
            } else {
                this.showNotAvailableMessage(card.title);
            }
        });

        return cardDiv;
    }

    handleN1Analysis() {
        console.log('启动N-1分析');
        // 跳转到批量N-1分析页面
        window.location.href = '/batch-n1';
    }

    handleTestCard(cardNumber) {
        console.log(`点击测试卡片 ${cardNumber}`);
        alert(`测试卡片 ${cardNumber} 功能正在开发中`);
    }

    showNotAvailableMessage(featureName) {
        const message = document.createElement('div');
        message.className = 'notification';
        message.innerHTML = `
            <div class="notification-content">
                <h4>功能暂不可用</h4>
                <p>${featureName} 功能正在开发中，敬请期待！</p>
                <button onclick="this.parentElement.parentElement.remove()">确定</button>
            </div>
        `;
        document.body.appendChild(message);

        // 3秒后自动移除
        setTimeout(() => {
            if (message.parentElement) {
                message.remove();
            }
        }, 3000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    const functionCards = new FunctionCards();
    functionCards.init();
});
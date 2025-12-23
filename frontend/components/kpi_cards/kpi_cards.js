// KPI卡片组件
class KPICards {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            layout: 'default', // default, compact, large
            animated: true,
            autoRefresh: false,
            refreshInterval: 30000, // 30秒
            ...options
        };
        
        this.cards = [];
        this.refreshTimer = null;
        
        this.init();
    }

    init() {
        this.render();
        if (this.options.autoRefresh) {
            this.startAutoRefresh();
        }
    }

    render() {
        if (!this.container) return;
        
        const layoutClass = this.options.layout !== 'default' ? this.options.layout : '';
        this.container.className = `kpi-board ${layoutClass}`;
        
        this.container.innerHTML = this.cards.map(card => this.renderCard(card)).join('');
        
        if (this.options.animated) {
            this.animateCards();
        }
    }

    renderCard(card) {
        const typeClass = card.type || 'primary';
        const trendClass = card.trend ? `trend-${card.trend.direction}` : '';
        const loadingClass = card.loading ? 'loading' : '';
        const iconHtml = card.icon ? `<div class="kpi-icon">${card.icon}</div>` : '';
        
        return `
            <div class="kpi-card ${typeClass} ${loadingClass}" data-id="${card.id}">
                ${iconHtml}
                <div class="kpi-content">
                    <div class="kpi-title">${card.title}</div>
                    <div class="kpi-value ${typeClass}">${this.formatValue(card.value, card.format)}</div>
                    ${card.trend ? `
                        <div class="kpi-trend ${trendClass}">
                            ${card.trend.direction === 'up' ? '↑' : card.trend.direction === 'down' ? '↓' : '→'}
                            ${card.trend.value}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    formatValue(value, format) {
        if (value === null || value === undefined) return '--';
        
        if (format === 'number') {
            return Number(value).toLocaleString();
        }
        
        if (format === 'percentage') {
            return `${Number(value).toFixed(1)}%`;
        }
        
        if (format === 'currency') {
            return `¥${Number(value).toLocaleString()}`;
        }
        
        if (format === 'decimal') {
            return Number(value).toFixed(2);
        }
        
        return value;
    }

    renderMiniChart(chartData) {
        if (!chartData || !chartData.data) return '';
        
        return `
            <div class="kpi-chart">
                <canvas class="kpi-sparkline" id="sparkline-${chartData.id}"></canvas>
            </div>
        `;
    }

    animateCards() {
        const cards = this.container.querySelectorAll('.kpi-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
        
        // 渲染迷你图表
        setTimeout(() => {
            this.renderSparklines();
        }, 500);
    }

    renderSparklines() {
        this.cards.forEach(card => {
            if (card.chart && card.chart.data) {
                this.drawSparkline(`sparkline-${card.chart.id}`, card.chart);
            }
        });
    }

    drawSparkline(canvasId, chartData) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
        
        const data = chartData.data;
        const width = canvas.width;
        const height = canvas.height;
        const padding = 8;
        
        const maxValue = Math.max(...data);
        const minValue = Math.min(...data);
        const range = maxValue - minValue || 1;
        
        ctx.strokeStyle = chartData.color || '#1890ff';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        ctx.beginPath();
        data.forEach((value, index) => {
            const x = padding + (index / (data.length - 1)) * (width - 2 * padding);
            const y = height - padding - ((value - minValue) / range) * (height - 2 * padding);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();
        
        // 添加渐变填充
        if (chartData.fill) {
            const gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, chartData.color || '#1890ff');
            gradient.addColorStop(1, 'rgba(24, 144, 255, 0.1)');
            
            ctx.fillStyle = gradient;
            ctx.lineTo(width - padding, height - padding);
            ctx.lineTo(padding, height - padding);
            ctx.closePath();
            ctx.fill();
        }
    }

    setCards(cards) {
        this.cards = cards;
        this.render();
    }

    addCard(card) {
        this.cards.push(card);
        this.render();
    }

    updateCard(id, updates) {
        const cardIndex = this.cards.findIndex(card => card.id === id);
        if (cardIndex !== -1) {
            this.cards[cardIndex] = { ...this.cards[cardIndex], ...updates };
            this.render();
        }
    }

    removeCard(id) {
        this.cards = this.cards.filter(card => card.id !== id);
        this.render();
    }

    getCard(id) {
        return this.cards.find(card => card.id === id);
    }

    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        this.refreshTimer = setInterval(() => {
            if (this.options.onRefresh) {
                this.options.onRefresh();
            }
        }, this.options.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    destroy() {
        this.stopAutoRefresh();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }

    // 静态方法：创建KPI卡片数据
    static createCard(id, title, value, options = {}) {
        return {
            id,
            title,
            value,
            type: options.type || 'primary',
            format: options.format || 'number',
            subtitle: options.subtitle,
            trend: options.trend,
            chart: options.chart,
            loading: options.loading || false
        };
    }

    // 静态方法：创建趋势数据
    static createTrend(direction, value) {
        return {
            direction, // 'up', 'down', 'stable'
            value // 趋势值，如 '+5.2%', '-2.1%'
        };
    }

    // 静态方法：创建图表数据
    static createChart(id, data, options = {}) {
        return {
            id,
            data,
            color: options.color,
            fill: options.fill !== false
        };
    }
}

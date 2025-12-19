// 信息组件
class InformationComponent {
    constructor() {
        this.init();
    }

    init() {
        // 初始化信息面板
        this.initInfoPanels();
        this.initStatsCards();
    }

    initInfoPanels() {
        // 为信息面板添加交互效果
        const panels = document.querySelectorAll('.info-panel');
        
        panels.forEach(panel => {
            panel.addEventListener('mouseenter', () => {
                panel.style.transform = 'translateX(5px)';
                panel.style.transition = 'transform 0.3s ease';
            });

            panel.addEventListener('mouseleave', () => {
                panel.style.transform = 'translateX(0)';
            });
        });
    }

    initStatsCards() {
        // 为统计卡片添加数字动画效果
        const statsNumbers = document.querySelectorAll('.stats-number');
        
        statsNumbers.forEach(element => {
            const finalValue = parseInt(element.textContent);
            if (!isNaN(finalValue)) {
                this.animateNumber(element, 0, finalValue, 1000);
            }
        });
    }

    animateNumber(element, start, end, duration) {
        const startTime = performance.now();
        
        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(start + (end - start) * progress);
            element.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    }

    // 创建信息面板的静态方法
    static createInfoPanel(title, content, type = 'info') {
        const panel = document.createElement('div');
        panel.className = `info-panel ${type}`;
        panel.innerHTML = `
            <h3>${title}</h3>
            <p>${content}</p>
        `;
        return panel;
    }

    // 创建统计卡片的静态方法
    static createStatsCard(number, label) {
        const card = document.createElement('div');
        card.className = 'stats-card';
        card.innerHTML = `
            <div class="stats-number">${number}</div>
            <div class="stats-label">${label}</div>
        `;
        return card;
    }

    // 创建进度条的静态方法
    static createProgressBar(percentage, label = '') {
        const container = document.createElement('div');
        container.className = 'progress-container';
        
        if (label) {
            const labelElement = document.createElement('div');
            labelElement.className = 'progress-label';
            labelElement.textContent = label;
            container.appendChild(labelElement);
        }
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        
        const progressFill = document.createElement('div');
        progressFill.className = 'progress-fill';
        progressFill.style.width = `${percentage}%`;
        
        progressBar.appendChild(progressFill);
        container.appendChild(progressBar);
        
        return container;
    }

    // 创建标签的静态方法
    static createTag(text, type = 'primary') {
        const tag = document.createElement('span');
        tag.className = `tag tag-${type}`;
        tag.textContent = text;
        return tag;
    }

    // 显示通知消息
    static showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <p>${message}</p>
            </div>
        `;

        // 添加通知样式
        if (!document.querySelector('#notification-style')) {
            const style = document.createElement('style');
            style.id = 'notification-style';
            style.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1000;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                    max-width: 400px;
                    animation: slideInRight 0.3s ease;
                    border-left: 4px solid var(--primary-color);
                }
                
                .notification-success {
                    border-left-color: var(--success-color);
                }
                
                .notification-warning {
                    border-left-color: var(--warning-color);
                }
                
                .notification-danger {
                    border-left-color: var(--danger-color);
                }
                
                .notification-content {
                    padding: 15px 20px;
                }
                
                .notification-content p {
                    margin: 0;
                    color: var(--dark-color);
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // 自动移除
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, duration);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new InformationComponent();
});
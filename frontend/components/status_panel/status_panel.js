/**
 * 状态面板组件
 * 显示执行状态和模型信息
 */

class StatusPanel {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            title: '状态面板',
            statusMessage: '正在初始化...',
            showModelInfo: true,
            modelInfo: {},
            fields: [],
            ...options
        };
        
        this.render();
    }

    render() {
        const panel = document.createElement('div');
        panel.className = 'status-panel-container';
        
        let html = `
            <div class="status-item">
                <div class="status-indicator"></div>
                <div class="status-message">${this.options.statusMessage}</div>
            </div>
        `;

        if (this.options.showModelInfo) {
            html += `
                <div class="model-info-panel">
                    <h3>模型信息</h3>
                    <div class="info-grid">
                        ${this.options.fields.map(field => `
                            <div class="info-item">
                                <span class="info-label">${field.label}:</span>
                                <span class="info-value">${this.options.modelInfo[field.key] || '-'}</span>
                            </div>
                        `).join('')}
                    </div>
                    <p>模型已成功加载并初始化，可以进行下一步配置。</p>
                </div>
            `;
        }

        panel.innerHTML = html;
        this.container.appendChild(panel);
    }

    updateStatus(message, status = 'loading') {
        const statusMessage = this.container.querySelector('.status-message');
        const indicator = this.container.querySelector('.status-indicator');
        
        if (statusMessage) {
            statusMessage.textContent = message;
        }
        
        if (indicator) {
            indicator.className = `status-indicator status-${status}`;
        }
    }
}

window.StatusPanel = StatusPanel;

/**
 * 验证面板组件
 * 显示配置验证结果和批量次数确认
 */

class ValidationPanel {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            title: '参数检查与确认',
            description: '请检查批量仿真配置，并确认仿真次数',
            showCountInput: true,
            showTaskId: false,
            validations: [],
            ...options
        };
        
        this.render();
    }

    render() {
        const panel = document.createElement('div');
        panel.className = 'validation-panel-container';
        
        let html = `
            <div class="panel-header">
                <h2>${this.options.title}</h2>
                <p>${this.options.description}</p>
            </div>
            
            <div class="validation-results">
        `;

        this.options.validations.forEach(validation => {
            html += `
                <div class="validation-card validation-${validation.status}">
                    <div class="card-icon">${this.getIcon(validation.status)}</div>
                    <div class="card-content">
                        <h4>${validation.title}</h4>
                        <p>${validation.message}</p>
                    </div>
                </div>
            `;
        });

        html += `</div>`;

        if (this.options.showCountInput) {
            html += `
                <div class="batch-count-input">
                    <label for="batchCount">批量仿真次数</label>
                    <div class="input-wrapper">
                        <input type="number" id="batchCount" min="1" max="100" value="10">
                        <span>次</span>
                    </div>
                    <small>请输入批量仿真的次数（范围：1-100）</small>
                </div>
            `;
        }

        panel.innerHTML = html;
        this.container.appendChild(panel);
    }

    getIcon(status) {
        switch (status) {
            case 'success':
                return '✓';
            case 'warning':
                return '!';
            case 'error':
                return '✗';
            default:
                return '';
        }
    }

    getBatchCount() {
        const input = this.container.querySelector('#batchCount');
        return input ? parseInt(input.value) : 10;
    }

    setBatchCount(count) {
        const input = this.container.querySelector('#batchCount');
        if (input) {
            input.value = count;
        }
    }
}

window.ValidationPanel = ValidationPanel;

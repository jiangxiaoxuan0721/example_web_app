/**
 * 参数输入组件
 * 用于显示和编辑N-1仿真流程中的各种参数
 */

class ParameterInput {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`ParameterInput: Container with id '${containerId}' not found`);
            return;
        }

        this.options = {
            showReset: true,
            showApply: true,
            showSave: true,
            resetText: '重置',
            applyText: '应用',
            saveText: '保存参数',
            ...options
        };

        this.parameters = {};
        this.callbacks = {
            onParameterChange: options.onParameterChange || (() => {}),
            onApply: options.onApply || (() => {}),
            onReset: options.onReset || (() => {}),
            onSave: options.onSave || (() => {}),
            ...options.callbacks
        };

        this.init();
    }

    init() {
        this.container.classList.add('parameter-input');
        this.render();
        
        // 尝试加载之前保存的参数
        if (this.options.autoLoad !== false) {
            this.loadParameters();
        }
    }

    setParameters(parameters) {
        this.parameters = parameters;
        this.render();
    }

    updateParameter(name, value) {
        if (this.parameters[name]) {
            this.parameters[name].value = value;
            this.render();
            this.callbacks.onParameterChange(name, value);
        }
    }

    render() {
        this.container.innerHTML = '';

        const formContainer = document.createElement('div');
        formContainer.className = 'parameter-form';

        // 渲染参数输入
        Object.entries(this.parameters).forEach(([key, param]) => {
            const formGroup = this.createFormGroup(key, param);
            formContainer.appendChild(formGroup);
        });

        this.container.appendChild(formContainer);

        // 操作按钮
        if (this.options.showReset || this.options.showApply || this.options.showSave) {
            const actionsContainer = document.createElement('div');
            actionsContainer.className = 'parameter-actions';

            if (this.options.showReset) {
                const resetButton = document.createElement('button');
                resetButton.className = 'btn btn-secondary';
                resetButton.textContent = this.options.resetText;
                resetButton.addEventListener('click', () => this.resetParameters());
                actionsContainer.appendChild(resetButton);
            }

            if (this.options.showSave) {
                const saveButton = document.createElement('button');
                saveButton.className = 'btn btn-secondary';
                saveButton.textContent = this.options.saveText;
                saveButton.addEventListener('click', () => this.saveParameters());
                actionsContainer.appendChild(saveButton);
            }

            if (this.options.showApply) {
                const applyButton = document.createElement('button');
                applyButton.className = 'btn btn-primary';
                applyButton.textContent = this.options.applyText;
                applyButton.addEventListener('click', () => this.applyParameters());
                actionsContainer.appendChild(applyButton);
            }

            this.container.appendChild(actionsContainer);
        }
    }

    createFormGroup(key, param) {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';

        // 标签
        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = param.label || key;
        if (param.required) {
            label.classList.add('required');
        }
        label.htmlFor = `param-${key}`;
        formGroup.appendChild(label);

        // 输入控件容器
        const inputContainer = document.createElement('div');
        inputContainer.className = 'input-container';

        // 根据参数类型创建不同的输入控件
        let inputElement;
        switch (param.type) {
            case 'select':
                inputElement = this.createSelectElement(key, param);
                break;
            case 'textarea':
                inputElement = this.createTextareaElement(key, param);
                break;
            case 'checkbox':
                inputElement = this.createCheckboxElement(key, param);
                break;
            case 'radio':
                inputElement = this.createRadioElement(key, param);
                break;
            case 'range':
                inputElement = this.createRangeElement(key, param);
                break;
            case 'number':
                inputElement = this.createNumberElement(key, param);
                break;
            case 'json':
                inputElement = this.createJsonElement(key, param);
                break;
            default:
                inputElement = this.createTextElement(key, param);
        }

        inputContainer.appendChild(inputElement);

        // 单位
        if (param.unit) {
            const unit = document.createElement('span');
            unit.className = 'input-unit';
            unit.textContent = param.unit;
            inputContainer.appendChild(unit);
        }

        formGroup.appendChild(inputContainer);

        // 帮助文本
        if (param.help) {
            const helpText = document.createElement('div');
            helpText.className = 'form-help';
            helpText.textContent = param.help;
            formGroup.appendChild(helpText);
        }

        return formGroup;
    }

    createTextElement(key, param) {
        const input = document.createElement('input');
        input.type = 'text';
        input.id = `param-${key}`;
        input.className = 'form-input';
        input.name = key;
        input.value = param.value || '';
        
        if (param.placeholder) {
            input.placeholder = param.placeholder;
        }

        if (param.maxLength) {
            input.maxLength = param.maxLength;
        }

        input.addEventListener('input', (e) => {
            param.value = e.target.value;
            this.callbacks.onParameterChange(key, e.target.value);
        });

        return input;
    }

    createNumberElement(key, param) {
        const input = document.createElement('input');
        input.type = 'number';
        input.id = `param-${key}`;
        input.className = 'form-input';
        input.name = key;
        input.value = param.value || '';
        
        if (param.min !== undefined) {
            input.min = param.min;
        }

        if (param.max !== undefined) {
            input.max = param.max;
        }

        if (param.step !== undefined) {
            input.step = param.step;
        }

        input.addEventListener('input', (e) => {
            param.value = parseFloat(e.target.value) || 0;
            this.callbacks.onParameterChange(key, param.value);
        });

        return input;
    }

    createSelectElement(key, param) {
        const select = document.createElement('select');
        select.id = `param-${key}`;
        select.className = 'form-select';
        select.name = key;
        
        if (param.options) {
            param.options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.label || option.value;
                
                if (option.value === param.value) {
                    optionElement.selected = true;
                }
                
                select.appendChild(optionElement);
            });
        }

        select.addEventListener('change', (e) => {
            param.value = e.target.value;
            this.callbacks.onParameterChange(key, e.target.value);
        });

        return select;
    }

    createTextareaElement(key, param) {
        const textarea = document.createElement('textarea');
        textarea.id = `param-${key}`;
        textarea.className = 'form-textarea';
        textarea.name = key;
        textarea.value = param.value || '';
        
        if (param.rows) {
            textarea.rows = param.rows;
        }

        if (param.placeholder) {
            textarea.placeholder = param.placeholder;
        }

        textarea.addEventListener('input', (e) => {
            param.value = e.target.value;
            this.callbacks.onParameterChange(key, e.target.value);
        });

        return textarea;
    }

    createCheckboxElement(key, param) {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `param-${key}`;
        checkbox.className = 'form-checkbox';
        checkbox.name = key;
        checkbox.checked = !!param.value;
        
        checkbox.addEventListener('change', (e) => {
            param.value = e.target.checked;
            this.callbacks.onParameterChange(key, e.target.checked);
        });

        return checkbox;
    }

    createRadioElement(key, param) {
        const container = document.createElement('div');
        container.className = 'radio-group';
        
        if (param.options) {
            param.options.forEach(option => {
                const radioWrapper = document.createElement('div');
                radioWrapper.className = 'radio-wrapper';
                
                const radio = document.createElement('input');
                radio.type = 'radio';
                radio.id = `param-${key}-${option.value}`;
                radio.name = key;
                radio.value = option.value;
                radio.checked = option.value === param.value;
                
                const label = document.createElement('label');
                label.htmlFor = `param-${key}-${option.value}`;
                label.textContent = option.label || option.value;
                
                radio.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        param.value = e.target.value;
                        this.callbacks.onParameterChange(key, e.target.value);
                    }
                });
                
                radioWrapper.appendChild(radio);
                radioWrapper.appendChild(label);
                container.appendChild(radioWrapper);
            });
        }
        
        return container;
    }

    createRangeElement(key, param) {
        const container = document.createElement('div');
        container.className = 'range-container';
        
        const range = document.createElement('input');
        range.type = 'range';
        range.id = `param-${key}`;
        range.className = 'form-range';
        range.name = key;
        range.value = param.value || param.min || 0;
        
        if (param.min !== undefined) {
            range.min = param.min;
        }
        
        if (param.max !== undefined) {
            range.max = param.max;
        }
        
        if (param.step !== undefined) {
            range.step = param.step;
        }
        
        const valueDisplay = document.createElement('span');
        valueDisplay.className = 'range-value';
        valueDisplay.textContent = range.value;
        
        range.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            param.value = value;
            valueDisplay.textContent = value;
            this.callbacks.onParameterChange(key, value);
        });
        
        container.appendChild(range);
        container.appendChild(valueDisplay);
        
        return container;
    }

    createJsonElement(key, param) {
        const textarea = document.createElement('textarea');
        textarea.id = `param-${key}`;
        textarea.className = 'form-textarea json-editor';
        textarea.name = key;
        textarea.value = typeof param.value === 'object' 
            ? JSON.stringify(param.value, null, 2) 
            : param.value || '';
        
        if (param.rows) {
            textarea.rows = param.rows;
        }
        
        // 添加JSON验证
        textarea.addEventListener('input', (e) => {
            try {
                const jsonValue = JSON.parse(e.target.value);
                param.value = jsonValue;
                textarea.classList.remove('invalid');
                this.callbacks.onParameterChange(key, jsonValue);
            } catch (error) {
                textarea.classList.add('invalid');
                // 不触发回调，因为输入不是有效的JSON
            }
        });
        
        return textarea;
    }

    getParameterValues() {
        const values = {};
        Object.entries(this.parameters).forEach(([key, param]) => {
            values[key] = param.value;
        });
        return values;
    }

    setParameterValues(values) {
        Object.entries(values).forEach(([key, value]) => {
            if (this.parameters[key]) {
                this.parameters[key].value = value;
            }
        });
        this.render();
    }

    resetParameters() {
        Object.keys(this.parameters).forEach(key => {
            if (this.parameters[key].defaultValue !== undefined) {
                this.parameters[key].value = this.parameters[key].defaultValue;
            }
        });
        this.render();
        this.callbacks.onReset();
    }

    applyParameters() {
        this.callbacks.onApply(this.getParameterValues());
    }

    saveParameters() {
        const parameterValues = this.getParameterValues();
        
        // 保存到本地存储
        const storageKey = `parameter-input-${this.container.id}`;
        localStorage.setItem(storageKey, JSON.stringify(parameterValues));
        
        // 触发保存回调
        this.callbacks.onSave(parameterValues);
        
        // 显示保存成功通知
        this.showNotification('参数已保存', 'success');
    }

    loadParameters() {
        const storageKey = `parameter-input-${this.container.id}`;
        const savedValues = localStorage.getItem(storageKey);
        
        if (savedValues) {
            try {
                const parameterValues = JSON.parse(savedValues);
                this.setParameterValues(parameterValues);
                this.showNotification('参数已加载', 'info');
                return true;
            } catch (error) {
                console.error('Failed to load saved parameters:', error);
                this.showNotification('加载参数失败', 'error');
            }
        }
        
        return false;
    }

    clearSavedParameters() {
        const storageKey = `parameter-input-${this.container.id}`;
        localStorage.removeItem(storageKey);
        this.showNotification('已清除保存的参数', 'info');
    }

    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = 'parameter-notification';
        notification.textContent = message;
        
        // 根据类型设置样式
        switch (type) {
            case 'success':
                notification.style.backgroundColor = 'var(--success-color)';
                break;
            case 'error':
                notification.style.backgroundColor = 'var(--danger-color)';
                break;
            default:
                notification.style.backgroundColor = 'var(--info-color)';
        }
        
        notification.style.color = 'white';
        notification.style.padding = '10px 15px';
        notification.style.borderRadius = '4px';
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1000';
        notification.style.opacity = '0.9';
        notification.style.transition = 'opacity 0.3s ease';
        
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// 导出组件
window.ParameterInput = ParameterInput;
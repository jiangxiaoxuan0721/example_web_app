/**
 * 参数表格组件
 * 显示和编辑仿真参数
 */

class ParameterTable {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            title: '参数配置',
            fields: [],
            editable: true,
            loadData: null,
            saveData: null,
            ...options
        };
        
        this.data = [];
        this.isEditing = false;
        this.render();
    }

    render() {
        const tableContainer = document.createElement('div');
        tableContainer.className = 'parameter-table-container';
        tableContainer.innerHTML = `
            <h3>${this.options.title}</h3>
            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            ${this.options.fields.map(field => `<th>${field.label}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="${this.options.fields.length}">正在加载参数...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="table-actions">
                <button class="btn btn-secondary" data-action="edit">编辑参数</button>
                <button class="btn btn-secondary" data-action="reload">加载默认</button>
                <button class="btn btn-primary" data-action="save" style="display: none;">保存参数</button>
                <button class="btn btn-secondary" data-action="cancel" style="display: none;">取消</button>
            </div>
        `;

        this.container.appendChild(tableContainer);
        this.bindEvents();
        this.loadData();
    }

    bindEvents() {
        const actions = this.container.querySelector('.table-actions');
        
        actions.querySelector('[data-action="edit"]')?.addEventListener('click', () => {
            this.showEditor();
        });

        actions.querySelector('[data-action="reload"]')?.addEventListener('click', () => {
            this.loadData();
        });

        actions.querySelector('[data-action="save"]')?.addEventListener('click', () => {
            this.save();
        });

        actions.querySelector('[data-action="cancel"]')?.addEventListener('click', () => {
            this.hideEditor();
        });
    }

    async loadData() {
        if (this.options.loadData) {
            const data = await this.options.loadData();
            this.setData(data);
        }
    }

    setData(data) {
        this.data = data;
        this.renderTable();
    }

    renderTable() {
        const tbody = this.container.querySelector('tbody');
        if (!tbody) return;

        tbody.innerHTML = this.data.map(row => `
            <tr>
                ${this.options.fields.map(field => `<td>${row[field.key] || '-'}</td>`).join('')}
            </tr>
        `).join('');
    }

    showEditor() {
        const tableWrapper = this.container.querySelector('.table-wrapper');
        const actions = this.container.querySelector('.table-actions');
        
        tableWrapper.style.display = 'none';
        actions.querySelector('[data-action="edit"]').style.display = 'none';
        actions.querySelector('[data-action="reload"]').style.display = 'none';
        actions.querySelector('[data-action="save"]').style.display = 'inline-block';
        actions.querySelector('[data-action="cancel"]').style.display = 'inline-block';

        let editor = this.container.querySelector('.parameter-editor');
        if (!editor) {
            editor = document.createElement('div');
            editor.className = 'parameter-editor';
            this.container.insertBefore(editor, actions);
        }

        editor.style.display = 'block';
        this.renderEditor(editor);
    }

    renderEditor(editor) {
        editor.innerHTML = `
            <h3>编辑参数</h3>
            <div class="json-editor-container">
                <textarea id="parameterEditor" placeholder='在此输入JSON格式的参数配置...'></textarea>
            </div>
            <div class="editor-actions">
                <button class="btn btn-secondary" data-action="validate">验证格式</button>
                <button class="btn btn-secondary" data-action="format">格式化</button>
            </div>
            <div class="validation-result"></div>
        `;

        const textarea = editor.querySelector('#parameterEditor');
        textarea.value = JSON.stringify(this.dataToParams(), null, 2);

        editor.querySelector('[data-action="validate"]')?.addEventListener('click', () => {
            this.validateEditor();
        });

        editor.querySelector('[data-action="format"]')?.addEventListener('click', () => {
            this.formatEditor();
        });
    }

    dataToParams() {
        const params = {};
        this.data.forEach(item => {
            const keys = item.name.split('.');
            let current = params;
            keys.forEach((key, index) => {
                if (index === keys.length - 1) {
                    current[key] = item.value;
                } else {
                    if (!current[key]) current[key] = {};
                    current = current[key];
                }
            });
        });
        return params;
    }

    validateEditor() {
        const textarea = this.container.querySelector('#parameterEditor');
        const resultDiv = this.container.querySelector('.validation-result');
        
        if (!textarea || !resultDiv) return;

        try {
            JSON.parse(textarea.value);
            resultDiv.innerHTML = '<div class="validation-success">JSON格式正确</div>';
        } catch (error) {
            resultDiv.innerHTML = `<div class="validation-error">JSON格式错误: ${error.message}</div>`;
        }
    }

    formatEditor() {
        const textarea = this.container.querySelector('#parameterEditor');
        if (!textarea) return;

        try {
            const parsed = JSON.parse(textarea.value);
            textarea.value = JSON.stringify(parsed, null, 2);
        } catch (error) {
            alert('JSON格式错误，无法格式化: ' + error.message);
        }
    }

    async save() {
        const textarea = this.container.querySelector('#parameterEditor');
        if (!textarea) return;

        try {
            const params = JSON.parse(textarea.value);
            
            if (this.options.saveData) {
                const result = await this.options.saveData(params);
                if (result.success) {
                    alert('参数保存成功！');
                    this.hideEditor();
                    this.loadData();
                } else {
                    alert('参数保存失败！');
                }
            } else {
                this.setData(this.paramsToData(params));
                this.hideEditor();
            }
        } catch (error) {
            alert('参数格式错误: ' + error.message);
        }
    }

    paramsToData(params) {
        const data = [];
        const flatten = (obj, prefix = '') => {
            Object.keys(obj).forEach(key => {
                const fullKey = prefix ? `${prefix}.${key}` : key;
                if (typeof obj[key] === 'object' && obj[key] !== null) {
                    flatten(obj[key], fullKey);
                } else {
                    data.push({
                        name: fullKey,
                        value: obj[key],
                        description: this.getDescription(fullKey)
                    });
                }
            });
        };
        flatten(params);
        return data;
    }

    getDescription(key) {
        return '参数说明';
    }

    hideEditor() {
        const tableWrapper = this.container.querySelector('.table-wrapper');
        const editor = this.container.querySelector('.parameter-editor');
        const actions = this.container.querySelector('.table-actions');
        
        if (tableWrapper) tableWrapper.style.display = 'block';
        if (editor) editor.style.display = 'none';
        if (actions) {
            actions.querySelector('[data-action="edit"]').style.display = 'inline-block';
            actions.querySelector('[data-action="reload"]').style.display = 'inline-block';
            actions.querySelector('[data-action="save"]').style.display = 'none';
            actions.querySelector('[data-action="cancel"]').style.display = 'none';
        }
    }
}

window.ParameterTable = ParameterTable;

/**
 * JSON编辑器组件
 * 提供JSON配置的编辑、验证、格式化功能
 */

class JsonEditor {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            title: 'JSON编辑器',
            description: '编辑JSON配置',
            defaultValue: '{}',
            height: '300px',
            maxHeight: '400px',
            onValidate: null,
            onFormat: null,
            onClear: null,
            showHelp: true,
            ...options
        };
        
        this.editor = null;
        this.render();
    }

    render() {
        const editorContainer = document.createElement('div');
        editorContainer.className = 'json-editor-wrapper';
        editorContainer.innerHTML = `
            <div class="editor-toolbar">
                <div class="toolbar-title">
                    ${this.options.title}
                </div>
                <div class="toolbar-actions">
                    <button class="btn btn-secondary btn-sm" data-action="validate">验证</button>
                    <button class="btn btn-secondary btn-sm" data-action="format">格式化</button>
                </div>
            </div>
            
            <div class="editor-container">
                <textarea class="json-textarea" style="height: ${this.options.height}; max-height: ${this.options.maxHeight}">${this.options.defaultValue}</textarea>
            </div>
            
            <div class="validation-result"></div>
        `;

        this.container.appendChild(editorContainer);
        this.editor = editorContainer.querySelector('.json-textarea');
        this.bindEvents();
    }

    bindEvents() {
        const toolbar = this.container.querySelector('.toolbar-actions');
        
        toolbar.querySelector('[data-action="validate"]')?.addEventListener('click', () => {
            this.validate();
            this.options.onValidate?.();
        });

        toolbar.querySelector('[data-action="format"]')?.addEventListener('click', () => {
            this.format();
            this.options.onFormat?.();
        });
    }

    getValue() {
        return this.editor?.value || '';
    }

    setValue(value) {
        if (this.editor) {
            this.editor.value = value;
        }
    }

    validate() {
        const resultDiv = this.container.querySelector('.validation-result');
        if (!resultDiv) return;

        try {
            JSON.parse(this.getValue());
            resultDiv.innerHTML = '<div class="validation-success">JSON格式正确</div>';
            return true;
        } catch (error) {
            resultDiv.innerHTML = `<div class="validation-error">JSON格式错误: ${error.message}</div>`;
            return false;
        }
    }

    format() {
        try {
            const parsed = JSON.parse(this.getValue());
            this.setValue(JSON.stringify(parsed, null, 2));
            return true;
        } catch (error) {
            if (this.options.showErrorAlert !== false) {
                alert('JSON格式错误，无法格式化: ' + error.message);
            }
            return false;
        }
    }

    clear() {
        this.setValue('');
    }
}

window.JsonEditor = JsonEditor;

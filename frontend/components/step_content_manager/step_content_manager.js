/**
 * 步骤内容管理器
 * 使用组件化的方式渲染步骤内容
 */

class StepContentManager {
    constructor(options = {}) {
        this.options = {
            configUrl: '/pages/n1_wizard/config/wizard_config.json',
            ...options
        };
        
        this.config = null;
        this.currentMode = null;
        this.currentStep = 0;
        this.loadConfig();
    }

    async loadConfig() {
        try {
            const response = await fetch(this.options.configUrl);
            this.config = await response.json();
        } catch (error) {
            console.error('Failed to load wizard config:', error);
        }
    }

    setMode(mode) {
        this.currentMode = mode;
    }

    setStep(stepIndex) {
        this.currentStep = stepIndex;
    }

    getCurrentStepConfig() {
        if (!this.config || !this.currentMode) return null;
        const modeConfig = this.config.modes[this.currentMode];
        return modeConfig.steps[this.currentStep];
    }

    async renderStepContent(stepBodyElement, stepActionsElement) {
        const stepConfig = this.getCurrentStepConfig();
        if (!stepConfig || !this.config) {
            console.error('Step configuration not loaded');
            return;
        }

        const componentConfig = this.config.components[stepConfig.component];
        if (!componentConfig) {
            console.error(`Component configuration not found: ${stepConfig.component}`);
            return;
        }

        // 清空容器
        stepBodyElement.innerHTML = '';
        stepActionsElement.innerHTML = '';

        // 根据组件类型渲染内容
        switch (componentConfig.type) {
            case 'status_panel':
                this.renderStatusPanel(stepBodyElement, componentConfig);
                break;
            case 'table':
                this.renderParameterTable(stepBodyElement, componentConfig);
                break;
            case 'json_editor':
                this.renderJsonEditor(stepBodyElement, componentConfig);
                break;
            case 'validation':
                this.renderValidationPanel(stepBodyElement, componentConfig);
                break;
            case 'form':
                this.renderForm(stepBodyElement, componentConfig);
                break;
            case 'list':
                this.renderList(stepBodyElement, componentConfig);
                break;
            case 'result':
                this.renderResultViewer(stepBodyElement, componentConfig);
                break;
            case 'explanation':
                this.renderExplanation(stepBodyElement, componentConfig);
                break;
            case 'execution':
                this.renderExecutionPanel(stepBodyElement, componentConfig);
                break;
            default:
                console.error(`Unknown component type: ${componentConfig.type}`);
        }

        // 渲染操作按钮
        this.renderActionButtons(stepActionsElement, stepConfig);
    }

    renderStatusPanel(container, config) {
        const stateManager = window.wizardStateManager;
        new StatusPanel(container, {
            title: '执行状态',
            statusMessage: '正在初始化仿真模型...',
            modelInfo: stateManager?.getModelInfo() || {},
            fields: config.fields || []
        });

        // 模拟初始化完成
        setTimeout(() => {
            const panel = container.querySelector('.status-panel-container');
            if (panel) {
                panel.querySelector('.status-message')?.classList.add('success');
                panel.querySelector('.status-message').textContent = '模型初始化完成';
            }
        }, 1000);
    }

    renderParameterTable(container, config) {
        new ParameterTable(container, {
            title: '参数配置',
            fields: config.fields,
            loadData: async () => {
                try {
                    const response = await fetch('/pages/n1_wizard/config/default_params.json');
                    if (response.ok) {
                        const params = await response.json();
                        return this.convertParamsToTableData(params);
                    }
                } catch (error) {
                    console.error('Failed to load parameters:', error);
                }
                return this.getSampleData();
            },
            saveData: async (params) => {
                if (window.wizardStateManager) {
                    window.wizardStateManager.updateSimulationConfig(params);
                }
                return { success: true };
            }
        });
    }

    renderJsonEditor(container, config) {
        new JsonEditor(container, {
            title: '批量配置 JSON',
            description: '配置批量仿真任务的参数',
            defaultValue: this.getDefaultBatchConfig(),
            height: '300px'
        });
    }

    renderValidationPanel(container, config) {
        new ValidationPanel(container, {
            title: '参数检查与确认',
            description: '请检查批量仿真配置，并确认仿真次数',
            showCountInput: config.showCountInput !== false,
            validations: config.validations || [
                { status: 'success', title: '配置格式正确', message: 'steps配置格式验证通过' },
                { status: 'success', title: '参数取值正确', message: '参数取值方式配置验证通过' },
                { status: 'warning', title: '需要确认批量次数', message: '检测到choices/range/random参数，需要指定批量仿真次数' }
            ]
        });
    }

    renderForm(container, config) {
        const form = document.createElement('div');
        form.className = 'parameter-form';
        form.innerHTML = `
            <form id="stepForm">
                ${config.fields.map(field => `
                    <div class="form-group">
                        <label>${field.label}</label>
                        ${field.type === 'checkbox' ? `
                            <label class="checkbox-label">
                                <input type="checkbox" name="${field.key}" ${field.checked ? 'checked' : ''}>
                                <span>启用此量测</span>
                            </label>
                        ` : field.type === 'select' ? `
                            <select name="${field.key}" class="form-control">
                                <option value="">请选择...</option>
                                ${field.options ? field.options.map(opt => `<option value="${opt.value}">${opt.label}</option>`).join('') : ''}
                            </select>
                        ` : `
                            <input type="${field.type}" name="${field.key}" class="form-control" ${field.value ? `value="${field.value}"` : ''}>
                        `}
                    </div>
                `).join('')}
            </form>
        `;
        container.appendChild(form);

        // 默认选中复选框
        if (config.fields.some(field => field.key === 'Vrms')) {
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = true);
        }
    }

    renderList(container, config) {
        const listContainer = document.createElement('div');
        listContainer.className = 'workflow-list';
        listContainer.innerHTML = `
            <h3>仿真流程模板</h3>
            <ol class="workflow-steps">
                <li><strong>加载模型</strong> - 初始化电力系统模型</li>
                <li><strong>配置潮流计算</strong> - 设置潮流计算参数</li>
                <li><strong>执行潮流计算</strong> - 计算系统初始状态</li>
                <li><strong>设置故障参数</strong> - 配置N-1故障场景</li>
                <li><strong>配置暂态仿真</strong> - 设置电磁暂态计算参数</li>
                <li><strong>添加量测</strong> - 配置输出信号</li>
                <li><strong>执行仿真</strong> - 运行N-1故障仿真</li>
                <li><strong>结果分析</strong> - 分析仿真结果</li>
            </ol>
        `;
        container.appendChild(listContainer);
    }

    renderResultViewer(container, config) {
        const viewer = document.createElement('div');
        viewer.className = 'result-viewer';
        viewer.innerHTML = `
            <h3>仿真结果</h3>
            <div class="result-tabs">
                <button class="tab-btn active" data-tab="voltage">电压分析</button>
                <button class="tab-btn" data-tab="frequency">频率分析</button>
                <button class="tab-btn" data-tab="angle">功角分析</button>
            </div>
            <div class="tab-content">
                <div class="tab-pane active" id="voltage-tab">
                    <div class="result-placeholder">
                        <p>电压稳定性分析结果将在此显示</p>
                    </div>
                </div>
                <div class="tab-pane" id="frequency-tab">
                    <div class="result-placeholder">
                        <p>频率稳定性分析结果将在此显示</p>
                    </div>
                </div>
                <div class="tab-pane" id="angle-tab">
                    <div class="result-placeholder">
                        <p>功角稳定性分析结果将在此显示</p>
                    </div>
                </div>
            </div>
            ${config.showTable ? `
                <div class="summary-table">
                    <h4>稳定性判断汇总</h4>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>指标</th>
                                <th>数值</th>
                                <th>稳定性</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>电压偏移</td>
                                <td>&lt; 5%</td>
                                <td><span style="color: #52c41a;">稳定</span></td>
                            </tr>
                            <tr>
                                <td>频率偏移</td>
                                <td>&lt; 0.5 Hz</td>
                                <td><span style="color: #52c41a;">稳定</span></td>
                            </tr>
                            <tr>
                                <td>最大功角</td>
                                <td>&lt; 90°</td>
                                <td><span style="color: #52c41a;">稳定</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            ` : ''}
        `;
        container.appendChild(viewer);

        // 绑定标签切换
        viewer.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                viewer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                viewer.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                e.target.classList.add('active');
                document.getElementById(`${tabName}-tab`).classList.add('active');
            });
        });
    }

    renderExplanation(container, config) {
        const explanation = document.createElement('div');
        explanation.className = 'parameter-explanation';
        explanation.innerHTML = `
            <h3>工具参数说明</h3>
            <div class="explanation-list">
                <div class="explanation-item">
                    <h4>initModelAndCreateSACanvas</h4>
                    <p>创建仿真画布，参数：无</p>
                </div>
                <div class="explanation-item">
                    <h4>power_flow_sample_simple_random</h4>
                    <p>生成随机潮流样本，参数：iterations (迭代次数)</p>
                </div>
                <div class="explanation-item">
                    <h4>setN_1_GroundFault</h4>
                    <p>设置N-1接地故障，参数：fault_bus (故障母线), fault_type (故障类型)</p>
                </div>
                <div class="explanation-item">
                    <h4>addComponentOutputMeasures</h4>
                    <p>添加量测信号，参数：rid (组件ID), key (信号键)</p>
                </div>
                <div class="explanation-item">
                    <h4>runProject</h4>
                    <p>执行仿真计算，参数：无</p>
                </div>
            </div>
        `;
        container.appendChild(explanation);
    }

    renderExecutionPanel(container, config) {
        const panel = document.createElement('div');
        panel.className = 'execution-panel';
        panel.innerHTML = `
            <div class="execution-status">
                <div class="status-indicator"></div>
                <div class="status-message">准备执行仿真...</div>
            </div>
            ${config.showProgress ? `
                <div class="progress-container" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-text">0%</div>
                </div>
            ` : ''}
        `;
        container.appendChild(panel);
    }

    renderActionButtons(container, stepConfig) {
        const navigation = window.wizardNavigation;
        if (!navigation) return;

        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'step-navigation-buttons';

        const currentStep = navigation.getCurrentStep();
        const totalSteps = navigation.options.totalSteps;

        // 上一步
        if (currentStep > 0) {
            actionsDiv.innerHTML += `<button class="btn btn-secondary" data-action="prev">上一步</button>`;
        }

        // 修改参数
        const editableSteps = ['power_flow_config', 'transient_config', 'fault_parameters'];
        if (editableSteps.includes(stepConfig.id)) {
            actionsDiv.innerHTML += `<button class="btn btn-secondary" data-action="edit" style="display: none;">修改参数</button>`;
        }

        // 下一步/完成
        if (currentStep < totalSteps - 1) {
            actionsDiv.innerHTML += `<button class="btn btn-primary" data-action="next">下一步</button>`;
        } else {
            actionsDiv.innerHTML += `<button class="btn btn-success" data-action="complete">完成</button>`;
        }

        container.appendChild(actionsDiv);
        this.bindNavigationEvents(actionsDiv, stepConfig);
    }

    bindNavigationEvents(actionsDiv, stepConfig) {
        const navigation = window.wizardNavigation;

        actionsDiv.querySelector('[data-action="prev"]')?.addEventListener('click', () => {
            const prevUrl = navigation.prevStep();
            if (prevUrl) window.location.href = prevUrl;
        });

        actionsDiv.querySelector('[data-action="next"]')?.addEventListener('click', () => {
            const nextUrl = navigation.nextStep();
            if (nextUrl) window.location.href = nextUrl;
        });

        actionsDiv.querySelector('[data-action="complete"]')?.addEventListener('click', () => {
            alert('仿真向导完成！');
            window.location.href = '/pages/index.html';
        });

        actionsDiv.querySelector('[data-action="edit"]')?.addEventListener('click', () => {
            const tableActions = document.querySelector('.table-actions');
            if (tableActions) {
                tableActions.querySelector('[data-action="edit"]')?.click();
            }
        });
    }

    convertParamsToTableData(params) {
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

    getSampleData() {
        return [
            { name: 'power_flow.iterations', value: '100', description: '潮流计算最大迭代次数' },
            { name: 'power_flow.tolerance', value: '1e-6', description: '潮流计算收敛精度' },
            { name: 'model_config.case_name', value: 'IEEE14', description: '模型名称' },
            { name: 'fault_parameters.fault_type', value: 'three_phase', description: '故障类型' }
        ];
    }

    getDescription(key) {
        const descriptions = {
            'power_flow.iterations': '潮流计算最大迭代次数',
            'power_flow.tolerance': '潮流计算收敛精度',
            'model_config.case_name': '模型名称',
            'fault_parameters.fault_type': '故障类型'
        };
        return descriptions[key] || '参数说明';
    }

    getDefaultBatchConfig() {
        return `{
  "steps": [
    {
      "name": "load_data",
      "params": {
        "case_name": "IEEE14"
      }
    },
    {
      "name": "run_power_flow",
      "params": {
        "iterations": {
          "range": {
            "start": 5,
            "end": 15,
            "step": 5
          }
        }
      }
    }
  ]
}`;
    }
}

window.StepContentManager = StepContentManager;

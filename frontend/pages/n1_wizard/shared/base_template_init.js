/**
 * 向导页面初始化脚本
 */

document.addEventListener('DOMContentLoaded', function() {
    // 从URL获取参数
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode') || 'single';
    const step = parseInt(urlParams.get('step')) || 0;

    // 初始化状态管理器
    window.wizardStateManager = new WizardStateManager({
        storageKey: 'n1_wizard_state'
    });

    // 初始化导航
    window.wizardNavigation = new WizardNavigation({
        mode: mode,
        totalSteps: mode === 'single' ? 8 : 6,
        titles: mode === 'single' ? [
            '加载模型', '潮流计算配置', '执行潮流计算',
            '故障参数设置', '电磁暂态配置', '添加量测信号',
            '执行仿真', '结果分析'
        ] : [
            '查看默认配置', '确认流程模板', '配置参数',
            '生成批量配置', '参数检查与确认', '提交批量任务'
        ],
        onStepChange: (stepIndex) => {
            console.log('Step changed to:', stepIndex);
        }
    });

    // 设置容器并恢复状态
    window.wizardNavigation.restoreState();
    window.wizardNavigation.setContainer('stepNavigator');
    window.wizardNavigation.goToStep(step);

    // 初始化步骤内容管理器
    window.stepContentManager = new StepContentManager();
    window.stepContentManager.setMode(mode);
    window.stepContentManager.setStep(step);

    // 等待配置加载完成后再渲染内容
    const checkConfig = setInterval(() => {
        if (window.stepContentManager.config) {
            clearInterval(checkConfig);

            // 渲染步骤内容
            const stepBody = document.getElementById('stepBody');
            const stepActions = document.getElementById('stepActions');
            if (stepBody && stepActions) {
                window.stepContentManager.renderStepContent(stepBody, stepActions);
            }

            // 更新页面标题
            const stepConfig = window.stepContentManager.getCurrentStepConfig();
            if (stepConfig) {
                updatePageTitle(mode, step, stepConfig);
            }

            // 绑定常用按钮事件
            bindCommonEvents();
        }
    }, 100);
});

function updatePageTitle(mode, stepIndex, stepConfig) {
    const pageTitle = document.getElementById('pageTitle');
    const pageHeader = document.getElementById('pageHeader');
    const pageSubtitle = document.getElementById('pageSubtitle');
    const stepTitle = document.getElementById('stepTitle');
    const stepDescription = document.getElementById('stepDescription');

    if (pageTitle) {
        pageTitle.textContent = `${stepConfig.title} - N-1仿真向导 - SIMBOT电力系统分析平台`;
    }

    if (pageHeader) {
        pageHeader.textContent = `N-1 仿真向导 - ${mode === 'single' ? '单次仿真' : '批量仿真'}`;
    }

    if (pageSubtitle) {
        pageSubtitle.textContent = `步骤 ${stepIndex + 1}/${mode === 'single' ? 8 : 6}: ${stepConfig.title}`;
    }

    if (stepTitle) {
        stepTitle.textContent = stepConfig.title;
    }

    if (stepDescription) {
        stepDescription.textContent = stepConfig.description;
    }

    // 更新帮助内容
    const helpDialogContent = document.getElementById('helpDialogContent');
    if (helpDialogContent) {
        helpDialogContent.innerHTML = `
            <h4>什么是N-1仿真？</h4>
            <p>N-1仿真是电力系统稳定性分析的重要方法，用于评估系统在单个元件故障后的稳定运行能力。</p>
            
            <h4>当前步骤</h4>
            <p>${stepConfig.description}</p>
            
            <h4>使用指南</h4>
            <ol>
                <li>按照步骤导航器指示完成当前步骤</li>
                <li>根据步骤要求设置相应参数或查看结果</li>
                <li>点击"下一步"继续，或点击"上一步"返回</li>
            </ol>
        `;
    }
}

function bindCommonEvents() {
    const backBtn = document.getElementById('backBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const helpBtn = document.getElementById('helpBtn');
    const closeHelpBtn = document.getElementById('closeHelpBtn');
    const helpDialog = document.getElementById('helpDialog');

    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.location.href = '/pages/index.html';
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            refreshPage();
        });
    }

    if (helpBtn) {
        helpBtn.addEventListener('click', () => {
            if (helpDialog) {
                helpDialog.style.display = 'flex';
            }
        });
    }

    if (closeHelpBtn) {
        closeHelpBtn.addEventListener('click', () => {
            if (helpDialog) {
                helpDialog.style.display = 'none';
            }
        });
    }

    // 点击对话框外部关闭
    if (helpDialog) {
        helpDialog.addEventListener('click', (e) => {
            if (e.target === helpDialog) {
                helpDialog.style.display = 'none';
            }
        });
    }
}

function refreshPage() {
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode') || 'single';
    const step = parseInt(urlParams.get('step')) || 0;

    // 清除当前内容
    const stepBody = document.getElementById('stepBody');
    const stepActions = document.getElementById('stepActions');
    if (stepBody) stepBody.innerHTML = '';
    if (stepActions) stepActions.innerHTML = '';

    // 重新加载配置
    window.stepContentManager.config = null;
    window.stepContentManager.loadConfig();

    // 等待配置加载后重新渲染
    const checkConfig = setInterval(() => {
        if (window.stepContentManager.config) {
            clearInterval(checkConfig);
            if (stepBody && stepActions) {
                window.stepContentManager.renderStepContent(stepBody, stepActions);
            }
        }
    }, 100);
}

/**
 * N-1仿真向导基础HTML模板
 * 用于生成每个步骤页面的基本结构
 */

class N1WizardBaseTemplate {
    static generatePageHtml(stepIndex, stepTitle, stepDescription, mode) {
        const baseUrl = '/pages/n1_wizard';
        
        return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${stepTitle} - N-1仿真向导 - SIMBOT电力系统分析平台</title>
    <link rel="stylesheet" href="${baseUrl}/../../main.css">
    <link rel="stylesheet" href="${baseUrl}/n1_wizard.css">
    <link rel="stylesheet" href="${baseUrl}/../../components/step_navigator/step_navigator.css">
    <link rel="stylesheet" href="${baseUrl}/../../components/parameter_table/parameter_table.css">
    <link rel="stylesheet" href="${baseUrl}/../../components/json_editor/json_editor.css">
    <link rel="stylesheet" href="${baseUrl}/../../components/status_panel/status_panel.css">
    <link rel="stylesheet" href="${baseUrl}/../../components/validation_panel/validation_panel.css">
    <link rel="stylesheet" href="${baseUrl}/../../components/buttons/buttons.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-left">
                <button id="backBtn" class="btn btn-secondary">返回主页</button>
            </div>
            <div class="header-center">
                <h1>N-1 仿真向导 - ${mode === 'single' ? '单次仿真' : '批量仿真'}</h1>
                <p class="subtitle">步骤 ${stepIndex + 1}/${mode === 'single' ? 8 : 6}: ${stepTitle}</p>
            </div>
            <div class="header-right">
                <button id="refreshBtn" class="btn btn-secondary">刷新</button>
                <button id="helpBtn" class="btn btn-secondary">帮助</button>
            </div>
        </header>

        <main class="main-content">
            <div class="wizard-container">
                <!-- 步骤导航 -->
                <div class="navigation-section">
                    <div id="stepNavigator"></div>
                </div>

                <!-- 步骤内容 -->
                <div id="stepContentContainer" class="steps-content-container">
                    <!-- 动态内容将在这里生成 -->
                    <div class="step-content active">
                        <div class="step-header">
                            <h2>${stepTitle}</h2>
                            <p>${stepDescription}</p>
                        </div>
                        <div class="step-body" id="stepBody">
                            <!-- 步骤特定内容将在这里生成 -->
                        </div>
                        <div class="step-actions" id="stepActions">
                            <!-- 步骤操作按钮将在这里生成 -->
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- 帮助对话框 -->
    <div id="helpDialog" class="dialog-overlay" style="display: none;">
        <div class="dialog">
            <div class="dialog-header">
                <h3>N-1仿真帮助</h3>
                <button id="closeHelpBtn" class="btn btn-icon">X</button>
            </div>
            <div class="dialog-content">
                <h4>什么是N-1仿真？</h4>
                <p>N-1仿真是电力系统稳定性分析的重要方法，用于评估系统在单个元件故障后的稳定运行能力。</p>
                
                <h4>当前步骤</h4>
                <p>${stepDescription}</p>
                
                <h4>使用指南</h4>
                <ol>
                    <li>按照步骤导航器指示完成当前步骤</li>
                    <li>根据步骤要求设置相应参数或查看结果</li>
                    <li>点击"下一步"继续，或点击"上一步"返回</li>
                </ol>
            </div>
        </div>
    </div>

    <!-- JavaScript模块 -->
    <script src="${baseUrl}/../../components/buttons/buttons.js"></script>
    <script src="${baseUrl}/../../components/step_navigator/step_navigator.js"></script>
    <script src="${baseUrl}/../../components/json_editor/json_editor.js"></script>
    <script src="${baseUrl}/../../components/status_panel/status_panel.js"></script>
    <script src="${baseUrl}/../../components/validation_panel/validation_panel.js"></script>
    <script src="${baseUrl}/../../components/parameter_table/parameter_table.js"></script>
    <script src="${baseUrl}/../../components/wizard_navigation/wizard_navigation.js"></script>
    <script src="${baseUrl}/../../components/wizard_state/wizard_state.js"></script>
    <script src="${baseUrl}/../../components/step_content_manager/step_content_manager.js"></script>
    <script src="${baseUrl}/shared/base_template_init.js"></script>
</body>
</html>
        `;
    }
}
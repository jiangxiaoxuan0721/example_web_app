/**
 * 向导导航组件
 * 处理步骤之间的导航和状态同步
 */

class WizardNavigation {
    constructor(options = {}) {
        this.options = {
            mode: 'single',
            totalSteps: 8,
            titles: [],
            allowSkip: false,
            onStepChange: null,
            ...options
        };
        
        this.currentStep = 0;
        this.stepStatuses = {};
        this.container = null;
        
        this.init();
    }

    init() {
        for (let i = 0; i < this.options.totalSteps; i++) {
            this.stepStatuses[i] = {
                title: this.options.titles[i] || `步骤${i + 1}`,
                completed: false,
                current: i === 0
            };
        }
    }

    setContainer(containerId) {
        this.container = document.getElementById(containerId);
        if (this.container) {
            this.render();
        }
    }

    render() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="step-navigator">
                <div class="steps-container">
                    ${this.getStepsHtml()}
                </div>
            </div>
        `;

        this.bindEvents();
    }

    getStepsHtml() {
        let html = '';
        
        for (let i = 0; i < this.options.totalSteps; i++) {
            const status = this.stepStatuses[i];
            const canJump = i <= this.currentStep || status.completed;
            
            html += `<div class="step-item ${status.current ? 'active' : ''} ${status.completed ? 'completed' : ''} ${canJump ? 'clickable' : ''}" data-step="${i}">`;
            html += `<div class="step-number">${i + 1}</div>`;
            html += `<div class="step-title">${status.title}</div>`;
            html += `</div>`;
            
            if (i < this.options.totalSteps - 1) {
                html += `<div class="step-connector ${i < this.currentStep ? 'active' : ''}"></div>`;
            }
        }
        
        return html;
    }

    bindEvents() {
        this.container.querySelectorAll('.step-item.clickable').forEach(item => {
            item.addEventListener('click', (e) => {
                const stepIndex = parseInt(e.currentTarget.dataset.step);
                this.jumpToStep(stepIndex);
            });
        });
    }

    goToStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.options.totalSteps) return null;
        
        if (this.stepStatuses[this.currentStep]) {
            this.stepStatuses[this.currentStep].current = false;
        }
        
        this.currentStep = stepIndex;
        this.stepStatuses[this.currentStep].current = true;
        
        this.saveState();
        this.render();
        this.options.onStepChange?.(stepIndex);
        
        return this.getStepPageUrl(stepIndex);
    }

    jumpToStep(stepIndex) {
        if (stepIndex >= 0 && stepIndex < this.options.totalSteps && 
            (stepIndex <= this.currentStep || this.stepStatuses[stepIndex].completed || this.options.allowSkip)) {
            const url = this.goToStep(stepIndex);
            if (url) {
                window.location.href = url;
            }
        }
    }

    nextStep() {
        if (this.currentStep < this.options.totalSteps - 1) {
            this.stepStatuses[this.currentStep].completed = true;
            const url = this.goToStep(this.currentStep + 1);
            return url;
        }
        return null;
    }

    prevStep() {
        if (this.currentStep > 0) {
            const url = this.goToStep(this.currentStep - 1);
            return url;
        }
        return null;
    }

    getStepPageUrl(stepIndex) {
        return `/pages/n1_wizard/steps/wizard_template.html?mode=${this.options.mode}&step=${stepIndex}`;
    }

    markCompleted(stepIndex) {
        if (stepIndex >= 0 && stepIndex < this.options.totalSteps) {
            this.stepStatuses[stepIndex].completed = true;
            this.render();
        }
    }

    getCurrentStep() {
        return this.currentStep;
    }

    saveState() {
        sessionStorage.setItem('wizard_navigation_state', JSON.stringify({
            currentStep: this.currentStep,
            stepStatuses: this.stepStatuses
        }));
    }

    restoreState() {
        const savedState = sessionStorage.getItem('wizard_navigation_state');
        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                this.currentStep = state.currentStep || 0;
                this.stepStatuses = state.stepStatuses || this.stepStatuses;
                return true;
            } catch (e) {
                console.error('Failed to restore navigation state:', e);
            }
        }
        return false;
    }

    clearState() {
        sessionStorage.removeItem('wizard_navigation_state');
    }
}

window.WizardNavigation = WizardNavigation;

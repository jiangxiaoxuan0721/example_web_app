/**
 * 通用步骤导航器组件
 * 用于显示和切换N-1仿真流程中的不同步骤
 */

class StepNavigator {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`StepNavigator: Container with id '${containerId}' not found`);
            return;
        }

        this.options = {
            showStepNumbers: true,
            allowSkip: false,
            ...options
        };

        this.steps = [];
        this.currentStep = 0;
        this.callbacks = {
            onStepChange: options.onStepChange || (() => {}),
            onStepComplete: options.onStepComplete || (() => {}),
            ...options.callbacks
        };

        this.init();
    }

    init() {
        this.container.classList.add('step-navigator');
        this.render();
    }

    setSteps(steps) {
        this.steps = steps;
        this.currentStep = 0;
        this.render();
        this.callbacks.onStepChange(0);
    }

    render() {
        this.container.innerHTML = '';

        const stepsContainer = document.createElement('div');
        stepsContainer.className = 'steps-container';

        this.steps.forEach((step, index) => {
            const stepElement = document.createElement('div');
            stepElement.className = `step-item ${index === this.currentStep ? 'active' : ''} ${step.completed ? 'completed' : ''}`;
            
            // 步骤编号
            if (this.options.showStepNumbers) {
                const stepNumber = document.createElement('div');
                stepNumber.className = 'step-number';
                stepNumber.textContent = index + 1;
                stepElement.appendChild(stepNumber);
            }

            // 步骤标题
            const stepTitle = document.createElement('div');
            stepTitle.className = 'step-title';
            stepTitle.textContent = step.title;
            stepElement.appendChild(stepTitle);

            // 点击事件
            stepElement.addEventListener('click', () => {
                if (this.options.allowSkip || index <= this.currentStep || step.completed) {
                    this.goToStep(index);
                }
            });

            stepsContainer.appendChild(stepElement);
        });

        this.container.appendChild(stepsContainer);

        // 导航按钮
        const navButtons = document.createElement('div');
        navButtons.className = 'nav-buttons';

        const prevButton = document.createElement('button');
        prevButton.className = 'btn btn-secondary prev-button';
        prevButton.textContent = '上一步';
        prevButton.disabled = this.currentStep === 0;
        prevButton.addEventListener('click', () => this.previousStep());

        const nextButton = document.createElement('button');
        nextButton.className = 'btn btn-primary next-button';
        nextButton.textContent = '下一步';
        nextButton.disabled = this.currentStep === this.steps.length - 1;
        nextButton.addEventListener('click', () => this.nextStep());

        navButtons.appendChild(prevButton);
        navButtons.appendChild(nextButton);
        this.container.appendChild(navButtons);
    }

    goToStep(index) {
        if (index < 0 || index >= this.steps.length) return;
        
        this.currentStep = index;
        this.updateStepDisplay();
        this.callbacks.onStepChange(index);
    }

    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.callbacks.onStepComplete(this.currentStep);
            this.currentStep++;
            this.updateStepDisplay();
            this.callbacks.onStepChange(this.currentStep);
            return true;
        }
        return false;
    }

    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateStepDisplay();
            this.callbacks.onStepChange(this.currentStep);
            return true;
        }
        return false;
    }

    markStepCompleted(index) {
        if (index >= 0 && index < this.steps.length) {
            this.steps[index].completed = true;
            this.updateStepDisplay();
        }
    }

    updateStepDisplay() {
        const stepItems = this.container.querySelectorAll('.step-item');
        stepItems.forEach((item, index) => {
            item.className = `step-item ${index === this.currentStep ? 'active' : ''} ${this.steps[index].completed ? 'completed' : ''}`;
        });

        const prevButton = this.container.querySelector('.prev-button');
        const nextButton = this.container.querySelector('.next-button');
        
        if (prevButton) prevButton.disabled = this.currentStep === 0;
        if (nextButton) nextButton.disabled = this.currentStep === this.steps.length - 1;
    }

    getCurrentStep() {
        return this.currentStep;
    }

    reset() {
        this.steps.forEach(step => step.completed = false);
        this.currentStep = 0;
        this.render();
        this.callbacks.onStepChange(0);
    }
}

// 导出组件
window.StepNavigator = StepNavigator;
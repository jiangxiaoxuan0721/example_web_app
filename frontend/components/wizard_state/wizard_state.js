/**
 * 向导状态管理组件
 * 管理步骤间共享的数据和配置
 */

class WizardStateManager {
    constructor(options = {}) {
        this.options = {
            storageKey: 'wizard_state',
            ...options
        };
        
        this.data = {
            mode: 'single',
            currentStep: -1,
            simulationConfig: {
                powerFlow: {},
                emtp: {},
                fault: {},
                measurements: []
            },
            batchConfig: {
                steps: [],
                zip: []
            },
            results: {},
            modelInfo: {}
        };
        
        this.restoreState();
    }

    setMode(mode) {
        this.data.mode = mode;
        this.saveState();
    }

    getMode() {
        return this.data.mode;
    }

    setCurrentStep(step) {
        this.data.currentStep = step;
        this.saveState();
    }

    getCurrentStep() {
        return this.data.currentStep;
    }

    updateSimulationConfig(config) {
        this.data.simulationConfig = { ...this.data.simulationConfig, ...config };
        this.saveState();
        return this.data.simulationConfig;
    }

    getSimulationConfig() {
        return this.data.simulationConfig;
    }

    updatePowerFlowConfig(config) {
        this.data.simulationConfig.powerFlow = { ...this.data.simulationConfig.powerFlow, ...config };
        this.saveState();
        return this.data.simulationConfig.powerFlow;
    }

    getPowerFlowConfig() {
        return this.data.simulationConfig.powerFlow;
    }

    updateFaultConfig(config) {
        this.data.simulationConfig.fault = { ...this.data.simulationConfig.fault, ...config };
        this.saveState();
        return this.data.simulationConfig.fault;
    }

    getFaultConfig() {
        return this.data.simulationConfig.fault;
    }

    updateEmtpConfig(config) {
        this.data.simulationConfig.emtp = { ...this.data.simulationConfig.emtp, ...config };
        this.saveState();
        return this.data.simulationConfig.emtp;
    }

    getEmtpConfig() {
        return this.data.simulationConfig.emtp;
    }

    updateMeasurementsConfig(measurements) {
        this.data.simulationConfig.measurements = measurements;
        this.saveState();
        return this.data.simulationConfig.measurements;
    }

    getMeasurementsConfig() {
        return this.data.simulationConfig.measurements;
    }

    updateBatchConfig(config) {
        this.data.batchConfig = { ...this.data.batchConfig, ...config };
        this.saveState();
        return this.data.batchConfig;
    }

    getBatchConfig() {
        return this.data.batchConfig;
    }

    updateResults(results) {
        this.data.results = { ...this.data.results, ...results };
        this.saveState();
        return this.data.results;
    }

    getResults() {
        return this.data.results;
    }

    updateModelInfo(modelInfo) {
        this.data.modelInfo = { ...this.data.modelInfo, ...modelInfo };
        this.saveState();
        return this.data.modelInfo;
    }

    getModelInfo() {
        return this.data.modelInfo;
    }

    saveState() {
        try {
            sessionStorage.setItem(this.options.storageKey, JSON.stringify(this.data));
        } catch (e) {
            console.error('Failed to save wizard state:', e);
        }
    }

    restoreState() {
        try {
            const savedData = sessionStorage.getItem(this.options.storageKey);
            if (savedData) {
                this.data = { ...this.data, ...JSON.parse(savedData) };
                return true;
            }
        } catch (e) {
            console.error('Failed to restore wizard state:', e);
        }
        return false;
    }

    clearState() {
        sessionStorage.removeItem(this.options.storageKey);
        this.data = {
            mode: 'single',
            currentStep: -1,
            simulationConfig: {
                powerFlow: {},
                emtp: {},
                fault: {},
                measurements: []
            },
            batchConfig: {
                steps: [],
                zip: []
            },
            results: {},
            modelInfo: {}
        };
    }

    exportConfig() {
        return {
            mode: this.data.mode,
            simulationConfig: this.data.simulationConfig,
            batchConfig: this.data.batchConfig,
            modelInfo: this.data.modelInfo,
            exportTime: new Date().toISOString()
        };
    }
}

window.WizardStateManager = WizardStateManager;

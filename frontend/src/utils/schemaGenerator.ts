import { UISchema, Block } from '../types/schema';
import { WizardConfig, ComponentConfig } from '../types/wizard';

/**
 * 从 Wizard 配置生成 UISchema
 */
export const generateSchemaFromWizard = (
  wizardConfig: WizardConfig,
  modeKey: string,
  stepIndex: number
): UISchema => {
  const mode = wizardConfig.modes[modeKey];
  const step = mode.steps[stepIndex];
  const componentConfig = wizardConfig.components[step.component];

  return {
    meta: {
      pageKey: `${modeKey}_${step.id}`,
      step: { current: stepIndex + 1, total: mode.steps.length },
      status: 'idle',
      schemaVersion: '1.0',
    },
    state: {
      params: {},
      runtime: {
        mode: modeKey,
        stepId: step.id,
        executionStrategy: step.executionStrategy,
        nextAction: step.nextAction,
      },
    },
    layout: { type: 'single' },
    blocks: [
      generateBlockFromConfig(step.id, componentConfig),
    ],
    actions: generateActions(step.executionStrategy, step.nextAction, stepIndex, mode.steps.length),
  };
};

// 导出类型供外部使用
export type { WizardConfig } from '../types/wizard';

/**
 * 从组件配置生成 Block
 */
const generateBlockFromConfig = (id: string, config: ComponentConfig): Block => {
  return {
    id,
    type: config.type as any,
    bind: 'state.params',
    props: config,
  };
};

/**
 * 根据 executionStrategy 和 nextAction 生成 Actions
 */
const generateActions = (
  executionStrategy: string,
  nextAction: string,
  currentStep: number,
  totalSteps: number
) => {
  const actions: Array<{ id: string; label: string; style?: 'primary' | 'danger' | 'secondary' }> = [];

  // 根据 executionStrategy 决定是否显示执行按钮
  if (executionStrategy === 'ask_execute' || executionStrategy === 'auto_wait_confirm') {
    actions.push({
      id: nextAction,
      label: getActionLabel(nextAction),
      style: 'primary',
    });
  }

  // 添加上一步按钮（除了第一步）
  if (currentStep > 0) {
    actions.push({
      id: 'prev',
      label: '上一步',
      style: 'secondary',
    });
  }

  // 添加下一步按钮（除了最后一步）
  if (currentStep < totalSteps - 1) {
    actions.push({
      id: 'next',
      label: '下一步',
      style: 'secondary',
    });
  }

  // 添加取消按钮
  actions.push({
    id: 'cancel',
    label: '取消',
    style: 'danger',
  });

  return actions;
};

/**
 * 获取 Action 的中文标签
 */
const getActionLabel = (action: string): string => {
  const labels: Record<string, string> = {
    confirm_modify: '确认修改',
    confirm_execute: '执行',
    confirm_config: '确认配置',
    confirm_count: '确认',
    confirm_submit: '提交任务',
    confirm_template: '确认模板',
  };
  return labels[action] || action;
};

/**
 * 生成模式选择页面的 UISchema
 */
export const generateModeSelectionSchema = (wizardConfig: WizardConfig): UISchema => {
  const modes = Object.entries(wizardConfig.modes);

  return {
    meta: {
      pageKey: 'mode_selection',
      step: { current: 0, total: 1 },
      status: 'idle',
      schemaVersion: '1.0',
    },
    state: {
      params: {
        selectedMode: modes[0]?.[0] || '',
      },
    },
    layout: { type: 'single' },
    blocks: [
      {
        id: 'mode_selection',
        type: 'form',
        bind: 'state.params',
        props: {
          fields: [
            {
              label: '选择仿真模式',
              key: 'selectedMode',
              type: 'select',
              options: modes.map(([key, mode]) => ({
                value: key,
                label: mode.name,
              })),
            },
          ],
        },
      },
    ],
    actions: [
      {
        id: 'confirm',
        label: '开始向导',
        style: 'primary',
      },
    ],
  };
};

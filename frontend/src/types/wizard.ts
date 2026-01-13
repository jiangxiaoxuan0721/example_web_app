/**
 * Wizard 配置类型定义
 * 对应原有的 wizard_config.json
 */

export type ExecutionStrategy = 'auto' | 'auto_wait_confirm' | 'ask_execute';

export type NextAction =
  | 'auto'
  | 'confirm_modify'
  | 'confirm_execute'
  | 'confirm_config'
  | 'confirm_count'
  | 'confirm_submit'
  | 'confirm_template';

export interface WizardStep {
  id: string;
  title: string;
  description: string;
  executionStrategy: ExecutionStrategy;
  component: string;
  nextAction: NextAction;
}

export interface WizardMode {
  name: string;
  description: string;
  steps: WizardStep[];
}

export interface ComponentConfig {
  type: string;
  fields?: any[];
  showProgress?: boolean;
  showStatus?: boolean;
  showImages?: boolean;
  showTable?: boolean;
  showCountInput?: boolean;
  showTaskId?: boolean;
}

export interface ActionDefinition {
  [key: string]: string;
}

export interface WizardConfig {
  modes: {
    [key: string]: WizardMode;
  };
  components: {
    [key: string]: ComponentConfig;
  };
  actions: ActionDefinition;
}

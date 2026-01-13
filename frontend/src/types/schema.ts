/**
 * UI Schema & Patch 技术规范 - TypeScript 类型定义 v1.0
 */

// ============ Meta（流程与控制） ============
export interface Meta {
  pageKey: string;
  step: { current: number; total: number };
  status: 'idle' | 'running' | 'locked';
  schemaVersion: '1.0';
}

// ============ Meta（流程与控制） ============
export interface Meta {
  pageKey: string;
  step: { current: number; total: number };
  status: 'idle' | 'running' | 'locked';
  schemaVersion: '1.0';
  runtime?: Record<string, any>;   // 运行期状态
}

// ============ State（业务状态） ============
export interface State {
  params?: Record<string, any>;    // 用户配置参数
  runtime?: Record<string, any>;   // 运行期状态
}

// ============ Meta（流程与控制） ============
export interface Meta {
  pageKey: string;
  step: { current: number; total: number };
  status: 'idle' | 'running' | 'locked';
  schemaVersion: '1.0';
  runtime?: Record<string, any>;   // 运行期状态
}

// ============ State（业务状态） ============
export interface State {
  params?: Record<string, any>;    // 用户配置参数
  runtime?: Record<string, any>;   // 运行期状态
}

// ============ Layout（页面结构） ============
export type Layout =
  | { type: 'single' }
  | { type: 'split'; direction: 'horizontal' | 'vertical'; ratio: number[] }
  | { type: 'tabs'; tabs: string[] };

// ============ Block（UI 单元） ============
export type BlockType = 'form' | 'table' | 'chart' | 'canvas' | 'log' | 'status_panel' | 'execution' | 'result' | 'list' | 'explanation' | 'json_editor' | 'validation' | 'task_submission';

export interface Block {
  id: string;
  type: BlockType;
  bind?: string;          // 绑定到 state 路径
  props?: Record<string, any>;
}

// ============ Action（用户触发点） ============
export interface Action {
  id: string;
  label: string;
  style?: 'primary' | 'danger' | 'secondary';
}

// ============ UISchema（完整 Schema） ============
export interface UISchema {
  meta: Meta;
  state: State;
  layout: Layout;
  blocks: Block[];
  actions?: Action[];
}

// ============ UIPatch（Patch 规范） ============
export interface UIPatch {
  [dotPath: string]: any;
}

// ============ UIEvent（Event 规范） ============
export interface UIEvent {
  type: string;
  pageKey: string;
  payload?: Record<string, any>;
  timestamp?: number;
}

// ============ Field（表单字段定义） ============
export type FieldType = 'text' | 'number' | 'select' | 'checkbox' | 'textarea' | 'json';

export interface FieldOption {
  value: string;
  label: string;
}

export interface Field {
  label: string;
  key: string;
  type: FieldType;
  options?: string[] | FieldOption[];      // 用于 select 类型
  rid?: string;           // 资源标识符
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

// ============ 能力白名单 ============
export const ALLOWED_LAYOUT_TYPES = ['single', 'split', 'tabs'] as const;
export const ALLOWED_BLOCK_TYPES = ['form', 'table', 'chart', 'canvas', 'log', 'status_panel', 'execution', 'result', 'list', 'explanation', 'json_editor', 'validation', 'task_submission'] as const;
export const ALLOWED_FIELD_TYPES = ['text', 'number', 'select', 'checkbox', 'textarea', 'json'] as const;

// ============ Patch 校验 ============
export const isValidPatch = (patch: UIPatch): boolean => {
  return Object.keys(patch).every(key => {
    // 检查是否为合法的点路径
    const segments = key.split('.');
    return segments.length > 0 && segments.every(s => s.length > 0);
  });
};

// ============ Schema 版本校验 ============
export const SCHEMA_VERSION = '1.0';

export const isSchemaVersionCompatible = (schema: UISchema): boolean => {
  return schema.meta.schemaVersion === SCHEMA_VERSION;
};

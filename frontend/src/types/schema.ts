/** Schema 类型定义 */

export interface FieldConfig {
  label: string;
  key: string;
  type: string;
  rid?: string;
  value?: any;
  description?: string;
  options?: Array<{ label: string; value: string }>;
}

export interface BlockProps {
  fields?: FieldConfig[];
  showProgress?: boolean;
  showStatus?: boolean;
  showImages?: boolean;
  showTable?: boolean;
  showCountInput?: boolean;
  showTaskId?: boolean;
}

export interface Block {
  id: string;
  type: string;
  bind: string;
  props?: BlockProps;
}

export interface ActionConfig {
  id: string;
  label: string;
  style: string;
}

export interface StepInfo {
  current: number;
  total: number;
}

export interface MetaInfo {
  pageKey: string;
  step: StepInfo;
  status: string;
  schemaVersion: string;
}

export interface StateInfo {
  params: Record<string, any>;
  runtime: Record<string, any>;
}

export interface LayoutInfo {
  type: string;
}

export interface UISchema {
  meta: MetaInfo;
  state: StateInfo;
  layout: LayoutInfo;
  blocks: Block[];
  actions?: ActionConfig[];
}

export interface PatchRecord {
  id: number;
  timestamp: string;
  patch: Record<string, any>;
}

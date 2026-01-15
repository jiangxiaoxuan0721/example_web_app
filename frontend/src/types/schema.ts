/** 图片配置接口 */
export interface PictureConfig {
  /** 是否显示全屏按钮 */
  showFullscreen?: boolean;
  /** 是否显示下载按钮 */
  showDownload?: boolean;
  /** 图片高度 */
  imageHeight?: string;
  /** 图片适应方式 */
  imageFit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';
  /** 是否懒加载 */
  lazy?: boolean;
  /** 加载失败时的回退内容 */
  fallback?: string;
  /** 子标题 */
  subtitle?: string;
}

/** Schema 类型定义 */

export interface FieldConfig extends PictureConfig {
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
  action_type?: string;  // 'api'（默认）或 'navigate'
  target_instance?: string;  // 目标实例ID（当action_type=navigate时使用）
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

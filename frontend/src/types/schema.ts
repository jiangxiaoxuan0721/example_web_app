/** Schema 类型定义 */

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

/** 表格列配置接口 */
export interface TableColumn {
  key: string;
  label: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;  // 是否可排序
  editable?: boolean;  // 列是否可编辑
  render?: string | ((value: any, record: any, index: number) => React.ReactNode);
  // 渲染类型，用于在 JSON 中指定简单的渲染逻辑
  renderType?: 'text' | 'tag' | 'badge' | 'progress' | 'image' | 'mixed';
  // tag 类型时的属性
  tagType?: (value: any) => 'success' | 'warning' | 'error' | 'info' | 'default';
  // badge 类型时的属性
  badgeColor?: string;
  // mixed 类型时的属性 - 组合多个元素
  components?: Array<{
    type: 'text' | 'tag' | 'badge' | 'progress' | 'image' | 'button' | 'spacer';
    field?: string;  // 从 record 中取值的字段名
    text?: string;    // 静态文本
    // tag/badge 特有属性
    tagType?: string;
    badgeColor?: string;
    // image 特有属性
    imageSize?: string;
    imageFit?: string;
    // button 特有属性
    buttonLabel?: string;
    buttonStyle?: 'primary' | 'secondary' | 'danger';
    buttonSize?: 'small' | 'medium' | 'large';
    actionType?: string;
    actionData?: any;
    // spacer 特有属性
    width?: string;
    // 布局属性
    align?: 'left' | 'center' | 'right' | 'flex-start' | 'flex-end';
    margin?: string;
  }>;
}

/** 字段配置接口 */
export interface FieldConfig extends PictureConfig {
  label: string;
  key: string;
  type: string;
  rid?: string;
  value?: any;
  description?: string;
  options?: Array<{ label: string; value: string }>;
  
  // 多选框属性
  selectedValues?: string[];
  
  // 表格属性
  columns?: TableColumn[];
  rowKey?: string;
  bordered?: boolean;
  striped?: boolean;
  hover?: boolean;
  emptyText?: string;
  tableEditable?: boolean;
  showHeader?: boolean;
  showPagination?: boolean;
  pageSize?: number;
  maxHeight?: string;
  compact?: boolean;

  // 嵌入渲染属性
  targetInstance?: string;  // 目标实例ID
  targetBlock?: string;     // 目标block ID
}

export interface BlockProps {
  fields?: FieldConfig[];
  actions?: ActionConfig[];  // Block 级别的操作按钮
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
  handler_type?: string;  // 处理器类型：set/increment/decrement/toggle/custom
  patches?: Record<string, any>;  // 要应用的 patch 映射（key为路径，value为值或操作配置）
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

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
  title: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;  // 是否可排序
  filterable?: boolean;  // 是否可过滤
  editable?: boolean;  // 列是否可编辑
  editType?: 'text' | 'number' | 'select';  // 编辑器类型
  options?: Array<{ label: string; value: string }>;  // 选项列表（editType=select 时使用）
  render?: string | ((value: any, record: any, index: number) => React.ReactNode);
  // 渲染类型，用于在 JSON 中指定简单的渲染逻辑
  renderType?: 'text' | 'tag' | 'badge' | 'progress' | 'image' | 'mixed';
  // tag 类型时的属性 - 支持字符串表达式
  tagType?: string;
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
  type: string;
  label: string;
  key: string;
  value?: any;
  description?: string;
  options?: Array<{ label: string; value: string }>;

  // 字段控制属性
  editable?: boolean;  // 是否可编辑（默认 true）
  required?: boolean;  // 是否必填（默认 false）
  disabled?: boolean;  // 是否禁用（默认 false）
  placeholder?: string;  // 占位符文本

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

  // 组件嵌入：渲染一个嵌套的 Block 配置
  blockConfig?: Block;  // 要渲染的嵌套 Block 配置
}

export interface BlockProps {
  fields?: FieldConfig[];
  actions?: ActionConfig[];  // Block 级别的操作按钮

  // Tabs 布局属性
  tabs?: Array<{
    label: string;
    fields?: FieldConfig[];
    actions?: ActionConfig[];  // Tab 级别的操作按钮
  }>;

  // Grid 布局属性
  cols?: number;
  gap?: string;

  // Accordion 布局属性
  panels?: Array<{
    title: string;
    fields?: FieldConfig[];
    actions?: ActionConfig[];  // Panel 级别的操作按钮
  }>;
}

export interface Block {
  id: string;
  layout: string;
  title?: string;
  props?: BlockProps;
}

export interface ActionConfig {
  id: string;
  label: string;
  style: string;
  action_type?: string;  // 'apply_patch'（默认）、'navigate'（实例导航）或 'navigate_block'（block导航）
  target_instance?: string;  // 目标实例ID（当action_type=navigate时使用）
  target_block?: string;  // 目标block ID（当action_type=navigate_block时使用）
  patches?: UnifiedPatch[];  // patch 数组，统一格式
  disabled?: boolean;  // 是否禁用
}

export interface StepInfo {
  current: number;
  total: number;
}

export interface StateInfo {
  params: Record<string, any>;
  runtime: Record<string, any>;
}

/** 统一 Patch 类型 */
export interface UnifiedPatch {
  op: 'set' | 'add' | 'remove' | 'append_to_list' | 'prepend_to_list' |
      'update_list_item' | 'remove_last' | 'merge' | 'increment' | 'decrement' | 'toggle';
  path: string;
  value?: any;
  index?: number;  // 仅 update_list_item 使用
}


export interface LayoutInfo {
  type: 'single' | 'grid' | 'flex' | 'tabs';
  columns?: number;      // grid 布局列数（默认 2）
  gap?: string;          // 间距（默认 "20px"）
}

export interface UISchema {
  page_key: string;
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

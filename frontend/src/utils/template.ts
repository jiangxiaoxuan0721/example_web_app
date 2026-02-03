/**
 * 模板引擎 - 支持 ${state.xxx} 和 ${runtime.xxx} 语法的变量替换
 */

import type { UISchema } from '../types/schema';

/**
 * 从选项列表中查找标签
 * @param value 选中的值
 * @param options 选项列表
 * @returns 对应的标签，如果找不到则返回原值
 */
export function getOptionLabel(
  value: any,
  options?: Array<{ label: string; value: string }>
): string {
  if (!value || !options || !Array.isArray(options)) {
    return String(value ?? '');
  }

  const found = options.find(opt => opt.value === String(value));
  return found ? found.label : String(value);
}

/**
 * 从选项列表中查找多个标签
 * @param values 选中的值数组
 * @param options 选项列表
 * @returns 对应的标签数组，如果找不到则返回原值
 */
export function getOptionLabels(
  values: any[],
  options?: Array<{ label: string; value: string }>
): string[] {
  if (!values || !Array.isArray(values) || !options || !Array.isArray(options)) {
    return [];
  }

  return values.map(v => getOptionLabel(v, options));
}

/**
 * 从 schema 中获取嵌套值
 * @param obj 对象
 * @param path 点分隔的路径，如 'state.params.userId'
 * @param defaultValue 默认值
 * @returns 找到的值或默认值
 */
export function getNestedValue(obj: any, path: string, defaultValue: any = ''): any {
  if (!path || !obj) {
    return defaultValue;
  }

  const keys = path.split('.');
  let current = obj;

  for (const key of keys) {
    if (current == null) {
      return defaultValue;
    }
    current = current[key];
  }

  return current !== undefined ? current : defaultValue;
}

/**
 * 渲染模板字符串，替换 ${state.xxx} 和 ${runtime.xxx} 占位符
 * @param template 模板字符串
 * @param schema 完整的 UISchema
 * @param extraContext 额外的上下文变量
 * @returns 渲染后的字符串
 */
export function renderTemplate(
  template: string | undefined | null,
  schema: UISchema | null,
  extraContext?: Record<string, any>
): string {
  if (!template || typeof template !== 'string') {
    return String(template ?? '');
  }

  if (!schema) {
    return template;
  }

  // 创建上下文对象
  const context = {
    state: schema.state || {},
    params: schema.state?.params || {},
    runtime: schema.state?.runtime || {},
    ...extraContext
  };

  // 正则表达式匹配 ${xxx} 格式的占位符
  // 支持嵌套路径，如 ${state.params.userId}、${runtime.timestamp}
  const templateRegex = /\$\{([^}]+)\}/g;

  return template.replace(templateRegex, (match, expression) => {
    const trimmed = expression.trim();

    // 处理 .label 后缀（从选项框获取标签）
    if (trimmed.endsWith('.label')) {
      const baseExpression = trimmed.slice(0, -6); // 移除 '.label'
      const baseValue = getNestedValue(context, baseExpression, match);
      
      // 从全局存储中查找对应的标签
      // 从路径中提取字段名，如 state.params.status.label -> status
      const parts = baseExpression.split('.');
      const fieldKey = parts[parts.length - 1];
      const optionLabels = (window as any).__optionLabels__ || {};
      const label = optionLabels[fieldKey];
      
      if (label !== undefined) {
        return label;
      }
      
      // 如果没有找到标签，返回原值
      return baseValue === match ? match : String(baseValue);
    }

    // 尝试从上下文中获取值
    const value = getNestedValue(context, trimmed, match);

    // 将值转换为字符串
    if (value === null || value === undefined) {
      return match; // 如果找不到值，保留原始占位符
    }

    if (Array.isArray(value)) {
      return value.join(', ');
    }

    return String(value);
  });
}

/**
 * 渲染字段配置中的所有模板字符串
 * @param field 字段配置
 * @param schema 完整的 UISchema
 * @returns 渲染后的字段配置
 */
export function renderFieldTemplate(
  field: any,
  schema: UISchema | null
): any {
  if (!field || typeof field !== 'object') {
    return field;
  }

  // 如果是 FieldConfig 对象
  if (field && typeof field === 'object') {
    const rendered: any = { ...field };

    // 渲染可渲染的字符串字段
    const stringFields = [
      'label',
      'description',
      'subtitle',
      'fallback',
      'emptyText',
      'placeholder'
    ];

    for (const fieldKey of stringFields) {
      if (rendered[fieldKey]) {
        rendered[fieldKey] = renderTemplate(rendered[fieldKey], schema);
      }
    }

    return rendered;
  }

  return field;
}

/**
 * 批量渲染多个模板字符串
 * @param templates 模板字符串映射
 * @param schema 完整的 UISchema
 * @returns 渲染后的字符串映射
 */
export function renderTemplates(
  templates: Record<string, string | undefined>,
  schema: UISchema | null
): Record<string, string> {
  const rendered: Record<string, string> = {};

  for (const [key, value] of Object.entries(templates)) {
    rendered[key] = renderTemplate(value, schema);
  }

  return rendered;
}

/** Patch 工具函数 */

import { UISchema } from '../types/schema';

/**
 * 获取字段值
 * @param schema - UISchema 对象
 * @param bindPath - 绑定路径（如 "state.params"）
 * @param fieldKey - 字段键
 * @returns 字段值
 */
export function getFieldValue(schema: UISchema, bindPath: string, fieldKey: string): any {
  const path = `${bindPath}.${fieldKey}`;
  const keys = path.split('.');
  let current: any = schema;

  for (const key of keys) {
    if (current === undefined || current === null) {
      return undefined;
    }
    current = current[key];
  }

  return current;
}

/**
 * 应用 patch 到 schema
 * @param schema - 原始 schema
 * @param patch - patch 对象（键为点路径，值为新值）
 * @returns 更新后的 schema
 */
export function applyPatchToSchema(schema: UISchema, patch: Record<string, any>): UISchema {
  console.log('[Patch] 应用 patch:', patch);
  console.log('[Patch] 原始 schema:', schema);

  // 深拷贝 schema
  const result = JSON.parse(JSON.stringify(schema));

  for (const [path, value] of Object.entries(patch)) {
    console.log(`[Patch] 应用: ${path} =`, value);
    setNestedValue(result, path, value);
  }

  console.log('[Patch] 更新后的 schema:', result);
  return result;
}

/**
 * 设置嵌套对象的值
 * @param obj - 目标对象
 * @param path - 点分隔路径（如 "state.params.count"）
 * @param value - 要设置的值
 */
function setNestedValue(obj: any, path: string, value: any): void {
  const keys = path.split('.');
  let current = obj;

  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (!(key in current)) {
      current[key] = {};
    }
    current = current[key];
  }

  const lastKey = keys[keys.length - 1];
  current[lastKey] = value;
}

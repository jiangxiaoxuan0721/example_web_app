import { UISchema, UIPatch } from '../types/schema';

/**
 * 根据 dot path 获取嵌套对象中的值
 * @param obj 目标对象
 * @param path 点路径，如 "state.params.speed"
 * @returns 路径对应的值
 */
export const getByDotPath = (obj: any, path: string): any => {
  return path.split('.').reduce((current, key) => current?.[key], obj);
};

/**
 * 根据 dot path 设置嵌套对象中的值
 * @param obj 目标对象
 * @param path 点路径，如 "state.params.speed"
 * @param value 要设置的值
 */
export const setByDotPath = (obj: any, path: string, value: any): void => {
  const keys = path.split('.');
  const lastKey = keys.pop()!;
  
  const target = keys.reduce((current, key) => {
    if (current[key] === undefined) {
      current[key] = {};
    }
    return current[key];
  }, obj);
  
  target[lastKey] = value;
};

/**
 * 应用 Patch 到 UISchema
 * @param schema 原始 Schema
 * @param patch 要应用的 Patch
 * @returns 应用 Patch 后的新 Schema（不可变）
 */
export const applyPatch = (schema: UISchema, patch: UIPatch): UISchema => {
  // 深拷贝 Schema
  const newSchema: UISchema = JSON.parse(JSON.stringify(schema));
  
  // 应用每个 patch 操作
  Object.entries(patch).forEach(([path, value]) => {
    setByDotPath(newSchema, path, value);
  });
  
  return newSchema;
};

/**
 * 批量应用多个 Patch
 * @param schema 原始 Schema
 * @param patches Patch 数组
 * @returns 应用所有 Patch 后的新 Schema
 */
export const applyPatches = (schema: UISchema, patches: UIPatch[]): UISchema => {
  return patches.reduce<UISchema>((currentSchema, patch) => applyPatch(currentSchema, patch), schema);
};

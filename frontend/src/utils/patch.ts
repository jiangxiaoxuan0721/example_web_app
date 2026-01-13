/** Patch 工具函数 */

/**
 * 应用 patch 到 schema
 * @param schema - 原始 schema
 * @param patch - patch 对象（键为点路径，值为任意类型）
 * @returns 应用 patch 后的新 schema
 */
export function applyPatchToSchema<T extends Record<string, any>>(
  schema: T,
  patch: Record<string, any>
): T {
  const newSchema = { ...schema };

  // 应用 patch（简单的点路径实现）
  for (const [path, value] of Object.entries(patch)) {
    const keys = path.split('.');
    let current: any = newSchema;

    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }

    current[keys[keys.length - 1]] = value;
  }

  return newSchema;
}

/**
 * 从 schema 中读取字段值
 * @param schema - schema 对象
 * @param bindPath - 绑定路径（如 "state.params"）
 * @param fieldKey - 字段键（如 "message"）
 * @returns 字段值
 */
export function getFieldValue(
  schema: any,
  bindPath: string,
  fieldKey: string
): any {
  // 1. 先解析 block.bind 路径
  let baseObj: any = schema;
  if (bindPath) {
    const bindPathKeys = bindPath.split('.');
    baseObj = bindPathKeys.reduce((obj: any, key: string) => obj?.[key], schema);
  }
  // 2. 再读取 field.key
  const fieldKeys = fieldKey.split('.');
  return fieldKeys.reduce((obj: any, key: string) => obj?.[key], baseObj);
}

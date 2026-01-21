/** Schema Store - 唯一真源 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { shallow } from 'zustand/shallow';
import type { UISchema } from '../types/schema';

interface SchemaStore {
  // Schema 唯一真源
  schema: UISchema | null;
  // 当前实例ID
  instanceId: string | null;

  // Actions
  setSchema: (schema: UISchema) => void;
  setInstanceId: (instanceId: string) => void;
  applyPatch: (patch: Record<string, any>) => void;
  reset: () => void;
}

export const useSchemaStore = create<SchemaStore>()(
  subscribeWithSelector((set) => ({
    schema: null,
    instanceId: null,

    setSchema: (schema) => {
      // Deep clone to ensure new reference
      const clonedSchema = JSON.parse(JSON.stringify(schema));
      set({ schema: clonedSchema });
    },

    setInstanceId: (instanceId) => set({ instanceId }),

    applyPatch: (patch) => set((state) => {
      if (!state.schema) return state;

      console.log('[SchemaStore] applyPatch 开始，patch:', patch);

      // Deep clone schema and apply patches
      const newSchema = JSON.parse(JSON.stringify(state.schema));

      for (const [path, value] of Object.entries(patch)) {
        const keys = path.split('.');
        let current: any = newSchema;

        for (let i = 0; i < keys.length - 1; i++) {
          if (!current[keys[i]]) {
            current[keys[i]] = {};
          }
          current = current[keys[i]];
        }

        console.log(`[SchemaStore] 设置路径 ${path} = ${value}`);
        current[keys[keys.length - 1]] = value;
      }

      console.log('[SchemaStore] newSchema 引用:', newSchema);
      console.log('[SchemaStore] oldSchema 引用:', state.schema);
      console.log('[SchemaStore] 引用是否不同:', newSchema !== state.schema);

      return { schema: newSchema };
    }),

    reset: () => set({ schema: null, instanceId: null })
  }))
);

// Selector for getting bound value
export const useBoundValue = (bindPath: string) => {
  return useSchemaStore((state) => {
    if (!state.schema) return undefined;

    const keys = bindPath.split('.');
    return keys.reduce((obj: any, key: string) => obj?.[key], state.schema);
  });
};

// Selector for getting field value - subscribe to entire schema to detect changes
export const useFieldValue = (bindPath: string, fieldKey: string) => {
  return useSchemaStore((state) => {
    // 返回整个 state 以触发任何变化
    // 组件将从 state.schema 中提取实际值
    return state.schema;
  });
};

// Helper to apply field-specific patch
export const useFieldPatch = () => {
  const { applyPatch } = useSchemaStore();

  return (bindPath: string, fieldKey: string, value: any) => {
    const path = bindPath ? `${bindPath}.${fieldKey}` : `state.params.${fieldKey}`;
    applyPatch({ [path]: value });
  };
};
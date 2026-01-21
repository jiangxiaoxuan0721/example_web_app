/** Schema Store - 唯一真源 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
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
    
    setSchema: (schema) => set({ schema }),
    setInstanceId: (instanceId) => set({ instanceId }),
    
    applyPatch: (patch) => set((state) => {
      if (!state.schema) return state;
      
      const newSchema = applyPatchToSchema(state.schema, patch);
      return { schema: newSchema };
    }),
    
    reset: () => set({ schema: null, instanceId: null })
  }))
);

// Helper function to apply patch to schema
function applyPatchToSchema<T extends Record<string, any>>(
  schema: T,
  patch: Record<string, any>
): T {
  const newSchema = { ...schema };

  // Apply patch (simple dot path implementation)
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

// Selector for getting bound value
export const useBoundValue = (bindPath: string) => {
  return useSchemaStore((state) => {
    if (!state.schema) return undefined;
    
    const keys = bindPath.split('.');
    return keys.reduce((obj: any, key: string) => obj?.[key], state.schema);
  });
};

// Selector for getting field value
export const useFieldValue = (bindPath: string, fieldKey: string) => {
  return useSchemaStore((state) => {
    if (!state.schema) return undefined;
    
    // 1. Resolve block.bind path
    let baseObj: any = state.schema;
    if (bindPath) {
      const bindPathKeys = bindPath.split('.');
      baseObj = bindPathKeys.reduce((obj: any, key: string) => obj?.[key], state.schema);
    }
    
    // 2. Read field.key
    const fieldKeys = fieldKey.split('.');
    return fieldKeys.reduce((obj: any, key: string) => obj?.[key], baseObj);
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
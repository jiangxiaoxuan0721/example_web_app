/** Schema Store - 唯一真源 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type { UISchema } from '../types/schema';

interface SchemaStore {
  // Schema 唯一真源
  schema: UISchema | null;
  // 当前实例ID
  instanceId: string | null;
  // 需要高亮的 block ID
  highlightBlockId: string | null;
  // 需要高亮的 field key
  highlightFieldKey: string | null;
  // 需要高亮的 action ID
  highlightActionId: string | null;

  // Actions
  setSchema: (schema: UISchema, highlight?: any) => void;
  setInstanceId: (instanceId: string) => void;
  applyPatch: (patch: Record<string, any>, isExternal?: boolean, isAddSet?: boolean) => void;
  highlightBlock: (blockId: string) => void;
  highlightField: (fieldKey: string) => void;
  highlightAction: (actionId: string) => void;
  reset: () => void;
}

export const useSchemaStore = create<SchemaStore>()(
  subscribeWithSelector((set) => ({
    schema: null,
    instanceId: null,
    highlightBlockId: null,
    highlightFieldKey: null,
    highlightActionId: null,

    setSchema: (schema, highlight) => {
      // Deep clone to ensure new reference
      const clonedSchema = JSON.parse(JSON.stringify(schema));
      set({ schema: clonedSchema });

      // Handle highlight if provided
      if (highlight) {
        const { highlightBlock, highlightField, highlightAction } = useSchemaStore.getState();
        if (highlight.type === "field" && highlight.key) {
          console.log(`[SchemaStore] 高亮 field: ${highlight.key}`);
          highlightField(highlight.key);
        } else if (highlight.type === "action" && highlight.id) {
          console.log(`[SchemaStore] 高亮 action: ${highlight.id}`);
          highlightAction(highlight.id);
        } else if (highlight.type === "block" && highlight.id) {
          console.log(`[SchemaStore] 高亮 block: ${highlight.id}`);
          highlightBlock(highlight.id);
        }
      }
    },

    setInstanceId: (instanceId) => set({ instanceId }),

    highlightBlock: (blockId) => {
      set({ highlightBlockId: blockId });
      setTimeout(() => {
        set({ highlightBlockId: null });
      }, 2000);
    },

    highlightField: (fieldKey) => {
      set({ highlightFieldKey: fieldKey });
      setTimeout(() => {
        set({ highlightFieldKey: null });
      }, 2000);
    },

    highlightAction: (actionId) => {
      set({ highlightActionId: actionId });
      setTimeout(() => {
        set({ highlightActionId: null });
      }, 2000);
    },

    applyPatch: (patch, isExternal = true, isAddSet = false) => set((state) => {
      if (!state.schema) return state;

      console.log('[SchemaStore] applyPatch 开始，patch:', patch, 'isExternal:', isExternal);

      // Deep clone schema and apply patches
      const newSchema = JSON.parse(JSON.stringify(state.schema));

      let affectedBlockId: string | null = null;
      let affectedFieldKey: string | null = null;
      let affectedActionId: string | null = null;

      for (const [path, value] of Object.entries(patch)) {
        const keys = path.split('.');
        console.log(`[SchemaStore] 处理路径: ${path}, keys: ${keys}`);

        // ===== 特殊路径处理（与后端 apply_patch_to_schema 保持一致） =====

        // 1. actions.X.patches - 更新 action 的 patches（全局 actions）
        if (keys.length >= 3 && keys[0] === 'actions' && keys[2] === 'patches') {
          const actionIndex = parseInt(keys[1]);
          if (!isNaN(actionIndex) && newSchema.actions?.[actionIndex]) {
            newSchema.actions[actionIndex].patches = value;
            affectedActionId = newSchema.actions[actionIndex].id;
            console.log(`[SchemaStore] 更新全局 action patches: ${affectedActionId}`);
          }
          continue;
        }

        // 2. blocks.X.props.actions.X.patches - 更新 block action 的 patches
        if (keys.length >= 5 && keys[0] === 'blocks' && keys[2] === 'props' && keys[3] === 'actions' && keys[5] === 'patches') {
          const blockIndex = parseInt(keys[1]);
          const actionIndex = parseInt(keys[4]);
          if (!isNaN(blockIndex) && !isNaN(actionIndex) && newSchema.blocks?.[blockIndex]) {
            const block = newSchema.blocks[blockIndex];
            if (block.props?.actions?.[actionIndex]) {
              block.props.actions[actionIndex].patches = value;
              affectedActionId = block.props.actions[actionIndex].id;
              console.log(`[SchemaStore] 更新 block action patches: ${affectedActionId}`);
            }
          }
          continue;
        }

        // 3. actions.X - 替换整个 action（全局 actions）
        if (keys.length >= 2 && keys[0] === 'actions') {
          const actionIndex = parseInt(keys[1]);
          if (!isNaN(actionIndex) && newSchema.actions?.[actionIndex]) {
            newSchema.actions[actionIndex] = value;
            affectedActionId = value.id || newSchema.actions[actionIndex].id;
            console.log(`[SchemaStore] 替换全局 action: ${affectedActionId}`);
          }
          continue;
        }

        // 4. blocks.X.props.actions.X - 替换 block action
        if (keys.length >= 5 && keys[0] === 'blocks' && keys[2] === 'props' && keys[3] === 'actions') {
          const blockIndex = parseInt(keys[1]);
          const actionIndex = parseInt(keys[4]);
          if (!isNaN(blockIndex) && !isNaN(actionIndex) && newSchema.blocks?.[blockIndex]) {
            const block = newSchema.blocks[blockIndex];
            if (block.props?.actions?.[actionIndex]) {
              block.props.actions[actionIndex] = value;
              affectedActionId = value.id || block.props.actions[actionIndex].id;
              console.log(`[SchemaStore] 替换 block action: ${affectedActionId}`);
            }
          }
          continue;
        }

        // 5. blocks.X.props.actions - 替换 block 的 actions 数组
        if (keys.length >= 4 && keys[0] === 'blocks' && keys[2] === 'props' && keys[3] === 'actions') {
          const blockIndex = parseInt(keys[1]);
          if (!isNaN(blockIndex) && newSchema.blocks?.[blockIndex]) {
            const block = newSchema.blocks[blockIndex];
            block.props = block.props || {};
            block.props.actions = Array.isArray(value) ? value : [];
            console.log(`[SchemaStore] 替换 block actions: block ${blockIndex}`);
          }
          continue;
        }

        // 3. state.params.key 或 state.runtime.key
        if (keys.length >= 3 && keys[0] === 'state') {
          const targetSection = keys[1];
          const targetKey = keys[2];

          if (targetSection === 'params') {
            if (!newSchema.state.params) newSchema.state.params = {};
            newSchema.state.params[targetKey] = value;
            affectedFieldKey = targetKey;
            console.log(`[SchemaStore] 设置 state.params.${targetKey} =`, value);
          } else if (targetSection === 'runtime') {
            if (!newSchema.state.runtime) newSchema.state.runtime = {};
            newSchema.state.runtime[targetKey] = value;
            if (!affectedBlockId && newSchema.blocks?.length > 0) {
              affectedBlockId = newSchema.blocks[0].id;
            }
            console.log(`[SchemaStore] 设置 state.runtime.${targetKey} =`, value);
          }
          continue;
        }

        // 4. blocks.X.props.fields.Y - 替换指定索引的字段
        if (keys.length >= 5 && keys[0] === 'blocks' && keys[2] === 'props' && keys[3] === 'fields') {
          const blockIndex = parseInt(keys[1]);
          const fieldIndex = parseInt(keys[4]);

          if (!isNaN(blockIndex) && !isNaN(fieldIndex) &&
            newSchema.blocks?.[blockIndex]) {
            const block = newSchema.blocks[blockIndex];
            affectedBlockId = block.id;

            if (!block.props) block.props = {};
            if (!block.props.fields) block.props.fields = [];

            // 确保 fields 是数组
            let fields = block.props.fields;
            if (!Array.isArray(fields)) {
              fields = Object.values(fields);
              block.props.fields = fields;
            }

            // 替换字段
            if (0 <= fieldIndex < fields.length) {
              const oldKey = fields[fieldIndex]?.key;
              fields[fieldIndex] = value;
              const newKey = value?.key;

              // 如果 key 改变了，更新 state
              if (oldKey && newKey && oldKey !== newKey) {
                if (oldKey in (newSchema.state.params || {})) {
                  delete newSchema.state.params[oldKey];
                }
                if (oldKey in (newSchema.state.runtime || {})) {
                  delete newSchema.state.runtime[oldKey];
                }
                if (newKey && !(newKey in (newSchema.state.params || {}))) {
                  if (!newSchema.state.params) newSchema.state.params = {};
                  newSchema.state.params[newKey] = "";
                }
              }

              affectedFieldKey = newKey || value?.key;
              console.log(`[SchemaStore] 替换字段 blocks[${blockIndex}].props.fields[${fieldIndex}]:`, affectedFieldKey);
            }
          }
          continue;
        }

        // 5. blocks.X.props.fields.Y.key - 修改字段属性
        if (keys.length >= 6 && keys[0] === 'blocks' && keys[2] === 'props' && keys[3] === 'fields') {
          const blockIndex = parseInt(keys[1]);
          const fieldIndex = parseInt(keys[4]);
          const fieldAttr = keys[5];

          if (!isNaN(blockIndex) && !isNaN(fieldIndex) &&
            newSchema.blocks?.[blockIndex]) {
            const block = newSchema.blocks[blockIndex];
            affectedBlockId = block.id;

            if (block.props?.fields) {
              let fields = block.props.fields;
              if (!Array.isArray(fields)) {
                fields = Object.values(fields);
                block.props.fields = fields;
              }

              if (0 <= fieldIndex < fields.length) {
                const field = fields[fieldIndex];

                if (fieldAttr === 'key') {
                  const oldKey = field?.key;
                  const newKey = value;

                  field[fieldAttr] = newKey;

                  // 更新 state
                  if (oldKey && newKey && oldKey !== newKey) {
                    if (oldKey in (newSchema.state.params || {})) {
                      newSchema.state.params[newKey] = newSchema.state.params[oldKey];
                      delete newSchema.state.params[oldKey];
                    }
                    if (oldKey in (newSchema.state.runtime || {})) {
                      newSchema.state.runtime[newKey] = newSchema.state.runtime[oldKey];
                      delete newSchema.state.runtime[oldKey];
                    }
                  }
                  affectedFieldKey = newKey;
                } else {
                  field[fieldAttr] = value;
                  affectedFieldKey = field?.key;
                }
                console.log(`[SchemaStore] 修改字段属性 blocks[${blockIndex}].props.fields[${fieldIndex}].${fieldAttr} =`, value);
              }
            }
          }
          continue;
        }

        // ===== 默认路径处理（通用的嵌套赋值） =====
        let current: any = newSchema;
        for (let i = 0; i < keys.length - 1; i++) {
          if (!current[keys[i]]) {
            current[keys[i]] = {};
          }
          current = current[keys[i]];
        }

        console.log(`[SchemaStore] 默认设置路径 ${path} = ${value}`);
        current[keys[keys.length - 1]] = value;
      }

      console.log('[SchemaStore] newSchema 引用:', newSchema);
      console.log('[SchemaStore] oldSchema 引用:', state.schema);
      console.log('[SchemaStore] 引用是否不同:', newSchema !== state.schema);

      // 只在 add/set 操作时设置高亮
      if (isAddSet) {
        if (affectedFieldKey) {
          console.log(`[SchemaStore] 高亮 field: ${affectedFieldKey}`);
          state.highlightField(affectedFieldKey);
        } else if (affectedActionId) {
          console.log(`[SchemaStore] 高亮 action: ${affectedActionId}`);
          state.highlightAction(affectedActionId);
        } else if (affectedBlockId) {
          console.log(`[SchemaStore] 高亮 block: ${affectedBlockId}`);
          state.highlightBlock(affectedBlockId);
        }
      }

      return { schema: newSchema };
    }),

    reset: () => set({ schema: null, instanceId: null, highlightBlockId: null, highlightFieldKey: null, highlightActionId: null })
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

// Helper to apply field-specific patch
export const useFieldPatch = () => {
  const { applyPatch } = useSchemaStore();

  return (bindPath: string, fieldKey: string, value: any, isAddSet = false) => {
    const path = bindPath ? `${bindPath}.${fieldKey}` : `state.params.${fieldKey}`;
    applyPatch({ [path]: value }, false, isAddSet);
  };
};
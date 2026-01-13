import { useState, useCallback } from 'react';
import { UISchema, UIPatch } from '../types/schema';
import { applyPatch } from '../utils/patch';

/**
 * Schema 状态管理 Hook
 * 提供统一的 Schema 状态更新接口
 */
export const useSchemaState = (initialSchema: UISchema) => {
  const [schema, setSchema] = useState<UISchema>(initialSchema);

  /**
   * 应用单个 Patch
   */
  const applySchemaPatch = useCallback((patch: UIPatch) => {
    setSchema(prevSchema => applyPatch(prevSchema, patch));
  }, []);

  /**
   * 批量应用多个 Patch
   */
  const applySchemaPatches = useCallback((patches: UIPatch[]) => {
    setSchema(prevSchema =>
      patches.reduce<UISchema>((current, patch) => applyPatch(current, patch), prevSchema)
    );
  }, []);

  /**
   * 更新状态（便捷方法）
   */
  const updateState = useCallback((key: string, value: any) => {
    applySchemaPatch({ [`state.${key}`]: value });
  }, [applySchemaPatch]);

  /**
   * 更新 Meta（便捷方法）
   */
  const updateMeta = useCallback((key: string, value: any) => {
    applySchemaPatch({ [`meta.${key}`]: value });
  }, [applySchemaPatch]);

  /**
   * 更新步骤
   */
  const goToStep = useCallback((step: number) => {
    updateMeta('step.current', step);
  }, [updateMeta]);

  /**
   * 设置状态
   */
  const setStatus = useCallback((status: UISchema['meta']['status']) => {
    updateMeta('status', status);
  }, [updateMeta]);

  return {
    schema,
    setSchema,
    applySchemaPatch,
    applySchemaPatches,
    updateState,
    updateMeta,
    goToStep,
    setStatus,
  };
};

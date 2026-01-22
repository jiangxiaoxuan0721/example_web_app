/** Patch 历史记录 Hook */

import { useState, useCallback } from 'react';
import type { PatchRecord } from '../types/schema';
import { loadPatchHistory, replayPatch as replayPatchApi } from '../utils/api';
import { getInstanceIdFromStorage } from '../utils/url';

export function usePatchHistory(onPatchApplied: (patch: Record<string, any>) => void) {
  const [patches, setPatches] = useState<PatchRecord[]>([]);

  // 加载 Patch 历史记录
  const loadPatches = useCallback(async (instanceId?: string) => {
    try {
      const targetInstanceId = instanceId || getInstanceIdFromStorage();
      const patches = await loadPatchHistory(targetInstanceId);
      setPatches(patches);
      console.log('[前端] Patch 历史加载成功:', patches);
    } catch (err) {
      console.error('[前端] 加载 Patch 历史失败:', err);
    }
  }, []);

  // 重放 Patch
  const replayPatch = useCallback(async (patchId: number) => {
    try {
      const currentInstanceId = getInstanceIdFromStorage();
      console.log(`[前端] 重放 Patch: ${patchId} (instanceId: ${currentInstanceId})`);

      const data = await replayPatchApi(patchId, currentInstanceId);

      if (data.status === 'success' && data.patch) {
        onPatchApplied(data.patch);
        console.log('[前端] Patch 重放成功');
      } else {
        console.error('[前端] Patch 重放失败:', data.message);
      }
    } catch (err) {
      console.error('[前端] Patch 重放失败:', err);
    }
  }, [onPatchApplied]);

  return {
    patches,
    loadPatches,
    replayPatch
  };
}

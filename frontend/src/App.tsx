/**
 * Agent 可编程 UI Runtime - 最小原型
 *
 * 职责（3件事）：
 * 1. 加载 Schema (GET /ui/schema?instanceId=xxx)
 * 2. 渲染 Schema
 * 3. 把用户行为变成 Event (POST /ui/event)
 *
 * 不做：
 * - 不存业务状态
 * - 不做流程判断
 * - 不生成 Schema
 *
 * 自检清单：
 * ✅ Schema 是唯一 UI 来源 - 是
 * ✅ 前端完全被动 - 是
 * ✅ Patch 能独立重放 - 是（支持历史记录和重放）
 * ✅ 去掉前端缓存能恢复 - 是
 * ✅ 支持多实例 - 是（通过 instanceId）
 */

import { useCallback, useState, useEffect, useRef } from 'react';
import type { UISchema } from './types/schema';
import { useSchema } from './hooks/useSchema';
import { usePatchHistory } from './hooks/usePatchHistory';
import { useWebSocket } from './hooks/useWebSocket';
import { emitEvent } from './utils/api';
import { applyPatchToSchema } from './utils/patch';
import Loading from './components/Loading';
import ErrorState from './components/ErrorState';
import InstanceSelector from './components/InstanceSelector';
import BlockRenderer from './components/BlockRenderer';
import ActionButton from './components/ActionButton';
import PatchHistory from './components/PatchHistory';
import DebugInfo from './components/DebugInfo';

export default function App() {
  const { currentInstanceId, schema, loading, error } = useSchema();

  // ============ Patch 管理逻辑 ============
  const [currentSchema, setCurrentSchema] = useState<UISchema | null>(schema);
  const isLoadingPatchesRef = useRef(false);

  // 当 schema 加载完成时更新
  const updateSchema = useCallback((patch: Record<string, any>) => {
    setCurrentSchema((prev) => {
      if (!prev) return prev;

      // 应用 patch
      const newSchema = applyPatchToSchema(prev, patch);
      console.log('[前端] Patch 已应用:', newSchema);
      return newSchema;
    });
  }, []);

  // 字段值改变（仅前端乐观更新，不立即同步到后端）
  const handleFieldChange = useCallback((fieldKey: string, value: any) => {
    console.log(`[前端] 字段改变: ${fieldKey} = ${value}`);

    // 更新本地状态（乐观更新），等待触发器操作时再同步到后端
    const patch = { [`state.params.${fieldKey}`]: value };
    updateSchema(patch);
  }, [updateSchema]);

  // Patch 历史记录 Hook
  const { patches, loadPatches, replayPatch } = usePatchHistory(updateSchema);

  // 防抖的 loadPatches - 避免重复加载
  const debouncedLoadPatches = useCallback(() => {
    if (isLoadingPatchesRef.current) {
      console.log('[App] 正在加载 Patch 历史，跳过');
      return;
    }

    isLoadingPatchesRef.current = true;
    console.log('[App] 开始加载 Patch 历史');
    loadPatches();

    // 300ms 后重置标志
    setTimeout(() => {
      isLoadingPatchesRef.current = false;
    }, 300);
  }, [loadPatches]);

  // 初始化时加载一次 Patch 历史
  useEffect(() => {
    debouncedLoadPatches();
  }, [debouncedLoadPatches]);

  // WebSocket 接收实时 Patch
  const { connected } = useWebSocket((patch) => {
    console.log('[App] 通过 WebSocket 收到 Patch:', patch);
    updateSchema(patch);
    // 刷新 Patch 历史记录
    debouncedLoadPatches();
  });

  // 当 schema 从后端加载时更新
  if (schema !== currentSchema && schema) {
    setCurrentSchema(schema);
  }

  // ============ 发送 Event ============
  const handleActionClick = useCallback(async (actionId: string) => {
    try {
      console.log(`[前端] 发送 Event: action:click (instanceId: ${currentInstanceId})`, { actionId });

      // 同步当前所有字段值到后端（触发器操作前先同步）
      const currentParams = currentSchema?.state?.params || {};
      console.log(`[前端] 同步 params 到后端:`, currentParams);

      const data = await emitEvent('action:click', currentInstanceId, {
        actionId,
        params: currentParams  // 携带所有当前字段值
      });
      console.log('[前端] 收到响应:', data);

      // 应用 Patch（WebSocket 推送会触发更新，不需要手动应用）
      // 后端不会通过 HTTP 返回 patch，避免重复更新
    } catch (err) {
      console.error('[前端] 发送 Event 失败:', err);
    }
  }, [currentInstanceId, currentSchema]);

  // 加载中
  if (loading) {
    return <Loading />;
  }

  // 错误状态
  if (error) {
    return <ErrorState error={error} />;
  }

  // 无 Schema
  if (!currentSchema) {
    return <div>No Schema</div>;
  }

  // ============ 主渲染 ============
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      fontFamily: 'Arial, sans-serif',
      padding: '20px'
    }}>
      {/* 实例选择器 */}
      <InstanceSelector currentInstanceId={currentInstanceId} />

      {/* Schema 渲染容器 */}
      <div style={{
        border: '1px solid #ccc',
        borderRadius: '8px',
        padding: '40px',
        maxWidth: '600px',
        width: '100%',
        textAlign: 'center'
      }}>
        {/* 渲染 Blocks */}
        {currentSchema.blocks?.map((block) => (
          <BlockRenderer
            key={block.id}
            block={block}
            schema={currentSchema}
            onFieldChange={handleFieldChange}
          />
        ))}

        {/* 渲染 Actions */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
          {currentSchema.actions?.map((action) => (
            <ActionButton
              key={action.id}
              action={action}
              onClick={() => handleActionClick(action.id)}
            />
          ))}
        </div>

        {/* Patch 历史记录 */}
        <PatchHistory patches={patches} onReplay={replayPatch} />

        {/* 调试信息 */}
        <DebugInfo schema={currentSchema} instanceId={currentInstanceId} wsConnected={connected} />
      </div>
    </div>
  );
}

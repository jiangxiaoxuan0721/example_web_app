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

import { useCallback, useState } from 'react';
import type { UISchema } from './types/schema';
import { useSchema } from './hooks/useSchema';
import { usePatchHistory } from './hooks/usePatchHistory';
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

  // 当 schema 加载完成时更新
  const updateSchema = useCallback((patch: Record<string, any>) => {
    setCurrentSchema((prev) => {
      if (!prev) return prev;
      const newSchema = applyPatchToSchema(prev, patch);
      console.log('[前端] Patch 已应用:', newSchema);
      return newSchema;
    });
  }, []);

  // Patch 历史记录 Hook
  const { patches, loadPatches, replayPatch } = usePatchHistory(updateSchema);

  // 当 schema 从后端加载时更新
  if (schema !== currentSchema && schema) {
    setCurrentSchema(schema);
  }

  // ============ 发送 Event ============
  const handleActionClick = useCallback(async (actionId: string) => {
    try {
      console.log(`[前端] 发送 Event: action:click (instanceId: ${currentInstanceId})`, { actionId });

      const data = await emitEvent('action:click', currentInstanceId, { actionId });
      console.log('[前端] 收到响应:', data);

      // 应用 Patch
      if (data.status === 'success' && data.patch) {
        updateSchema(data.patch);
        // 刷新 Patch 历史记录
        loadPatches();
      }
    } catch (err) {
      console.error('[前端] 发送 Event 失败:', err);
    }
  }, [currentInstanceId, updateSchema, loadPatches]);

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
          <BlockRenderer key={block.id} block={block} schema={currentSchema} />
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
        <DebugInfo schema={currentSchema} instanceId={currentInstanceId} />
      </div>
    </div>
  );
}

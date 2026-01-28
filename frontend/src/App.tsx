/**
 * Agent 可编程 UI Runtime V2 - 纯 Schema 驱动
 *
 * 职责（3件事）：
 * 1. 加载 Schema (GET /ui/schema?instanceId=xxx)
 * 2. 监听 Schema 变化并渲染
 * 3. 发送事件到后端
 *
 * 新架构改进：
 * - Schema Store: 唯一真源，不再维护额外状态
 * - Event Emitter: 统一事件流，所有交互都通过事件
 * - Generic Renderer: 通用组件模板，支持动态扩展
 */

import { useEffect } from 'react';
import { useSchemaStore } from './store/schemaStore';
import { useMultiInstanceStore } from './store/multiInstanceStore';
import { useSchema } from './hooks/useSchema';
import { usePatchHistory } from './hooks/usePatchHistory';
import { useWebSocket } from './hooks/useWebSocket';
import { useEventEmitter } from './utils/eventEmitter';
import {
  Loading,
  ErrorState,
  InstanceSelector,
  BlockRenderer,
  ActionButton,
  PatchHistory,
  DebugInfo,
  Sidebar
} from './components';
import "./index.css";


export default function App() {
  const { currentInstanceId, schema: initialSchema, loading, error, loadingText } = useSchema();
  const { schema: storeSchema, setSchema, applyPatch, setInstanceId, highlightBlockId, highlightFieldKey, highlightActionId } = useSchemaStore();
  const { setInstance: setMultiInstance } = useMultiInstanceStore();
  const { emitInstanceSwitch } = useEventEmitter();

  // ============ Patch 历史管理 ============
  const { patches, loadPatches, replayPatch } = usePatchHistory(applyPatch);

  // 当 schema 从后端加载时更新 Store
  useEffect(() => {
    if (initialSchema) {
      console.log('[App] 从后端加载的 Schema:', initialSchema);
      console.log('[App] Schema.state:', initialSchema.state);
      setSchema(initialSchema);
      // 同时保存到多实例 store，供嵌入渲染使用
      if (currentInstanceId) {
        setMultiInstance(currentInstanceId, initialSchema);
      }
    }
  }, [initialSchema, setSchema, currentInstanceId, setMultiInstance]);
  
  // 当实例ID变化时更新 Store
  useEffect(() => {
    if (currentInstanceId) {
      setInstanceId(currentInstanceId);
    }
  }, [currentInstanceId, setInstanceId]);
  
  // 初始化时加载 Patch 历史
  useEffect(() => {
    if (currentInstanceId) {
      loadPatches();
    }
  }, [currentInstanceId, loadPatches]);
  
  // WebSocket 接收实时 Patch 和实例切换消息
  const { connected: wsConnected } = useWebSocket(
    // 处理 Patch
    (patch) => {
      console.log('[App] 通过 WebSocket 收到 Patch:', patch);
      console.log('[App] Patch 路径:', Object.keys(patch));

      const currentSchema = useSchemaStore.getState().schema;
      console.log('[App] 当前 Schema 的 state.params:', currentSchema?.state?.params);

      applyPatch(patch, true);

      const newSchema = useSchemaStore.getState().schema;
      console.log('[App] Apply Patch 后的 state.params:', newSchema?.state?.params);
      // 刷新 Patch 历史记录
      loadPatches(currentInstanceId);
    },
    // 处理实例切换和 schema 更新
    (instanceId, schema) => {
      console.log('[App] 通过 WebSocket 处理 schema 更新:', instanceId);
      if (schema) {
        console.log('[App] Schema blocks 数量:', schema?.blocks?.length || 0);
        console.log('[App] Schema actions 数量:', schema?.actions?.length || 0);
        // 如果提供了 schema，直接使用它
        // schema 来自 WebSocket，类型为 Record<string, any>，在这里做类型断言以满足 setSchema 的 UISchema 参数
        setSchema(schema as any, (schema as any).highlight);
        // 同时保存到多实例 store
        setMultiInstance(instanceId, schema as any);
        console.log('[App] Schema 已更新到 store');
      }

      if (instanceId && instanceId !== currentInstanceId) {
        // 切换到新实例
        if (!schema) {
          // switch_to_instance 不返回 schema，直接调用 emitInstanceSwitch
          console.log('[App] 触发实例切换:', instanceId);
          emitInstanceSwitch(instanceId);
        } else {
          handleInstanceSwitch(instanceId);
        }
      } else if (instanceId) {
        // schema 更新时也加载 patch 历史
        loadPatches(instanceId);
      }
    }
  );

  // 处理实例切换
  const handleInstanceSwitch = (newInstanceId: string) => {
    emitInstanceSwitch(newInstanceId);
  };
  
  // 加载中
  if (loading) {
    return <Loading text={loadingText} />;
  }
  
  // 错误状态
  if (error) {
    return <ErrorState error={error} />;
  }
  
  // ============ 主渲染 ============
    return (
    <div className="pta-layout">
      <Sidebar />

      <div className="pta-container">
        {/* 顶部固定区域 - 实例选择器 */}
        <div className="pta-header">
          <InstanceSelector
            currentInstanceId={currentInstanceId}
            onInstanceSwitch={handleInstanceSwitch}
          />
        </div>

        {/* 主要内容区域 - 可滚动 */}
        <div className="pta-content">
          {/* Schema 渲染容器 */}
          <div className="pta-schema-container">
            {/* 渲染 Blocks */}
            {storeSchema?.blocks?.map((block) => (
              <BlockRenderer
                key={block.id}
                block={block}
                highlightField={highlightFieldKey}
                highlightBlockId={highlightBlockId}
              />
            ))}

            {/* 渲染全局 Actions（保留向后兼容） */}
            <div className="pta-actions-container">
              {storeSchema?.actions?.map((action) => (
                <ActionButton
                  key={action.id}
                  action={action}
                  highlighted={action.id === highlightActionId}
                  onNavigate={handleInstanceSwitch}
                />
              ))}
            </div>

            {/* 调试信息 - 默认展开 */}
            <details className="pta-details" open>
              <summary className="pta-details__summary">
                调试信息
              </summary>
              <div className="pta-details__content">
                <DebugInfo instanceId={currentInstanceId} wsConnected={wsConnected} />
              </div>
            </details>

            {/* Patch 历史记录 - 折叠式 */}
            <details className="pta-details">
              <summary className="pta-details__summary">
                Patch 历史记录
              </summary>
              <div className="pta-details__content">
                <PatchHistory patches={patches} onReplay={replayPatch} />
              </div>
            </details>
          </div>
        </div>
      </div>
    </div>
  );
}
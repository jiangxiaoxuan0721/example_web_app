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
import { useSchema } from './hooks/useSchema';
import { usePatchHistory } from './hooks/usePatchHistory';
import { useWebSocket } from './hooks/useWebSocket';
import { useEventEmitter } from './utils/eventEmitter';
import Loading from './components/Loading';
import ErrorState from './components/ErrorState';
import InstanceSelector from './components/InstanceSelector';
import BlockRenderer from './components/BlockRenderer';
import ActionButton from './components/ActionButton';
import PatchHistory from './components/PatchHistory';
import DebugInfo from './components/DebugInfo';

// 注册自定义字段类型渲染器（示例）
// import { registerFieldRenderer } from './components/GenericFieldRenderer';

// 注册自定义块类型渲染器（示例）
// import { registerBlockRenderer } from './components/BlockRenderer';

// 可以在这里注册自定义渲染器
// registerFieldRenderer('custom', CustomFieldRenderer);
// registerBlockRenderer('custom', CustomBlockRenderer);

export default function App() {
  const { currentInstanceId, schema, loading, error } = useSchema();
  const { setSchema, applyPatch, setInstanceId } = useSchemaStore();
  const { emitInstanceSwitch } = useEventEmitter();
  
  // ============ Patch 历史管理 ============
  const { patches, loadPatches, replayPatch } = usePatchHistory(applyPatch);
  
  // 当 schema 从后端加载时更新 Store
  useEffect(() => {
    if (schema) {
      setSchema(schema);
    }
  }, [schema, setSchema]);
  
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
  
  // WebSocket 接收实时 Patch
  useWebSocket((patch) => {
    console.log('[App] 通过 WebSocket 收到 Patch:', patch);
    applyPatch(patch);
    // 刷新 Patch 历史记录
    loadPatches();
  });
  
  // 处理实例切换
  const handleInstanceSwitch = (newInstanceId: string) => {
    emitInstanceSwitch(newInstanceId);
  };
  
  // 加载中
  if (loading) {
    return <Loading />;
  }
  
  // 错误状态
  if (error) {
    return <ErrorState error={error} />;
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
      <InstanceSelector 
        currentInstanceId={currentInstanceId} 
        onInstanceSwitch={handleInstanceSwitch}
      />
      
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
        {schema?.blocks?.map((block) => (
          <BlockRenderer
            key={block.id}
            block={block}
            schema={schema!}  // schema 已经通过 schema? 检查，这里可以安全使用
          />
        ))}
        
        {/* 渲染 Actions */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
          {schema?.actions?.map((action) => (
            <ActionButton
              key={action.id}
              action={action}
              onClick={() => useEventEmitter().emitActionClick(action.id)}
            />
          ))}
        </div>
        
        {/* Patch 历史记录 */}
        <PatchHistory patches={patches} onReplay={replayPatch} />
        
        {/* 调试信息 */}
        {schema && <DebugInfo schema={schema} instanceId={currentInstanceId} wsConnected={true} />}
      </div>
    </div>
  );
}
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
import { getInstanceIdFromUrl, getHighlightFromUrl } from './utils/url';
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
  const { currentInstanceId, schema, loading, error, loadingText } = useSchema();
  const { setSchema, applyPatch, setInstanceId } = useSchemaStore();
  const { emitInstanceSwitch } = useEventEmitter();
  
  // 获取localStorage中的高亮字段
  const highlightField = getHighlightFromUrl(); // 使用这个函数会自动从URL迁移到localStorage
  
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
  
  // WebSocket 接收实时 Patch 和实例切换消息
  useWebSocket(
    // 处理 Patch
    (patch) => {
      console.log('[App] 通过 WebSocket 收到 Patch:', patch);
      applyPatch(patch);
      // 刷新 Patch 历史记录
      loadPatches();
    },
    // 处理实例切换
    (instanceId, schema) => {
      console.log('[App] 通过 WebSocket 切换到实例:', instanceId);
      if (instanceId !== currentInstanceId) {
        // 切换到新实例
        handleInstanceSwitch(instanceId);
        
        // 如果提供了 schema，直接使用它
        if (schema) {
          // schema 来自 WebSocket，类型为 Record<string, any>，在这里做类型断言以满足 setSchema 的 UISchema 参数
          setSchema(schema as any);
        }
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
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif',
      padding: '20px',
      backgroundColor: '#f5f5f5'
    }}>
      {/* 顶部固定区域 - 实例选择器 */}
      <div style={{
        marginBottom: '20px',
        backgroundColor: 'white',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <InstanceSelector 
          currentInstanceId={currentInstanceId} 
          onInstanceSwitch={handleInstanceSwitch}
        />
      </div>
      
      {/* 主要内容区域 - 可滚动 */}
      <div style={{
        flex: 1,
        overflow: 'auto',
        maxWidth: '1200px',
        margin: '0 auto',
        width: '100%'
      }}>
        {/* Schema 渲染容器 */}
        <div style={{
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '30px',
          backgroundColor: 'white',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          textAlign: 'left'
        }}>
          {/* 渲染 Blocks */}
          {schema?.blocks?.map((block) => (
            <BlockRenderer
              key={block.id}
              block={block}
              schema={schema!}  // schema 已经通过 schema? 检查，这里可以安全使用
              highlightField={highlightField}
            />
          ))}
          
          {/* 渲染 Actions */}
          <div style={{ 
            display: 'flex', 
            gap: '10px', 
            justifyContent: 'center',
            marginTop: '20px',
            paddingTop: '15px',
            borderTop: '1px solid #eee'
          }}>
            {schema?.actions?.map((action) => (
              <ActionButton
                key={action.id}
                action={action}
                onApiClick={() => useEventEmitter().emitActionClick(action.id)}
                onNavigate={handleInstanceSwitch}
              />
            ))}
          </div>
          
          {/* 调试信息 - 折叠式 */}
          {schema && (
            <details style={{ 
              marginTop: '20px', 
              paddingTop: '15px',
              borderTop: '1px solid #eee'
            }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold', color: '#666' }}>
                调试信息 (点击展开)
              </summary>
              <div style={{ marginTop: '10px' }}>
                <DebugInfo schema={schema} instanceId={currentInstanceId} wsConnected={true} />
              </div>
            </details>
          )}
          
          {/* Patch 历史记录 - 折叠式 */}
          <details style={{ 
            marginTop: '15px'
          }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold', color: '#666' }}>
              Patch 历史记录 (点击展开)
            </summary>
            <div style={{ marginTop: '10px' }}>
              <PatchHistory patches={patches} onReplay={replayPatch} />
            </div>
          </details>
        </div>
      </div>
    </div>
  );
}
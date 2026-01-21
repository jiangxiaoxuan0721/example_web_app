/** 调试信息组件 */

import { useSchemaStore } from '../store/schemaStore';

interface DebugInfoProps {
  instanceId: string;
  wsConnected?: boolean;
}

export default function DebugInfo({ instanceId, wsConnected }: DebugInfoProps) {
  const schema = useSchemaStore((state) => state.schema);
  const isDev = (import.meta as any).env?.DEV ?? false;

  if (!isDev) {
    return null;
  }

  if (!schema) {
    return null;
  }

  const runtimeMessage = schema.state.runtime?.message;
  const runtimeStatus = schema.state.runtime?.status;

  return (
    <div style={{
      marginTop: '20px',
      padding: '10px',
      background: '#f5f5f5',
      borderRadius: '4px',
      fontSize: '11px',
      textAlign: 'left',
      fontFamily: 'monospace',
      maxHeight: '150px',
      overflow: 'auto',
      border: '1px solid #ddd'
    }}>
      <strong>Debug - Instance: {instanceId}</strong> |{' '}
      <strong>WebSocket: </strong>
      <span style={{ color: wsConnected ? 'green' : 'red' }}>
        {wsConnected ? '✓ Connected' : '✗ Disconnected'}
      </span>

      {/* 显示运行时状态消息 - 紧凑显示 */}
      {runtimeMessage && (
        <div style={{
          marginTop: '8px',
          padding: '6px',
          background: runtimeStatus === 'submitted' ? '#d4edda' : '#fff3cd',
          border: `1px solid ${runtimeStatus === 'submitted' ? '#c3e6cb' : '#ffc107'}`,
          borderRadius: '3px',
          fontSize: '11px'
        }}>
          <span style={{ fontWeight: 'bold' }}>{runtimeStatus}: </span>
          <span>{runtimeMessage}</span>
        </div>
      )}

      <div style={{ marginTop: '8px' }}>
        <strong>State:</strong>
      </div>
      <pre style={{ margin: '4px 0 0', fontSize: '10px', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
        {JSON.stringify(schema.state, null, 2)}
      </pre>
    </div>
  );
}

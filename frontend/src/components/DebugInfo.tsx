/** 调试信息组件 */

import type { UISchema } from '../types/schema';

interface DebugInfoProps {
  schema: UISchema;
  instanceId: string;
}

export default function DebugInfo({ schema, instanceId }: DebugInfoProps) {
  const isDev = (import.meta as any).env?.DEV ?? false;

  if (!isDev) {
    return null;
  }

  return (
    <div style={{
      marginTop: '20px',
      padding: '15px',
      background: '#f5f5f5',
      borderRadius: '4px',
      fontSize: '12px',
      textAlign: 'left',
      fontFamily: 'monospace',
      maxHeight: '200px',
      overflow: 'auto'
    }}>
      <strong>Debug - State (instance: {instanceId}):</strong>
      <pre style={{ margin: '5px 0 0 0' }}>
        {JSON.stringify(schema.state, null, 2)}
      </pre>
    </div>
  );
}

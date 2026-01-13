/** 实例选择器组件 */

interface InstanceSelectorProps {
  currentInstanceId: string;
}

export default function InstanceSelector({ currentInstanceId }: InstanceSelectorProps) {
  return (
    <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
      当前实例: <strong>{currentInstanceId}</strong> |
      <a href="?instanceId=demo" style={{ color: '#007bff', marginLeft: '10px' }}>demo</a> |{' '}
      <a href="?instanceId=counter" style={{ color: '#007bff' }}>counter</a> |{' '}
      <a href="?instanceId=form" style={{ color: '#007bff' }}>form</a>
    </div>
  );
}

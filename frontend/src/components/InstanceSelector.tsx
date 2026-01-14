/** 实例选择器组件 */

interface InstanceSelectorProps {
  currentInstanceId: string;
  onInstanceSwitch?: (newInstanceId: string) => void;
}

export default function InstanceSelector({ currentInstanceId, onInstanceSwitch }: InstanceSelectorProps) {
  const handleInstanceClick = (instanceId: string) => {
    if (onInstanceSwitch) {
      onInstanceSwitch(instanceId);
    } else {
      // Fallback to URL navigation
      window.location.href = `?instanceId=${instanceId}`;
    }
  };

  return (
    <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
      当前实例: <strong>{currentInstanceId}</strong> |
      <button 
        onClick={() => handleInstanceClick('demo')} 
        style={{ 
          background: 'none', 
          border: 'none', 
          color: '#007bff', 
          marginLeft: '10px', 
          cursor: 'pointer',
          textDecoration: 'underline'
        }}
      >
        demo
      </button> |{' '}
      <button 
        onClick={() => handleInstanceClick('counter')} 
        style={{ 
          background: 'none', 
          border: 'none', 
          color: '#007bff', 
          cursor: 'pointer',
          textDecoration: 'underline'
        }}
      >
        counter
      </button> |{' '}
      <button 
        onClick={() => handleInstanceClick('form')} 
        style={{ 
          background: 'none', 
          border: 'none', 
          color: '#007bff', 
          cursor: 'pointer',
          textDecoration: 'underline'
        }}
      >
        form
      </button> |{' '}
      <button 
        onClick={() => handleInstanceClick('json_viewer')} 
        style={{ 
          background: 'none', 
          border: 'none', 
          color: '#007bff', 
          cursor: 'pointer',
          textDecoration: 'underline'
        }}
      >
        json_viewer
      </button>
    </div>
  );
}

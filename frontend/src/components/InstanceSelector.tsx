/** 实例选择器组件 */

import React, { useState, useEffect } from 'react';

interface Instance {
  instance_id: string;
  title?: string;
  description?: string;
  blocks_count?: number;
  actions_count?: number;
}

interface InstancesResponse {
  status: string;
  instances: Instance[];
  total: number;
}

interface InstanceSelectorProps {
  currentInstanceId: string;
  onInstanceSwitch?: (newInstanceId: string) => void;
}

export default function InstanceSelector({ currentInstanceId, onInstanceSwitch }: InstanceSelectorProps) {
  const [instances, setInstances] = useState<Instance[]>([]);
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    // 从后端获取实例列表
    fetch('/ui/instances')
      .then(response => response.json())
      .then((data: InstancesResponse) => {
        if (data.status === 'success') {
          setInstances(data.instances);
        }
      })
      .catch(error => {
        console.error('Failed to fetch instances:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleInstanceClick = async (instanceId: string) => {
    if (instanceId === currentInstanceId) {
      return; // 不切换到当前实例
    }
    
    setSwitching(true);
    
    try {
      if (onInstanceSwitch) {
        await onInstanceSwitch(instanceId);
      } else {
        // Fallback to localStorage update
        localStorage.setItem('instanceId', instanceId);
        // 手动触发页面刷新以加载新实例
        window.location.reload();
      }
    } finally {
      setSwitching(false);
    }
  };

  if (loading) {
    return (
      <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
        加载实例列表中...
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
        加载实例列表中...
      </div>
    );
  }

  return (
    <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
      <span>
        当前实例: <strong>{currentInstanceId}</strong>
        {switching && (
          <span style={{ marginLeft: '10px', color: '#888' }}>
            <span style={{ 
              display: 'inline-block', 
              width: '12px', 
              height: '12px', 
              border: '2px solid #f3f3f3', 
              borderTop: '2px solid #3498db', 
              borderRadius: '50%', 
              animation: 'spin 1s linear infinite',
              marginRight: '5px'
            }}></span>
            切换中...
          </span>
        )}
      </span>
      <div style={{ marginTop: '5px' }}>
        快速切换:
        {instances.map((instance, index) => (
          <React.Fragment key={instance.instance_id}>
            <button 
              onClick={() => handleInstanceClick(instance.instance_id)} 
              disabled={instance.instance_id === currentInstanceId || switching}
              style={{ 
                background: instance.instance_id === currentInstanceId ? '#007bff' : 'none', 
                border: '1px solid #007bff', 
                color: instance.instance_id === currentInstanceId ? 'white' : '#007bff', 
                cursor: instance.instance_id === currentInstanceId || switching ? 'not-allowed' : 'pointer',
                textDecoration: 'none',
                borderRadius: '3px',
                padding: '2px 6px',
                margin: '0 2px',
                fontSize: '12px',
                opacity: switching ? 0.6 : 1
              }}
            >
              {instance.instance_id}
            </button>
          </React.Fragment>
        ))}
      </div>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

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

  const handleInstanceClick = (instanceId: string) => {
    if (onInstanceSwitch) {
      onInstanceSwitch(instanceId);
    } else {
      // Fallback to URL navigation
      window.location.href = `?instanceId=${instanceId}`;
    }
  };

  if (loading) {
    return (
      <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
        加载实例列表中...
      </div>
    );
  }

  return (
    <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
      当前实例: <strong>{currentInstanceId}</strong> |
      {instances.map((instance, index) => (
        <React.Fragment key={instance.instance_id}>
          <button 
            onClick={() => handleInstanceClick(instance.instance_id)} 
            style={{ 
              background: 'none', 
              border: 'none', 
              color: '#007bff', 
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            {instance.instance_id}
          </button>
          {index < instances.length - 1 ? ' | ' : ''}
        </React.Fragment>
      ))}
    </div>
  );
}

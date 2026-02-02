/** 实例选择器组件 */

import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import DebugModal from './DebugModal';
import PatchHistory from './PatchHistory';

interface Instance {
  instance_name: string;
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
  patches?: any[];
  onReplay?: (patchId: number) => void;
}

export default function InstanceSelector({ currentInstanceId, onInstanceSwitch, patches = [], onReplay }: InstanceSelectorProps) {
  const [instances, setInstances] = useState<Instance[]>([]);
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);
  const [showDebugModal, setShowDebugModal] = useState(false);
  const [showPatchHistory, setShowPatchHistory] = useState(false);

  // 获取 WebSocket 连接状态（仅用于显示）
  const { connected: wsConnected } = useWebSocket(() => { }, () => { });

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
    <>
      <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowDebugModal(true)}
            style={{
              padding: '6px 12px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500',
              transition: 'background-color 0.2s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#5a6268'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#6c757d'}
          >
            🔧 调试
          </button>
          <button
            onClick={() => setShowPatchHistory(!showPatchHistory)}
            style={{
              padding: '6px 12px',
              backgroundColor: showPatchHistory ? '#28a745' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500',
              transition: 'background-color 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = showPatchHistory ? '#218838' : '#0056b3';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = showPatchHistory ? '#28a745' : '#007bff';
            }}
          >
            {showPatchHistory ? '📜 隐藏' : '📜 重放'}
          </button>
        </div>
      </div>
      <div style={{ marginTop: '5px' }}>
        快速切换:
        {instances.map((instance, index) => (
          <React.Fragment key={instance.instance_name}>
            <button
              onClick={() => handleInstanceClick(instance.instance_name)}
              disabled={instance.instance_name === currentInstanceId || switching}
              style={{
                background: instance.instance_name === currentInstanceId ? '#007bff' : 'none',
                border: '1px solid #007bff',
                color: instance.instance_name === currentInstanceId ? 'white' : '#007bff',
                cursor: instance.instance_name === currentInstanceId || switching ? 'not-allowed' : 'pointer',
                textDecoration: 'none',
                borderRadius: '3px',
                padding: '2px 6px',
                margin: '0 2px',
                fontSize: '12px',
                opacity: switching ? 0.6 : 1
              }}
            >
              {instance.instance_name}
            </button>
          </React.Fragment>
        ))}
      </div>

      {/* Patch 历史记录面板 */}
      {showPatchHistory && (
        <div style={{
          marginTop: '15px',
          padding: '16px',
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        }}>
          <PatchHistory patches={patches} onReplay={onReplay || (() => { })} />
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      {/* 调试模态框 */}
      {showDebugModal && (
        <DebugModal
          instanceId={currentInstanceId}
          wsConnected={wsConnected}
          onClose={() => setShowDebugModal(false)}
        />
      )}
    </>
  );
}

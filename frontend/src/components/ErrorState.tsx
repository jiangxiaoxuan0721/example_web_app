/** 错误状态组件 */

import { useState, useEffect } from 'react';

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

interface ErrorStateProps {
  error: string;
}

export default function ErrorState({ error }: ErrorStateProps) {
  const [instances, setInstances] = useState<Instance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
    localStorage.setItem('instanceId', instanceId);
    window.location.href = `?instanceId=${instanceId}`;
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '20px',
      background: 'linear-gradient(135deg,rgb(156, 158, 168) 0%,rgb(91, 86, 97) 100%)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '16px',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        maxWidth: '600px',
        width: '100%',
        textAlign: 'center'
      }}>
        {/* 错误图标 */}
        <div style={{
          width: '80px',
          height: '80px',
          margin: '0 auto 20px',
          backgroundColor: '#fee2e2',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>

        {/* 错误标题 */}
        <h2 style={{
          margin: '0 0 12px',
          color: '#1f2937',
          fontSize: '24px',
          fontWeight: '700'
        }}>
          实例未找到
        </h2>

        {/* 错误信息 */}
        <p style={{
          margin: '0 0 30px',
          color: '#6b7280',
          fontSize: '16px',
          lineHeight: '1.6'
        }}>
          {error}
        </p>

        {/* 实例列表 */}
        <div style={{ textAlign: 'left' }}>
          <p style={{
            margin: '0 0 16px',
            color: '#374151',
            fontSize: '15px',
            fontWeight: '600'
          }}>
            {loading ? '📋 加载可用实例...' : `📋 可用实例 (${instances.length})`}
          </p>

          {loading ? (
            <div style={{
              padding: '20px',
              backgroundColor: '#f9fafb',
              borderRadius: '8px',
              textAlign: 'center',
              color: '#9ca3af'
            }}>
              <div style={{
                display: 'inline-block',
                width: '24px',
                height: '24px',
                border: '3px solid #e5e7eb',
                borderTop: '3px solid #6366f1',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
            </div>
          ) : instances.length === 0 ? (
            <div style={{
              padding: '20px',
              backgroundColor: '#fef3c7',
              borderRadius: '8px',
              color: '#92400e',
              fontSize: '14px'
            }}>
              暂无可用实例
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gap: '10px',
              maxHeight: '400px',
              overflowY: 'auto',
              padding: '4px'
            }}>
              {instances.map((instance) => (
                <button
                  key={instance.instance_id}
                  onClick={() => handleInstanceClick(instance.instance_id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px 16px',
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    textAlign: 'left',
                    width: '100%'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#6366f1';
                    e.currentTarget.style.backgroundColor = '#f5f3ff';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(99, 102, 241, 0.15)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e5e7eb';
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#1f2937',
                      marginBottom: '4px'
                    }}>
                      {instance.instance_id}
                    </div>
                    {instance.title && (
                      <div style={{
                        fontSize: '13px',
                        color: '#6b7280',
                        marginBottom: '4px'
                      }}>
                        {instance.title}
                      </div>
                    )}
                    {instance.description && (
                      <div style={{
                        fontSize: '12px',
                        color: '#9ca3af'
                      }}>
                        {instance.description}
                      </div>
                    )}
                  </div>
                  {(instance.blocks_count !== undefined || instance.actions_count !== undefined) && (
                    <div style={{
                      display: 'flex',
                      gap: '8px',
                      marginLeft: '12px'
                    }}>
                      {instance.blocks_count !== undefined && (
                        <span style={{
                          fontSize: '11px',
                          padding: '3px 8px',
                          backgroundColor: '#dbeafe',
                          color: '#1e40af',
                          borderRadius: '12px',
                          fontWeight: '500'
                        }}>
                          📦 {instance.blocks_count}
                        </span>
                      )}
                      {instance.actions_count !== undefined && (
                        <span style={{
                          fontSize: '11px',
                          padding: '3px 8px',
                          backgroundColor: '#dcfce7',
                          color: '#166534',
                          borderRadius: '12px',
                          fontWeight: '500'
                        }}>
                          ⚡ {instance.actions_count}
                        </span>
                      )}
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
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

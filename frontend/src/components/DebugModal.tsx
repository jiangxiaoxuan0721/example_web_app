/** 调试模态框组件 */

import React, { useState } from 'react';
import { useSchemaStore } from '../store/schemaStore';

interface DebugModalProps {
  instanceId: string;
  wsConnected: boolean;
  onClose: () => void;
}

export default function DebugModal({ instanceId, wsConnected, onClose }: DebugModalProps) {
  const schema = useSchemaStore((state) => state.schema);
  const [activeTab, setActiveTab] = useState<'debug' | 'schema'>('debug');
  const [copied, setCopied] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const debugInfo = {
    instanceId,
    wsConnected,
    blocksCount: schema?.blocks?.length || 0,
    actionsCount: schema?.actions?.length || 0,
    stateParams: schema?.state?.params || null,
    timestamp: new Date().toISOString()
  };

  const debugInfoText = JSON.stringify(debugInfo, null, 2);
  const schemaText = JSON.stringify(schema, null, 2);

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '800px',
          height: '600px',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* 头部 */}
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid #e5e7eb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#f9fafb'
          }}
        >
          <h3
            style={{
              margin: 0,
              fontSize: '18px',
              fontWeight: 'bold',
              color: '#333'
            }}
          >
            调试面板
          </h3>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#666',
              padding: '0 8px',
              lineHeight: 1
            }}
          >
            ×
          </button>
        </div>

        {/* 标签页 */}
        <div
          style={{
            display: 'flex',
            borderBottom: '1px solid #e5e7eb'
          }}
        >
          <button
            onClick={() => setActiveTab('debug')}
            style={{
              flex: 1,
              padding: '12px 20px',
              border: 'none',
              borderBottom: activeTab === 'debug' ? '2px solid #007bff' : '2px solid transparent',
              backgroundColor: activeTab === 'debug' ? '#fff' : '#f9fafb',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: activeTab === 'debug' ? 'bold' : 'normal',
              color: activeTab === 'debug' ? '#007bff' : '#666',
              transition: 'all 0.2s ease'
            }}
          >
            调试信息
          </button>
          <button
            onClick={() => setActiveTab('schema')}
            style={{
              flex: 1,
              padding: '12px 20px',
              border: 'none',
              borderBottom: activeTab === 'schema' ? '2px solid #007bff' : '2px solid transparent',
              backgroundColor: activeTab === 'schema' ? '#fff' : '#f9fafb',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: activeTab === 'schema' ? 'bold' : 'normal',
              color: activeTab === 'schema' ? '#007bff' : '#666',
              transition: 'all 0.2s ease'
            }}
          >
            实例 Schema
          </button>
        </div>

        {/* 内容区域 */}
        <div
          style={{
            flex: 1,
            overflow: 'auto',
            position: 'relative'
          }}
        >
          {/* 复制按钮 */}
          <button
            onClick={() => handleCopy(activeTab === 'debug' ? debugInfoText : schemaText)}
            style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '6px 12px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '13px',
              zIndex: 10,
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            {copied ? '✓ 已复制' : '📋 复制'}
          </button>

          {/* 调试信息标签页 */}
          {activeTab === 'debug' && (
            <pre
              style={{
                margin: 0,
                padding: '20px',
                fontSize: '12px',
                fontFamily: 'Consolas, Monaco, Courier New, monospace',
                lineHeight: '1.5',
                color: '#333',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}
            >
              {debugInfoText}
            </pre>
          )}

          {/* Schema 标签页 */}
          {activeTab === 'schema' && (
            <pre
              style={{
                margin: 0,
                padding: '20px',
                fontSize: '12px',
                fontFamily: 'Consolas, Monaco, Courier New, monospace',
                lineHeight: '1.5',
                color: '#333',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}
            >
              {schemaText}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

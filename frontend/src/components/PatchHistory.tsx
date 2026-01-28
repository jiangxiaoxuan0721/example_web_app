/** Patch 历史记录组件 */

import { useState } from 'react';
import { PatchRecord } from '../types/schema';

interface PatchHistoryProps {
  patches: PatchRecord[];
  onReplay: (patchId: number) => void;
}

export default function PatchHistory({ patches, onReplay }: PatchHistoryProps) {
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  if (patches.length === 0) {
    return null;
  }

  const handleCopy = async (patchId: number, patchText: string) => {
    try {
      await navigator.clipboard.writeText(patchText);
      setCopiedId(patchId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('复制失败:', err);
    }
  };

  const handleToggleExpand = (patchId: number) => {
    setExpandedId(expandedId === patchId ? null : patchId);
  };

  const formatPatch = (patch: any): string => {
    return JSON.stringify(patch, null, 2);
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div style={{
      padding: '16px',
      backgroundColor: '#fafafa',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      fontSize: '13px',
      textAlign: 'left'
    }}>
      {/* 标题区域 */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '12px',
        paddingBottom: '8px',
        borderBottom: '2px solid #e5e7eb'
      }}>
        <strong style={{
          fontSize: '15px',
          color: '#333',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span style={{ fontSize: '16px' }}>📜</span>
          Patch 历史记录
        </strong>
        <span style={{
          fontSize: '12px',
          color: '#666',
          backgroundColor: '#e5e7eb',
          padding: '2px 8px',
          borderRadius: '4px'
        }}>
          共 {patches.length} 条
        </span>
      </div>

      {/* Patch 列表 - 限制高度 */}
      <div style={{
        maxHeight: '300px',
        overflowY: 'auto',
        overflowX: 'hidden',
        paddingRight: '4px'
      }}>
        {patches.map((patchRecord) => {
          const patchText = formatPatch(patchRecord.patch);
          const isExpanded = expandedId === patchRecord.id;

          return (
            <div
              key={patchRecord.id}
              style={{
                marginBottom: '10px',
                padding: '12px',
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#007bff';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 123, 255, 0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e5e7eb';
                e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
              }}
              onClick={() => handleToggleExpand(patchRecord.id)}
            >
              {/* Patch 头部 */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  flex: 1
                }}>
                  <span style={{
                    fontSize: '16px',
                    transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                    transition: 'transform 0.2s ease'
                  }}>
                    ▶
                  </span>
                  <div>
                    <div style={{
                      fontWeight: 'bold',
                      fontSize: '13px',
                      color: '#333',
                      marginBottom: '2px'
                    }}>
                      Patch #{patchRecord.id}
                    </div>
                    <div style={{
                      fontSize: '11px',
                      color: '#666'
                    }}>
                      {formatDate(patchRecord.timestamp)}
                    </div>
                  </div>
                </div>

                {/* 操作按钮 */}
                <div style={{
                  display: 'flex',
                  gap: '6px'
                }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopy(patchRecord.id, patchText);
                    }}
                    style={{
                      padding: '4px 8px',
                      backgroundColor: copiedId === patchRecord.id ? '#10b981' : '#6c757d',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '11px',
                      transition: 'background-color 0.2s ease',
                      minWidth: '60px'
                    }}
                    onMouseEnter={(e) => {
                      if (copiedId !== patchRecord.id) {
                        e.currentTarget.style.backgroundColor = '#5a6268';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (copiedId !== patchRecord.id) {
                        e.currentTarget.style.backgroundColor = '#6c757d';
                      }
                    }}
                  >
                    {copiedId === patchRecord.id ? '✓ 已复制' : '📋 复制'}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onReplay(patchRecord.id);
                    }}
                    style={{
                      padding: '4px 12px',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '11px',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#0056b3';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#007bff';
                    }}
                  >
                    ▶ 重放
                  </button>
                </div>
              </div>

              {/* Patch 内容 - 可展开/折叠 */}
              {isExpanded && (
                <div style={{
                  marginTop: '10px',
                  paddingTop: '10px',
                  borderTop: '1px solid #e5e7eb'
                }}>
                  <pre style={{
                    margin: '0',
                    fontSize: '11px',
                    fontFamily: 'Consolas, Monaco, Courier New, monospace',
                    lineHeight: '1.4',
                    color: '#333',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    backgroundColor: '#f8f9fa',
                    padding: '8px',
                    borderRadius: '4px',
                    maxHeight: '150px',
                    overflowY: 'auto'
                  }}>
                    {patchText}
                  </pre>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 滚动条样式 */}
      <style>{`
        div::-webkit-scrollbar {
          width: 6px;
        }
        div::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 3px;
        }
        div::-webkit-scrollbar-thumb {
          background: #c1c1c1;
          border-radius: 3px;
        }
        div::-webkit-scrollbar-thumb:hover {
          background: #a1a1a1;
        }
      `}</style>
    </div>
  );
}


/** 模态框组件 */

import { useEffect } from 'react';

interface ModalProps {
  visible: boolean;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  onCancel: () => void;
  onOk?: () => void;
  okText?: string;
  cancelText?: string;
  width?: number;
  maskClosable?: boolean;
}

export default function Modal({
  visible,
  title,
  children,
  footer,
  onCancel,
  onOk,
  okText = '确定',
  cancelText = '取消',
  width = 520,
  maskClosable = true
}: ModalProps) {
  // 禁止背景滚动
  useEffect(() => {
    if (visible) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [visible]);

  if (!visible) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.45)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        ...(maskClosable && {
          cursor: 'pointer'
        })
      }}
      onClick={maskClosable ? onCancel : undefined}
    >
      <div
        style={{
          background: '#fff',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          width: width,
          maxWidth: '90vw',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          ...(maskClosable && {
            cursor: 'default'
          })
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* 标题 */}
        {title && (
          <div
            style={{
              padding: '16px 24px',
              borderBottom: '1px solid #f0f0f0',
              fontSize: '16px',
              fontWeight: '600',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <span>{title}</span>
            <button
              onClick={onCancel}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '20px',
                cursor: 'pointer',
                color: '#999',
                padding: 0,
                lineHeight: 1
              }}
            >
              ×
            </button>
          </div>
        )}

        {/* 内容 */}
        <div
          style={{
            padding: '24px',
            overflow: 'auto',
            flex: 1
          }}
        >
          {children}
        </div>

        {/* 底部操作栏 */}
        {footer !== undefined ? (
          footer
        ) : onOk && onCancel && (
          <div
            style={{
              padding: '16px 24px',
              borderTop: '1px solid #f0f0f0',
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '12px'
            }}
          >
            <button
              onClick={onCancel}
              style={{
                padding: '8px 24px',
                borderRadius: '4px',
                border: '1px solid #d9d9d9',
                background: '#fff',
                color: '#666',
                fontSize: '14px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#f5f5f5';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#fff';
              }}
            >
              {cancelText}
            </button>
            <button
              onClick={onOk}
              style={{
                padding: '8px 24px',
                borderRadius: '4px',
                border: 'none',
                background: '#007bff',
                color: '#fff',
                fontSize: '14px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#0056b3';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#007bff';
              }}
            >
              {okText}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

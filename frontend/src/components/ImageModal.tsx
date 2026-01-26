/** 图片查看器模态框组件 - 用于全屏查看图片和HTML内容 */

import { useEffect } from 'react';

interface ImageModalProps {
  visible: boolean;
  url: string;
  title?: string;
  alt?: string;
  onClose: () => void;
}

export default function ImageModal({ visible, url, title, alt, onClose }: ImageModalProps) {
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

  // 检查是否为HTML链接
  const isHtmlLink = () => {
    if (!url) return false;
    return /\.(html?)(\?.*)?$/i.test(url) ||
           (url.includes('wave_') && url.includes('.html')) ||
           url.endsWith('.html') ||
           url.indexOf('.html?') !== -1;
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.9)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 10000,
        cursor: 'pointer'
      }}
      onClick={onClose}
    >
      {/* 内容区域 */}
      {isHtmlLink() ? (
        <iframe
          src={url}
          title={title || alt}
          style={{
            position: 'absolute',
            top: '2.5%',
            left: '2.5%',
            width: '95%',
            height: '95%',
            border: 'none',
            borderRadius: '8px',
            backgroundColor: 'white',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            cursor: 'default'
          }}
          onClick={(e) => e.stopPropagation()}
        />
      ) : (
        <img
          src={url}
          alt={alt || title}
          style={{
            maxWidth: '90%',
            maxHeight: '90%',
            objectFit: 'contain',
            borderRadius: '8px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            cursor: 'default'
          }}
          onClick={(e) => e.stopPropagation()}
        />
      )}

      {/* 关闭按钮 */}
      <button
        onClick={onClose}
        style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          width: '48px',
          height: '48px',
          background: 'rgba(255, 255, 255, 0.15)',
          color: 'white',
          border: 'none',
          borderRadius: '50%',
          fontSize: '28px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
        }}
      >
        ×
      </button>

      {/* 标题（如果有） */}
      {title && (
        <div
          style={{
            position: 'absolute',
            bottom: '30px',
            left: '50%',
            transform: 'translateX(-50%)',
            color: 'white',
            fontSize: '16px',
            fontWeight: '500',
            textShadow: '0 2px 8px rgba(0,0,0,0.5)',
            pointerEvents: 'none'
          }}
        >
          {title}
        </div>
      )}

      {/* 提示文本 */}
      <div
        style={{
          position: 'absolute',
          top: '30px',
          left: '20px',
          color: 'rgba(255, 255, 255, 0.6)',
          fontSize: '12px',
          pointerEvents: 'none'
        }}
      >
        点击背景或 × 关闭
      </div>
    </div>
  );
}

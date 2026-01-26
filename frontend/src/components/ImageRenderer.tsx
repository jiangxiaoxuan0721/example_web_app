/**
 * 增强版图片渲染器 - 支持多种功能，包括HTML内容、全屏查看、下载等
 */

import React, { useState, useRef } from 'react';

interface ImageProps {
  source: string;               // 图片URL、链接或base64数据
  title?: string;               // 图片标题
  subtitle?: string;            // 图片副标题
  width?: string | number;      // 图片宽度
  height?: string | number;     // 图片高度
  fit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';  // 图片适应方式
  lazy?: boolean;              // 是否懒加载
  fallback?: string;            // 加载失败时的备用图片
  alt?: string;                // 图片alt属性
  showFullscreen?: boolean;     // 是否显示全屏按钮
  showDownload?: boolean;       // 是否显示下载按钮
  onLoad?: () => void;         // 加载完成回调
  onError?: () => void;        // 加载失败回调
  className?: string;          // 自定义CSS类名
  style?: React.CSSProperties;  // 自定义样式
}

export default function ImageRenderer({
  source,
  title,
  subtitle,
  width = '100%',
  height = 'auto',
  fit = 'contain',
  lazy = false,
  fallback,
  alt,
  showFullscreen = true,
  showDownload = true,
  onLoad,
  onError,
  className = '',
  style = {}
}: ImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [showToolbar, setShowToolbar] = useState(false);
  const [fullscreenOpen, setFullscreenOpen] = useState(false);
  const [retryKey, setRetryKey] = useState(0); // 用于重试加载

  const imageRef = useRef<HTMLImageElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // 检查是否为HTML链接
  const isHtmlLink = () => {
    if (!source) return false;
    return /\.(html?)(\?.*)?$/i.test(source) ||
      (source.includes('wave_') && source.includes('.html')) ||
      source.endsWith('.html') ||
      source.indexOf('.html?') !== -1;
  };

  // 处理加载成功
  const handleLoad = () => {
    setIsLoaded(true);
    setHasError(false);
    if (onLoad) onLoad();
  };

  // 处理加载失败
  const handleError = () => {
    setHasError(true);
    setIsLoaded(false);

    // 如果有备用图片且不是HTML链接，则尝试加载备用图片
    if (fallback && !isHtmlLink() && imageRef.current) {
      imageRef.current.src = fallback;
    } else {
      if (onError) onError();
    }
  };

  // 重试加载
  const handleRetry = () => {
    setHasError(false);
    setIsLoaded(false);
    setRetryKey(prev => prev + 1); // 更新key以强制重新加载
  };

  // 打开全屏
  const openFullscreen = () => {
    if (hasError) return;
    setFullscreenOpen(true);
  };

  // 下载图片/HTML
  const handleDownload = () => {
    if (hasError) return;

    if (isHtmlLink()) {
      // 对于HTML链接，直接在新窗口打开
      window.open(source, '_blank');
    } else if (imageRef.current) {
      // 创建下载链接
      const link = document.createElement('a');
      link.href = imageRef.current.src;
      link.download = title || 'image';
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // 渲染图片/iframe
  const renderContent = () => {
    if (isHtmlLink()) {
      return (
        <div
          className="iframe-wrapper"
          style={{
            position: 'relative',
            width: '100%',
            paddingTop: '56.25%', // 16:9宽高比
            overflow: 'hidden'
          }}
        >
          <iframe
            key={retryKey}
            ref={iframeRef}
            src={source}
            onLoad={handleLoad}
            onError={handleError}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              border: 'none',
              borderRadius: '4px'
            }}
            title={title || alt}
          />
        </div>
      );
    } else {
      return (
        <img
          key={retryKey}
          ref={imageRef}
          src={source}
          alt={alt || title}
          onLoad={handleLoad}
          onError={handleError}
          loading={lazy ? 'lazy' : undefined}
          style={{
            width: '100%',
            height: '100%',
            objectFit: fit,
            cursor: isLoaded && !hasError ? 'pointer' : 'default'
          }}
          onClick={isLoaded && !hasError ? openFullscreen : undefined}
        />
      );
    }
  };

  // 渲染加载指示器
  const renderLoading = () => (
    <div className="picture-loading" style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#f5f5f5',
      zIndex: 2
    }}>
      <div className="loading-spinner" style={{
        width: '32px',
        height: '32px',
        border: '3px solid #f3f3f3',
        borderTop: '3px solid #1890ff',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        marginBottom: '12px'
      }}></div>
      <div className="loading-text" style={{
        fontSize: '14px',
        color: '#666'
      }}>加载中...</div>
    </div>
  );

  // 渲染错误指示器
  const renderError = () => (
    <div className="picture-error" style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#fafafa',
      zIndex: 2
    }}>
      <div className="error-icon" style={{
        fontSize: '32px',
        marginBottom: '12px',
        color: '#f5222d'
      }}>⚠</div>
      <div className="error-text" style={{
        fontSize: '14px',
        color: '#666',
        marginBottom: '16px'
      }}>图片加载失败</div>
      {fallback && !isHtmlLink() && (
        <button
          className="retry-btn"
          onClick={handleRetry}
          style={{
            padding: '6px 16px',
            background: '#1890ff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >重试</button>
      )}
    </div>
  );

  // 渲染工具栏
  const renderToolbar = () => {
    if (!isLoaded || hasError || (!showFullscreen && !showDownload)) return null;

    return (
      <div
        className="picture-toolbar"
        style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          display: 'flex',
          gap: '8px',
          zIndex: 3,
          opacity: showToolbar ? 1 : 0.7,
          transition: 'opacity 0.3s ease'
        }}
      >
        {showFullscreen && (
          <button
            className="toolbar-btn fullscreen-btn"
            onClick={openFullscreen}
            title="全屏查看"
            style={{
              width: '36px',
              height: '36px',
              background: 'rgba(0, 0, 0, 0.6)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >⛶</button>
        )}
        {showDownload && (
          <button
            className="toolbar-btn download-btn"
            onClick={handleDownload}
            title="下载"
            style={{
              width: '36px',
              height: '36px',
              background: 'rgba(0, 0, 0, 0.6)',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >↓</button>
        )}
      </div>
    );
  };

  // 渲染全屏模态框
  const renderFullscreen = () => {
    if (!fullscreenOpen) return null;

    return (
      <div
        className="picture-fullscreen-modal"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'rgba(0, 0, 0, 0.9)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}
        onClick={() => setFullscreenOpen(false)}
      >
        {isHtmlLink() ? (
          <iframe
            className="html-fullscreen-content"
            src={source}
            style={{
              border: 'none',
              borderRadius: '4px',
              width: '95%',
              height: '95%',
              backgroundColor: 'white',
              boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
            }}
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <img
            className="fullscreen-image"
            src={source}
            alt={alt || title}
            style={{
              maxWidth: '90%',
              maxHeight: '90%',
              objectFit: 'contain',
              borderRadius: '4px'
            }}
            onClick={(e) => e.stopPropagation()}
          />
        )}
        <button
          className="fullscreen-close"
          onClick={() => setFullscreenOpen(false)}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            width: '40px',
            height: '40px',
            background: 'rgba(255, 255, 255, 0.2)',
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            fontSize: '24px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >×</button>
      </div>
    );
  };

  return (
    <div
      className={`picture-container ${isLoaded ? 'loaded' : ''} ${className}`}
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        borderRadius: '8px',
        background: '#f8f9fa',
        transition: 'all 0.3s ease',
        width,
        ...style
      }}
      onMouseEnter={() => setShowToolbar(true)}
      onMouseLeave={() => setShowToolbar(false)}
    >
      {/* 标题区域 */}
      {(title || subtitle) && (
        <div className="picture-header" style={{
          padding: '16px',
          background: '#fff',
          borderBottom: '1px solid #e8e8e8'
        }}>
          {title && (
            <h3 className="picture-title" style={{
              fontSize: '18px',
              fontWeight: 600,
              margin: '0 0 4px 0',
              color: '#333'
            }}>{title}</h3>
          )}
          {subtitle && (
            <div className="picture-subtitle" style={{
              fontSize: '14px',
              color: '#666'
            }}>{subtitle}</div>
          )}
        </div>
      )}

      {/* 内容包装器 */}
      <div
        className="picture-wrapper"
        style={{
          position: 'relative',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height
        }}
      >
        {/* 图片/iframe内容 */}
        {renderContent()}

        {/* 加载指示器 */}
        {!isLoaded && !hasError && renderLoading()}

        {/* 错误指示器 */}
        {hasError && renderError()}

        {/* 工具栏 */}
        {renderToolbar()}
      </div>

      {/* 全屏模态框 */}
      {renderFullscreen()}

      {/* 添加CSS动画 */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }
          .picture-container.loaded .picture-image {
            animation: fadeIn 0.5s ease;
          }
          .picture-fullscreen-modal {
            animation: fadeIn 0.3s ease;
          }
        `
      }} />
    </div>
  );
}
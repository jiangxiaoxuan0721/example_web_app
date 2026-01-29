/**
 * 富内容渲染器 - 专门用于渲染HTML内容，支持图片全屏查看
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import type { UISchema } from '../types/schema';
import { renderTemplate } from '../utils/template';
import ImageModal from './ImageModal';

interface RichContentProps {
  html?: string;          // HTML内容
  schema?: UISchema | null; // 完整的 schema，用于模板渲染
  width?: string | number; // 容器宽度
  height?: string | number; // 容器高度
  maxHeight?: string | number; // 最大高度
  className?: string;      // 自定义CSS类名
  style?: React.CSSProperties; // 自定义样式
}

export default function RichContentRenderer({
  html,
  schema,
  width = "100%",
  height,
  maxHeight = "600px",
  className = "",
  style = {}
}: RichContentProps) {
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [currentImage, setCurrentImage] = useState<{ url: string; title?: string; alt?: string } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 为HTML中的所有图片添加点击事件
  useEffect(() => {
    if (!html || !containerRef.current) return;

    const container = containerRef.current;
    const images = container.querySelectorAll('img');

    const handleImageClick = (e: MouseEvent) => {
      const target = e.target as HTMLImageElement;
      if (target.tagName === 'IMG') {
        e.preventDefault();
        e.stopPropagation();
        const alt = target.alt || '';
        const title = target.title || '';
        setCurrentImage({ url: target.src, title, alt });
        setImageModalOpen(true);
      }
    };

    images.forEach(img => {
      img.style.cursor = 'pointer';
      img.addEventListener('click', handleImageClick);
    });

    return () => {
      images.forEach(img => {
        img.removeEventListener('click', handleImageClick);
      });
    };
  }, [html]);

  // 渲染 HTML 内容中的模板
  const renderedHtml = useMemo(() => renderTemplate(html, schema ?? null), [html, schema]);

  // 如果没有内容，返回空
  if (!html) {
    return <div className="rich-content-empty">无内容</div>;
  }

  return (
    <>
      <div
        ref={containerRef}
        className={`rich-html-container ${className}`}
        style={{
          width,
          padding: '16px',
          height,
          maxHeight,
          overflow: 'auto',
          boxSizing: 'border-box',
          // 确保内容不会溢出容器
          wordWrap: 'break-word',
          overflowWrap: 'break-word',
          // 为表格等元素设置滚动
          overflowX: 'auto',
          // 设置最大宽度以防止内容溢出
          maxWidth: '100%',
          marginBottom: '16px',
          ...style
        }}
        dangerouslySetInnerHTML={{ __html: renderedHtml }}
      />
      {/* 图片模态框 */}
      {currentImage && (
        <ImageModal
          visible={imageModalOpen}
          url={currentImage.url}
          title={currentImage.title}
          alt={currentImage.alt}
          onClose={() => {
            setImageModalOpen(false);
            setCurrentImage(null);
          }}
        />
      )}
    </>
  );
}

// 便捷的HTML渲染组件
export function HTMLRenderer({
  html,
  ...props
}: RichContentProps) {
  return <RichContentRenderer html={html} {...props} />;
}
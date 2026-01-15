/**
 * 富内容渲染器 - 专门用于渲染HTML内容
 */

import React from 'react';
import { Card } from './index';

interface RichContentProps {
  html?: string;          // HTML内容
  width?: string | number; // 容器宽度
  height?: string | number; // 容器高度
  maxHeight?: string | number; // 最大高度
  className?: string;      // 自定义CSS类名
  style?: React.CSSProperties; // 自定义样式
}

export default function RichContentRenderer({
  html,
  width = "100%",
  height,
  maxHeight = "600px",
  className = "",
  style = {}
}: RichContentProps) {
  // 如果没有内容，返回空
  if (!html) {
    return <div className="rich-content-empty">无内容</div>;
  }

  return (
    <Card style={{
      width,
      marginBottom: '16px',
      ...style
    }}>
      <div
        className={`rich-html-container ${className}`}
        style={{
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
          maxWidth: '100%'
        }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </Card>
  );
}

// 便捷的HTML渲染组件
export function HTMLRenderer({
  html,
  ...props
}: RichContentProps) {
  return <RichContentRenderer html={html} {...props} />;
}
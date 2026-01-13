/** Markdown 渲染组件 */

import { useState, useEffect } from 'react';

interface MarkdownProps {
  content: string;
  className?: string;
}

export default function Markdown({ content, className }: MarkdownProps) {
  const [renderedContent, setRenderedContent] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const renderMarkdown = async () => {
      try {
        setLoading(true);

        // 简单的 Markdown 解析（如果需要更强大的功能，可以集成 marked.js 或 react-markdown）
        let result = content
          // 标题
          .replace(/^### (.*$)/gm, '<h3 style="margin: 1em 0 0.5em 0; font-size: 1.5em; font-weight: 600;">$1</h3>')
          .replace(/^## (.*$)/gm, '<h2 style="margin: 1em 0 0.5em 0; font-size: 1.75em; font-weight: 600;">$1</h2>')
          .replace(/^# (.*$)/gm, '<h1 style="margin: 1em 0 0.5em 0; font-size: 2em; font-weight: 600;">$1</h1>')
          // 粗体
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          // 斜体
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          // 代码
          .replace(/`(.*?)`/g, '<code style="background: #f4f4f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 0.9em;">$1</code>')
          // 代码块
          .replace(/```([\s\S]*?)```/g, '<pre style="background: #f6f8fa; padding: 16px; border-radius: 8px; overflow: auto;"><code>$1</code></pre>')
          // 链接
          .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" style="color: #007bff; text-decoration: underline;">$1</a>')
          // 列表
          .replace(/^\- (.*$)/gm, '<li style="margin: 4px 0;">$1</li>')
          // 换行
          .replace(/\n/g, '<br>');

        // 包装列表项
        if (result.includes('<li>')) {
          result = result.replace(/(<li.*<\/li>)/s, '<ul style="padding-left: 20px; margin: 8px 0;">$1</ul>');
        }

        setRenderedContent(result);
      } catch (err) {
        console.error('Markdown 渲染失败:', err);
        setRenderedContent(content);
      } finally {
        setLoading(false);
      }
    };

    renderMarkdown();
  }, [content]);

  if (loading) {
    return <div style={{ color: '#999' }}>加载中...</div>;
  }

  return (
    <div
      className={className}
      style={{
        lineHeight: '1.6',
        color: '#333'
      }}
      dangerouslySetInnerHTML={{ __html: renderedContent }}
    />
  );
}

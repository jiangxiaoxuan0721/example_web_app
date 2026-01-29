/** 卡片容器组件 */

import React from 'react';

interface CardProps {
  title?: string | React.ReactNode;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export default function Card({ title, children, style }: CardProps) {
  return (
    <div
      style={{
        border: '1px solid #ccc',
        borderRadius: '8px',
        padding: '20px',
        background: '#fff',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        ...style
      }}
    >
      {title && (
        <h2
          style={{
            marginTop: 0,
            marginBottom: '20px',
            fontSize: '18px',
            color: '#333'
          }}
        >
          {title}
        </h2>
      )}
      {children}
    </div>
  );
}

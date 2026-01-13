/** 代码块显示组件 */

interface CodeBlockProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
}

export default function CodeBlock({ code, language = 'text', showLineNumbers = false }: CodeBlockProps) {
  const lines = code.split('\n');

  return (
    <div
      style={{
        background: '#282c34',
        borderRadius: '8px',
        padding: '16px',
        overflow: 'auto',
        fontSize: '14px',
        fontFamily: 'Consolas, Monaco, "Courier New", monospace',
        position: 'relative'
      }}
    >
      {/* 语言标签 */}
      {language && (
        <div
          style={{
            position: 'absolute',
            top: '8px',
            right: '8px',
            background: '#3b4252',
            color: '#abb2bf',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
        >
          {language}
        </div>
      )}

      {/* 代码内容 */}
      <pre
        style={{
          margin: 0,
          padding: showLineNumbers ? '0 12px 0 48px' : 0,
          color: '#abb2bf',
          lineHeight: '1.6'
        }}
      >
        {showLineNumbers ? (
          <div style={{ position: 'relative' }}>
            {/* 行号 */}
            <div
              style={{
                position: 'absolute',
                left: 0,
                top: 0,
                width: '40px',
                textAlign: 'right',
                color: '#5c6370',
                paddingRight: '8px',
                userSelect: 'none'
              }}
            >
              {lines.map((_, index) => (
                <div key={index + 1} style={{ lineHeight: '1.6' }}>
                  {index + 1}
                </div>
              ))}
            </div>
            {/* 代码 */}
            <code>{code}</code>
          </div>
        ) : (
          <code>{code}</code>
        )}
      </pre>
    </div>
  );
}

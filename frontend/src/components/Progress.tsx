/** 进度条组件 */

interface ProgressProps {
  current: number;
  total: number;
  showLabel?: boolean;
}

export default function Progress({ current, total, showLabel = true }: ProgressProps) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div style={{ marginBottom: '20px' }}>
      {showLabel && (
        <div style={{ marginBottom: '8px', fontSize: '14px', color: '#666' }}>
          进度: {current} / {total} ({percentage}%)
        </div>
      )}
      <div
        style={{
          width: '100%',
          height: '8px',
          background: '#e0e0e0',
          borderRadius: '4px',
          overflow: 'hidden'
        }}
      >
        <div
          style={{
            width: `${percentage}%`,
            height: '100%',
            background: '#007bff',
            transition: 'width 0.3s ease'
          }}
        />
      </div>
    </div>
  );
}

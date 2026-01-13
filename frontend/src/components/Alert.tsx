/** 警告/提示框组件 */

type AlertType = 'info' | 'success' | 'warning' | 'error';

interface AlertProps {
  type?: AlertType;
  message: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

const typeStyles: Record<AlertType, { background: string; color: string; border: string }> = {
  info: { background: '#e7f3ff', color: '#004085', border: '#b3d7ff' },
  success: { background: '#d4edda', color: '#155724', border: '#c3e6cb' },
  warning: { background: '#fff3cd', color: '#856404', border: '#ffeeba' },
  error: { background: '#f8d7da', color: '#721c24', border: '#f5c6cb' }
};

const typeLabels: Record<AlertType, string> = {
  info: '提示',
  success: '成功',
  warning: '警告',
  error: '错误'
};

export default function Alert({ type = 'info', message, dismissible = false, onDismiss }: AlertProps) {
  const style = typeStyles[type];

  return (
    <div
      style={{
        padding: '12px 16px',
        marginBottom: '16px',
        borderRadius: '4px',
        background: style.background,
        color: style.color,
        border: `1px solid ${style.border}`,
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px'
      }}
    >
      <strong style={{ minWidth: '40px' }}>{typeLabels[type]}:</strong>
      <span style={{ flex: 1 }}>{message}</span>
      {dismissible && (
        <button
          onClick={onDismiss}
          style={{
            background: 'none',
            border: 'none',
            color: style.color,
            fontSize: '18px',
            cursor: 'pointer',
            padding: 0,
            lineHeight: 1
          }}
        >
          ×
        </button>
      )}
    </div>
  );
}

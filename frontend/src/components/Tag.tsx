/** 标签组件 */

type TagType = 'default' | 'success' | 'warning' | 'error' | 'info';

interface TagProps {
  type?: TagType;
  label: string;
  closable?: boolean;
  onClose?: () => void;
  style?: React.CSSProperties;
}

const typeStyles: Record<TagType, { background: string; color: string }> = {
  default: { background: '#f0f0f0', color: '#333' },
  success: { background: '#d4edda', color: '#155724' },
  warning: { background: '#fff3cd', color: '#856404' },
  error: { background: '#f8d7da', color: '#721c24' },
  info: { background: '#e7f3ff', color: '#004085' }
};

export default function Tag({ type = 'default', label, closable = false, onClose, style }: TagProps) {
  const styles = typeStyles[type];

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '4px 12px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: '500',
        background: styles.background,
        color: styles.color,
        gap: '8px',
        ...style
      }}
    >
      <span>{label}</span>
      {closable && (
        <span
          onClick={onClose}
          style={{
            cursor: 'pointer',
            fontSize: '14px',
            lineHeight: 1,
            opacity: 0.6,
            transition: 'opacity 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.opacity = '1';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.opacity = '0.6';
          }}
        >
          ×
        </span>
      )}
    </span>
  );
}

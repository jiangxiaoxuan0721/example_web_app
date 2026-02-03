/** 标签组件 */

type TagType = 'default' | 'success' | 'warning' | 'error' | 'info';

interface TagProps {
  type?: TagType | string;  // 允许传入状态字符串，自动映射到对应的颜色类型
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

/**
 * 根据状态值自动映射到对应的颜色类型
 * @param typeOrStatus 状态字符串或颜色类型
 * @returns 对应的颜色类型
 */
const mapStatusToType = (typeOrStatus: string | undefined): TagType => {
  if (!typeOrStatus) return 'default';

  // 如果已经是有效的颜色类型，直接返回
  const validTypes: TagType[] = ['default', 'success', 'warning', 'error', 'info'];
  if (validTypes.includes(typeOrStatus as TagType)) {
    return typeOrStatus as TagType;
  }

  // 否则根据状态值映射到颜色类型
  const status = String(typeOrStatus).toLowerCase();

  if (['active', 'completed', 'done', 'success', 'enabled', 'open'].includes(status)) {
    return 'success';  // 绿色
  } else if (['pending', 'waiting', 'warning', 'processing'].includes(status)) {
    return 'warning';  // 黄色
  } else if (['error', 'failed', 'danger', 'rejected'].includes(status)) {
    return 'error';    // 红色
  } else if (['info'].includes(status)) {
    return 'info';      // 蓝色
  }
  // inactive, disabled, closed, 以及其他未知状态都使用 default（灰色）
  return 'default';     // 灰色
};

export default function Tag({ type, label, closable = false, onClose, style }: TagProps) {
  // 自动映射状态到颜色类型
  const tagType = mapStatusToType(type);
  const styles = typeStyles[tagType];

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

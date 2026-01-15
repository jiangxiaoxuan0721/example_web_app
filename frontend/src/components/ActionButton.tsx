/** 操作按钮组件 */

import { ActionConfig } from '../types/schema';

interface ActionButtonProps {
  action: ActionConfig;
  onApiClick: () => void;  // API 操作回调
  onNavigate?: (targetInstance: string) => void;  // 导航操作回调（可选）
}

export default function ActionButton({ action, onApiClick, onNavigate }: ActionButtonProps) {
  const getBackgroundColor = (hover: boolean = false) => {
    if (action.style === 'primary') {
      return hover ? '#0056b3' : '#007bff';
    } else if (action.style === 'danger') {
      return hover ? '#c82333' : '#dc3545';
    } else {
      return hover ? '#545b62' : '#6c757d';
    }
  };

  // 确定点击处理方式
  const handleClick = () => {
    if (action.action_type === 'navigate' && onNavigate && action.target_instance) {
      // 导航到目标实例
      onNavigate(action.target_instance);
    } else {
      // 默认为 API 操作
      onApiClick();
    }
  };

  return (
    <button
      onClick={handleClick}
      style={{
        padding: '12px 24px',
        fontSize: '16px',
        borderRadius: '4px',
        border: 'none',
        cursor: 'pointer',
        background: getBackgroundColor(false),
        color: 'white',
        transition: 'background 0.2s'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = getBackgroundColor(true);
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = getBackgroundColor(false);
      }}
      title={action.action_type === 'navigate' ? `导航到实例: ${action.target_instance}` : undefined}
    >
      {action.label}
      {action.action_type === 'navigate' && (
        <span style={{ marginLeft: '5px' }}>→</span>
      )}
    </button>
  );
}

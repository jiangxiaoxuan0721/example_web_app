/** 操作按钮组件 */

import { ActionConfig } from '../types/schema';

interface ActionButtonProps {
  action: ActionConfig;
  onClick: () => void;
}

export default function ActionButton({ action, onClick }: ActionButtonProps) {
  const getBackgroundColor = (hover: boolean = false) => {
    if (action.style === 'primary') {
      return hover ? '#0056b3' : '#007bff';
    } else if (action.style === 'danger') {
      return hover ? '#c82333' : '#dc3545';
    } else {
      return hover ? '#545b62' : '#6c757d';
    }
  };

  return (
    <button
      onClick={onClick}
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
    >
      {action.label}
    </button>
  );
}

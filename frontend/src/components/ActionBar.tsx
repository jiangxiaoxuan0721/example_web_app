import { Action } from '../types/schema';

/**
 * Action Button 组件
 */
export const ActionButton = ({ 
  action, 
  onClick, 
  disabled = false 
}: { 
  action: Action; 
  onClick: () => void;
  disabled?: boolean;
}) => {
  return (
    <button
      className={`action-btn action-btn-${action.style || 'secondary'}`}
      onClick={onClick}
      disabled={disabled}
    >
      {action.label}
    </button>
  );
};

/**
 * Action Bar 组件 - 渲染所有 Actions
 */
export const ActionBar = ({ 
  actions, 
  onActionClick,
  disabled = false 
}: { 
  actions?: Action[];
  onActionClick: (action: Action) => void;
  disabled?: boolean;
}) => {
  if (!actions || actions.length === 0) {
    return null;
  }

  return (
    <div className="action-bar">
      {actions.map((action) => (
        <ActionButton
          key={action.id}
          action={action}
          onClick={() => onActionClick(action)}
          disabled={disabled}
        />
      ))}
    </div>
  );
};

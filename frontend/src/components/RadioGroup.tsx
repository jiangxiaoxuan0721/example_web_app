/** 单选按钮组组件 */

import { FieldConfig } from '../types/schema';
import { getOptionLabel } from '../utils/template';

export interface RadioGroupProps {
  field: FieldConfig;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function RadioGroup({ field, value, onChange, disabled }: RadioGroupProps) {
  const options = field.options || [];
  const isDisabled = disabled || field.editable === false;
  const isRequired = field.required === true;
  const isEditable = field.editable !== false;

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{
        display: 'block',
        marginBottom: '10px',
        fontWeight: '600',
        fontSize: '15px',
        color: '#374151'
      }}>
        {field.label}
        {isRequired && <span style={{ color: 'red', marginLeft: '4px' }}>*</span>}
      </label>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {options.map((option) => (
          <label
            key={option.value}
            style={{
              display: 'flex',
              alignItems: 'center',
              minWidth: '60px',
              padding: '8px 16px',
              border: value === option.value ? '2px solid #6366f1' : '2px solid #e5e7eb',
              borderRadius: '8px',
              backgroundColor: isDisabled ? '#f9fafb' : (value === option.value ? '#eef2ff' : 'white'),
              cursor: isDisabled ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              userSelect: 'none',
              opacity: isDisabled ? 0.7 : 1
            }}
            onMouseEnter={(e) => {
              if (!isDisabled && value !== option.value) {
                e.currentTarget.style.borderColor = '#a5b4fc';
                e.currentTarget.style.backgroundColor = '#fafafa';
              }
            }}
            onMouseLeave={(e) => {
              if (!isDisabled && value !== option.value) {
                e.currentTarget.style.borderColor = '#e5e7eb';
                e.currentTarget.style.backgroundColor = 'white';
              }
            }}
          >
            <input
              type="radio"
              name={field.key}
              value={option.value}
              checked={value === option.value}
              onChange={(e) => {
                const newValue = e.target.value;
                onChange?.(newValue);
                // 存储到 state.params 中以便模板使用
                if (field.key) {
                  const label = getOptionLabel(newValue, options);
                  (window as any).__optionLabels__ = (window as any).__optionLabels__ || {};
                  (window as any).__optionLabels__[field.key] = label;
                }
              }}
              disabled={isDisabled}
              required={isRequired}
              style={{
                width: '16px',
                height: '16px',
                marginRight: '8px',
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                accentColor: '#6366f1'
              }}
            />
            <span style={{
              fontSize: '14px',
              fontWeight: value === option.value ? '600' : '500',
              color: isDisabled ? '#9ca3af' : (value === option.value ? '#4f46e5' : '#374151')
            }}>
              {option.label}
            </span>
          </label>
        ))}
      </div>
      {!isEditable && !disabled && (
        <div style={{ marginTop: '4px', color: '#999', fontSize: '12px' }}>
          此字段不可编辑
        </div>
      )}
    </div>
  );
}

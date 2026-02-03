/** 多选下拉组件 */

import { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';
import { getOptionLabel, getOptionLabels } from '../utils/template';

export interface MultiSelectProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function MultiSelect({ field, value, onChange, disabled }: MultiSelectProps) {
  const selectedOptions = Array.isArray(value) ? value : [];
  const isDisabled = disabled || field.editable === false;
  const isRequired = field.required === true;
  const isEditable = field.editable !== false;
  const options = field.options || [];

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
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
        {options.map((option) => {
          const isSelected = selectedOptions.includes(option.value);
          return (
            <label
              key={option.value}
              style={{
                display: 'flex',
                alignItems: 'center',
                minWidth: '60px',
                padding: '8px 16px',
                border: isSelected ? '2px solid #6366f1' : '2px solid #e5e7eb',
                borderRadius: '8px',
                backgroundColor: isDisabled ? '#f9fafb' : (isSelected ? '#eef2ff' : 'white'),
                color: isDisabled ? '#9ca3af' : (isSelected ? '#4f46e5' : '#374151'),
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                userSelect: 'none',
                opacity: isDisabled ? 0.7 : 1
              }}
              onMouseEnter={(e) => {
                if (!isDisabled && !isSelected) {
                  e.currentTarget.style.borderColor = '#a5b4fc';
                  e.currentTarget.style.backgroundColor = '#fafafa';
                }
              }}
              onMouseLeave={(e) => {
                if (!isDisabled && !isSelected) {
                  e.currentTarget.style.borderColor = '#e5e7eb';
                  e.currentTarget.style.backgroundColor = 'white';
                }
              }}
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => {
                  let newValue;
                  if (isSelected) {
                    newValue = selectedOptions.filter((v: string) => v !== option.value);
                  } else {
                    newValue = [...selectedOptions, option.value];
                  }
                  onChange?.(newValue);
                  // 存储到 state.params 中以便模板使用
                  if (field.key) {
                    const labels = getOptionLabels(newValue, options);
                    (window as any).__optionLabels__ = (window as any).__optionLabels__ || {};
                    (window as any).__optionLabels__[field.key] = labels.join(', ');
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
                fontWeight: isSelected ? '600' : '500'
              }}>
                {option.label}
              </span>
            </label>
          );
        })}
      </div>
      {!isEditable && !disabled && (
        <div style={{ marginTop: '4px', color: '#999', fontSize: '12px' }}>
          此字段不可编辑
        </div>
      )}
      {field.description && (
        <div style={{ marginTop: '8px', color: '#666', fontSize: '14px' }}>
          {field.description}
        </div>
      )}
    </div>
  );
}
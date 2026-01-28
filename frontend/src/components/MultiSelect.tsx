/** 多选下拉组件 */

import { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';

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
      </label>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
        {field.options?.map((option) => {
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
                backgroundColor: isSelected ? '#eef2ff' : 'white',
                color: isSelected ? '#4f46e5' : '#374151',
                cursor: disabled ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                userSelect: 'none',
                opacity: disabled ? 0.6 : 1
              }}
              onMouseEnter={(e) => {
                if (!disabled && !isSelected) {
                  e.currentTarget.style.borderColor = '#a5b4fc';
                  e.currentTarget.style.backgroundColor = '#fafafa';
                }
              }}
              onMouseLeave={(e) => {
                if (!disabled && !isSelected) {
                  e.currentTarget.style.borderColor = '#e5e7eb';
                  e.currentTarget.style.backgroundColor = 'white';
                }
              }}
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => {
                  if (isSelected) {
                    onChange?.(selectedOptions.filter((v: string) => v !== option.value));
                  } else {
                    onChange?.([...selectedOptions, option.value]);
                  }
                }}
                disabled={disabled}
                style={{
                  width: '16px',
                  height: '16px',
                  marginRight: '8px',
                  cursor: disabled ? 'not-allowed' : 'pointer',
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
      {field.description && (
        <div style={{ marginTop: '8px', color: '#666', fontSize: '14px' }}>
          {field.description}
        </div>
      )}
    </div>
  );
}
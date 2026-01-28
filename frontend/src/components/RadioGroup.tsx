/** 单选按钮组组件 */

import { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';

export interface RadioGroupProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function RadioGroup({ field, value, onChange, disabled }: RadioGroupProps) {
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
              backgroundColor: value === option.value ? '#eef2ff' : 'white',
              cursor: disabled ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              userSelect: 'none'
            }}
            onMouseEnter={(e) => {
              if (!disabled && value !== option.value) {
                e.currentTarget.style.borderColor = '#a5b4fc';
                e.currentTarget.style.backgroundColor = '#fafafa';
              }
            }}
            onMouseLeave={(e) => {
              if (!disabled && value !== option.value) {
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
              onChange={(e) => onChange?.(e.target.value)}
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
              fontWeight: value === option.value ? '600' : '500',
              color: value === option.value ? '#4f46e5' : '#374151'
            }}>
              {option.label}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}

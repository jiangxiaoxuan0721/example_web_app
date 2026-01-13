/** 单选按钮组组件 */

import { FieldConfig } from '../types/schema';
import { getFieldValue } from '../utils/patch';
import type { UISchema } from '../types/schema';

interface RadioGroupProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
}

export default function RadioGroup({ field, schema, bindPath, onChange, disabled }: RadioGroupProps) {
  const value = getFieldValue(schema, bindPath, field.key) || '';
  const options = field.options || [];

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {options.map((option) => (
          <label
            key={option.value}
            style={{
              display: 'flex',
              alignItems: 'center',
              cursor: disabled ? 'not-allowed' : 'pointer'
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
                width: '18px',
                height: '18px',
                marginRight: '8px',
                cursor: disabled ? 'not-allowed' : 'pointer'
              }}
            />
            <span>{option.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

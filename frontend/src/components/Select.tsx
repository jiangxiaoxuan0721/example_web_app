/** 下拉选择组件 */

import { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';

export interface SelectProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function Select({ field, value, onChange, disabled }: SelectProps) {
  const options = field.options || [];

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <select
        value={String(value)}
        onChange={(e) => onChange?.(e.target.value)}
        disabled={disabled}
        style={{
          width: '100%',
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: '#fff',
          fontSize: '16px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          boxSizing: 'border-box'
        }}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

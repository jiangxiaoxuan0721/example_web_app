/** 下拉选择组件 */

import { FieldConfig } from '../types/schema';
import { getFieldValue } from '../utils/patch';
import type { UISchema } from '../types/schema';

interface SelectProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
}

export default function Select({ field, schema, bindPath, onChange, disabled }: SelectProps) {
  const value = getFieldValue(schema, bindPath, field.key) || '';
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

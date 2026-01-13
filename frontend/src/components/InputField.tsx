/** 输入框组件 */

import { FieldConfig } from '../types/schema';
import { getFieldValue } from '../utils/patch';
import type { UISchema } from '../types/schema';

interface InputFieldProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
}

export default function InputField({ field, schema, bindPath, onChange, disabled }: InputFieldProps) {
  const value = getFieldValue(schema, bindPath, field.key) || '';

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <input
        type={field.type}
        value={String(value)}
        onChange={(e) => onChange?.(e.target.value)}
        disabled={disabled}
        placeholder={field.description}
        style={{
          width: '100%',
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: '#fff',
          fontSize: '16px',
          boxSizing: 'border-box'
        }}
      />
    </div>
  );
}

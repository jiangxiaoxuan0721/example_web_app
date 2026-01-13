/** 数字输入框组件 */

import { FieldConfig } from '../types/schema';
import { getFieldValue } from '../utils/patch';
import type { UISchema } from '../types/schema';

interface NumberInputProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  onChange?: (value: number) => void;
  disabled?: boolean;
}

export default function NumberInput({ field, schema, bindPath, onChange, disabled }: NumberInputProps) {
  const value = getFieldValue(schema, bindPath, field.key) ?? 0;

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <input
        type="number"
        value={Number(value)}
        onChange={(e) => onChange?.(Number(e.target.value))}
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

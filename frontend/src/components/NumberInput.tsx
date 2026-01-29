/** 数字输入框组件 */

import { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';

export interface NumberInputProps {
  field: FieldConfig;
  schema?: UISchema;
  bindPath?: string;
  value?: number;
  onChange?: (value: number) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function NumberInput({ field, value, onChange, disabled, highlighted }: NumberInputProps) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <input
        type="number"
        value={Number(value ?? 0)}
        onChange={(e) => onChange?.(Number(e.target.value))}
        disabled={disabled}
        placeholder={field.description}
        style={{
          width: '100%',
          padding: '12px',
          border: highlighted ? '2px solid #007bff' : '1px solid #ddd',
          borderRadius: '4px',
          background: '#fff',
          fontSize: '16px',
          boxSizing: 'border-box'
        }}
      />
    </div>
  );
}

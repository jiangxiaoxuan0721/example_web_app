/** 输入框组件 */

import { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';

export interface InputFieldProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function InputField({ field, value, onChange, disabled, highlighted }: InputFieldProps) {
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

/** 多行文本框组件 */

import { FieldConfig } from '../types/schema';
import { getFieldValue } from '../utils/patch';
import type { UISchema } from '../types/schema';

interface TextAreaProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
  rows?: number;
}

export default function TextArea({ field, schema, bindPath, onChange, disabled, rows = 4 }: TextAreaProps) {
  const value = getFieldValue(schema, bindPath, field.key) || '';

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <textarea
        value={String(value)}
        onChange={(e) => onChange?.(e.target.value)}
        disabled={disabled}
        placeholder={field.description}
        rows={rows}
        style={{
          width: '100%',
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: '#fff',
          fontSize: '16px',
          resize: 'vertical',
          fontFamily: 'Arial, sans-serif',
          boxSizing: 'border-box'
        }}
      />
    </div>
  );
}

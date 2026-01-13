/** 复选框组件 */

import { FieldConfig } from '../types/schema';
import { getFieldValue } from '../utils/patch';
import type { UISchema } from '../types/schema';

interface CheckBoxProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  onChange?: (value: boolean) => void;
  disabled?: boolean;
}

export default function CheckBox({ field, schema, bindPath, onChange, disabled }: CheckBoxProps) {
  const value = getFieldValue(schema, bindPath, field.key) ?? false;

  return (
    <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center' }}>
      <input
        type="checkbox"
        checked={Boolean(value)}
        onChange={(e) => onChange?.(e.target.checked)}
        disabled={disabled}
        style={{
          width: '18px',
          height: '18px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          marginRight: '8px'
        }}
      />
      <label style={{ fontWeight: 'bold', cursor: disabled ? 'not-allowed' : 'pointer' }}>
        {field.label}
      </label>
    </div>
  );
}

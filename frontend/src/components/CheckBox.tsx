/** 复选框组件 */

import { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';

export interface CheckBoxProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function CheckBox({ field, value, onChange, disabled }: CheckBoxProps) {
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

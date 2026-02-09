/** 复选框组件 */
import { FieldConfig } from '../types/schema';

export interface CheckBoxProps {
  field: FieldConfig;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function CheckBox({ field, value, onChange, disabled }: CheckBoxProps) {
  const isDisabled = disabled || field.editable === false;
  const isRequired = field.required === true;
  const isEditable = field.editable !== false;

  return (
    <div style={{ marginBottom: '16px', display: 'flex', alignItems: 'center' }}>
      <input
        type="checkbox"
        checked={Boolean(value)}
        onChange={(e) => onChange?.(e.target.checked)}
        disabled={isDisabled}
        required={isRequired}
        style={{
          width: '18px',
          height: '18px',
          cursor: isDisabled ? 'not-allowed' : 'pointer',
          marginRight: '8px'
        }}
      />
      <label style={{ fontWeight: 'bold', cursor: isDisabled ? 'not-allowed' : 'pointer' }}>
        {field.label}
        {isRequired && <span style={{ color: 'red', marginLeft: '4px' }}>*</span>}
      </label>
      {!isEditable && !disabled && (
        <div style={{ marginLeft: '8px', color: '#999', fontSize: '12px' }}>
          (不可编辑)
        </div>
      )}
    </div>
  );
}

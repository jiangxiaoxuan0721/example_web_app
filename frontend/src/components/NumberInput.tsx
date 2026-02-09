/** 数字输入框组件 */
import { FieldConfig } from '../types/schema';

export interface NumberInputProps {
  field: FieldConfig;
  value?: number;
  onChange?: (value: number) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function NumberInput({ field, value, onChange, disabled, highlighted }: NumberInputProps) {
  // editable 为 false 时禁用编辑（但 disabled 优先级更高）
  const isDisabled = disabled || field.editable === false;
  const isRequired = field.required === true;
  const isEditable = field.editable !== false;

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
        {isRequired && <span style={{ color: 'red', marginLeft: '4px' }}>*</span>}
      </label>
      <input
        type="number"
        value={Number(value ?? 0)}
        onChange={(e) => onChange?.(Number(e.target.value))}
        disabled={isDisabled}
        required={isRequired}
        placeholder={field.description}
        style={{
          width: '100%',
          padding: '12px',
          border: highlighted ? '2px solid #007bff' : '1px solid #ddd',
          borderRadius: '4px',
          background: isDisabled ? '#f5f5f5' : '#fff',
          fontSize: '16px',
          cursor: isDisabled ? 'not-allowed' : 'auto',
          boxSizing: 'border-box'
        }}
      />
      {!isEditable && !disabled && (
        <div style={{ marginTop: '4px', color: '#999', fontSize: '12px' }}>
          此字段不可编辑
        </div>
      )}
    </div>
  );
}

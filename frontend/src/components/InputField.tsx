/** 输入框组件 */
import { FieldConfig } from '../types/schema';

export interface InputFieldProps {
  field: FieldConfig;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function InputField({ field, value, onChange, disabled, highlighted }: InputFieldProps) {
  // editable 为 false 时禁用编辑（但 disabled 优先级更高）
  const isDisabled = disabled || field.editable === false;
  // required 属性用于表单验证
  const isRequired = field.required === true;
  const isEditable = field.editable !== false;
  // 处理 undefined/null 值，显示空字符串而不是 "undefined"/"null"
  const displayValue = value !== undefined && value !== null ? String(value) : '';

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
        {isRequired && <span style={{ color: 'red', marginLeft: '4px' }}>*</span>}
      </label>
      <input
        type={field.type}
        value={displayValue}
        onChange={(e) => onChange?.(e.target.value)}
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

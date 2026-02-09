/** 多行文本框组件 */
import { FieldConfig } from '../types/schema';

interface TextAreaProps {
  field: FieldConfig;
  value: any;
  onChange?: (value: string) => void;
  disabled?: boolean;
  rows?: number;
}

export default function TextArea({ field, value, onChange, disabled, rows = 4 }: TextAreaProps) {
  const displayValue = value !== undefined && value !== null ? String(value) : '';
  const isDisabled = disabled || field.editable === false;
  const isRequired = field.required === true;
  const isEditable = field.editable !== false;

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
        {isRequired && <span style={{ color: 'red', marginLeft: '4px' }}>*</span>}
      </label>
      <textarea
        value={displayValue}
        onChange={(e) => onChange?.(e.target.value)}
        disabled={isDisabled}
        required={isRequired}
        placeholder={field.description}
        rows={rows}
        style={{
          width: '100%',
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: isDisabled ? '#f5f5f5' : '#fff',
          fontSize: '16px',
          resize: isDisabled ? 'none' : 'vertical',
          cursor: isDisabled ? 'not-allowed' : 'auto',
          fontFamily: 'Arial, sans-serif',
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

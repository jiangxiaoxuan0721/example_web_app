/** 下拉选择组件 */

import { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';
import { getOptionLabel } from '../utils/template';

export interface SelectProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  value: any;
  onChange?: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

export default function Select({ field, value, onChange, disabled }: SelectProps) {
  const options = field.options || [];
  const isDisabled = disabled || field.editable === false;
  const isRequired = field.required === true;
  const isEditable = field.editable !== false;
  // 处理 undefined/null 值
  const displayValue = value !== undefined && value !== null ? String(value) : '';

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
        {isRequired && <span style={{ color: 'red', marginLeft: '4px' }}>*</span>}
      </label>
      <select
        value={displayValue}
        onChange={(e) => {
          // 更新值时，同时更新 label 映射
          const newValue = e.target.value;
          onChange?.(newValue);
          // 存储到 state.params 中以便模板使用
          if (field.key) {
            const label = getOptionLabel(newValue, options);
            // 将 label 存储到对应的字段路径
            (window as any).__optionLabels__ = (window as any).__optionLabels__ || {};
            (window as any).__optionLabels__[field.key] = label;
          }
        }}
        disabled={isDisabled}
        required={isRequired}
        style={{
          width: '100%',
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: isDisabled ? '#f5f5f5' : '#fff',
          fontSize: '16px',
          cursor: isDisabled ? 'not-allowed' : 'pointer',
          boxSizing: 'border-box'
        }}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {!isEditable && !disabled && (
        <div style={{ marginTop: '4px', color: '#999', fontSize: '12px' }}>
          此字段不可编辑
        </div>
      )}
    </div>
  );
}

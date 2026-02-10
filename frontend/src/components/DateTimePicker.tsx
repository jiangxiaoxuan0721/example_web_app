import React from 'react';

interface DateTimePickerProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
  min?: string;
  max?: string;
  required?: boolean;
}

export default function DateTimePicker({
  value,
  onChange,
  disabled = false,
  placeholder = '选择日期时间',
  min,
  max,
  required = false
}: DateTimePickerProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
  };

  return (
    <input
      type="datetime-local"
      value={value || ''}
      onChange={handleChange}
      disabled={disabled}
      placeholder={placeholder}
      min={min}
      max={max}
      required={required}
      style={{
        padding: '8px 12px',
        border: '1px solid #d9d9d9',
        borderRadius: '4px',
        fontSize: '14px',
        width: '100%',
        boxSizing: 'border-box',
        cursor: disabled ? 'not-allowed' : 'pointer',
        backgroundColor: disabled ? '#f5f5f5' : 'white',
        color: disabled ? '#bfbfbf' : 'inherit'
      }}
    />
  );
}

/** 字段显示组件 */

import { FieldConfig } from '../types/schema';
import { getFieldValue } from '../utils/patch';
import type { UISchema } from '../types/schema';

interface FieldDisplayProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
}

export default function FieldDisplay({ field, schema, bindPath }: FieldDisplayProps) {
  const value = getFieldValue(schema, bindPath, field.key);

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <div
        style={{
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: '#f9f9f9',
          fontSize: '16px'
        }}
      >
        {String(value)}
      </div>
    </div>
  );
}

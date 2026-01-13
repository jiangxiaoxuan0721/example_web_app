/** Block 渲染器组件 */

import { Block, UISchema, FieldConfig } from '../types/schema';
import FieldDisplay from './FieldDisplay';
import InputField from './InputField';
import NumberInput from './NumberInput';
import TextArea from './TextArea';
import Select from './Select';
import CheckBox from './CheckBox';
import RadioGroup from './RadioGroup';

interface BlockRendererProps {
  block: Block;
  schema: UISchema;
  onFieldChange?: (fieldKey: string, value: any) => void;
  disabled?: boolean;
}

/**
 * 根据字段类型渲染对应的输入组件
 */
function FieldRenderer({
  field,
  schema,
  bindPath,
  onFieldChange,
  disabled
}: {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  onFieldChange?: (fieldKey: string, value: any) => void;
  disabled?: boolean;
}) {
  const handleFieldChange = (value: any) => {
    if (onFieldChange) {
      onFieldChange(field.key, value);
    }
  };

  // 只读模式：显示 FieldDisplay
  if (!onFieldChange || disabled) {
    return <FieldDisplay field={field} schema={schema} bindPath={bindPath} />;
  }

  // 可编辑模式：根据类型渲染对应组件
  switch (field.type) {
    case 'number':
      return (
        <NumberInput
          field={field}
          schema={schema}
          bindPath={bindPath}
          onChange={handleFieldChange}
        />
      );
    case 'textarea':
      return (
        <TextArea
          field={field}
          schema={schema}
          bindPath={bindPath}
          onChange={handleFieldChange}
        />
      );
    case 'select':
      return (
        <Select
          field={field}
          schema={schema}
          bindPath={bindPath}
          onChange={handleFieldChange}
        />
      );
    case 'checkbox':
      return (
        <CheckBox
          field={field}
          schema={schema}
          bindPath={bindPath}
          onChange={handleFieldChange}
        />
      );
    case 'radio':
      return (
        <RadioGroup
          field={field}
          schema={schema}
          bindPath={bindPath}
          onChange={handleFieldChange}
        />
      );
    case 'text':
    default:
      return (
        <InputField
          field={field}
          schema={schema}
          bindPath={bindPath}
          onChange={handleFieldChange}
        />
      );
  }
}

export default function BlockRenderer({ block, schema, onFieldChange, disabled }: BlockRendererProps) {
  if (block.type === 'form' && block.props?.fields) {
    return (
      <div key={block.id} style={{ marginBottom: '20px' }}>
        {block.props.fields.map((field) => (
          <FieldRenderer
            key={field.key}
            field={field}
            schema={schema}
            bindPath={block.bind}
            onFieldChange={onFieldChange}
            disabled={disabled}
          />
        ))}
      </div>
    );
  }

  return null;
}

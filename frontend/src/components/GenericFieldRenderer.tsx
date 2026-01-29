/** 通用字段渲染器 - 基于类型注册表的可扩展渲染 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import type { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';
import { useFieldPatch } from '../store/schemaStore';
import { useMultiInstanceStore } from '../store/multiInstanceStore';
import { useEventEmitter } from '../utils/eventEmitter';
import { renderTemplate, renderFieldTemplate } from '../utils/template';
import ImageRenderer from './ImageRenderer';
import BlockRenderer from './BlockRenderer';
import InputField from './InputField';
import NumberInput from './NumberInput';
import TextArea from './TextArea';
import Select from './Select';
import CheckBox from './CheckBox';
import RadioGroup from './RadioGroup';
import MultiSelect from './MultiSelect';
import Table from './Table';
import Tag from './Tag';
import Progress from './Progress';
import Badge from './Badge';
import JSONViewer from './JSONViewer';
import RichContentRenderer from './RichContentRenderer';
import Modal from './Modal';

// 字段渲染器接口
export interface FieldRenderer {
  (props: FieldRendererProps): JSX.Element;
}

interface FieldRendererProps {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  value: any;
  onChange: (value: any) => void;
  disabled?: boolean;
  highlighted?: boolean;
}

// 字段类型注册表
interface FieldRendererRegistry {
  [fieldType: string]: FieldRenderer;
}

// 渲染图片字段的辅助函数
const renderImage = ({ field, value }: {
  field: FieldConfig;
  value: any;
}) => {
  // 提取图片信息 - 优先使用 state 中的 value，否则使用 field.value
  const stateImageUrl = typeof value === 'string' ? value : (value?.url || '');
  const imageUrl = stateImageUrl || field.value || '';
  const imageTitle = typeof value === 'object' ? (value?.title || field.description) : field.description;
  const imageAlt = typeof value === 'object' ? (value?.alt || field.label) : field.label;

  // 如果没有URL，显示占位符
  if (!imageUrl) {
    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <div style={{
          border: '1px dashed #ccc',
          borderRadius: '4px',
          padding: '20px',
          textAlign: 'center',
          color: '#888'
        }}>
          无图片URL
        </div>
        {field.description && (
          <div style={{ marginTop: '4px', color: '#666', fontSize: '12px' }}>
            {field.description}
          </div>
        )}
      </div>
    );
  }

  // 使用最佳配置
  const defaultProps = {
    height: field.imageHeight || 'auto',
    fit: field.imageFit || 'contain',
    showFullscreen: field.showFullscreen !== false,
    showDownload: field.showDownload !== false,
    subtitle: field.subtitle,
    lazy: field.lazy,
    fallback: field.fallback
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <ImageRenderer
        source={imageUrl}
        title={imageTitle}
        alt={imageAlt}
        {...defaultProps}
      />
      {field.description && (
        <div style={{ marginTop: '4px', color: '#666', fontSize: '12px' }}>
          {field.description}
        </div>
      )}
    </div>
  );
};

// 默认渲染器注册表
const defaultRenderers: FieldRendererRegistry = {
  text: ({ field, value, onChange, disabled, highlighted }) => (
    <InputField
      field={field}
      schema={null as any}
      bindPath=""
      value={value}
      onChange={onChange}
      disabled={disabled}
      highlighted={highlighted}
    />
  ),

  number: ({ field, value, onChange, disabled, highlighted }) => (
    <NumberInput
      field={field}
      value={value}
      onChange={onChange}
      disabled={disabled}
      highlighted={highlighted}
    />
  ),

  textarea: ({ field, onChange, disabled }) => (
    <TextArea
      field={field}
      schema={null as any}
      bindPath=""
      onChange={onChange}
      disabled={disabled}
    />
  ),

  checkbox: ({ field, value, onChange, disabled }) => (
    <CheckBox
      field={field}
      schema={null as any}
      bindPath=""
      value={value}
      onChange={onChange}
      disabled={disabled}
    />
  ),

  select: ({ field, value, onChange, disabled, highlighted }) => (
    <Select
      field={field}
      schema={null as any}
      bindPath=""
      value={value}
      onChange={onChange}
      disabled={disabled}
      highlighted={highlighted}
    />
  ),

  json: ({ field, value, schema }) => {
    // 渲染 value 中的模板变量
    let renderedValue: any;
    if (typeof value === 'object' && value !== null) {
      renderedValue = value;
    } else if (typeof value === 'string') {
      const templateRendered = schema ? renderTemplate(value, schema) : value;
      try {
        renderedValue = JSON.parse(templateRendered);
      } catch {
        renderedValue = templateRendered;
      }
    } else {
      renderedValue = value;
    }

    // 使用 JSONViewer 展示 JSON
    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <JSONViewer data={renderedValue} expandDepth={2} showLineNumbers={false} />
      </div>
    );
  },

  radio: ({ field, value, onChange, disabled }) => (
    <RadioGroup
      field={field}
      schema={null as any}
      bindPath=""
      value={value}
      onChange={onChange}
      disabled={disabled}
    />
  ),

  html: ({ field, value, schema }) => {
    // 对于 html 类型，优先使用 field.value 作为默认值
    // 如果 state 中有值，则使用 state 中的值（覆盖默认值）
    const htmlContent = value !== undefined && value !== null && value !== '' ? value : field.value;

    return (
      <div>
        {field.label && (
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            {field.label}
          </label>
        )}
        <RichContentRenderer html={htmlContent} schema={schema} style={{ marginBottom: '16px' }} />
        {field.description && (
          <div style={{ marginTop: '4px', color: '#666', fontSize: '12px' }}>
            {field.description}
          </div>
        )}
      </div>
    );
  },

  image: ({ field, value }) => {
    return renderImage({ field, value });
  },

  multiselect: ({ field, value, onChange, disabled, highlighted }) => (
    <MultiSelect
      field={field}
      schema={null as any}
      bindPath=""
      value={value}
      onChange={onChange}
      disabled={disabled}
      highlighted={highlighted}
    />
  ),

  tag: ({ field, value }) => {
    const tags = Array.isArray(value) ? value : [];

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {tags.map((tag: any, index: number) => {
            const tagType = tag.type || 'default';
            return (
              <Tag
                key={index}
                type={tagType}
                label={tag.label || tag}
              />
            );
          })}
          {(!tags || tags.length === 0) && (
            <span style={{ color: '#999', fontSize: '14px' }}>暂无标签</span>
          )}
        </div>
      </div>
    );
  },

  progress: ({ field, value }) => {
    const current = value?.current || 0;
    const total = value?.total || 100;
    const showLabel = value?.showLabel !== false;

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <Progress current={current} total={total} showLabel={showLabel} />
      </div>
    );
  },

  badge: ({ field, value }) => {
    const badgeConfig = value || {};

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <Badge
          count={badgeConfig.count}
          dot={badgeConfig.dot}
          color={badgeConfig.color}
          showZero={badgeConfig.showZero}
          max={badgeConfig.max}
        >
          <span
            style={{
              padding: '12px 24px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              background: '#fff',
              fontSize: '14px'
            }}
          >
            {badgeConfig.label || '通知'}
          </span>
        </Badge>
      </div>
    );
  },

  table: ({ field, value }) => (
    <Table field={field} value={value} />
  ),

  modal: ({ value, onChange }) => {
    const modalState = value || { visible: false };

    return (
      <Modal
        visible={modalState.visible || false}
        title={modalState.title}
        width={modalState.width || 520}
        maskClosable={true}
        onOk={() => {
          if (modalState.onOk) modalState.onOk();
          onChange({ ...modalState, visible: false });
        }}
        onCancel={() => {
          onChange({ ...modalState, visible: false });
        }}
        okText={modalState.okText}
        cancelText={modalState.cancelText}
        footer={undefined}
      >
        <div dangerouslySetInnerHTML={{ __html: modalState.content || '' }} />
      </Modal>
    );
  },

  component: ({ field }) => {
    const getInstance = useMultiInstanceStore((state) => state.getInstance);
    const targetInstance = field.targetInstance;

    if (!targetInstance) {
      return (
        <div style={{ color: '#999', padding: '20px' }}>
          未指定目标实例
        </div>
      );
    }

    const targetSchema = getInstance(targetInstance);

    if (!targetSchema) {
      return (
        <div style={{ color: '#999', padding: '20px' }}>
          目标实例不存在: {targetInstance}
        </div>
      );
    }

    // 如果指定了 targetBlock，只渲染指定的 block
    if (field.targetBlock) {
      const targetBlock = targetSchema.blocks.find(b => b.id === field.targetBlock);
      if (targetBlock) {
        return (
          <div style={{ marginBottom: '16px' }}>
            <BlockRenderer block={targetBlock} />
          </div>
        );
      } else {
        return (
          <div style={{ color: '#999', padding: '20px' }}>
            目标 block 不存在: {field.targetBlock}
          </div>
        );
      }
    }

    // 否则渲染所有 block（无标题）
    return (
      <div style={{ marginBottom: '16px' }}>
        {targetSchema.blocks.map((block) => (
          <BlockRenderer key={block.id} block={block} />
        ))}
      </div>
    );
  }
};

// 全局渲染器注册表
let fieldRenderers: FieldRendererRegistry = { ...defaultRenderers };

/**
 * 注册新的字段类型渲染器
 */
export const registerFieldRenderer = (fieldType: string, renderer: FieldRenderer): void => {
  fieldRenderers = {
    ...fieldRenderers,
    [fieldType]: renderer
  };
};

/**
 * 获取所有注册的字段类型
 */
export const getRegisteredFieldTypes = (): string[] => {
  return Object.keys(fieldRenderers);
};

/**
 * 通用字段渲染器组件
 */
export default function GenericFieldRenderer({
  field,
  schema,
  bindPath,
  disabled = false,
  highlighted = false
}: {
  field: FieldConfig;
  schema: UISchema;
  bindPath: string;
  disabled?: boolean;
  highlighted?: boolean;
}) {
  console.log('[GenericFieldRenderer] 初始化 - field:', field.label, 'bindPath:', bindPath, 'field.key:', field.key);

  // 渲染字段配置中的模板
  const renderedField = useMemo(() => renderFieldTemplate(field, schema), [field, schema]);

  // 从传入的 schema 中提取值
  const storedValue = useMemo(() => {
    // 1. Resolve block.bind path
    let baseObj: any = schema;
    let actualPath = 'schema';

    console.log('[GenericFieldRenderer] useMemo - bindPath:', bindPath, 'field.key:', field.key);

    if (bindPath) {
      const bindPathKeys = bindPath.split('.');
      baseObj = bindPathKeys.reduce((obj: any, key: string) => obj?.[key], schema);
      actualPath = `schema.${bindPath}`;
      console.log('[GenericFieldRenderer] bindPath 分解:', bindPathKeys, 'baseObj:', baseObj);
    }

    // 2. Read field.key
    const fieldKeys = field.key.split('.');
    const finalValue = fieldKeys.reduce((obj: any, key: string) => obj?.[key], baseObj);
    actualPath += `.${field.key}`;

    console.log('[GenericFieldRenderer] 字段:', field.label, '最终路径:', actualPath, '值:', finalValue);
    return finalValue;
  }, [schema, bindPath, field.key, field.label]);

  // 本地状态用于乐观更新
  const [localValue, setLocalValue] = useState(storedValue);
  const fieldPatch = useFieldPatch();
  const { emitFieldChange } = useEventEmitter();

  // 当 Store 中的值变化时，同步到本地状态
  useEffect(() => {
    console.log('[GenericFieldRenderer] 值变化:', { field: field.label, old: localValue, new: storedValue });
    setLocalValue(storedValue);
  }, [storedValue]);

  // 处理值变更
  const handleChange = useCallback((newValue: any) => {
    // 立即更新本地状态（乐观更新）
    setLocalValue(newValue);

    // 应用本地补丁（立即更新 Schema Store）
    fieldPatch(bindPath, field.key, newValue);

    // 同时发送事件到后端（防抖处理）
    emitFieldChange(field.key, newValue, bindPath);
  }, [field.key, bindPath, emitFieldChange, fieldPatch]);

  const renderer = fieldRenderers[renderedField.type] || fieldRenderers.text;

  return renderer({
    field: renderedField,
    schema,
    bindPath,
    value: localValue,
    onChange: handleChange,
    disabled,
    highlighted
  });
}
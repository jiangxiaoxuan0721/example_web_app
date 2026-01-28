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
import Select from './Select';
import CheckBox from './CheckBox';
import RadioGroup from './RadioGroup';
import MultiSelect from './MultiSelect';
import Table from './Table';

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
  // 提取图片信息
  const imageUrl = typeof value === 'string' ? value : (value?.url || '');
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
  text: ({ field, value, onChange, disabled, highlighted, schema }) => {
    // 渲染 value 中的模板变量
    let displayValue: string;
    if (typeof value === 'object' && value !== null) {
      // 如果是对象，转换为 JSON 字符串
      displayValue = JSON.stringify(value);
    } else if (typeof value === 'string') {
      // 如果是字符串，渲染模板
      displayValue = schema ? renderTemplate(value, schema) : value;
    } else {
      displayValue = String(value ?? '');
    }

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          fontWeight: '600',
          fontSize: '14px',
          color: '#333'
        }}>
          {field.label}
        </label>
        <input
          type="text"
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder={field.description}
          style={{
            width: '100%',
            padding: '10px 14px',
            border: highlighted ? '2px solid #007bff' : '1px solid #e5e7eb',
            borderRadius: '6px',
            backgroundColor: '#ffffff',
            fontSize: '14px',
            lineHeight: '1.5',
            color: '#333',
            boxSizing: 'border-box',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
            transition: 'all 0.2s ease',
            outline: 'none'
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = highlighted ? '#007bff' : '#007bff';
            e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0, 123, 255, 0.1)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = highlighted ? '#007bff' : '#e5e7eb';
            e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
          }}
        />
        {field.description && (
          <div style={{ marginTop: '6px', color: '#6b7280', fontSize: '12px', lineHeight: '1.4' }}>
            {field.description}
          </div>
        )}
      </div>
    );
  },

  number: ({ field, value, onChange, disabled, highlighted }) => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{
        display: 'block',
        marginBottom: '8px',
        fontWeight: '600',
        fontSize: '14px',
        color: '#333'
      }}>
        {field.label}
      </label>
      <input
        type="number"
        value={value !== undefined ? String(value) : ''}
        onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
        disabled={disabled}
        placeholder={field.description}
        style={{
          width: '100%',
          padding: '10px 14px',
          border: highlighted ? '2px solid #007bff' : '1px solid #e5e7eb',
          borderRadius: '6px',
          backgroundColor: '#ffffff',
          fontSize: '14px',
          lineHeight: '1.5',
          color: '#333',
          boxSizing: 'border-box',
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
          transition: 'all 0.2s ease',
          outline: 'none'
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = highlighted ? '#007bff' : '#007bff';
          e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0, 123, 255, 0.1)';
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = highlighted ? '#007bff' : '#e5e7eb';
          e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
        }}
      />
    </div>
  ),

  textarea: ({ field, value, onChange, disabled, schema }) => {
    // 渲染 value 中的模板变量
    let displayValue: string;
    if (typeof value === 'object' && value !== null) {
      // 如果是对象，转换为 JSON 字符串
      displayValue = JSON.stringify(value);
    } else if (typeof value === 'string') {
      // 如果是字符串，渲染模板
      displayValue = schema ? renderTemplate(value, schema) : value;
    } else {
      displayValue = String(value ?? '');
    }

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          fontWeight: '600',
          fontSize: '14px',
          color: '#333'
        }}>
          {field.label}
        </label>
        <textarea
          value={displayValue}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder={field.description}
          rows={4}
          style={{
            width: '100%',
            padding: '10px 14px',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            backgroundColor: '#ffffff',
            fontSize: '14px',
            lineHeight: '1.5',
            color: '#333',
            boxSizing: 'border-box',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
            transition: 'all 0.2s ease',
            outline: 'none',
            resize: 'vertical',
            fontFamily: 'inherit'
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = '#007bff';
            e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0, 123, 255, 0.1)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = '#e5e7eb';
            e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
          }}
        />
        {field.description && (
          <div style={{ marginTop: '6px', color: '#6b7280', fontSize: '12px', lineHeight: '1.4' }}>
            {field.description}
          </div>
        )}
      </div>
    );
  },

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


  json: ({ field, value, onChange, disabled, schema }) => {
    // 渲染 value 中的模板变量
    let renderedValue: any;
    if (typeof value === 'object' && value !== null) {
      // 如果是对象，直接使用
      renderedValue = value;
    } else if (typeof value === 'string') {
      // 如果是字符串，尝试解析为 JSON 或渲染模板
      const templateRendered = schema ? renderTemplate(value, schema) : value;
      try {
        renderedValue = JSON.parse(templateRendered);
      } catch {
        renderedValue = templateRendered;
      }
    } else {
      renderedValue = value;
    }

    const [jsonValue, setJsonValue] = useState(
      typeof renderedValue === 'object' ? JSON.stringify(renderedValue, null, 2) : String(renderedValue || '{}')
    );
    const [isValid, setIsValid] = useState(true);

    useEffect(() => {
      const newJsonValue = typeof renderedValue === 'object' ? JSON.stringify(renderedValue, null, 2) : String(renderedValue || '{}');
      setJsonValue(newJsonValue);
    }, [renderedValue]);

    const handleChange = (newValue: string) => {
      setJsonValue(newValue);

      try {
        const parsed = JSON.parse(newValue);
        setIsValid(true);
        onChange(parsed);
      } catch (e) {
        setIsValid(false);
      }
    };

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <textarea
          value={jsonValue}
          onChange={(e) => handleChange(e.target.value)}
          disabled={disabled}
          placeholder={field.description || '{"key": "value"}'}
          rows={8}
          style={{
            width: '100%',
            padding: '12px',
            border: `1px solid ${isValid ? '#ddd' : '#ff4444'}`,
            borderRadius: '4px',
            background: '#f8f8f8',
            fontSize: '14px',
            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
            boxSizing: 'border-box',
            resize: 'vertical'
          }}
        />
        {!isValid && (
          <div style={{ color: '#ff4444', fontSize: '12px', marginTop: '4px' }}>
            无效的JSON格式
          </div>
        )}
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
    // HTML字段是只读的，不支持编辑
    // 渲染 HTML 内容中的模板变量
    const renderedHtml = renderTemplate(value, schema);
    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <div
          style={{
            border: '1px solid #ddd',
            borderRadius: '4px',
            padding: '12px',
            backgroundColor: '#f9f9f9',
            minHeight: '100px',
            maxHeight: '400px',
            overflow: 'auto'
          }}
          dangerouslySetInnerHTML={{ __html: renderedHtml }}
        />
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
    const typeStyles: Record<string, { background: string; color: string }> = {
      default: { background: '#f0f0f0', color: '#333' },
      success: { background: '#d4edda', color: '#155724' },
      warning: { background: '#fff3cd', color: '#856404' },
      error: { background: '#f8d7da', color: '#721c24' },
      info: { background: '#e7f3ff', color: '#004085' }
    };

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {tags.map((tag: any, index: number) => {
            const tagType = tag.type || 'default';
            const styles = typeStyles[tagType] || typeStyles.default;
            return (
              <span
                key={index}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '4px 12px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '500',
                  background: styles.background,
                  color: styles.color
                }}
              >
                {tag.label || tag}
              </span>
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
    const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        {showLabel && (
          <div style={{ marginBottom: '8px', fontSize: '14px', color: '#666' }}>
            进度: {current} / {total} ({percentage}%)
          </div>
        )}
        <div
          style={{
            width: '100%',
            height: '8px',
            background: '#e0e0e0',
            borderRadius: '4px',
            overflow: 'hidden'
          }}
        >
          <div
            style={{
              width: `${percentage}%`,
              height: '100%',
              background: '#007bff',
              transition: 'width 0.3s ease'
            }}
          />
        </div>
      </div>
    );
  },

  badge: ({ field, value }) => {
    const badgeConfig = value || {};
    const displayCount = badgeConfig.count !== undefined
      ? (badgeConfig.count > (badgeConfig.max || 99) ? `${badgeConfig.max}+` : badgeConfig.count)
      : undefined;

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <div style={{ position: 'relative', display: 'inline-block' }}>
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
          {(badgeConfig.dot || (displayCount !== undefined && (badgeConfig.showZero || displayCount !== 0))) && (
            <span
              style={{
                position: 'absolute',
                top: '-8px',
                right: '-8px',
                minWidth: badgeConfig.dot ? '8px' : '20px',
                height: badgeConfig.dot ? '8px' : '20px',
                borderRadius: '10px',
                background: badgeConfig.color || '#f5222d',
                color: '#fff',
                fontSize: badgeConfig.dot ? '0' : '12px',
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: badgeConfig.dot ? '0' : '0 6px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                zIndex: 10
              }}
            >
              {badgeConfig.dot ? '' : displayCount}
            </span>
          )}
        </div>
      </div>
    );
  },

  table: ({ field, value }) => (
    <Table field={field} value={value} />
  ),
  
  modal: ({ value, onChange }) => {
    const modalState = value || { visible: false };
    const visible = modalState.visible || false;
    const childrenHtml = modalState.content || '';

    return (
      <div style={{ marginBottom: '16px' }}>
        {visible && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.45)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
              cursor: 'pointer'
            }}
            onClick={() => {
              onChange({ ...modalState, visible: false });
            }}
          >
            <div
              style={{
                background: '#fff',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                width: modalState.width || 520,
                maxWidth: '90vw',
                maxHeight: '90vh',
                display: 'flex',
                flexDirection: 'column',
                cursor: 'default'
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {modalState.title && (
                <div
                  style={{
                    padding: '16px 24px',
                    borderBottom: '1px solid #f0f0f0',
                    fontSize: '16px',
                    fontWeight: '600',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <span>{modalState.title}</span>
                  <button
                    onClick={() => {
                      onChange({ ...modalState, visible: false });
                    }}
                    style={{
                      background: 'none',
                      border: 'none',
                      fontSize: '20px',
                      cursor: 'pointer',
                      color: '#999',
                      padding: 0,
                      lineHeight: 1
                    }}
                  >
                    ×
                  </button>
                </div>
              )}
              <div
                style={{
                  padding: '24px',
                  overflow: 'auto',
                  flex: 1
                }}
                dangerouslySetInnerHTML={{ __html: childrenHtml }}
              />
              <div
                style={{
                  padding: '16px 24px',
                  borderTop: '1px solid #f0f0f0',
                  display: 'flex',
                  justifyContent: 'flex-end',
                  gap: '12px'
                }}
              >
                <button
                  onClick={() => {
                    onChange({ ...modalState, visible: false });
                  }}
                  style={{
                    padding: '8px 24px',
                    borderRadius: '4px',
                    border: '1px solid #d9d9d9',
                    background: '#fff',
                    color: '#666',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  {modalState.cancelText || '取消'}
                </button>
                <button
                  onClick={() => {
                    if (modalState.onOk) modalState.onOk();
                    onChange({ ...modalState, visible: false });
                  }}
                  style={{
                    padding: '8px 24px',
                    borderRadius: '4px',
                    border: 'none',
                    background: '#007bff',
                    color: '#fff',
                    fontSize: '14px',
                    cursor: 'pointer'
                  }}
                >
                  {modalState.okText || '确定'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
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
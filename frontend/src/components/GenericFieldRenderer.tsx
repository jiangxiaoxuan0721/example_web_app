/** 通用字段渲染器 - 基于类型注册表的可扩展渲染 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import type { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';
import { useFieldPatch } from '../store/schemaStore';
import { useEventEmitter } from '../utils/eventEmitter';
import ImageRenderer from './ImageRenderer';

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
  text: ({ field, value, onChange, disabled, highlighted }) => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <input
        type="text"
        value={String(value || '')}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={field.description}
        style={{
          width: '100%',
          padding: '12px',
          border: highlighted ? '3px solid #007bff' : '1px solid #ddd',
          borderRadius: '4px',
          background: '#fff',
          fontSize: '16px',
          boxSizing: 'border-box',
          boxShadow: highlighted ? '0 0 8px rgba(0, 123, 255, 0.6)' : 'none',
          transition: 'all 0.3s ease'
        }}
      />
    </div>
  ),

  number: ({ field, value, onChange, disabled, highlighted }) => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
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
          padding: '12px',
          border: highlighted ? '3px solid #007bff' : '1px solid #ddd',
          borderRadius: '4px',
          background: '#fff',
          fontSize: '16px',
          boxSizing: 'border-box',
          boxShadow: highlighted ? '0 0 8px rgba(0, 123, 255, 0.6)' : 'none',
          transition: 'all 0.3s ease'
        }}
      />
    </div>
  ),
  
  textarea: ({ field, value, onChange, disabled }) => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <textarea
        value={String(value || '')}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={field.description}
        rows={4}
        style={{
          width: '100%',
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: '#fff',
          fontSize: '16px',
          boxSizing: 'border-box',
          resize: 'vertical'
        }}
      />
    </div>
  ),
  
  checkbox: ({ field, value, onChange, disabled }) => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'flex', alignItems: 'center', fontWeight: 'bold' }}>
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          style={{ marginRight: '8px' }}
        />
        {field.label}
      </label>
      {field.description && (
        <div style={{ marginLeft: '20px', color: '#666', fontSize: '14px' }}>
          {field.description}
        </div>
      )}
    </div>
  ),
  
  select: ({ field, value, onChange, disabled, highlighted }) => (
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      <select
        value={value !== undefined ? String(value) : ''}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        style={{
          width: '100%',
          padding: '12px',
          border: highlighted ? '3px solid #007bff' : '1px solid #ddd',
          borderRadius: '4px',
          background: '#fff',
          fontSize: '16px',
          boxSizing: 'border-box',
          boxShadow: highlighted ? '0 0 8px rgba(0, 123, 255, 0.6)' : 'none',
          transition: 'all 0.3s ease'
        }}
      >
        <option value="">请选择...</option>
        {field.options?.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  ),
  
  json: ({ field, value, onChange, disabled }) => {
    const [jsonValue, setJsonValue] = useState(
      typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value || '{}')
    );
    const [isValid, setIsValid] = useState(true);
    
    useEffect(() => {
      const newJsonValue = typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value || '{}');
      setJsonValue(newJsonValue);
    }, [value]);
    
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
    <div style={{ marginBottom: '16px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
        {field.label}
      </label>
      {field.options?.map((option) => (
        <div key={option.value} style={{ marginBottom: '4px' }}>
          <label style={{ display: 'flex', alignItems: 'center' }}>
            <input
              type="radio"
              name={`radio-${field.key}`}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              disabled={disabled}
              style={{ marginRight: '8px' }}
            />
            {option.label}
          </label>
        </div>
      ))}
    </div>
  ),
  
  html: ({ field, value }) => {
    // HTML字段是只读的，不支持编辑
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
          dangerouslySetInnerHTML={{ __html: String(value || '') }}
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

  const renderer = fieldRenderers[field.type] || fieldRenderers.text;

  return renderer({
    field,
    schema,
    bindPath,
    value: localValue,
    onChange: handleChange,
    disabled,
    highlighted
  });
}
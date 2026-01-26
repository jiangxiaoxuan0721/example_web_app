/** 通用字段渲染器 - 基于类型注册表的可扩展渲染 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import type { FieldConfig } from '../types/schema';
import type { UISchema } from '../types/schema';
import { useFieldPatch } from '../store/schemaStore';
import { useMultiInstanceStore } from '../store/multiInstanceStore';
import { useEventEmitter } from '../utils/eventEmitter';
import { renderTemplate, renderFieldTemplate } from '../utils/template';
import ImageRenderer from './ImageRenderer';
import ImageModal from './ImageModal';
import BlockRenderer from './BlockRenderer';

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
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
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
        {field.description && (
          <div style={{ marginTop: '4px', color: '#666', fontSize: '12px' }}>
            {field.description}
          </div>
        )}
      </div>
    );
  },

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
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
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
            padding: '12px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            background: '#fff',
            fontSize: '16px',
            boxSizing: 'border-box',
            resize: 'vertical'
          }}
        />
        {field.description && (
          <div style={{ marginTop: '4px', color: '#666', fontSize: '12px' }}>
            {field.description}
          </div>
        )}
      </div>
    );
  },

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

  multiselect: ({ field, value, onChange, disabled, highlighted }) => {
    const selectedOptions = Array.isArray(value) ? value : [];

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {field.options?.map((option) => {
            const isSelected = selectedOptions.includes(option.value);
            return (
              <label
                key={option.value}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '8px 12px',
                  border: highlighted && isSelected ? '2px solid #007bff' : '1px solid #ddd',
                  borderRadius: '4px',
                  background: isSelected ? '#007bff' : '#fff',
                  color: isSelected ? '#fff' : '#333',
                  cursor: disabled ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s',
                  opacity: disabled ? 0.6 : 1,
                  boxShadow: highlighted && isSelected ? '0 0 8px rgba(0, 123, 255, 0.6)' : 'none'
                }}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => {
                    if (isSelected) {
                      onChange(selectedOptions.filter((v: string) => v !== option.value));
                    } else {
                      onChange([...selectedOptions, option.value]);
                    }
                  }}
                  disabled={disabled}
                  style={{ marginRight: '8px' }}
                />
                {option.label}
              </label>
            );
          })}
        </div>
        {field.description && (
          <div style={{ marginTop: '8px', color: '#666', fontSize: '14px' }}>
            {field.description}
          </div>
        )}
      </div>
    );
  },

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

  table: ({ field, value }) => {
    const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
    const [imageModalOpen, setImageModalOpen] = useState(false);
    const [currentImage, setCurrentImage] = useState<{ url: string; title?: string; alt?: string } | null>(null);

    const columns = field.columns || [];
    const data = Array.isArray(value) ? value : [];
    const rowKey = field.rowKey || 'id';
    const bordered = field.bordered !== false;
    const striped = field.striped !== false;
    const hover = field.hover !== false;
    const emptyText = field.emptyText || '暂无数据';
    const showHeader = field.showHeader !== false;
    const compact = field.compact || false;
    const maxHeight = field.maxHeight;

    // 排序处理
    const handleSort = (columnKey: string) => {
      setSortConfig((prevConfig) => {
        if (prevConfig?.key === columnKey) {
          // 切换排序方向
          if (prevConfig.direction === 'asc') {
            return { key: columnKey, direction: 'desc' };
          } else {
            return null; // 取消排序
          }
        } else {
          return { key: columnKey, direction: 'asc' }; // 新列，升序
        }
      });
    };

    // 排序数据
    const sortedData = useMemo(() => {
      if (!sortConfig) return data;

      return [...data].sort((a, b) => {
        const aValue = a[sortConfig.key];
        const bValue = b[sortConfig.key];

        if (aValue === bValue) return 0;

        let comparison = 0;
        if (aValue < bValue) comparison = -1;
        else comparison = 1;

        return sortConfig.direction === 'desc' ? -comparison : comparison;
      });
    }, [data, sortConfig]);

    // 简单的表达式求值器
    const evaluateExpression = (expr: string, val: any): any => {
      if (!expr || typeof expr !== 'string') return val;
      try {
        // 支持 value => xxx 格式的箭头函数表达式
        const match = expr.match(/^value\s*=>\s*(.+)$/);
        if (match) {
          const body = match[1];
          // 简单的条件表达式求值
          const conditions = body.split('?');
          if (conditions.length === 3) {
            const condition = conditions[0].trim();
            const trueValue = conditions[1].trim();
            const falseValue = conditions[2].trim();
            // 简单的相等比较
            if (condition.includes('===') || condition.includes('==')) {
              const [left, right] = condition.split(/===?/).map(s => s.trim());
              const leftVal = left === 'value' ? val : left.replace(/['"]/g, '');
              const rightVal = right.replace(/['"]/g, '');
              const isMatch = String(leftVal) === rightVal;
              return isMatch ? trueValue.replace(/['"]/g, '') : falseValue.replace(/['"]/g, '');
            } else {
              // 处理简单的布尔值判断 (value ? 'success' : 'default')
              let conditionVal = val;
              if (condition === 'value') {
                conditionVal = val;
              } else {
                // 尝试求值
                try {
                  conditionVal = new Function('value', `return ${condition}`)(val);
                } catch {
                  conditionVal = val;
                }
              }
              return conditionVal ? trueValue.replace(/['"]/g, '') : falseValue.replace(/['"]/g, '');
            }
          }
        }
        return val;
      } catch (e) {
        console.warn('Expression evaluation failed:', e);
        return val;
      }
    };

    // 渲染单元格内容
    const renderCell = (column: any, val: any, record: any, index: number) => {
      // 如果有 renderType，使用内置渲染器
      if (column.renderType) {
        switch (column.renderType) {
          case 'mixed':
            // 组合多个元素 - 支持 FreeRenderer 渲染
            if (!column.components || column.components.length === 0) {
              return String(val || '');
            }

            return (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                flexWrap: 'wrap',
                justifyContent: column.align || 'left'
              }}>
                {column.components.map((comp: any, compIndex: number) => {
                  const componentValue = comp.field ? record[comp.field] : val;

                  switch (comp.type) {
                    case 'text':
                      return (
                        <span key={compIndex} style={{
                          fontSize: '14px',
                          color: '#333',
                          marginLeft: comp.margin || 0
                        }}>
                          {comp.text || componentValue}
                        </span>
                      );

                    case 'tag':
                      let tagType = 'default';
                      if (comp.tagType) {
                        const match = comp.tagType.match(/value\s*===?\s*['"]?([^'"']+)['"]?/);
                        if (match && match[1] === String(componentValue)) {
                          tagType = comp.tagType.split('=>')[1]?.trim().replace(/['"]/g, '') || 'default';
                        } else if (['success', 'warning', 'error', 'info'].includes(comp.tagType)) {
                          tagType = comp.tagType;
                        }
                      } else {
                        // 自动判断
                        if (['success', 'active', 'completed', 'done'].includes(String(componentValue))) tagType = 'success';
                        else if (['warning', 'pending', 'waiting'].includes(String(componentValue))) tagType = 'warning';
                        else if (['error', 'failed', 'danger', 'rejected'].includes(String(componentValue))) tagType = 'error';
                        else if (['info', 'processing'].includes(String(componentValue))) tagType = 'info';
                      }

                      const tagStyles: Record<string, any> = {
                        default: { background: '#e9ecef', color: '#495057' },
                        success: { background: '#d4edda', color: '#155724' },
                        warning: { background: '#fff3cd', color: '#856404' },
                        error: { background: '#f8d7da', color: '#721c24' },
                        info: { background: '#d1ecf1', color: '#0c5460' }
                      };
                      const style = tagStyles[tagType] || tagStyles.default;

                      return (
                        <span key={compIndex} style={{
                          display: 'inline-block',
                          padding: '4px 12px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '500',
                          ...style,
                          marginLeft: comp.margin || 0
                        }}>
                          {componentValue}
                        </span>
                      );

                    case 'badge':
                      return (
                        <span key={compIndex} style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          minWidth: '20px',
                          height: '20px',
                          padding: '0 6px',
                          borderRadius: '10px',
                          background: comp.badgeColor || '#f5222d',
                          color: '#fff',
                          fontSize: '12px',
                          fontWeight: 'bold',
                          marginLeft: comp.margin || 0
                        }}>
                          {componentValue}
                        </span>
                      );

                    case 'progress':
                      const current = componentValue?.current || 0;
                      const total = componentValue?.total || 100;
                      const percent = total > 0 ? (current / total) * 100 : 0;
                      return (
                        <div key={compIndex} style={{
                          width: '100px',
                          marginLeft: comp.margin || 0
                        }}>
                          <div style={{
                            height: '6px',
                            background: '#e9ecef',
                            borderRadius: '3px',
                            overflow: 'hidden'
                          }}>
                            <div style={{
                              width: `${percent}%`,
                              height: '100%',
                              background: '#007bff',
                              transition: 'width 0.3s'
                            }} />
                          </div>
                        </div>
                      );

                    case 'image':
                      return (
                        <img
                          key={compIndex}
                          src={componentValue}
                          alt=""
                          style={{
                            width: comp.imageSize || '32px',
                            height: comp.imageSize || '32px',
                            objectFit: comp.imageFit || 'cover',
                            borderRadius: '4px',
                            marginLeft: comp.margin || 0
                          }}
                        />
                      );

                    case 'button':
                      const buttonStyle = comp.buttonStyle || 'primary';
                      const buttonStyles: Record<string, any> = {
                        primary: {
                          background: '#007bff',
                          color: '#fff',
                          border: 'none'
                        },
                        secondary: {
                          background: '#fff',
                          color: '#007bff',
                          border: '1px solid #007bff'
                        },
                        danger: {
                          background: '#dc3545',
                          color: '#fff',
                          border: 'none'
                        }
                      };
                      const sizeStyles: Record<string, any> = {
                        small: { padding: '4px 12px', fontSize: '12px' },
                        medium: { padding: '6px 16px', fontSize: '14px' },
                        large: { padding: '8px 20px', fontSize: '16px' }
                      };

                      return (
                        <button
                          key={compIndex}
                          onClick={() => {
                            console.log(`[Table Button] Clicked on row ${index}, action: ${comp.actionType}`, comp.actionData);
                            // 可以通过事件发送到后端
                            // emitFieldChange 可以用于发送操作事件
                          }}
                          style={{
                            padding: '6px 16px',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontWeight: '500',
                            transition: 'all 0.2s',
                            ...buttonStyles[buttonStyle],
                            ...sizeStyles[comp.buttonSize || 'medium'],
                            marginLeft: comp.margin || 0
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.opacity = '0.8';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.opacity = '1';
                          }}
                        >
                          {comp.buttonLabel || '操作'}
                        </button>
                      );

                    case 'spacer':
                      return (
                        <div key={compIndex} style={{
                          width: comp.width || '8px',
                          flexShrink: 0
                        }} />
                      );

                    default:
                      return null;
                  }
                })}
              </div>
            );

          case 'text':
          case 'tag':
            let tagType = 'default';
            if (column.tagType) {
              if (typeof column.tagType === 'function') {
                tagType = column.tagType(val);
              } else if (typeof column.tagType === 'string') {
                tagType = evaluateExpression(column.tagType, val) || 'default';
              }
            }
            const tagStyles: Record<string, any> = {
              default: { background: '#e9ecef', color: '#495057' },
              success: { background: '#d4edda', color: '#155724' },
              warning: { background: '#fff3cd', color: '#856404' },
              error: { background: '#f8d7da', color: '#721c24' },
              info: { background: '#d1ecf1', color: '#0c5460' }
            };
            const style = tagStyles[tagType] || tagStyles.default;

            // 支持自定义渲染文本配置
            let displayValue = val;
            if (column.renderText) {
              if (typeof column.renderText === 'function') {
                displayValue = column.renderText(val);
              } else if (typeof column.renderText === 'string') {
                // 支持简单的文本映射格式: "true:已完成|false:未完成"
                const mappings = column.renderText.split('|');
                for (const mapping of mappings) {
                  const [key, text] = mapping.split(':');
                  if (String(val) === key.trim()) {
                    displayValue = text;
                    break;
                  }
                }
              }
            } else if (typeof val === 'boolean') {
              // 默认的布尔值显示（向后兼容）
              displayValue = val ? '已完成' : '未完成';
            }

            return (
              <span style={{
                display: 'inline-block',
                padding: '4px 12px',
                borderRadius: '4px',
                fontSize: '12px',
                fontWeight: '500',
                ...style
              }}>
                {displayValue}
              </span>
            );
          case 'badge':
            return (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                minWidth: '20px',
                height: '20px',
                padding: '0 6px',
                borderRadius: '10px',
                background: column.badgeColor || '#f5222d',
                color: '#fff',
                fontSize: '12px',
                fontWeight: 'bold'
              }}>
                {val}
              </span>
            );
          case 'progress':
            const current = val?.current || 0;
            const total = val?.total || 100;
            const percent = total > 0 ? (current / total) * 100 : 0;
            return (
              <div style={{ width: '100%' }}>
                <div style={{
                  height: '6px',
                  background: '#e9ecef',
                  borderRadius: '3px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${percent}%`,
                    height: '100%',
                    background: '#007bff',
                    transition: 'width 0.3s'
                  }} />
                </div>
              </div>
            );
          case 'image':
            const imageSrc = typeof val === 'string' ? val : (val?.url || '');
            const imageTitle = typeof val === 'object' ? (val?.title || column.label) : column.label;

            if (!imageSrc) {
              return <span style={{ color: '#999', fontSize: '12px' }}>无图片</span>;
            }

            // 使用全屏模态框查看
            return (
              <>
                <button
                  onClick={() => {
                    setCurrentImage({ url: imageSrc, title: imageTitle });
                    setImageModalOpen(true);
                  }}
                  style={{
                    padding: '6px 16px',
                    borderRadius: '4px',
                    border: '1px solid #007bff',
                    background: '#fff',
                    color: '#007bff',
                    fontSize: '12px',
                    cursor: 'pointer',
                    fontWeight: '500',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#007bff';
                    e.currentTarget.style.color = '#fff';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#fff';
                    e.currentTarget.style.color = '#007bff';
                  }}
                >
                  点击查看
                </button>
                {/* 图片模态框 */}
                {currentImage && currentImage.url === imageSrc && (
                  <ImageModal
                    visible={imageModalOpen}
                    url={currentImage.url}
                    title={currentImage.title}
                    alt={imageTitle}
                    onClose={() => {
                      setImageModalOpen(false);
                      setCurrentImage(null);
                    }}
                  />
                )}
              </>
            );
        }
      }

      // 如果有自定义 render 函数，使用它
      if (typeof column.render === 'function') {
        return column.render(val, record, index);
      }

      // 默认文本渲染
      return String(val || '');
    };

    if (!data || data.length === 0) {
      return (
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            {field.label}
          </label>
          <div
            style={{
              padding: '40px',
              textAlign: 'center',
              color: '#999',
              background: '#f9f9f9',
              borderRadius: '8px'
            }}
          >
            {emptyText}
          </div>
        </div>
      );
    }

    return (
      <div style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
          {field.label}
        </label>
        <div
          style={{
            overflowX: 'auto',
            maxHeight: maxHeight,
            overflowY: maxHeight ? 'auto' : 'visible'
          }}
        >
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              background: '#fff',
              borderRadius: '8px',
              overflow: 'hidden'
            }}
          >
            {showHeader && (
              <thead
                style={{
                  background: '#f8f9fa',
                  borderBottom: bordered ? '2px solid #dee2e6' : 'none',
                  position: 'sticky',
                  top: 0,
                  zIndex: 1
                }}
              >
                <tr>
                  {columns.map((column: any) => {
                    const isSorted = sortConfig?.key === column.key;
                    const sortIcon = isSorted && sortConfig
                      ? (sortConfig.direction === 'asc' ? '↑' : '↓')
                      : (column.sortable ? '↕' : '');

                    return (
                      <th
                        key={column.key}
                        onClick={() => column.sortable && handleSort(column.key)}
                        style={{
                          padding: compact ? '8px 12px' : '12px 16px',
                          textAlign: column.align || 'left',
                          fontWeight: '600',
                          color: '#495057',
                          fontSize: '14px',
                          borderBottom: '1px solid #dee2e6',
                          width: column.width,
                          whiteSpace: 'nowrap',
                          cursor: column.sortable ? 'pointer' : 'default',
                          userSelect: 'none',
                          background: isSorted ? '#e7f3ff' : 'transparent',
                          transition: 'background 0.2s'
                        }}
                      >
                        {column.label}
                        <span style={{ marginLeft: '4px', color: isSorted ? '#007bff' : '#999' }}>
                          {sortIcon}
                        </span>
                      </th>
                    );
                  })}
                </tr>
              </thead>
            )}
            <tbody>
              {sortedData.map((record: any, index: number) => {
                const rowKeyVal = record[rowKey] || index;

                return (
                  <tr
                    key={rowKeyVal}
                    style={{
                      borderBottom: bordered ? '1px solid #dee2e6' : 'none',
                      transition: 'background 0.2s',
                      ...(striped && index % 2 === 0 && { background: '#f8f9fa' })
                    }}
                    onMouseEnter={(e) => {
                      if (hover) {
                        e.currentTarget.style.background = '#e9ecef';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = '';
                    }}
                  >
                    {columns.map((column: any) => {
                      const val = record[column.key];
                      return (
                        <td
                          key={column.key}
                          style={{
                            padding: compact ? '8px 12px' : '12px 16px',
                            textAlign: column.align || 'left',
                            fontSize: '14px',
                            color: '#212529',
                            borderBottom: bordered ? '1px solid #dee2e6' : 'none'
                          }}
                        >
                          {renderCell(column, val, record, index)}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {field.showPagination && data.length > 0 && (
          <div style={{
            marginTop: '12px',
            padding: '12px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: '#f8f9fa',
            borderRadius: '4px'
          }}>
            <span style={{ fontSize: '14px', color: '#666' }}>
              共 {data.length} 条记录
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                disabled
                style={{
                  padding: '6px 12px',
                  border: '1px solid #dee2e6',
                  background: '#fff',
                  borderRadius: '4px',
                  cursor: 'not-allowed',
                  color: '#999'
                }}
              >
                上一页
              </button>
              <span style={{ padding: '6px 12px' }}>
                1
              </span>
              <button
                disabled
                style={{
                  padding: '6px 12px',
                  border: '1px solid #dee2e6',
                  background: '#fff',
                  borderRadius: '4px',
                  cursor: 'not-allowed',
                  color: '#999'
                }}
              >
                下一页
              </button>
            </div>
          </div>
        )}
      </div>
    );
  },

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
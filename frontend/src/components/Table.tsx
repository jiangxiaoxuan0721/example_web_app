/** 增强表格组件 - 支持排序、分页、多种渲染类型 */

import { useState, useMemo, useEffect } from 'react';
import { useEventEmitter } from '../utils/eventEmitter';
import { useFieldPatch } from '../store/schemaStore';
import ImageModal from './ImageModal';
import { renderTemplate } from '../utils/template';
import type { FieldConfig, TableColumn } from '../types/schema';

// 扩展列配置，添加 Table 组件特有的属性
export interface Column extends Omit<TableColumn, 'components' | 'tagType'> {
  tagType?: string | ((val: any) => string);
  renderText?: string | ((val: any) => string);
  components?: MixedComponent[];
  editable?: boolean;
  editType?: 'text' | 'number' | 'select';
  options?: Array<{ label: string; value: string }>;
}

// 混合渲染组件配置
interface MixedComponent {
  type: 'text' | 'tag' | 'badge' | 'progress' | 'image' | 'button' | 'spacer';
  field?: string;
  text?: string;
  tagType?: string;
  badgeColor?: string;
  buttonLabel?: string;
  buttonStyle?: 'primary' | 'secondary' | 'danger';
  buttonSize?: 'small' | 'medium' | 'large';
  actionId?: string;
  id?: string;
  confirmMessage?: string;
  params?: Record<string, any>;
  tooltip?: string;
  margin?: string;
  imageSize?: string;
  imageFit?: 'cover' | 'contain';
  width?: string;
}

interface TableProps {
  field: Pick<FieldConfig, 'key' | 'label' | 'columns' | 'rowKey' | 'bordered' | 'striped' | 'hover' | 'emptyText' | 'showHeader' | 'compact' | 'maxHeight' | 'showPagination' | 'pageSize' | 'tableEditable' | 'rowSelection'>;
  value: any[];
}

export default function Table({ field, value }: TableProps) {
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
  const [imageModalOpen, setImageModalOpen] = useState(false);
  const [currentImage, setCurrentImage] = useState<{ url: string; title?: string; alt?: string; isHtml?: boolean } | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [editingCell, setEditingCell] = useState<{ rowIndex: number; columnKey: string } | null>(null);
  const [editingValue, setEditingValue] = useState<string>('');
  const [selectedRows, setSelectedRows] = useState<Set<any>>(new Set());

  const { emitTableButtonClick } = useEventEmitter();
  const fieldPatch = useFieldPatch();

  const columns: Column[] = (field.columns as Column[]) || [];
  const data = Array.isArray(value) ? value : [];
  const rowKey = field.rowKey || 'id';
  const bordered = field.bordered !== false;
  const striped = field.striped !== false;
  const hover = field.hover !== false;
  const emptyText = field.emptyText || '暂无数据';
  const showHeader = field.showHeader !== false;
  const compact = field.compact || false;
  const maxHeight = field.maxHeight;
  const showPagination = field.showPagination !== false;
  const pageSize = field.pageSize || 10;
  const tableEditable = field.tableEditable || false;
  const rowSelection = field.rowSelection || false;

  // 排序处理
  const handleSort = (columnKey: string) => {
    setSortConfig((prevConfig) => {
      if (prevConfig?.key === columnKey) {
        if (prevConfig.direction === 'asc') {
          return { key: columnKey, direction: 'desc' };
        } else {
          return null;
        }
      } else {
        return { key: columnKey, direction: 'asc' };
      }
    });
  };

  // 行选择处理
  const handleRowSelect = (record: any) => {
    const rowKeyValue = record[rowKey];
    setSelectedRows((prevSelected) => {
      const newSelected = new Set(prevSelected);
      if (newSelected.has(rowKeyValue)) {
        newSelected.delete(rowKeyValue);
      } else {
        newSelected.add(rowKeyValue);
      }
      return newSelected;
    });
  };

  // 全选/取消全选
  const handleSelectAll = () => {
    const allSelected = selectedRows.size === paginatedData.length;
    setSelectedRows(allSelected ? new Set() : new Set(paginatedData.map((record: any) => record[rowKey])));
  };

  // 检查行是否被选中
  const isRowSelected = (record: any) => {
    return selectedRows.has(record[rowKey]);
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

  // 分页逻辑
  const totalPages = Math.ceil(sortedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = sortedData.slice(startIndex, endIndex);

  // 检查是否全选
  const isAllSelected = paginatedData.length > 0 && paginatedData.every((record: any) => selectedRows.has(record[rowKey]));

  // 同步选中行到 state
  useEffect(() => {
    if (rowSelection) {
      const fullRecords = data.filter((record: any) => selectedRows.has(record[rowKey]));
      fieldPatch('state.params', `${field.key}_selected`, fullRecords);
    }
  }, [selectedRows, data, rowSelection, field.key, rowKey, fieldPatch]);

  // 当排序或数据变化时，重置到第一页
  useMemo(() => {
    setCurrentPage(1);
  }, [data.length]);

  // 处理单元格编辑
  const handleCellEdit = (rowIndex: number, columnKey: string, newValue: any) => {
    // 更新表格数据中的对应单元格
    const updatedData = [...data];
    updatedData[startIndex + rowIndex] = {
      ...updatedData[startIndex + rowIndex],
      [columnKey]: newValue
    };

    // 通过 fieldPatch 更新到 state
    fieldPatch('state.params', field.key, updatedData);

    console.log(`[Table] 单元格编辑: row=${rowIndex}, column=${columnKey}, newValue=${newValue}`);
  };

  // 开始编辑
  const startEditing = (rowIndex: number, columnKey: string) => {
    const record = data[startIndex + rowIndex];
    const value = record[columnKey];
    
    // 如果列有 renderType（如 progress、tag 等），则不允许编辑
    const column = columns.find(col => col.key === columnKey);
    if (column?.renderType==="progress") {
      return;
    }
    
    setEditingValue(String(value ?? ''));
    setEditingCell({ rowIndex, columnKey });
  };

  // 取消编辑
  const cancelEditing = () => {
    setEditingCell(null);
    setEditingValue('');
  };

  // 保存编辑
  const saveEditing = () => {
    if (!editingCell) return;

    const { rowIndex, columnKey } = editingCell;
    const column = columns.find(col => col.key === columnKey);

    if (column) {
      let parsedValue: any = editingValue;

      // 根据编辑类型解析值
      switch (column.editType) {
        case 'number':
          parsedValue = editingValue !== '' ? parseFloat(editingValue) : null;
          break;
        case 'select':
          // select 类型直接使用值
          parsedValue = editingValue;
          break;
        default:
          // text 类型直接使用字符串
          parsedValue = editingValue;
      }

      handleCellEdit(rowIndex, columnKey, parsedValue);
    }

    cancelEditing();
  };

  // 处理键盘事件（回车保存，Escape 取消）
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      saveEditing();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      cancelEditing();
    }
  };

  // 简单的表达式求值器
  const evaluateExpression = (expr: string, val: any): any => {
    if (!expr || typeof expr !== 'string') return val;
    try {
      const match = expr.match(/^value\s*=>\s*(.+)$/);
      if (match) {
        const body = match[1];
        const conditions = body.split('?');
        if (conditions.length === 3) {
          const condition = conditions[0].trim();
          const trueValue = conditions[1].trim();
          const falseValue = conditions[2].trim();

          if (condition.includes('===') || condition.includes('==')) {
            const [left, right] = condition.split(/===?/).map(s => s.trim());
            const leftVal = left === 'value' ? val : left.replace(/['"]/g, '');
            const rightVal = right.replace(/['"]/g, '');
            const isMatch = String(leftVal) === rightVal;
            return isMatch ? trueValue.replace(/['"]/g, '') : falseValue.replace(/['"]/g, '');
          } else {
            let conditionVal = val;
            if (condition === 'value') {
              conditionVal = val;
            } else {
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
      console.warn('[evaluateExpression] Expression evaluation failed:', e, 'expr:', expr, 'val:', val);
      return val;
    }
  };

  // 渲染单元格内容
  const renderCell = (column: Column, val: any, record: any, index: number) => {
    // 如果有 renderType，使用内置渲染器
    if (column.renderType) {
      switch (column.renderType) {
        case 'mixed':
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
              {column.components.map((comp: MixedComponent, compIndex: number) => {
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
                      } else {
                        // Tag 组件会自动映射状态值到颜色类型
                        tagType = comp.tagType;
                      }
                    } else {
                      // 使用 componentValue，Tag 组件会自动映射
                      tagType = String(componentValue);
                    }

                    const tagStyles: Record<string, any> = {
                      default: { background: '#e9ecef', color: '#495057' },
                      success: { background: '#d4edda', color: '#155724' },
                      warning: { background: '#fff3cd', color: '#856404' },
                      error: { background: '#f8d7da', color: '#721c24' },
                      info: { background: '#d1ecf1', color: '#0c5460' }
                    };

                    // 根据映射规则获取实际的颜色类型
                    const mappedType = (() => {
                      const status = String(tagType).toLowerCase();
                      if (['active', 'completed', 'done', 'success', 'enabled', 'open'].includes(status)) {
                        return 'success';
                      } else if (['pending', 'waiting', 'warning', 'processing'].includes(status)) {
                        return 'warning';
                      } else if (['error', 'failed', 'danger', 'rejected'].includes(status)) {
                        return 'error';
                      } else if (['info'].includes(status)) {
                        return 'info';
                      }
                      return 'default';  // inactive, disabled, closed, 其他未知状态
                    })();

                    const style = tagStyles[mappedType] || tagStyles.default;

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
                    const trimmedSrc = String(componentValue || '').trim();
                    const isComponentHtml = trimmedSrc.startsWith('<') ||
                      (trimmedSrc.includes('<') && trimmedSrc.includes('>') &&
                       trimmedSrc.indexOf('<') < trimmedSrc.indexOf('>') &&
                       trimmedSrc.indexOf('<') < 10);

                    // 检查是否为HTML链接
                    const isHtmlLink = !isComponentHtml && (/\.(html?)(\?.*)?$/i.test(trimmedSrc) ||
                      trimmedSrc.endsWith('.html') ||
                      (trimmedSrc.includes('wave_') && trimmedSrc.includes('.html')));

                    if (isComponentHtml || isHtmlLink) {
                      return (
                        <button
                          key={compIndex}
                          onClick={() => {
                            setImageModalOpen(true);
                            setCurrentImage({ url: trimmedSrc, title: 'HTML内容', isHtml: true });
                          }}
                          style={{
                            padding: '4px 12px',
                            background: '#007bff',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '13px',
                            marginLeft: comp.margin || 0
                          }}
                        >
                          查看内容
                        </button>
                      );
                    }

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

                    const handleButtonClick = () => {
                      if (comp.confirmMessage) {
                        if (window.confirm(comp.confirmMessage)) {
                          emitTableButtonClick(
                            comp.id || `btn_${index}`,
                            comp.actionId,
                            record,
                            index,
                            comp.params,
                            undefined,
                            field.key
                          );
                        }
                      } else {
                        emitTableButtonClick(
                          comp.id || `btn_${index}`,
                          comp.actionId,
                          record,
                          index,
                          comp.params,
                          undefined,
                          field.key
                        );
                      }
                    };

                    return (
                      <button
                        key={compIndex}
                        onClick={handleButtonClick}
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
                        title={comp.tooltip || comp.buttonLabel}
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
          } else {
            // 使用 val 作为状态值，Tag 组件会自动映射
            tagType = String(val);
          }
          const tagStyles: Record<string, any> = {
            default: { background: '#e9ecef', color: '#495057' },
            success: { background: '#d4edda', color: '#155724' },
            warning: { background: '#fff3cd', color: '#856404' },
            error: { background: '#f8d7da', color: '#721c24' },
            info: { background: '#d1ecf1', color: '#0c5460' }
          };

          // 根据映射规则获取实际的颜色类型
          const mappedType = (() => {
            const status = String(tagType).toLowerCase();
            if (['active', 'completed', 'done', 'success', 'enabled', 'open'].includes(status)) {
              return 'success';
            } else if (['pending', 'waiting', 'warning', 'processing'].includes(status)) {
              return 'warning';
            } else if (['error', 'failed', 'danger', 'rejected'].includes(status)) {
              return 'error';
            } else if (['info'].includes(status)) {
              return 'info';
            }
            return 'default';  // inactive, disabled, closed, 其他未知状态
          })();

          const style = tagStyles[mappedType] || tagStyles.default;

          let displayValue = val;
          if (column.renderText) {
            if (typeof column.renderText === 'function') {
              displayValue = column.renderText(val);
            } else if (typeof column.renderText === 'string') {
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
          const imageTitle = typeof val === 'object' ? (val?.title || column.title) : column.title;

          if (!imageSrc) {
            return <span style={{ color: '#999', fontSize: '12px' }}>无内容</span>;
          }

          const trimmedSrc = imageSrc.trim();
          const isHtml = trimmedSrc.startsWith('<') || (trimmedSrc.includes('<') && trimmedSrc.includes('>') && trimmedSrc.indexOf('<') < trimmedSrc.indexOf('>') && trimmedSrc.indexOf('<') < 10);

          // 检查是否为HTML链接
          const isHtmlLink = !isHtml && (/\.(html?)(\?.*)?$/i.test(trimmedSrc) ||
            trimmedSrc.endsWith('.html') ||
            (trimmedSrc.includes('wave_') && trimmedSrc.includes('.html')));

          if (isHtml || isHtmlLink) {
            return (
              <>
                <button
                  onClick={() => {
                    setCurrentImage({ url: imageSrc, title: imageTitle || 'HTML 内容', isHtml: true });
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
                  查看内容
                </button>
                {currentImage && currentImage.url === imageSrc && (
                  <ImageModal
                    visible={imageModalOpen}
                    url={currentImage.url}
                    title={currentImage.title}
                    alt={imageTitle}
                    isHtml={true}
                    onClose={() => {
                      setImageModalOpen(false);
                      setCurrentImage(null);
                    }}
                  />
                )}
              </>
            );
          } else {
            return (
              <>
                <button
                  onClick={() => {
                    setCurrentImage({ url: imageSrc, title: imageTitle || 'image' });
                    setImageModalOpen(true);
                  }}
                  style={{
                    padding: '4px',
                    borderRadius: '4px',
                    border: '1px solid #ddd',
                    background: '#fff',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '40px',
                    minWidth: '40px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#007bff';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,123,255,0.2)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#ddd';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                  title={imageTitle || '点击查看大图'}
                >
                  <img
                    src={imageSrc}
                    alt={imageTitle || 'avatar'}
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                    onLoad={(e) => {
                      (e.target as HTMLImageElement).style.display = 'block';
                    }}
                    style={{
                      width: '32px',
                      height: '32px',
                      objectFit: 'cover',
                      borderRadius: '3px',
                      pointerEvents: 'none',
                      display: 'none'
                    }}
                  />
                </button>
                {currentImage && currentImage.url === imageSrc && (
                  <ImageModal
                    visible={imageModalOpen}
                    url={currentImage.url}
                    title={currentImage.title}
                    alt={imageTitle}
                    isHtml={false}
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
    }

    // 如果有自定义 render 函数或字符串，使用它
    if (column.render) {
      if (typeof column.render === 'function') {
        return column.render(val, record, index);
      } else if (typeof column.render === 'string') {
        // 字符串类型，进行模板渲染
        return renderTemplate(column.render, record);
      }
    }

    // 默认文本渲染
    if (val === null || val === undefined) {
      return '';
    }
    if (typeof val === 'object') {
      // 空对象显示为空字符串，非空对象显示为 JSON 字符串
      return Object.keys(val).length === 0 ? '' : JSON.stringify(val);
    }
    return String(val);
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
                {rowSelection && (
                  <th
                    style={{
                      padding: compact ? '8px 12px' : '12px 16px',
                      textAlign: 'center',
                      fontWeight: '600',
                      color: '#495057',
                      fontSize: '14px',
                      borderBottom: '1px solid #dee2e6',
                      width: '40px',
                      userSelect: 'none'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isAllSelected}
                      onChange={handleSelectAll}
                      style={{ cursor: 'pointer' }}
                    />
                  </th>
                )}
                {columns.map((column: Column) => {
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
                      {column.title}
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
            {paginatedData.map((record: any, index: number) => {
              const rowKeyVal = record[rowKey] || index;
              const actualIndex = startIndex + index;

              return (
                <tr
                  key={rowKeyVal}
                  style={{
                    borderBottom: bordered ? '1px solid #dee2e6' : 'none',
                    transition: 'background 0.2s',
                    ...(striped && actualIndex % 2 === 0 && { background: '#f8f9fa' })
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
                  {rowSelection && (
                    <td
                      style={{
                        padding: compact ? '8px 12px' : '12px 16px',
                        textAlign: 'center',
                        fontSize: '14px',
                        color: '#212529',
                        borderBottom: bordered ? '1px solid #dee2e6' : 'none',
                        background: isRowSelected(record) ? '#e6f7ff' : undefined,
                        transition: 'background 0.2s'
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isRowSelected(record)}
                        onChange={() => handleRowSelect(record)}
                        style={{ cursor: 'pointer' }}
                      />
                    </td>
                  )}
                  {columns.map((column: Column) => {
                    const val = record[column.key];
                    const isEditable = tableEditable && column.editable !== false;
                    const isEditing = editingCell?.rowIndex === index && editingCell?.columnKey === column.key;

                    return (
                      <td
                        key={column.key}
                        style={{
                          padding: compact ? '8px 12px' : '12px 16px',
                          textAlign: column.align || 'left',
                          fontSize: '14px',
                          color: '#212529',
                          borderBottom: bordered ? '1px solid #dee2e6' : 'none',
                          background: isEditing ? '#fff7e6' : undefined
                        }}
                        onClick={() => {
                          if (isEditable && !isEditing && !column.renderType) {
                            startEditing(index, column.key);
                          }
                        }}
                        onDoubleClick={() => {
                          if (isEditable && !isEditing && column.renderType !== "progress") {
                            startEditing(index, column.key);
                          }
                        }}
                      >
                        {isEditing ? (
                          // 可编辑输入框
                          <div
                            onMouseDown={(e) => e.stopPropagation()}
                            onClick={(e) => e.stopPropagation()}
                          >
                            {column.editType === 'select' ? (
                              <select
                                value={editingValue}
                                onChange={(e) => setEditingValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                onBlur={saveEditing}
                                autoFocus
                                style={{
                                  padding: '4px 8px',
                                  fontSize: '14px',
                                  border: '1px solid #007bff',
                                  borderRadius: '4px',
                                  outline: 'none',
                                  width: '100%',
                                  minWidth: '80px'
                                }}
                              >
                                <option value="">请选择</option>
                                {column.options?.map((opt, optIdx) => (
                                  <option key={optIdx} value={opt.value}>
                                    {opt.label}
                                  </option>
                                ))}
                              </select>
                            ) : (
                              <input
                                type={column.editType === 'number' ? 'number' : 'text'}
                                value={editingValue}
                                onChange={(e) => setEditingValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                onBlur={saveEditing}
                                autoFocus
                                style={{
                                  padding: '4px 8px',
                                  fontSize: '14px',
                                  border: '1px solid #007bff',
                                  borderRadius: '4px',
                                  outline: 'none',
                                  width: '100%',
                                  minWidth: '80px'
                                }}
                              />
                            )}
                          </div>
                        ) : isEditable && !column.renderType ? (
                          // 可编辑但不在编辑状态
                          <div
                            style={{
                              padding: '4px 8px',
                              borderRadius: '4px',
                              cursor: 'pointer',
                              transition: 'background 0.2s'
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.background = '#e9ecef';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.background = 'transparent';
                            }}
                          >
                            {renderCell(column, val, record, actualIndex)}
                          </div>
                        ) : (
                          // 不可编辑
                          <div>
                            {renderCell(column, val, record, actualIndex)}
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {showPagination && sortedData.length > 0 && (
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
            共 {sortedData.length} 条记录，第 {currentPage} / {totalPages} 页
          </span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              style={{
                padding: '6px 12px',
                border: '1px solid #dee2e6',
                background: '#fff',
                borderRadius: '4px',
                cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                color: currentPage === 1 ? '#999' : '#212529',
                fontSize: '14px'
              }}
            >
              首页
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              style={{
                padding: '6px 12px',
                border: '1px solid #dee2e6',
                background: '#fff',
                borderRadius: '4px',
                cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                color: currentPage === 1 ? '#999' : '#212529',
                fontSize: '14px'
              }}
            >
              上一页
            </button>

            {(() => {
              const getPageNumbers = () => {
                const pages: (number | string)[] = [];
                const maxVisiblePages = 5;

                if (totalPages <= maxVisiblePages) {
                  for (let i = 1; i <= totalPages; i++) {
                    pages.push(i);
                  }
                } else {
                  if (currentPage <= 3) {
                    for (let i = 1; i <= 4; i++) {
                      pages.push(i);
                    }
                    pages.push('...');
                    pages.push(totalPages);
                  } else if (currentPage >= totalPages - 2) {
                    pages.push(1);
                    pages.push('...');
                    for (let i = totalPages - 3; i <= totalPages; i++) {
                      pages.push(i);
                    }
                  } else {
                    pages.push(1);
                    pages.push('...');
                    for (let i = currentPage - 1; i <= currentPage + 1; i++) {
                      pages.push(i);
                    }
                    pages.push('...');
                    pages.push(totalPages);
                  }
                }
                return pages;
              };

              return getPageNumbers().map((page, idx) => (
                <button
                  key={idx}
                  onClick={() => typeof page === 'number' && setCurrentPage(page)}
                  disabled={page === '...'}
                  style={{
                    padding: '6px 12px',
                    border: '1px solid #dee2e6',
                    background: currentPage === page ? '#007bff' : '#fff',
                    color: currentPage === page ? '#fff' : '#212529',
                    borderRadius: '4px',
                    cursor: page === '...' ? 'default' : 'pointer',
                    fontSize: '14px',
                    fontWeight: currentPage === page ? '600' : 'normal'
                  }}
                >
                  {page}
                </button>
              ));
            })()}

            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              style={{
                padding: '6px 12px',
                border: '1px solid #dee2e6',
                background: '#fff',
                borderRadius: '4px',
                cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                color: currentPage === totalPages ? '#999' : '#212529',
                fontSize: '14px'
              }}
            >
              下一页
            </button>
            <button
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
              style={{
                padding: '6px 12px',
                border: '1px solid #dee2e6',
                background: '#fff',
                borderRadius: '4px',
                cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                color: currentPage === totalPages ? '#999' : '#212529',
                fontSize: '14px'
              }}
            >
              末页
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/** Block 渲染器 V2 - 使用通用渲染模板 */

import { useState } from 'react';
import type { Block, UISchema, ActionConfig } from '../types/schema';
import { useSchemaStore } from '../store/schemaStore';
import GenericFieldRenderer from './GenericFieldRenderer';
import ActionButton from './ActionButton';
import Card from './Card';
import { renderTemplate } from '../utils/template';

interface BlockRendererProps {
  block: Block;
  disabled?: boolean;
  highlightField?: string | null;
  highlightBlockId?: string | null;
  actions?: ActionConfig[];  // 可选的 block 级别 actions
}

/**
 * 块渲染器注册表接口
 */
interface BlockRendererInternalProps extends BlockRendererProps {
  schema: UISchema;
}

export interface BlockRenderer {
  (props: BlockRendererInternalProps): JSX.Element;
}

// 块渲染器注册表
const blockRenderers: Record<string, BlockRenderer> = {
  form: ({ block, schema, disabled, highlightField, highlightBlockId, actions }) => {
    const isHighlighted = highlightBlockId === block.id;
    // 确保 fields 始终是数组，处理各种可能的格式
    let fields: any[] = [];
    if (block.props?.fields) {
      if (Array.isArray(block.props.fields)) {
        fields = block.props.fields;
      } else if (typeof block.props.fields === 'object') {
        // 如果 fields 是对象，转换为数组
        fields = Object.values(block.props.fields);
      }
    }

    // 合并 block.props.actions 和传入的 actions
    const blockActions = block.props?.actions || [];
    const allActions = actions ? [...blockActions, ...actions] : blockActions;

    const handleNavigate = (targetInstance: string) => {
      // 通过 window.location 触发导航
      window.location.hash = `#instance=${targetInstance}`;
    };

    return (
      <div
        key={block.id}
        id={`block-${block.id}`}
        style={{
          marginBottom: '20px',
          padding: '20px',
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          transition: 'background-color 0.3s ease, box-shadow 0.3s ease',
          ...(isHighlighted ? {
            backgroundColor: '#fff3cd',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          } : {})
        }}
      >
        {/* 渲染字段 */}
        {fields.map((field) => (
          <GenericFieldRenderer
            key={field.key}
            field={field}
            schema={schema}
            bindPath={block.bind}
            disabled={disabled}
            highlighted={field.key === highlightField}
          />
        ))}

        {/* 渲染 block 级别的 actions */}
        {allActions.length > 0 && (
          <div
            style={{
              marginTop: '16px',
              display: 'flex',
              gap: '12px',
              flexWrap: 'wrap'
            }}
          >
            {allActions.map((action) => (
              <ActionButton
                key={action.id}
                action={action}
                highlighted={false}
                onNavigate={handleNavigate}
                blockId={block.id}
              />
            ))}
          </div>
        )}
      </div>
    );
  },

  display: ({ block, schema, highlightBlockId }) => {
    // 获取绑定路径的值
    const getValue = (path: string) => {
      const keys = path.split('.');
      return keys.reduce((obj: any, key: string) => obj?.[key], schema);
    };

    const value = getValue(block.bind);
    const isHighlighted = highlightBlockId === block.id;

    // 渲染 value 中的模板变量
    let renderedValue: any;
    if (typeof value === 'object' && value !== null) {
      // 如果是对象，转换为 JSON 字符串
      renderedValue = JSON.stringify(value, null, 2);
    } else if (typeof value === 'string') {
      // 如果是字符串，渲染模板
      renderedValue = renderTemplate(value, schema);
    } else {
      renderedValue = String(value ?? '');
    }

    return (
      <div
        key={block.id}
        id={`block-${block.id}`}
        style={{
          marginBottom: '20px',
          padding: '20px',
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          transition: 'background-color 0.3s ease, box-shadow 0.3s ease',
          ...(isHighlighted ? {
            backgroundColor: '#fff3cd',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          } : {})
        }}
      >
        <div style={{
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: '#f9f9f9',
          fontSize: '16px'
        }}>
          {typeof renderedValue === 'object' ? JSON.stringify(renderedValue, null, 2) : String(renderedValue)}
        </div>
      </div>
    );
  },

  // 布局类型 1: 标签页布局 - 支持多个选项卡
  tabs: ({ block, schema, disabled, highlightField, highlightBlockId }) => {
    const [activeTab, setActiveTab] = useState(0);
    const isHighlighted = highlightBlockId === block.id;
    const instanceId = useSchemaStore((state) => state.instanceId);

    const handleNavigate = (targetInstance: string) => {
      window.location.hash = `#instance=${targetInstance}`;
    };

    return (
      <div
        key={block.id}
        id={`block-${block.id}`}
        style={{
          marginBottom: '20px',
          padding: '20px',
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          ...(isHighlighted ? {
            backgroundColor: '#fff3cd',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          } : {})
        }}
      >
        {block.title && (
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontSize: '18px', color: '#333' }}>
            {block.title}
          </h3>
        )}
        <div style={{ marginBottom: '16px', borderBottom: '1px solid #e5e7eb' }}>
          {block.props?.tabs?.map((tab: any, index: number) => (
            <button
              key={index}
              onClick={() => setActiveTab(index)}
              style={{
                padding: '8px 16px',
                background: activeTab === index ? '#007bff' : 'transparent',
                color: activeTab === index ? '#fff' : '#666',
                border: 'none',
                borderBottom: activeTab === index ? '2px solid #007bff' : 'none',
                cursor: 'pointer',
                fontSize: '14px',
                marginRight: '8px'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div>
          {block.props?.tabs?.[activeTab]?.fields?.map((field: any) => (
            <GenericFieldRenderer
              key={field.key}
              field={field}
              schema={schema}
              bindPath={block.bind}
              disabled={disabled}
              highlighted={field.key === highlightField}
            />
          ))}
        </div>

        {/* 渲染 block 级别的 actions */}
        {block.props?.actions && block.props.actions.length > 0 && (
          <div style={{ marginTop: '16px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {block.props.actions.map((action: ActionConfig) => (
              <ActionButton
                key={action.id}
                action={action}
                highlighted={false}
                onNavigate={handleNavigate}
                blockId={block.id}
              />
            ))}
          </div>
        )}
      </div>
    );
  },

  // 布局类型 2: 网格布局 - 响应式网格
  grid: ({ block, schema, disabled, highlightField, highlightBlockId }) => {
    const isHighlighted = highlightBlockId === block.id;
    const instanceId = useSchemaStore((state) => state.instanceId);
    let fields: any[] = [];
    if (block.props?.fields) {
      if (Array.isArray(block.props.fields)) {
        fields = block.props.fields;
      } else if (typeof block.props.fields === 'object') {
        fields = Object.values(block.props.fields);
      }
    }

    const cols = block.props?.cols || 3;
    const gap = block.props?.gap || '16px';

    const handleNavigate = (targetInstance: string) => {
      window.location.hash = `#instance=${targetInstance}`;
    };

    return (
      <div
        key={block.id}
        id={`block-${block.id}`}
        style={{
          marginBottom: '20px',
          padding: '20px',
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          ...(isHighlighted ? {
            backgroundColor: '#fff3cd',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          } : {})
        }}
      >
        {block.title && (
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontSize: '18px', color: '#333' }}>
            {block.title}
          </h3>
        )}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${cols}, 1fr)`,
            gap: gap,
            flexWrap: 'wrap'
          }}
        >
          {fields.map((field) => (
            <GenericFieldRenderer
              key={field.key}
              field={field}
              schema={schema}
              bindPath={block.bind}
              disabled={disabled}
              highlighted={field.key === highlightField}
            />
          ))}
        </div>

        {/* 渲染 block 级别的 actions */}
        {block.props?.actions && block.props.actions.length > 0 && (
          <div style={{ marginTop: '16px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {block.props.actions.map((action) => (
              <ActionButton
                key={action.id}
                action={action}
                highlighted={false}
                onNavigate={handleNavigate}
                blockId={block.id}
              />
            ))}
          </div>
        )}
      </div>
    );
  },

  // 布局类型 3: 折叠面板布局
  accordion: ({ block, schema, disabled, highlightField, highlightBlockId }) => {
    const [openPanels, setOpenPanels] = useState<Set<number>>(new Set([0]));
    const isHighlighted = highlightBlockId === block.id;
    const instanceId = useSchemaStore((state) => state.instanceId);

    const togglePanel = (index: number) => {
      const newPanels = new Set(openPanels);
      if (newPanels.has(index)) {
        newPanels.delete(index);
      } else {
        newPanels.add(index);
      }
      setOpenPanels(newPanels);
    };

    const handleNavigate = (targetInstance: string) => {
      window.location.hash = `#instance=${targetInstance}`;
    };

    return (
      <div
        key={block.id}
        id={`block-${block.id}`}
        style={{
          marginBottom: '20px',
          ...(isHighlighted ? {
            backgroundColor: '#fff3cd',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          } : {})
        }}
      >
        {block.title && (
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontSize: '18px', color: '#333' }}>
            {block.title}
          </h3>
        )}
        {block.props?.panels?.map((panel: any, index: number) => {
          const panelsLength = block.props?.panels?.length || 0;
          return (
            <Card
              key={index}
              style={{
                marginBottom: index < (panelsLength - 1) ? '12px' : 0,
                cursor: 'pointer'
              }}
              title={
                <div
                  onClick={() => togglePanel(index)}
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                >
                  <span>{panel.title}</span>
                  <span style={{ fontSize: '20px', fontWeight: 'bold' }}>
                    {openPanels.has(index) ? '−' : '+'}
                  </span>
                </div>
              }
            >
              {openPanels.has(index) && panel.fields?.map((field: any) => (
                <GenericFieldRenderer
                  key={field.key}
                  field={field}
                  schema={schema}
                  bindPath={block.bind}
                  disabled={disabled}
                  highlighted={field.key === highlightField}
                />
            ))}
            {/* 渲染 panel 级别的 actions */}
            {panel.actions && panel.actions.length > 0 && (
              <div style={{ marginTop: '12px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                {panel.actions.map((action) => (
                  <ActionButton
                    key={action.id}
                    action={action}
                    highlighted={false}
                    onNavigate={handleNavigate}
                    blockId={block.id}
                  />
                ))}
              </div>
            )}
          </Card>
          );
        })}
      </div>
    );
  }
};

/**
 * 注册新的块类型渲染器
 */
export const registerBlockRenderer = (blockType: string, renderer: BlockRenderer): void => {
  blockRenderers[blockType] = renderer;
};

/**
 * 获取所有注册的块类型
 */
export const getRegisteredBlockTypes = (): string[] => {
  return Object.keys(blockRenderers);
};

/**
 * 通用块渲染器组件
 */
export default function BlockRenderer({ block, disabled, highlightField, highlightBlockId, actions }: BlockRendererProps) {
  const schema = useSchemaStore((state) => state.schema);
  const renderer = blockRenderers[block.type];

  if (!schema) {
    console.warn('[BlockRenderer] Schema not available in store');
    return null;
  }

  if (!renderer) {
    console.warn(`[BlockRenderer] Unknown block type: ${block.type}`);
    return null;
  }

  return renderer({ block, schema, disabled, highlightField, highlightBlockId, actions });
}
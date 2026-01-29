/**
 * Schema 顶层布局渲染器
 * 根据 layout.type 决定如何排列 blocks 和全局 actions
 */

import { useState } from 'react';
import type { UISchema, ActionConfig } from '../types/schema';
import BlockRenderer from './BlockRenderer';
import ActionButton from './ActionButton';

interface SchemaLayoutRendererProps {
  schema: UISchema | null | undefined;
  onNavigate: (instanceId: string) => void;
  highlightField?: string | null;
  highlightBlockId?: string | null;
  highlightActionId?: string | null;
}

/**
 * single 布局：垂直堆叠（默认）
 */
const SingleLayout = ({
  schema,
  onNavigate,
  highlightField,
  highlightBlockId,
  highlightActionId,
}: Omit<SchemaLayoutRendererProps, 'schema'> & { schema: UISchema }) => {
  return (
    <div className="pta-schema-container">
      {/* 渲染 Blocks */}
      {schema.blocks?.map((block) => (
        <BlockRenderer
          key={block.id}
          block={block}
          highlightField={highlightField}
          highlightBlockId={highlightBlockId}
        />
      ))}

      {/* 渲染全局 Actions */}
      {schema.actions && schema.actions.length > 0 && (
        <div className="pta-actions-container">
          {schema.actions.map((action) => (
            <ActionButton
              key={action.id}
              action={action}
              highlighted={action.id === highlightActionId}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * grid 布局：网格排列 blocks
 */
const GridLayout = ({
  schema,
  onNavigate,
  highlightField,
  highlightBlockId,
  highlightActionId,
}: Omit<SchemaLayoutRendererProps, 'schema'> & { schema: UISchema }) => {
  const cols = schema.layout?.columns || 2;
  const gap = schema.layout?.gap || '20px';

  return (
    <div className="pta-schema-container">
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gap: gap,
          marginBottom: '20px',
        }}
      >
        {/* 渲染 Blocks */}
        {schema.blocks?.map((block) => (
          <BlockRenderer
            key={block.id}
            block={block}
            highlightField={highlightField}
            highlightBlockId={highlightBlockId}
          />
        ))}
      </div>

      {/* 渲染全局 Actions */}
      {schema.actions && schema.actions.length > 0 && (
        <div className="pta-actions-container">
          {schema.actions.map((action) => (
            <ActionButton
              key={action.id}
              action={action}
              highlighted={action.id === highlightActionId}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * flex 布局：水平排列 blocks
 */
const FlexLayout = ({
  schema,
  onNavigate,
  highlightField,
  highlightBlockId,
  highlightActionId,
}: Omit<SchemaLayoutRendererProps, 'schema'> & { schema: UISchema }) => {
  const gap = schema.layout?.gap || '20px';

  return (
    <div className="pta-schema-container">
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: gap,
          marginBottom: '20px',
        }}
      >
        {/* 渲染 Blocks */}
        {schema.blocks?.map((block) => (
          <div key={block.id} style={{ flex: '1 1 300px', minWidth: '280px' }}>
            <BlockRenderer
              block={block}
              highlightField={highlightField}
              highlightBlockId={highlightBlockId}
            />
          </div>
        ))}
      </div>

      {/* 渲染全局 Actions */}
      {schema.actions && schema.actions.length > 0 && (
        <div className="pta-actions-container">
          {schema.actions.map((action) => (
            <ActionButton
              key={action.id}
              action={action}
              highlighted={action.id === highlightActionId}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * tabs 布局：blocks 分组到不同标签页
 */
const TabsLayout = ({
  schema,
  onNavigate,
  highlightField,
  highlightBlockId,
  highlightActionId,
}: Omit<SchemaLayoutRendererProps, 'schema'> & { schema: UISchema }) => {
  const [activeTab, setActiveTab] = useState(0);

  // 将 blocks 分配到不同标签页
  // 使用 block 的 order 属性分组，或者平均分配
  const tabCount = Math.min(schema.blocks?.length || 0, 3);
  const tabs = Array.from({ length: tabCount }, (_, index) => {
    const start = Math.floor((schema.blocks?.length || 0) * index / tabCount);
    const end = Math.floor((schema.blocks?.length || 0) * (index + 1) / tabCount);
    return schema.blocks?.slice(start, end) || [];
  });

  return (
    <div className="pta-schema-container">
      {/* 标签页导航 */}
      <div
        style={{
          marginBottom: '20px',
          borderBottom: '2px solid #e5e7eb',
          display: 'flex',
          gap: '4px',
        }}
      >
        {tabs.map((_, index) => (
          <button
            key={index}
            onClick={() => setActiveTab(index)}
            style={{
              padding: '10px 20px',
              background: 'transparent',
              border: 'none',
              borderBottom: activeTab === index ? '3px solid #007bff' : 'none',
              color: activeTab === index ? '#007bff' : '#666',
              fontWeight: activeTab === index ? '600' : '400',
              cursor: 'pointer',
              fontSize: '14px',
              transition: 'all 0.2s ease',
            }}
          >
            Tab {index + 1}
          </button>
        ))}
      </div>

      {/* 当前标签页内容 */}
      <div>
        {tabs[activeTab]?.map((block) => (
          <BlockRenderer
            key={block.id}
            block={block}
            highlightField={highlightField}
            highlightBlockId={highlightBlockId}
          />
        ))}
      </div>

      {/* 渲染全局 Actions */}
      {schema.actions && schema.actions.length > 0 && (
        <div
          style={{
            marginTop: '20px',
            padding: '20px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px',
            display: 'flex',
            gap: '12px',
            flexWrap: 'wrap',
          }}
        >
          {schema.actions.map((action) => (
            <ActionButton
              key={action.id}
              action={action}
              highlighted={action.id === highlightActionId}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * Schema 顶层布局渲染器主组件
 */
export default function SchemaLayoutRenderer(props: SchemaLayoutRendererProps) {
  const { schema } = props;

  if (!schema) {
    return null;
  }

  const layoutType = schema.layout?.type || 'single';

  // 根据布局类型渲染
  switch (layoutType) {
    case 'grid':
      return <GridLayout {...props} schema={schema} />;
    case 'flex':
      return <FlexLayout {...props} schema={schema} />;
    case 'tabs':
      return <TabsLayout {...props} schema={schema} />;
    case 'single':
    default:
      return <SingleLayout {...props} schema={schema} />;
  }
}

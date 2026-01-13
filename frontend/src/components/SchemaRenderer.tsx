import { UISchema } from '../types/schema';
import { BlockRenderer } from './BlockRenderer';
import { ActionBar } from './ActionBar';
import { useEvent } from '../hooks/useEvent';

/**
 * Schema Renderer 组件 - 完整渲染一个 UISchema
 */
export const SchemaRenderer = ({ schema }: { schema: UISchema }) => {
  const { emit } = useEvent();
  const { meta, layout, blocks, actions } = schema;

  const handleActionClick = (action: any) => {
    emit('action_click', {
      actionId: action.id,
    });
  };

  const renderLayout = () => {
    switch (layout.type) {
      case 'single':
        return (
          <div className="layout-single">
            {blocks.map((block) => (
              <div key={block.id} className="block-wrapper">
                <BlockRenderer block={block} schema={schema} />
              </div>
            ))}
          </div>
        );
      
      case 'split':
        const ratio = layout.ratio || [50, 50];
        return (
          <div className={`layout-split layout-split-${layout.direction}`}>
            {blocks.map((block, index) => (
              <div 
                key={block.id} 
                className="block-wrapper"
                style={{ flex: `${ratio[index] || 1}` }}
              >
                <BlockRenderer block={block} schema={schema} />
              </div>
            ))}
          </div>
        );
      
      case 'tabs':
        const activeTab = meta.runtime?.activeTab || 0;
        return (
          <div className="layout-tabs">
            <div className="tabs-header">
              {layout.tabs.map((tab, index) => (
                <button
                  key={index}
                  className={`tab-btn ${index === activeTab ? 'active' : ''}`}
                  onClick={() => emit('tab_change', { tabIndex: index })}
                >
                  {tab}
                </button>
              ))}
            </div>
            <div className="tabs-content">
              <BlockRenderer block={blocks[activeTab]} schema={schema} />
            </div>
          </div>
        );
      
      default:
        return <div>Unknown layout type</div>;
    }
  };

  return (
    <div className="schema-renderer">
      {/* Meta 信息（可选） */}
      {meta && (
        <div className="schema-meta">
          <span className="page-key">{meta.pageKey}</span>
          <span className="step-info">
            Step {meta.step.current} / {meta.step.total}
          </span>
          <span className={`status status-${meta.status}`}>
            {meta.status}
          </span>
        </div>
      )}

      {/* 渲染布局 */}
      {renderLayout()}

      {/* 渲染 Actions */}
      <ActionBar
        actions={actions}
        onActionClick={handleActionClick}
        disabled={meta.status === 'locked'}
      />
    </div>
  );
};

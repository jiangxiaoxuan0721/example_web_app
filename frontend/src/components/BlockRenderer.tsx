/** Block 渲染器 V2 - 使用通用渲染模板 */

import type { Block, UISchema } from '../types/schema';
import { useSchemaStore } from '../store/schemaStore';
import GenericFieldRenderer from './GenericFieldRenderer';

interface BlockRendererProps {
  block: Block;
  disabled?: boolean;
  highlightField?: string | null;
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
  form: ({ block, schema, disabled, highlightField }) => (
    <div key={block.id} id={`block-${block.id}`} style={{ marginBottom: '20px' }}>
      {block.props?.fields?.map((field) => (
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
  ),

  display: ({ block, schema }) => {
    // 获取绑定路径的值
    const getValue = (path: string) => {
      const keys = path.split('.');
      return keys.reduce((obj: any, key: string) => obj?.[key], schema);
    };

    const value = getValue(block.bind);

    return (
      <div key={block.id} id={`block-${block.id}`} style={{ marginBottom: '20px' }}>
        <div style={{
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          background: '#f9f9f9',
          fontSize: '16px'
        }}>
          {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
        </div>
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
export default function BlockRenderer({ block, disabled, highlightField }: BlockRendererProps) {
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

  return renderer({ block, schema, disabled, highlightField });
}
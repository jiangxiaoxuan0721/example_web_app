/** JSON 查看器组件 */

import { useState } from 'react';

interface JSONViewerProps {
  data: any;
  expandDepth?: number;
  showLineNumbers?: boolean;
}

interface TreeNodeProps {
  data: any;
  key?: string;
  isLast?: boolean;
  expandDepth?: number;
  currentDepth?: number;
  showLineNumbers?: boolean;
  path?: string;
}

function TreeNode({ data, key, isLast, expandDepth = 2, currentDepth = 0, showLineNumbers = false, path = '' }: TreeNodeProps) {
  const [expanded, setExpanded] = useState(currentDepth < expandDepth);
  const currentPath = path ? `${path}.${key}` : key;

  const getDataType = (value: any): string => {
    if (value === null) return 'null';
    if (Array.isArray(value)) return 'Array';
    if (typeof value === 'object') return 'Object';
    return typeof value;
  };

  const dataType = getDataType(data);
  const isExpandable = dataType === 'Object' || dataType === 'Array';
  const isArray = dataType === 'Array';

  if (!isExpandable) {
    return (
      <div style={{ lineHeight: '1.6' }}>
        {showLineNumbers && <span style={{ color: '#999', marginRight: '8px', minWidth: '40px', display: 'inline-block' }}></span>}
        <span style={{ color: '#7d8799' }}>
          {key !== undefined && <span style={{ color: '#e06c75' }}>"{key}"</span>}
          {key !== undefined && <span style={{ color: '#999' }}>: </span>}
          <span style={{ color: '#98c379' }}>
            {typeof data === 'string' ? `"${data}"` : String(data)}
          </span>
          {!isLast && <span style={{ color: '#999' }}>,</span>}
        </span>
      </div>
    );
  }

  const entries = isArray ? data : Object.entries(data);

  return (
    <div style={{ marginLeft: currentDepth * 16 }}>
      <div
        style={{
          cursor: 'pointer',
          userSelect: 'none'
        }}
        onClick={() => setExpanded(!expanded)}
      >
        {showLineNumbers && <span style={{ color: '#999', marginRight: '8px', minWidth: '40px', display: 'inline-block' }}></span>}
        <span style={{ color: '#e06c75' }}>
          {expanded ? '▼' : '▶'}
        </span>
        <span style={{ color: '#7d8799', marginLeft: '4px' }}>
          {key !== undefined && <span style={{ color: '#e06c75' }}>"{key}"</span>}
          {key !== undefined && <span style={{ color: '#999' }}>: </span>}
          <span style={{ color: '#e06c75' }}>
            {isArray ? `Array(${data.length})` : `Object${Object.keys(data).length > 0 ? ` {${Object.keys(data).length}}` : ''}`}
          </span>
          {!isLast && <span style={{ color: '#999' }}>,</span>}
        </span>
      </div>

      {expanded && (
        <div style={{ marginLeft: '8px' }}>
          {entries.map((entry: any, index: number) => {
            const itemKey = isArray ? index : entry[0];
            const itemValue = isArray ? entry : entry[1];
            const isItemLast = index === entries.length - 1;

            return (
              <TreeNode
                key={String(itemKey)}
                data={itemValue}
                isLast={isItemLast}
                expandDepth={expandDepth}
                currentDepth={currentDepth + 1}
                showLineNumbers={showLineNumbers}
                path={currentPath}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function JSONViewer({ data, expandDepth = 2, showLineNumbers = false }: JSONViewerProps) {
  return (
    <div
      style={{
        background: '#282c34',
        borderRadius: '8px',
        padding: '16px',
        overflow: 'auto',
        fontFamily: 'Consolas, Monaco, "Courier New", monospace',
        fontSize: '14px',
        maxHeight: '500px'
      }}
    >
      <TreeNode
        data={data}
        expandDepth={expandDepth}
        currentDepth={0}
        showLineNumbers={showLineNumbers}
        isLast={true}
      />
    </div>
  );
}

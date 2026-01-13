/** 表格组件 */

interface Column {
  key: string;
  label: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, record: any, index: number) => React.ReactNode;
}

interface TableProps {
  columns: Column[];
  data: any[];
  rowKey?: string;
  bordered?: boolean;
  striped?: boolean;
  hover?: boolean;
  emptyText?: string;
}

export default function Table({
  columns,
  data,
  rowKey = 'id',
  bordered = true,
  striped = true,
  hover = true,
  emptyText = '暂无数据'
}: TableProps) {
  if (!data || data.length === 0) {
    return (
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
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          background: '#fff',
          borderRadius: '8px',
          overflow: 'hidden'
        }}
      >
        <thead
          style={{
            background: '#f8f9fa',
            borderBottom: bordered ? '2px solid #dee2e6' : 'none'
          }}
        >
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                style={{
                  padding: '12px 16px',
                  textAlign: column.align || 'left',
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '14px',
                  borderBottom: '1px solid #dee2e6',
                  width: column.width,
                  whiteSpace: 'nowrap'
                }}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((record, index) => {
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
                  if (hover) {
                    e.currentTarget.style.background = striped && index % 2 === 0 ? '#f8f9fa' : '#fff';
                  }
                }}
              >
                {columns.map((column) => {
                  const value = record[column.key];

                  return (
                    <td
                      key={column.key}
                      style={{
                        padding: '12px 16px',
                        textAlign: column.align || 'left',
                        fontSize: '14px',
                        color: '#212529',
                        borderBottom: bordered ? '1px solid #dee2e6' : 'none'
                      }}
                    >
                      {column.render ? column.render(value, record, index) : String(value)}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

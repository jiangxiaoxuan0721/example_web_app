/** 表格组件 */

import React, { useState } from 'react';

interface Column {
  key: string;
  title: string;
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
  showPagination?: boolean;
  pageSize?: number;
}

export default function Table({
  columns,
  data,
  rowKey = 'id',
  bordered = true,
  striped = true,
  hover = true,
  emptyText = '暂无数据',
  showPagination = false,
  pageSize = 10
}: TableProps) {
  const [currentPage, setCurrentPage] = useState(1);

  // 分页逻辑
  const totalPages = Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentData = data.slice(startIndex, endIndex);

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

  // 分页控件组件
  const PaginationControls = () => {
    if (!showPagination || totalPages <= 1) return null;

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

    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          marginTop: '16px',
          gap: '8px'
        }}
      >
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

        {getPageNumbers().map((page, index) => (
          <button
            key={index}
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
        ))}

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

        <div style={{
          marginLeft: '16px',
          fontSize: '14px',
          color: '#6c757d'
        }}>
          共 {data.length} 条，第 {currentPage} / {totalPages} 页
        </div>
      </div>
    );
  };

  return (
    <div>
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
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentData.map((record, index) => {
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
                    if (hover) {
                      e.currentTarget.style.background = striped && actualIndex % 2 === 0 ? '#f8f9fa' : '#fff';
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
                        {column.render ? column.render(value, record, actualIndex) : String(value)}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <PaginationControls />
    </div>
  );
}

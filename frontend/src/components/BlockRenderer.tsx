import { UISchema, Block, Field, FieldOption } from '../types/schema';
import { getByDotPath } from '../utils/patch';
import { useEvent } from '../hooks/useEvent';

/**
 * 基础 Block 组件 - 根据 Block 类型渲染对应的 UI
 */
export const BlockRenderer = ({ block, schema }: { block: Block; schema: UISchema }) => {
  // 获取绑定数据
  const boundData = block.bind ? getByDotPath(schema, block.bind) : undefined;

  switch (block.type) {
    case 'form':
      return <FormBlock block={block} data={boundData} />;
    case 'table':
      return <TableBlock block={block} data={boundData} />;
    case 'status_panel':
      return <StatusPanel block={block} data={boundData} />;
    case 'execution':
      return <ExecutionPanel block={block} data={boundData} />;
    case 'result':
      return <ResultPanel block={block} data={boundData} />;
    case 'list':
      return <ListBlock block={block} data={boundData} />;
    case 'explanation':
      return <ExplanationBlock block={block} data={boundData} />;
    case 'json_editor':
      return <JsonEditorBlock block={block} data={boundData} />;
    case 'validation':
      return <ValidationBlock block={block} data={boundData} />;
    case 'task_submission':
      return <TaskSubmissionBlock block={block} data={boundData} />;
    default:
      return <div>Unknown block type: {block.type}</div>;
  }
};

/**
 * Form Block - 表单组件
 */
const FormBlock = ({ block, data }: { block: Block; data?: any }) => {
  const { emit } = useEvent();
  const fields = block.props?.fields as Field[] || [];

  return (
    <div className="block-form">
      {fields.map((field, index) => (
        <div key={index} className="form-field">
          <label>{field.label}</label>
          {renderFieldInput(field, data, emit)}
        </div>
      ))}
    </div>
  );
};

/**
 * 渲染表单字段输入
 */
const renderFieldInput = (field: Field, data?: any, emit?: (type: string, payload?: any) => void) => {
  const value = data?.[field.key];

  const handleChange = (newValue: any) => {
    emit?.('field_change', {
      fieldKey: field.key,
      value: newValue,
    });
  };

  switch (field.type) {
    case 'text':
    case 'number':
      return (
        <input
          type={field.type}
          value={value || ''}
          onChange={(e) => handleChange(e.target.value)}
          disabled={field.disabled}
          placeholder={field.placeholder}
        />
      );
    case 'select':
      return (
        <select
          value={value || ''}
          onChange={(e) => handleChange(e.target.value)}
          disabled={field.disabled}
        >
          {field.options?.map((opt, i) => (
            <option key={i} value={typeof opt === 'object' ? (opt as FieldOption).value : opt}>
              {typeof opt === 'object' ? (opt as FieldOption).label : opt}
            </option>
          ))}
        </select>
      );
    case 'checkbox':
      return (
        <input
          type="checkbox"
          checked={value || false}
          onChange={(e) => handleChange(e.target.checked)}
          disabled={field.disabled}
        />
      );
    case 'textarea':
      return (
        <textarea
          value={value || ''}
          onChange={(e) => handleChange(e.target.value)}
          disabled={field.disabled}
          placeholder={field.placeholder}
        />
      );
    case 'json':
      return (
        <textarea
          value={typeof value === 'object' ? JSON.stringify(value, null, 2) : (value || '')}
          onChange={(e) => {
            try {
              handleChange(JSON.parse(e.target.value));
            } catch {
              handleChange(e.target.value);
            }
          }}
          disabled={field.disabled}
          rows={10}
          style={{ fontFamily: 'monospace' }}
        />
      );
    default:
      return <input type="text" value={value || ''} onChange={(e) => handleChange(e.target.value)} />;
  }
};

/**
 * Table Block - 表格组件
 */
const TableBlock = ({ block, data }: { block: Block; data?: any[] }) => {
  const fields = block.props?.fields as Field[] || [];
  const rows = Array.isArray(data) ? data : [];

  return (
    <table className="block-table">
      <thead>
        <tr>
          {fields.map((field, index) => (
            <th key={index}>{field.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {fields.map((field, fieldIndex) => (
              <td key={fieldIndex}>{row[field.key]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

/**
 * Status Panel Block - 状态面板组件
 */
const StatusPanel = ({ block, data }: { block: Block; data?: any }) => {
  const fields = block.props?.fields as Field[] || [];

  return (
    <div className="block-status-panel">
      {fields.map((field, index) => (
        <div key={index} className="status-item">
          <span className="status-label">{field.label}:</span>
          <span className="status-value">{data?.[field.key] || '-'}</span>
        </div>
      ))}
    </div>
  );
};

/**
 * Execution Panel Block - 执行面板组件
 */
const ExecutionPanel = ({ block, data }: { block: Block; data?: any }) => {
  const showProgress = block.props?.showProgress ?? true;
  const showStatus = block.props?.showStatus ?? true;
  const progress = data?.progress ?? 0;
  const status = data?.status ?? 'pending';

  return (
    <div className="block-execution-panel">
      {showStatus && (
        <div className="execution-status">
          <span className="status-label">状态:</span>
          <span className={`status-value status-${status}`}>{status}</span>
        </div>
      )}
      {showProgress && (
        <div className="execution-progress">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
          <span className="progress-text">{progress}%</span>
        </div>
      )}
    </div>
  );
};

/**
 * Result Panel Block - 结果面板组件
 */
const ResultPanel = ({ block, data }: { block: Block; data?: any }) => {
  const showImages = block.props?.showImages ?? true;
  const showTable = block.props?.showTable ?? true;

  return (
    <div className="block-result-panel">
      {showTable && data?.table && (
        <TableBlock block={block} data={data.table} />
      )}
      {showImages && data?.images && (
        <div className="result-images">
          {data.images.map((img: string, index: number) => (
            <img key={index} src={img} alt={`Result ${index + 1}`} />
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * List Block - 列表组件
 */
const ListBlock = ({ block, data }: { block: Block; data?: any[] }) => {
  const fields = block.props?.fields as string[] || ['name', 'description'];
  const items = Array.isArray(data) ? data : [];

  return (
    <div className="block-list">
      {items.map((item, index) => (
        <div key={index} className="list-item">
          {fields.map((field) => (
            <div key={field} className="list-item-field">
              <strong>{field}:</strong> {item[field]}
            </div>
          ))}
        </div>
      ))}
      {items.length === 0 && <div className="list-empty">暂无数据</div>}
    </div>
  );
};

/**
 * Explanation Block - 说明组件
 */
const ExplanationBlock = ({ block, data }: { block: Block; data?: any[] }) => {
  const fields = block.props?.fields as string[] || ['tool', 'parameters'];
  const explanations = Array.isArray(data) ? data : [];

  return (
    <div className="block-explanation">
      {explanations.map((item, index) => (
        <div key={index} className="explanation-item">
          <h4>{item[fields[0]]}</h4>
          <pre>{JSON.stringify(item[fields[1]], null, 2)}</pre>
        </div>
      ))}
    </div>
  );
};

/**
 * Json Editor Block - JSON 编辑器组件
 */
const JsonEditorBlock: React.FC<{ block: Block; data?: any }> = ({ block, data }) => {
  const { emit } = useEvent();
  const fields = block.props?.fields as string[] || [];

  const jsonValue = typeof data === 'object' ? JSON.stringify(data, null, 2) : (data || '{}');

  const handleChange = (newValue: string) => {
    try {
      emit('json_editor_change', {
        json: JSON.parse(newValue),
      });
    } catch {
      // 不处理 JSON 解析错误，让用户继续编辑
    }
  };

  return (
    <div className="block-json-editor">
      <textarea
        value={jsonValue}
        onChange={(e) => handleChange(e.target.value)}
        rows={20}
        style={{ fontFamily: 'monospace', fontSize: '14px' }}
      />
      {fields.map((field) => (
        <div key={field} className="json-editor-field">
          <label>{field}:</label>
          <span>{data?.[field] || '-'}</span>
        </div>
      ))}
    </div>
  );
};

/**
 * Validation Block - 验证组件
 */
const ValidationBlock: React.FC<{ block: Block; data?: any }> = ({ block, data }) => {
  const { emit } = useEvent();
  const showCountInput = block.props?.showCountInput ?? true;
  const count = data?.count || 1;

  return (
    <div className="block-validation">
      {showCountInput && (
        <div className="validation-field">
          <label>批量次数：</label>
          <input
            type="number"
            min="1"
            max="1000"
            value={count}
            onChange={(e) => emit('validation_count_change', { count: parseInt(e.target.value) || 1 })}
          />
        </div>
      )}
      {data?.errors && data.errors.length > 0 && (
        <div className="validation-errors">
          <h4>验证错误：</h4>
          <ul>
            {data.errors.map((error: string, index: number) => (
              <li key={index} className="error-item">{error}</li>
            ))}
          </ul>
        </div>
      )}
      {data?.warnings && data.warnings.length > 0 && (
        <div className="validation-warnings">
          <h4>警告：</h4>
          <ul>
            {data.warnings.map((warning: string, index: number) => (
              <li key={index} className="warning-item">{warning}</li>
            ))}
          </ul>
        </div>
      )}
      {(!data?.errors || data.errors.length === 0) && (!data?.warnings || data.warnings.length === 0) && (
        <div className="validation-success">
          ✅ 配置验证通过
        </div>
      )}
    </div>
  );
};

/**
 * Task Submission Block - 任务提交组件
 */
const TaskSubmissionBlock: React.FC<{ block: Block; data?: any }> = ({ block, data }) => {
  const showTaskId = block.props?.showTaskId ?? true;
  const showStatus = block.props?.showStatus ?? true;
  const taskId = data?.taskId;
  const status = data?.status || 'pending';

  return (
    <div className="block-task-submission">
      {showTaskId && taskId && (
        <div className="task-id">
          <strong>任务 ID：</strong>
          <code>{taskId}</code>
        </div>
      )}
      {showStatus && (
        <div className="task-status">
          <strong>状态：</strong>
          <span className={`status-badge status-${status}`}>{status}</span>
        </div>
      )}
      {data?.message && (
        <div className="task-message">{data.message}</div>
      )}
    </div>
  );
};

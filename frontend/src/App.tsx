import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import {SchemaRenderer} from './components/SchemaRenderer';
import { useEvent } from './hooks/useEvent';
import { useMCPConnection, useMCPCommand } from './hooks/useMCP';
import { UISchema } from './types/schema';
import { useState, useEffect } from 'react';

/**
 * 主页
 */
const HomePage = () => {
  return (
    <div className="page-home">
      <header className="header">
        <h1>SIMBOT 电力系统分析平台</h1>
        <p className="subtitle">SIMBOT Power System Analysis Platform</p>
      </header>
      <main className="main-content">
        <div className="cards-grid">
          <Link to="/n1-wizard" className="mode-card">
            <div className="mode-icon">1</div>
            <h3>N-1 仿真向导</h3>
            <p>N-1 故障仿真分析工具</p>
          </Link>
          <Link to="/batch-n1" className="mode-card">
            <div className="mode-icon">2</div>
            <h3>批量 N-1 仿真</h3>
            <p>批量故障场景分析工具</p>
          </Link>
        </div>
      </main>
    </div>
  );
};

/**
 * N-1 Wizard 页面
 */
const N1WizardPage = () => {
  const { emit, useEventListener } = useEvent();
  const navigate = useNavigate();
  const { isConnected, sendEvent } = useMCPConnection(true);
  const { sendCommand: mcpSendCommand } = useMCPCommand();
  
  // Schema 从后端 Agent/MCP 获取
  const [schema, setSchema] = useState<UISchema | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMCPConnected, setIsMCPConnected] = useState(false);

  // 监听 MCP 连接状态
  useEffect(() => {
    setIsMCPConnected(isConnected);
  }, [isConnected]);

  // 初始化 - 通过 MCP 获取初始 Schema
  useEffect(() => {
    const initWizard = async () => {
      try {
        setIsLoading(true);
        setError(null);

        if (isMCPConnected) {
          // 方式 1：通过 MCP 工具获取初始 Schema
          const response = await mcpSendCommand('render_page', {
            page_key: 'mode_selection'
          });
          
          if (response.success) {
            setSchema(response.schema);
          } else {
            throw new Error(response.error || '获取 Schema 失败');
          }
        } else {
          // 方式 2：回退到本地配置（当 MCP 未连接时）
          console.warn('[N1Wizard] MCP 未连接，使用本地配置');
          const wizardConfigResponse = await fetch('/api/wizard/config');
          if (wizardConfigResponse.ok) {
            const wizardConfig = await wizardConfigResponse.json();
            
            const modeSelectionSchema: UISchema = {
              meta: {
                pageKey: 'mode_selection',
                step: { current: 0, total: 1 },
                status: 'idle',
                schemaVersion: '1.0',
              },
              state: {
                params: {},
                runtime: {},
              },
              layout: { type: 'single' as const },
              blocks: [
                {
                  id: 'mode_selection',
                  type: 'form',
                  bind: 'state.params',
                  props: {
                    fields: [
                      {
                        label: '选择仿真模式',
                        key: 'selectedMode',
                        type: 'select',
                        options: Object.entries(wizardConfig.modes || {}).map(([key, mode]: [string, any]) => ({
                          value: key,
                          label: mode.name,
                        })),
                      },
                    ],
                  },
                },
              ],
              actions: [
                { id: 'confirm', label: '开始向导', style: 'primary' },
                { id: 'cancel', label: '取消', style: 'secondary' },
              ],
            };
            
            setSchema(modeSelectionSchema);
          } else {
            throw new Error('获取配置失败');
          }
        }
      } catch (err) {
        console.error('初始化 Wizard 失败:', err);
        setError(err instanceof Error ? err.message : '未知错误');
        setIsLoading(false);
      } finally {
        setIsLoading(false);
      }
    };

    // 延迟执行，等待 MCP 连接
    const timer = setTimeout(() => {
      initWizard();
    }, 500);

    return () => clearTimeout(timer);
  }, [isMCPConnected]);

  // 监听字段变化 - 前端只负责发射事件
  useEventListener('field_change', (event) => {
    const { fieldKey, value } = event.payload || {};
    
    // 通过 MCP 发送到后端 Agent
    if (isMCPConnected) {
      sendEvent('field_change', { fieldKey, value }, schema?.meta?.pageKey);
    }
    
    // 发送到后端 API（回退方案）
    emit('backend_request', {
      type: 'field_change',
      payload: { fieldKey, value },
    });
    
    // 同时更新本地状态（临时优化用户体验）
    setSchema(prevSchema => {
      if (!prevSchema) return prevSchema;
      return {
        ...prevSchema,
        state: {
          ...prevSchema.state,
          params: {
            ...prevSchema.state.params,
            [fieldKey]: value,
          },
        },
      };
    });
  });

  // 监听 Action 点击 - 前端只负责发射事件
  useEventListener('action_click', async (event) => {
    const { actionId } = event.payload || {};

    // 通过 MCP 发送到后端 Agent
    if (isMCPConnected) {
      sendEvent('action_click', { actionId }, schema?.meta?.pageKey);
    }
    
    // 发送到后端 API（回退方案）
    emit('backend_request', {
      type: 'action_click',
      payload: { actionId },
    });

    // 根据不同的 action 做不同的处理
    if (actionId === 'confirm') {
      const selectedMode = schema?.state?.params?.selectedMode;
      if (selectedMode) {
        // 通过 MCP 发送选择模式的请求
        if (isMCPConnected) {
          sendEvent('select_mode', { mode: selectedMode }, schema?.meta?.pageKey);
        }
        
        // 通过 MCP 渲染下一步页面
        try {
          const response = await mcpSendCommand('render_page', {
            page_key: `${selectedMode}_0`,
            mode: selectedMode,
            step_index: 0
          });
          
          if (response.success) {
            setSchema(response.schema);
          } else {
            throw new Error(response.error || '渲染页面失败');
          }
        } catch (err) {
          console.error('渲染页面失败:', err);
        }
      }
    } else if (actionId === 'cancel') {
      navigate('/');
    } else if (actionId === 'next') {
      // 处理下一步
      const mode = schema?.state?.runtime?.mode;
      const currentStep = schema?.meta?.step?.current || 0;
      const totalSteps = schema?.meta?.step?.total || 0;
      
      if (mode && currentStep < totalSteps) {
        try {
          const response = await mcpSendCommand('render_page', {
            page_key: `${mode}_${currentStep}`,
            mode: mode,
            step_index: currentStep
          });
          
          if (response.success) {
            setSchema(response.schema);
          } else {
            throw new Error(response.error || '渲染页面失败');
          }
        } catch (err) {
          console.error('渲染页面失败:', err);
        }
      }
    } else if (actionId === 'prev') {
      // 处理上一步
      const mode = schema?.state?.runtime?.mode;
      const currentStep = schema?.meta?.step?.current || 0;
      
      if (mode && currentStep > 1) {
        try {
          const response = await mcpSendCommand('render_page', {
            page_key: `${mode}_${currentStep - 2}`,
            mode: mode,
            step_index: currentStep - 2
          });
          
          if (response.success) {
            setSchema(response.schema);
          } else {
            throw new Error(response.error || '渲染页面失败');
          }
        } catch (err) {
          console.error('渲染页面失败:', err);
        }
      }
    }
  });

  if (isLoading) {
    return (
      <div className="page-wizard">
        <div className="loading">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-wizard">
        <div className="error">
          <h3>加载失败</h3>
          <p>{error}</p>
          <button className="btn btn-secondary" onClick={() => navigate('/')}>返回主页</button>
        </div>
      </div>
    );
  }

  if (!schema) {
    return <div>Loading...</div>;
  }

  const modeTitle = schema.meta?.runtime?.mode 
    ? '向导进行中' 
    : '选择仿真模式';

  return (
    <div className="page-wizard">
      <header className="header">
        <Link to="/" className="btn btn-secondary">返回主页</Link>
        <div className="header-center">
          <h1>N-1 仿真向导</h1>
          <p className="subtitle">{modeTitle}</p>
        </div>
        <div className="header-right">
          <div style={{ 
            padding: '8px 12px',
            borderRadius: '4px',
            fontSize: '12px',
            marginRight: '8px',
            background: isMCPConnected ? '#4caf50' : '#f44336',
            color: 'white'
          }}>
            {isMCPConnected ? '✓ MCP 已连接' : '✗ MCP 未连接'}
          </div>
          <button className="btn btn-secondary">帮助</button>
        </div>
      </header>

      {/* 显示当前状态信息（用于调试） */}
      <div className="debug-info" style={{ 
        background: '#f5f5f5', 
        padding: '16px', 
        borderRadius: '8px', 
        marginBottom: '20px',
        fontSize: '12px',
        fontFamily: 'monospace',
        border: '1px solid #ddd'
      }}>
        <strong>调试信息（生产环境应移除）：</strong>
        <pre style={{ margin: '8px 0 0 0' }}>
{JSON.stringify(schema.meta, null, 2)}
        </pre>
      </div>

      <main className="main-content">
        <SchemaRenderer schema={schema} />
      </main>
    </div>
  );
};

/**
 * 批量 N-1 页面
 */
const BatchN1Page = () => {
  return (
    <div className="page-batch">
      <header className="header">
        <Link to="/" className="btn btn-secondary">返回主页</Link>
        <div className="header-center">
          <h1>批量 N-1 仿真</h1>
          <p className="subtitle">Batch N-1 Simulation</p>
        </div>
      </header>
      <main className="main-content">
        <div className="placeholder">批量仿真功能开发中...</div>
      </main>
    </div>
  );
};

/**
 * App 根组件
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/n1-wizard" element={<N1WizardPage />} />
        <Route path="/batch-n1" element={<BatchN1Page />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

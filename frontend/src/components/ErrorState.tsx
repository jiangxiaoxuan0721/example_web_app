/** 错误状态组件 */

interface ErrorStateProps {
  error: string;
}

export default function ErrorState({ error }: ErrorStateProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      color: 'red'
    }}>
      <div>{error}</div>
      <div style={{ marginTop: '20px', fontSize: '14px' }}>
        可用实例：
        <br/>
        <a href="?instanceId=demo" style={{ color: '#007bff' }}>demo</a> |{' '}
        <a href="?instanceId=counter" style={{ color: '#007bff' }}>counter</a> |{' '}
        <a href="?instanceId=form" style={{ color: '#007bff' }}>form</a>
      </div>
    </div>
  );
}

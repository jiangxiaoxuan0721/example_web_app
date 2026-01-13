/** 加载动画组件 */

interface SpinnerProps {
  size?: number;
  color?: string;
}

export default function Spinner({ size = 40, color = '#007bff' }: SpinnerProps) {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: size + 20,
        width: size + 20
      }}
    >
      <div
        style={{
          width: size,
          height: size,
          border: `4px solid ${color}33`,
          borderTop: `4px solid ${color}`,
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}
      />
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

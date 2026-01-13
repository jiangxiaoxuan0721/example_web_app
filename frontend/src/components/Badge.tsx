/** 徽章组件 */

interface BadgeProps {
  count?: number;
  dot?: boolean;
  children: React.ReactNode;
  color?: string;
  showZero?: boolean;
  max?: number;
}

export default function Badge({ count, dot = false, children, color = '#f5222d', showZero = false, max = 99 }: BadgeProps) {
  const displayCount = count !== undefined && count > 0 ? (count > max ? `${max}+` : count) : undefined;

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      {children}
      {(dot || (displayCount !== undefined && (showZero || displayCount !== 0))) && (
        <span
          style={{
            position: 'absolute',
            top: '-8px',
            right: '-8px',
            minWidth: dot ? '8px' : '20px',
            height: dot ? '8px' : '20px',
            borderRadius: '10px',
            background: color,
            color: '#fff',
            fontSize: dot ? '0' : '12px',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: dot ? '0' : '0 6px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            zIndex: 10
          }}
        >
          {dot ? '' : displayCount}
        </span>
      )}
    </div>
  );
}

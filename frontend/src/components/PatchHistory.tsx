/** Patch 历史记录组件 */

import { PatchRecord } from '../types/schema';

interface PatchHistoryProps {
  patches: PatchRecord[];
  onReplay: (patchId: number) => void;
}

export default function PatchHistory({ patches, onReplay }: PatchHistoryProps) {
  if (patches.length === 0) {
    return null;
  }

  return (
    <div style={{
      marginTop: '30px',
      padding: '15px',
      background: '#f5f5f5',
      borderRadius: '4px',
      fontSize: '12px',
      textAlign: 'left',
      maxHeight: '200px',
      overflow: 'auto'
    }}>
      <strong style={{ marginBottom: '8px', display: 'block' }}>
        Patch 历史记录（可独立重放）
      </strong>
      <div style={{ marginTop: '8px' }}>
        {patches.map((patchRecord) => (
          <div
            key={patchRecord.id}
            style={{
              marginBottom: '8px',
              padding: '8px',
              background: 'white',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
            onClick={() => onReplay(patchRecord.id)}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#f0f0f0';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'white';
            }}
          >
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
              Patch #{patchRecord.id} - {new Date(patchRecord.timestamp).toLocaleTimeString()}
            </div>
            <pre style={{ margin: '0', fontSize: '10px' }}>
              {JSON.stringify(patchRecord.patch, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}

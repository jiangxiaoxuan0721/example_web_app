import React, { useState } from 'react';

interface FileUploadProps {
  value: string | string[];
  onChange: (value: string | string[]) => void;
  disabled?: boolean;
  accept?: string;
  multiple?: boolean;
  required?: boolean;
  maxSize?: number; // MB
}

export default function FileUpload({
  value,
  onChange,
  disabled = false,
  accept = '*/*',
  multiple = false,
  required = false,
  maxSize = 10
}: FileUploadProps) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    handleFiles(Array.from(files));
  };

  const handleFiles = (files: File[]) => {
    setError('');

    // 验证文件大小
    const oversizedFiles = files.filter(file => file.size > maxSize * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      setError(`文件大小超过限制（最大 ${maxSize}MB）`);
      return;
    }

    // 验证文件类型（如果指定了 accept）
    if (accept !== '*/*') {
      const acceptedTypes = accept.split(',').map(t => t.trim());
      const invalidFiles = files.filter(file => {
        return !acceptedTypes.some(t => {
          if (t.startsWith('.')) {
            return file.name.toLowerCase().endsWith(t.toLowerCase());
          }
          return file.type === t;
        });
      });

      if (invalidFiles.length > 0) {
        setError(`不支持的文件类型`);
        return;
      }
    }

    // 读取文件并转换为 base64（简单实现，生产环境应使用文件上传 API）
    const readFilePromises = files.map(file => {
      return new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    });

    Promise.all(readFilePromises)
      .then(results => {
        if (multiple) {
          const currentValue = Array.isArray(value) ? value : (value ? [value] : []);
          onChange([...currentValue, ...results]);
        } else {
          onChange(results[0]);
        }
      })
      .catch(err => {
        setError('文件读取失败');
        console.error('File read error:', err);
      });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    handleFiles(files);
  };

  const handleRemove = (index?: number) => {
    if (multiple && Array.isArray(value)) {
      const newValue = value.filter((_, i) => i !== index);
      onChange(newValue);
    } else {
      onChange('');
    }
  };

  // 显示已上传的文件
  const displayValue = Array.isArray(value) ? value : (value ? [value] : []);

  return (
    <div>
      <input
        type="file"
        id={`file-upload-${Math.random().toString(36).substring(2, 11)}`}
        onChange={handleChange}
        disabled={disabled}
        accept={accept}
        multiple={multiple}
        required={required && displayValue.length === 0}
        style={{ display: 'none' }}
      />

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => {
          if (!disabled) {
            const input = document.querySelector(`input[type="file"]`) as HTMLInputElement;
            input?.click();
          }
        }}
        style={{
          border: `2px dashed ${dragOver ? '#1890ff' : '#d9d9d9'}`,
          borderRadius: '8px',
          padding: '24px',
          textAlign: 'center',
          cursor: disabled ? 'not-allowed' : 'pointer',
          backgroundColor: disabled ? '#f5f5f5' : (dragOver ? '#f0f7ff' : '#fafafa'),
          transition: 'all 0.2s'
        }}
      >
        <div style={{ fontSize: '24px', marginBottom: '8px' }}>📁</div>
        <div style={{ fontSize: '14px', color: '#595959' }}>
          {dragOver ? '释放文件以上传' : '点击或拖拽文件到此处'}
        </div>
        <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: '4px' }}>
          支持格式：{accept === '*/*' ? '任意' : accept}
          {multiple && '（支持多选）'}
          {!multiple && '（单选）'}
        </div>
      </div>

      {error && (
        <div style={{
          color: '#ff4d4f',
          fontSize: '12px',
          marginTop: '8px'
        }}>
          {error}
        </div>
      )}

      {displayValue.length > 0 && (
        <div style={{ marginTop: '12px' }}>
          <div style={{ fontSize: '12px', color: '#595959', marginBottom: '8px' }}>
            已上传的文件（{displayValue.length}）：
          </div>
          {displayValue.map((fileData, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '8px',
                backgroundColor: '#f5f5f5',
                borderRadius: '4px',
                marginBottom: '4px',
                fontSize: '12px'
              }}
            >
              {fileData.startsWith('data:image') ? (
                <img
                  src={fileData}
                  alt={`文件 ${index + 1}`}
                  style={{
                    width: '40px',
                    height: '40px',
                    objectFit: 'cover',
                    marginRight: '8px',
                    borderRadius: '4px'
                  }}
                />
              ) : (
                <div style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: '#d9d9d9',
                  borderRadius: '4px',
                  marginRight: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '18px'
                }}>
                  📄
                </div>
              )}
              <div style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                文件 {index + 1}
              </div>
              {!disabled && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemove(multiple ? index : undefined);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#ff4d4f',
                    cursor: 'pointer',
                    padding: '4px 8px',
                    fontSize: '12px'
                  }}
                >
                  删除
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

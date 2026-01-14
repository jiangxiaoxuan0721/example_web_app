/** 组件统一导出 */

// UI 组件
export { default as Loading } from './Loading';
export { default as ErrorState } from './ErrorState';
export { default as InstanceSelector } from './InstanceSelector';
export { default as FieldDisplay } from './FieldDisplay';
export { default as BlockRenderer } from './BlockRenderer';
export { default as ActionButton } from './ActionButton';
export { default as PatchHistory } from './PatchHistory';
export { default as DebugInfo } from './DebugInfo';

// 新架构组件
export { default as GenericFieldRenderer } from './GenericFieldRenderer';
export { registerFieldRenderer } from './GenericFieldRenderer';
export { registerBlockRenderer, getRegisteredBlockTypes } from './BlockRenderer';

// 表单组件
export { default as InputField } from './InputField';
export { default as NumberInput } from './NumberInput';
export { default as TextArea } from './TextArea';
export { default as Select } from './Select';
export { default as CheckBox } from './CheckBox';
export { default as RadioGroup } from './RadioGroup';

// 其他 UI 组件
export { default as Progress } from './Progress';
export { default as Alert } from './Alert';
export { default as Card } from './Card';
export { default as Spinner } from './Spinner';

// 数据展示组件
export { default as CodeBlock } from './CodeBlock';
export { default as Markdown } from './Markdown';
export { default as JSONViewer } from './JSONViewer';
export { default as Table } from './Table';

// 反馈组件
export { default as Tag } from './Tag';
export { default as Badge } from './Badge';
export { default as Modal } from './Modal';

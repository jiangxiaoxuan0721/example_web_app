# 模块化开发详细指导

## 1. 模块定义与边界

### 1.1 什么是模块？

模块是具有单一职责、高内聚、低耦合的代码单元。每个模块应该：

- **单一职责**：只负责一个明确的功能领域
- **高内聚**：模块内部功能紧密相关
- **低耦合**：模块间依赖最小化

### 1.2 模块边界划分原则

#### JavaScript模块边界

```bash
utils.js      → 通用工具函数（可跨项目复用）
api.js        → 所有HTTP请求（数据获取层）
table.js      → 表格相关DOM操作（视图层）
graph.js      → 图表可视化（视图层）
main.js       → 业务逻辑协调（控制层）
```

#### CSS模块边界

```bash
main.css      → 全局样式和布局
component.css → 特定组件样式（如需要）
theme.css     → 主题相关样式（如需要）
```

#### Python模块边界

```bash
data_generator/    → 数据生成（外部API调用）
data_processor/   → 数据处理和转换
models/           → 数据模型定义
utils/            → 通用工具函数
```

## 2. 命名约定

### 2.1 文件命名

```bash
JavaScript:  kebab-case.js (如: user-manager.js)
CSS:         kebab-case.css (如: user-profile.css)
Python:      snake_case.py (如: user_service.py)
```

### 2.2 函数命名

```bash
JavaScript:  camelCase (如: getUserData, displayTable)
Python:      snake_case (如: get_user_data, display_table)
```

### 2.3 变量命名

```bash
常量:        UPPER_SNAKE_CASE (如: API_BASE_URL)
变量:        camelCase / snake_case
布尔值:      is/has/can/should 前缀 (如: isLoading, hasData)
```

### 2.4 CSS类命名

```bash
BEM方法论:  block__element--modifier
示例:      .table__header--sorted
           .btn--primary
           .user-card__avatar
```

## 3. 代码风格指南

### 3.1 JavaScript代码风格

#### 函数定义

```javascript
// ✅ 好的做法
/**
 * 获取用户数据
 * @param {number} userId - 用户ID
 * @param {object} options - 请求选项
 * @returns {Promise<object>} 用户数据
 */
async function getUserData(userId, options = {}) {
    try {
        const response = await fetch(`/api/users/${userId}`, options);
        return await response.json();
    } catch (error) {
        throw new Error(`获取用户数据失败: ${error.message}`);
    }
}

// ❌ 避免的做法
function getUser(id) {
    // 缺少文档注释
    // 缺少错误处理
    return fetch('/api/users/' + id);
}
```

#### 模块导出

```javascript
// utils.js - 工具函数模块
export function formatDate(date) { /* ... */ }
export function validateEmail(email) { /* ... */ }

// 使用时
import { formatDate, validateEmail } from './utils.js';
```

### 3.2 CSS代码风格

#### 组织结构

```css
/* 1. CSS变量定义 */
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --border-radius: 5px;
}

/* 2. 基础样式重置 */
* { box-sizing: border-box; }

/* 3. 布局组件 */
.container { /* ... */ }
.header { /* ... */ }

/* 4. 功能组件 */
.btn { /* ... */ }
.table { /* ... */ }

/* 5. 状态修饰符 */
.btn--primary { /* ... */ }
.btn--disabled { /* ... */ }
```

### 3.3 Python代码风格

#### 函数的定义

```python
# ✅ 好的做法
def process_user_data(user_id: int, options: dict = None) -> dict:
    """
    处理用户数据
    
    Args:
        user_id: 用户ID
        options: 处理选项
        
    Returns:
        处理后的用户数据
        
    Raises:
        ValueError: 当用户ID无效时
    """
    if not user_id or user_id <= 0:
        raise ValueError("用户ID必须为正整数")
    
    options = options or {}
    # 处理逻辑...
    return processed_data

# ❌ 避免的做法
def process_data(id):
    # 缺少类型注解
    # 缺少文档字符串
    # 缺少参数验证
    pass
```

## 4. 模块化实现策略

### 4.1 依赖管理

```javascript
// 依赖层次：utils → api → feature → main
// 加载顺序：先基础模块，后业务模块

<script src="/static/js/utils.js"></script>
<script src="/static/js/api.js"></script>
<script src="/static/js/table.js"></script>
<script src="/static/js/graph.js"></script>
<script src="/static/js/main.js"></script>
```

### 4.2 模块间通信

```javascript
// 使用事件系统进行模块间通信
class EventBus {
    constructor() {
        this.events = {};
    }
    
    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    }
    
    emit(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(data));
        }
    }
}

// 使用示例
const eventBus = new EventBus();

// 在table.js中
eventBus.emit('dataLoaded', tableData);

// 在graph.js中
eventBus.on('dataLoaded', (data) => {
    updateChart(data);
});
```

### 4.3 配置管理

```javascript
// config.js - 集中管理配置
const CONFIG = {
    API: {
        BASE_URL: '/api',
        TIMEOUT: 5000,
        ENDPOINTS: {
            USERS: '/users',
            TABLES: '/tables'
        }
    },
    UI: {
        MESSAGE_DURATION: 3000,
        TABLE_PAGE_SIZE: 20
    }
};

export default CONFIG;
```

## 5. 文件大小控制

### 5.1 拆分标准

- **< 200行**：保持单文件
- **200-500行**：考虑按功能拆分
- **> 500行**：必须拆分为多个文件

### 5.2 拆分示例

```javascript
// 原始文件：table.js (600行)
// 拆分为：
// ├── table-core.js    (核心表格功能)
// ├── table-filter.js  (过滤功能)
// ├── table-sort.js    (排序功能)
// └── table-export.js  (导出功能)
```

## 6. 最佳实践

### 6.1 错误处理

```javascript
// 统一错误处理
class ErrorHandler {
    static handle(error, context = '') {
        console.error(`[${context}] 错误:`, error);
        showMessage(`操作失败: ${error.message}`, 'error');
    }
}

// 使用示例
try {
    const data = await fetchData();
} catch (error) {
    ErrorHandler.handle(error, '数据加载');
}
```

### 6.2 性能优化

```javascript
// 防抖和节流
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 使用示例
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', debounce(handleSearch, 300));
```

### 6.3 测试友好

```javascript
// 依赖注入，便于测试
class DataManager {
    constructor(apiClient = defaultApiClient) {
        this.api = apiClient;
    }
    
    async loadData() {
        return await this.api.get('/data');
    }
}

// 测试时可以注入mock对象
const mockApi = { get: () => Promise.resolve(mockData) };
const manager = new DataManager(mockApi);
```

## 7. 代码审查检查清单

### 7.1 模块化检查

- [ ] 每个文件是否只负责一个功能？
- [ ] 模块间依赖是否清晰？
- [ ] 是否存在循环依赖？
- [ ] 函数是否遵循单一职责原则？

### 7.2 命名检查

- [ ] 文件名是否符合约定？
- [ ] 函数/变量名是否清晰表达意图？
- [ ] 是否避免缩写和模糊命名？

### 7.3 代码质量检查

- [ ] 是否有适当的注释和文档？
- [ ] 是否有错误处理机制？
- [ ] 是否遵循代码风格指南？
- [ ] 是否有重复代码？

通过遵循这些指导原则，可以确保代码的可维护性、可扩展性和团队协作效率。

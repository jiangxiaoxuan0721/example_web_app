# Data Processor 数据处理模块

负责将仿真数据处理成前端需要的格式。

## 功能

- 解析 CloudPSS 仿真结果
- 计算 KPI 指标
- 格式化数据供前端展示

## 开发

在此目录下编写数据处理的 Python 代码。

## 示例

```python
def process_data(raw_data):
    """处理仿真数据"""
    processed = {
        'kpi': {...},
        'cases': [...]
    }
    return processed
```

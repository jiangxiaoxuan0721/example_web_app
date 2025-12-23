# Data Generator 数据生成模块

负责调用 CloudPSS API 获取电力系统仿真数据。

## 功能

- 调用 CloudPSS 仿真接口
- 获取潮流计算、短路计算等仿真结果
- 保存仿真数据到输出目录

## 开发

在此目录下编写 CloudPSS 仿真相关的 Python 代码。

## 示例

```python
def run_simulation(project_id, parameters):
    """运行 CloudPSS 仿真"""
    # 调用 CloudPSS API
    # 返回仿真结果
    pass
```

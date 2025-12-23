# Pages 页面模板

所有页面模板和页面特定的逻辑。

## 页面列表

| 页面 | 路径 | 功能 |
|------|------|------|
| index | / | 主页，功能卡片导航 |
| batch_n_1 | /batch-n1 | 批量 N-1 分析页面 |
| not_support | /not-supported | 不支持页面（404） |

## 页面结构

每个页面包含：
- `page_name.html`: 页面模板
- `page_name.css`: 页面特定样式
- `page_name.js`: 页面逻辑

## 开发指南

新增页面时，创建对应目录并包含 HTML、CSS、JS 三个文件。

在 `app.py` 中添加路由：
```python
@app.route('/page-path')
def page_name():
    return render_template('page_dir/page_name.html')
```

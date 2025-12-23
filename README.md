# 电力系统分析平台

基于 Flask 的电力系统分析 Web 应用，采用组件化前端架构。

## 快速开始

```bash
python app.py
```

访问 `http://<IP>:50890` 验证应用运行。

## 项目结构

```
├── app.py                  # Flask 应用入口
├── config.py               # 全局配置
├── backend/                # 后端模块
├── frontend/               # 前端资源
├── data_source/            # 数据源
└── output/                # 数据输出
```

## 技术栈

- **后端**: Flask (Python)
- **前端**: 原生 HTML/CSS/JavaScript
- **样式**: CSS 变量主题系统

## 配置

修改 `config.py` 中的服务器配置和 CloudPSS Token。

支持环境变量：
- `SERVER_HOST`: 服务器地址（默认 0.0.0.0）
- `SERVER_PORT`: 端口号（默认 50890）
- `DEBUG`: 调试模式（默认 True）
- `CLOUDPSS_TOKEN`: CloudPSS Token

## 文档

- [项目说明](INSTRUCTURE.md)
- [应用开发规范](solo_app.md)

## License

MIT

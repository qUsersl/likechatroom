# LikeChat 聊天室

LikeChat 是一个基于 Python Flask 和 WebSocket 技术的 B/S 架构在线聊天室应用。它支持多人实时聊天、多媒体内容嵌入、Emoji 表情以及 AI 智能助手互动。

## ✨ 主要功能

*   **用户登录**：支持昵称登录，统一验证密码（默认：123456），支持选择不同的服务器节点（本地/公共）。
*   **多人实时群聊**：基于 WebSocket 实现低延迟的多人即时通讯。
*   **富文本/多媒体交互**：
    *   **Emoji 表情**：内置丰富的 Emoji 表情选择器。
    *   **@电影 功能**：发送 `@电影 [视频URL]` 可直接在聊天框内解析并播放视频（支持 400x400 iframe 嵌入）。
    *   **AI 助手 (@成小理)**：发送 `@成小理 [问题]` 可与集成的大语言模型进行实时流式对话。
*   **响应式界面**：采用 TailwindCSS 开发，适配 PC 和移动端设备。
*   **在线状态**：实时显示在线人数和用户列表。

## 🛠️ 技术栈

*   **后端**：Python 3, Flask, Flask-SocketIO, Eventlet
*   **前端**：HTML5, JavaScript, TailwindCSS (CDN), Socket.IO Client
*   **AI 集成**：OpenAI SDK (对接 SiliconFlow API)

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8+。建议使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 激活虚拟环境 (Linux/macOS)
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置文件

项目配置文件位于 `config.py`，包含服务器列表和 AI 接口配置：

```python
# config.py

# 服务器列表配置
SERVERS = [
    {"name": "本地服务器 ", "value": "127.0.0.1:5000"},
    {"name": "公共服务器 ", "value": "http://your-public-url.com"}
]

# AI 模型配置 (使用 SiliconFlow 或兼容 OpenAI 格式的接口)
AI_API_KEY = "your-api-key"
AI_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
AI_BASE_URL = "https://api.siliconflow.cn/v1/"
```

### 4. 启动服务

```bash
python app.py
```

服务默认运行在 `http://127.0.0.1:5000`。

## 📖 开发指南

### 项目结构

*   `app.py`: 核心后端入口，处理 HTTP 路由和 WebSocket 事件。
*   `config.py`: 全局配置文件。
*   `templates/`: HTML 模板文件。
    *   `login.html`: 登录页面。
    *   `chat.html`: 聊天主界面，包含核心前端逻辑（SocketIO, DOM操作, SSE AI对话）。
*   `requirements.txt`: 项目依赖列表。

### 关键功能实现说明

#### 1. 消息处理 (app.py)
所有聊天消息通过 WebSocket 的 `send_message` 事件处理。
*   **普通消息**：直接广播到房间。
*   **@电影 指令**：解析 `msg.startswith('@电影 ')`，将消息类型转换为 `video` 并替换为解析 URL。

#### 2. AI 对话 (@成小理)
采用 Server-Sent Events (SSE) 实现流式回复。
*   **前端 (`chat.html`)**：检测 `@成小理` 指令，通过 `EventSource` 连接 `/api/ai_chat` 接口。为保证回复顺序，采用“先本地回显用户消息，再触发 AI 请求”的策略。
*   **后端 (`app.py`)**：`/api/ai_chat` 路由调用 LLM API，并以 `text/event-stream` 格式流式返回数据。

#### 3. 公共服务器适配
为了支持内网穿透后的公共访问，SocketIO 初始化时配置了 `cors_allowed_origins="*"` 以解决跨域问题。

## 📝 待办/后续计划

*   [ ] 完善 `@音乐`、`@天气`、`@新闻` 等更多指令接口。
*   [ ] 实现聊天历史记录持久化存储（数据库集成）。
*   [ ] 优化用户头像上传/自定义功能。

---
Created for LikeChat Project.

# AI Chat Application / AI 智能助手

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## 🇬🇧 English Documentation

An advanced AI Chat Web Application built with **FastAPI** and **Vue 3**, featuring multi-modal capabilities, web browsing, and a stunning cosmic UI.

### ✨ Key Features

#### 🧠 Intelligent Chat
*   **Multi-Model Support**: Integrated with **Deepseek** and **Qwen (Alibaba)** models (Qwen-Plus, Qwen-VL-Max).
*   **Streaming Responses**: Real-time typewriter effect for a smooth conversational experience.
*   **Markdown & LaTeX**: Full support for Markdown formatting and mathematical formulas rendering (KaTeX).
*   **Session Management**: Auto-saving, renaming, and AI-generated session summaries.

#### 👁️ Multi-Modal & File Processing
*   **Multi-Image Support**: Upload multiple images simultaneously. Images are stored locally and analyzed by Vision Language Models (Qwen-VL).
*   **Document Analysis**: Intelligent parsing of **PDF** (extracts both text and images), **DOCX**, and **TXT** files.
*   **Image Preview**: Interactive image preview and management in the chat interface.

#### 🌐 Web Browsing Capability
*   **Auto-Browsing**: Automatically detects URLs in your messages.
*   **Content Extraction**: Fetches and parses web page content to provide context-aware answers based on live internet data.

#### 🎨 Modern UI/UX
*   **Cosmic Design**: Stunning dynamic star trails background with rotating animation.
*   **Glassmorphism**: Elegant frosted glass effects for sidebars, cards, and inputs.
*   **Dark Theme**: Optimized dark mode for comfortable viewing in low-light environments.
*   **Responsive**: Fully responsive layout built with **Tailwind CSS**.

### 🛠️ Tech Stack
*   **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic, BeautifulSoup4 (Web Scraping)
*   **Frontend**: Vue 3, Vite, Pinia, Tailwind CSS, KaTeX
*   **Database**: SQLite (Default)

### 🚀 Quick Start

#### Prerequisites
*   Python 3.10+
*   Node.js 18+

#### 1. Backend Setup
```bash
cd backend
# Install dependencies
pip install -r requirements.txt
# Run server
python -m uvicorn app.main:app --reload
```
Server runs at `http://localhost:8000`.

#### 2. Frontend Setup
```bash
cd frontend
# Install dependencies
npm install
# Run dev server
npm run dev
```
App runs at `http://localhost:5173`.

#### 3. Environment Variables
Create a `.env` file in the `backend` directory:
```env
QWEN_API_KEY=your_qwen_key
DEEPSEEK_API_KEY=your_deepseek_key
SECRET_KEY=your_jwt_secret
```

---

<a name="chinese"></a>
## 🇨🇳 中文文档

一个基于 **FastAPI** 和 **Vue 3** 构建的高级 AI 聊天 Web 应用，具备多模态处理、联网搜索能力以及令人惊艳的星空 UI 设计。

### ✨ 主要功能

#### 🧠 智能对话
*   **多模型支持**：集成 **Deepseek** 和 **通义千问 (Qwen)** 系列模型 (支持 Qwen-Plus, Qwen-VL-Max)。
*   **流式响应**：支持打字机效果的实时流式输出，提供流畅的对话体验。
*   **Markdown & 公式渲染**：完美支持 Markdown 格式排版以及 LaTeX 数学公式渲染 (KaTeX)。
*   **会话管理**：支持会话自动保存、重命名以及 AI 自动生成会话标题摘要。

#### 👁️ 多模态与文件处理
*   **多图支持**：支持一次性上传多张图片。图片保存于本地服务器并由视觉大模型 (Qwen-VL) 进行深度解析。
*   **文档分析**：智能解析 **PDF**（自动提取文本和包含的图片）、**DOCX** 和 **TXT** 文件。
*   **图片预览**：聊天界面支持图片的交互式预览和管理。

#### 🌐 联网浏览能力
*   **自动联网**：自动检测用户消息中的 URL 链接。
*   **内容提取**：实时抓取并解析网页正文内容，让 AI 能够根据最新的互联网信息回答问题。

#### 🎨 现代 UI/UX 设计
*   **星空主题**：绚丽的动态星轨背景，带有旋转和流星特效。
*   **玻璃拟态**：侧边栏、对话框和输入框采用磨砂玻璃效果 (Glassmorphism)，极具科技感。
*   **深色模式**：全局深色主题适配，保护视力且更具沉浸感。
*   **响应式布局**：基于 **Tailwind CSS** 构建，适配各种屏幕尺寸。

### 🛠️ 技术栈
*   **后端**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic, BeautifulSoup4 (网页抓取)
*   **前端**: Vue 3, Vite, Pinia, Tailwind CSS, KaTeX
*   **数据库**: SQLite (默认)

### 🚀 快速开始

#### 前置要求
*   Python 3.10+
*   Node.js 18+

#### 1. 后端设置
```bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 启动服务器
python -m uvicorn app.main:app --reload
```
后端服务运行在 `http://localhost:8000`。

#### 2. 前端设置
```bash
cd frontend
# 安装依赖
npm install
# 启动开发服务器
npm run dev
```
前端应用运行在 `http://localhost:5173`。

#### 3. 环境变量
在 `backend` 目录下创建 `.env` 文件：
```env
QWEN_API_KEY=your_qwen_key
DEEPSEEK_API_KEY=your_deepseek_key
SECRET_KEY=your_jwt_secret
```

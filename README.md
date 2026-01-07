# AI Chat Application
An AI Chat Web App with Multi-modal support (Text/File), built with FastAPI and Vue 3.

## Features
- **User Authentication**: Register and Login with JWT security.
- **AI Integration**: Support for Deepseek and Qwen (Alibaba) models.
- **Real-time Chat**: Streaming responses with typewriter effect.
- **Multi-modal Support**: Upload PDF/DOCX/TXT files to extract text and chat about them.
- **Chat History**: Auto-saved sessions and message history.
- **Responsive UI**: Modern interface built with Tailwind CSS.

## Tech Stack
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Vue 3, Vite, Pinia, Tailwind CSS
- **Database**: SQLite (Default) / PostgreSQL (Supported)

## Setup & Run

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend
1. Navigate to `backend` directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
   Server runs at `http://localhost:8000`.

### Frontend
1. Navigate to `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the dev server:
   ```bash
   npm run dev
   ```
   App runs at `http://localhost:5173`.

## Environment Variables
The app reads `.env` from the root directory. Ensure `QWEN_API_KEY` or `DEEPSEEK_API_KEY` are set.

# Semantix Chat

A ChatGPT-like web application with support for multiple LLM providers (OpenAI, Claude) and file upload capabilities.

## Features

- 🤖 Multiple LLM support (OpenAI GPT models, Claude models)
- 💬 Conversation history management
- 📁 File upload and PDF processing
- 🎨 Modern ChatGPT-like UI
- 🔧 Configurable hosting port (default: 5669)
- 🐳 Docker containerization

## Quick Start

### Using Docker (Recommended)
```bash
docker-compose up --build
```

### Manual Setup

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 5669
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

3. **Environment Configuration**
Create a `.env` file in the backend directory:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
PORT=5669
```

## API Endpoints

- `GET /chat/conversations` - Get conversation history
- `POST /chat/conversations` - Create new conversation
- `POST /chat/conversations/{id}/messages` - Send message
- `POST /chat/upload` - Upload file

## Architecture

- **Backend**: Python FastAPI with conversation management
- **Frontend**: React with modern UI components
- **Storage**: In-memory conversation storage (can be extended to database)
- **File Processing**: PDF text extraction and processing
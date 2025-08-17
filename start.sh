#!/bin/bash

# Semantix Chat Startup Script

set -e

echo "🚀 Starting Semantix Chat Application"
echo "=================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed or not in PATH"
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Creating backend/.env file from template..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env and add your API keys:"
    echo "   - OPENAI_API_KEY=your_openai_key"
    echo "   - ANTHROPIC_API_KEY=your_anthropic_key"
    echo ""
fi

# Build and start the application
echo "🔨 Building and starting containers..."
docker-compose up --build

echo "✅ Application should be running at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5669"
echo "   Health Check: http://localhost:5669/health"
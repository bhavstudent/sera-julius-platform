#!/bin/bash
# =====================================================================
# SERA JULIUS PLATFORM — ONE-CLICK LINUX / AWS EC2 DEPLOYMENT SCRIPT
# =====================================================================

set -e

echo "🚀 [SERA DEPLOY] Initializing SERA Julius Platform Deployment..."

# 1. Check Docker & Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed."
    exit 1
fi

# 2. Setup Environment Variables
if [ ! -f .env ]; then
    echo "📋 [SERA DEPLOY] Copying .env.example to .env..."
    cp .env.example .env
fi

# 3. Build & Run Frontend Assets
echo "📦 [SERA DEPLOY] Building Frontend Assets..."
cd frontend
npm install --silent || true
npm run build
cd ..

# 4. Launch Docker Containers (PostgreSQL, Redis, Neo4j, Backend, Nginx)
echo "🐳 [SERA DEPLOY] Launching Microservice Stack with Docker Compose..."
docker compose up -d --build

echo ""
echo "====================================================================="
echo "✅ SERA JULIUS PLATFORM IS LIVE & DEPLOYED!"
echo "====================================================================="
echo "  - Nginx Reverse Proxy : http://localhost (Port 80)"
echo "  - FastAPI Backend API : http://localhost:8000"
echo "  - PostgreSQL Database : localhost:5432"
echo "  - Redis In-Memory     : localhost:6379"
echo "  - Neo4j Graph DB      : localhost:7474 / bolt://localhost:7687"
echo "====================================================================="

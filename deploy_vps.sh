#!/bin/bash
# =====================================================================
# SERA PLATFORM — 1-CLICK AUTOMATED VPS / ORACLE CLOUD DEPLOYMENT SCRIPT
# =====================================================================

set -e

echo "🚀 Starting SERA Platform Deployment..."

# 1. Update system packages
sudo apt-get update -y && sudo apt-get upgrade -y

# 2. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# 3. Install Docker Compose plugin if not present
if ! docker compose version &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin
fi

# 4. Configure firewall rules for HTTP, HTTPS, WebSockets & API
echo "🛡️ Configuring Firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 8000/tcp
    sudo ufw allow 5173/tcp
    sudo ufw allow 5432/tcp
    sudo ufw allow 6379/tcp
    sudo ufw allow 7687/tcp
    sudo ufw --force enable
fi

# 5. Build and launch all 6 SERA Docker containers
echo "⚡ Building & Launching SERA Platform Containers..."
sudo docker compose up -d --build

# 6. Check Container Health
echo ""
echo "====================================================================="
echo "✅ SERA PLATFORM SUCCESSFULLY DEPLOYED!"
echo "====================================================================="
sudo docker compose ps
echo ""
echo "🌐 Access Points:"
echo "   - Frontend UI:        http://$(curl -s ifconfig.me):5173 (or :80)"
echo "   - Backend API Docs:   http://$(curl -s ifconfig.me):8000/docs"
echo "   - WebSocket Stream:   ws://$(curl -s ifconfig.me):8000/ws"
echo "====================================================================="

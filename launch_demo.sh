#!/bin/bash

# Get the current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 INTITIALIZING IOT DEMO LAUNCH SEQUENCE..."
echo "📂 Working Directory: $DIR"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker is not running. Please start Docker Desktop first!"
  exit 1
fi

echo "🐳 Ensuring Containers are up..."
docker-compose up -d
sleep 2

echo "🖥️  Opening Terminals..."

# 1. GATEWAY (Data Generator)
osascript -e "tell application \"Terminal\" to do script \"cd '$DIR' && clear && echo '==================================================' && echo '🟢 GATEWAY SERVICE (Data Generator)' && echo '==================================================' && docker exec -it python-apps python src/gateway/gateway.py\""

# 2. PERSISTER (Database Saver - Mongo Visualization)
osascript -e "tell application \"Terminal\" to do script \"cd '$DIR' && clear && echo '==================================================' && echo '💾 PERSISTER SERVICE (MongoDB Storage)' && echo '==================================================' && docker exec -it python-apps python src/persister/persister.py\""

# 3. ALERT SYSTEM (Abnormal Data Notification)
osascript -e "tell application \"Terminal\" to do script \"cd '$DIR' && clear && echo '==================================================' && echo '🚨 ALERT SYSTEM (Real-time Notifications)' && echo '==================================================' && docker exec -it python-apps python src/alert/alert_system.py\""

# 4. SPARK ENGINE (Analytics)
# Clear old checkpoints to prevent "Concurrent update" errors
docker exec spark-master rm -rf /tmp/checkpoints

# We add a small sleep here to let the others initialize first
osascript -e "tell application \"Terminal\" to do script \"cd '$DIR' && clear && echo '==================================================' && echo '⚡ SPARK STREAMING ENGINE' && echo '==================================================' && echo '⏳ Waiting 5s for initialization...' && sleep 5 && docker exec -it spark-master spark-submit /app/src/spark/processor.py\""


echo "✅ All systems launched!"
echo "🌐 Open your NEW Dashboard: http://localhost:3000"
echo "🔌 API Docs available at: http://localhost:8000/docs"
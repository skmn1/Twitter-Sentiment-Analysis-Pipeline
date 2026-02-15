#!/bin/bash

# launch.sh - Launch the complete pipeline

echo "🚀 Starting Tweet Analysis Pipeline..."

# Set environment
export PYTHONPATH=$PWD:$PYTHONPATH

# Check Docker services and restart if needed
echo "📦 Checking Docker services..."
if ! docker-compose ps | grep -q "kafka.*Up"; then
    echo "⚠️  Kafka not running, starting Docker services..."
    docker-compose up -d
    echo "⏳ Waiting for services to initialize (30 seconds)..."
    sleep 30
else
    echo "✅ Docker services already running"
fi

# Verify services
echo "✅ Verifying services..."
docker-compose ps

# Wait for Kafka to be responsive
echo "🔗 Waiting for Kafka broker to be ready..."
for i in {1..30}; do
    if docker exec kafka cub kafka-ready -b localhost:9092 1 30 &>/dev/null; then
        echo "✅ Kafka broker is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Kafka broker failed to start. Check logs:"
        docker-compose logs kafka | tail -20
        exit 1
    fi
    echo "  Attempt $i/30..."
    sleep 1
done

# Start Spark consumer in background
echo "⚡ Starting Spark consumer..."
python consumer/spark_consumer.py > logs/spark_consumer.log 2>&1 &
SPARK_PID=$!
sleep 5

# Start producer in background
echo "📤 Starting Kafka producer..."
python -m producer.stream_simulator > logs/producer.log 2>&1 &
PRODUCER_PID=$!
sleep 3

# Start Streamlit dashboard
echo "📊 Starting dashboard..."
echo "Dashboard will be available at http://localhost:8501"
echo ""
echo "Background processes:"
echo "  Spark Consumer PID: $SPARK_PID"
echo "  Producer PID: $PRODUCER_PID"
echo ""
streamlit run dashboard/app.py

# Twitter Sentiment Analysis Pipeline

A real-time big data pipeline for Twitter sentiment analysis using Kafka, Spark Streaming, MongoDB, and Streamlit.

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐      ┌──────────┐      ┌────────────────┐
│  Tweet Dataset  │───▶ │    Kafka      │────▶│  Spark Streaming│────▶│ MongoDB   │────▶│   Streamlit    │
│ (JSON File)     │      │   Producer   │      │   Consumer      │      │          │      │   Dashboard    │
└─────────────────┘      └──────────────┘      └─────────────────┘      └──────────┘      └────────────────┘
                               │                       │                                         │
                               ▼                       ▼                                         ▼
                         ┌──────────┐          ┌─────────────┐                            ┌──────────┐
                         │  Kafka   │          │  Sentiment  │                            │  Real-   │
                         │  Broker  │          │  Analysis   │                            │  Time    │
                         └──────────┘          └─────────────┘                            │  Viz     │
                               │                       │                                  └──────────┘
                               ▼                       ▼
                         ┌──────────┐          ┌─────────────┐
                         │Zookeeper │          │  Entity     │
                         │          │          │ Extraction  │
                         └──────────┘          └─────────────┘
```

### Detailed Component Architecture

#### 1. **Data Ingestion Layer**
- **Stream Simulator** (`producer/stream_simulator.py`)
  - Reads tweets from JSON dataset
  - Simulates real-time streaming at configurable rate (default: 50 tweets/sec)
  - Publishes to Kafka topic `tweets_stream`
  - Supports continuous looping for long-running demos

#### 2. **Message Streaming Layer**
- **Apache Kafka** (Port: 9092)
  - Distributed message broker
  - Topic: `tweets_stream`
  - Provides fault-tolerance and scalability
- **Zookeeper** (Port: 2181)
  - Coordination service for Kafka cluster

#### 3. **Processing Layer**
- **Spark Streaming Consumer** (`consumer/spark_consumer.py`)
  - Consumes tweets from Kafka in micro-batches
  - Performs sentiment analysis using VADER
  - Extracts hashtags and mentions
  - Processes batches every 5 seconds
  - Technologies:
    - PySpark 3.3.0
    - Spark Structured Streaming
    - Kafka-Spark Integration

#### 4. **Storage Layer**
- **MongoDB** (Port: 27017)
  - NoSQL database for flexible tweet storage
  - Database: `twitter_analysis`
  - Collection: `tweets`
  - Stores enriched tweet data with sentiment scores

#### 5. **Visualization Layer**
- **Streamlit Dashboard** (Port: 8501)
  - Real-time visualization of sentiment trends
  - Interactive charts and metrics
  - Auto-refreshing data displays

## 📋 Components

### 1. **Producer** (`producer/`)
- **stream_simulator.py**: Simulates real-time tweet streaming by reading from dataset and publishing to Kafka
- **config.py**: Configuration file for Kafka, MongoDB, and streaming parameters

### 2. **Consumer** (`consumer/`)
- **spark_consumer.py**: Spark Streaming application that consumes tweets from Kafka, performs sentiment analysis, and stores results in MongoDB

### 3. **Dashboard** (`dashboard/`)
- **app.py**: Streamlit web dashboard for real-time visualization of sentiment analysis results

### 4. **Utilities** (`utils/`)
- **sentiment_analysis.py**: Sentiment analysis logic, hashtag and mention extraction
- **database.py**: MongoDB connection and operations

### 5. **Infrastructure** (`docker-compose.yml`)
- **Zookeeper**: Kafka coordination service
- **Kafka**: Message broker for streaming data
- **MongoDB**: NoSQL database for storing analyzed tweets

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Java 11 (for Spark)
- Apache Spark 3.3.0

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd tweet-analysis
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Apache Spark** (if not already installed)
```bash
# Download and extract Spark
wget https://archive.apache.org/dist/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3.tgz
tar xzf spark-3.3.0-bin-hadoop3.tgz
sudo mv spark-3.3.0-bin-hadoop3 /opt/spark

# Add to PATH
export SPARK_HOME=/opt/spark
export PATH=$SPARK_HOME/bin:$PATH

# Add to ~/.bashrc for persistence
echo 'export SPARK_HOME=/opt/spark' >> ~/.bashrc
echo 'export PATH=$SPARK_HOME/bin:$PATH' >> ~/.bashrc
```

4. **Prepare the dataset**
- Place your `tweets_clean.json` file in the `data/` directory
- The dataset should contain tweet data in JSON format

### Running the Pipeline

Follow these steps to launch the complete pipeline:

#### Step 1: Create and Activate Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Step 2: Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

The requirements include:
- `pyspark==3.3.0` - Spark processing engine
- `kafka-python==2.0.2` - Kafka client
- `pymongo==4.5.0` - MongoDB driver
- `streamlit==1.28.0` - Dashboard framework
- `textblob==0.17.1` & `vaderSentiment==3.3.2` - Sentiment analysis
- `plotly==5.17.0` - Interactive visualizations

#### Step 3: Start Infrastructure Services

```bash
# Start Docker containers (Kafka, Zookeeper, MongoDB)
docker-compose up -d

# Wait 10-15 seconds for services to initialize
sleep 15

# Verify all containers are running
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                              STATUS          PORTS
kafka          confluentinc/cp-kafka:7.4.0        Up X minutes   0.0.0.0:9092->9092/tcp
zookeeper      confluentinc/cp-zookeeper:latest   Up X minutes   0.0.0.0:2181->2181/tcp
mongodb        mongo:latest                       Up X minutes   0.0.0.0:27017->27017/tcp
```

#### Step 4: Start Spark Consumer (Terminal 1)

```bash
# Set PYTHONPATH to project root
export PYTHONPATH=/path/to/tweet-analysis:$PYTHONPATH

# Start Spark consumer
python consumer/spark_consumer.py
```

Expected output:
```
INFO:__main__:✅ Spark Session initialized
INFO:__main__:🔗 Connecting to Kafka: localhost:9092
INFO:__main__:✅ Kafka stream connected
INFO:__main__:🚀 Spark Consumer started - Waiting for data...
```

#### Step 5: Start Kafka Producer (Terminal 2)

```bash
# Navigate to project directory
cd /path/to/tweet-analysis

# Set PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH

# Start producer
python -m producer.stream_simulator
```

Expected output:
```
INFO:__main__:✅ Kafka Producer initialized
INFO:__main__:📊 Dataset loaded: 1578438 tweets
INFO:__main__:🚀 Starting stream (50 tweets/sec)
INFO:__main__:📤 100 tweets sent
INFO:__main__:📤 200 tweets sent
...
```

You should see in the Spark consumer terminal:
```
INFO:__main__:✅ Batch 0: 243 tweets processed
INFO:__main__:✅ Batch 1: 250 tweets processed
...
```

#### Step 6: Launch Dashboard (Terminal 3)

```bash
# Start Streamlit dashboard
streamlit run dashboard/app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open your browser and navigate to **http://localhost:8501**

### Quick Launch Script

For convenience, you can use this script to launch all components:

```bash
#!/bin/bash

# launch.sh - Launch the complete pipeline

echo "🚀 Starting Tweet Analysis Pipeline..."

# Start Docker services
echo "📦 Starting Docker services..."
docker-compose up -d
sleep 15

# Check if services are running
echo "✅ Verifying services..."
docker ps | grep -E "kafka|mongodb|zookeeper"

# Set environment
export PYTHONPATH=$PWD:$PYTHONPATH

# Start Spark consumer in background
echo "⚡ Starting Spark consumer..."
python consumer/spark_consumer.py > logs/spark_consumer.log 2>&1 &

sleep 5

# Start producer in background
echo "📤 Starting Kafka producer..."
python -m producer.stream_simulator > logs/producer.log 2>&1 &

sleep 3

# Start Streamlit dashboard
echo "📊 Starting dashboard..."
echo "Dashboard will be available at http://localhost:8501"
streamlit run dashboard/app.py

```

Save as `launch.sh`, make executable (`chmod +x launch.sh`), and run: `./launch.sh`

## 📊 Configuration

### Producer Configuration (`producer/config.py`)
```python
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "tweets_stream"
TWEETS_PER_SECOND = 50  # Streaming rate
DATASET_PATH = "data/tweets_clean.json"
LOOP_DATASET = True  # Loop through dataset continuously
```

### MongoDB Configuration
```python
MONGO_URI = "mongodb://admin:password@localhost:27017/"
MONGO_DB = "twitter_analysis"
MONGO_COLLECTION = "tweets"
```

## 🔍 Features

- **Real-time Processing**: Processes tweets as they stream through Kafka
- **Sentiment Analysis**: Analyzes tweet sentiment (Positive/Negative/Neutral) using VADER
- **Entity Extraction**: Extracts hashtags and mentions from tweet text
- **Data Storage**: Stores processed tweets in MongoDB with full metadata
- **Live Dashboard**: Real-time visualization with Streamlit
- **Scalable Architecture**: Built on industry-standard big data tools

## 📸 Screenshots

### Dashboard Overview

The Streamlit dashboard provides real-time visualization of tweet sentiment analysis with interactive charts and metrics.

![Dashboard Main View](images/dashboard-screenshot.png)
*Main dashboard showing real-time sentiment analysis metrics and visualizations*

### Sentiment Distribution

Real-time charts displaying sentiment distribution across positive, negative, and neutral tweets with percentage breakdowns.

![Sentiment Distribution](images/sentiment-charts1.png)
*Sentiment distribution pie chart showing the proportion of different sentiment categories*

### Hashtag Analysis

Visual analysis of the most frequently occurring hashtags in the processed tweets.

![Hashtag Analysis](images/sentiment-charts2.png)
*Top hashtags word cloud and frequency chart from tweet analysis*

### Detailed Tweets View

Detailed table view showing individual tweets with their sentiment scores, hashtags, and metadata.

![Detailed Tweets](images/sentiment-charts3.png)
*Real-time feed of processed tweets with sentiment analysis results*

## 🔄 Data Flow

### 1. Tweet Ingestion
```python
# Producer reads tweets from JSON file
tweet = {
    "id": 1467810369,
    "text": "This is an amazing product! #love",
    "created_at": "Mon Apr 06 22:19:45 PDT 2009",
    "user": "@switchfoot"
}
```

### 2. Kafka Streaming
- Producer serializes tweet to JSON
- Publishes to Kafka topic `tweets_stream`
- Kafka maintains message queue for fault tolerance

### 3. Spark Processing
```python
# Spark consumer applies transformations:
- Parse JSON from Kafka
- Extract text field
- Perform sentiment analysis → "Positive", score: 0.85
- Extract entities → hashtags: ["love"], mentions: []
- Add processing timestamp
```

### 4. Data Enrichment
```python
# Enriched tweet structure:
{
    "id": 1467810369,
    "text": "This is an amazing product! #love",
    "created_at": "Mon Apr 06 22:19:45 PDT 2009",
    "user": "@switchfoot",
    "sentiment": "Positive",
    "sentiment_score": 0.85,
    "hashtags": ["love"],
    "mentions": [],
    "processing_timestamp": "2026-02-15T09:44:40.123Z"
}
```

### 5. MongoDB Storage
- Batch writes to MongoDB collection
- Indexed for fast querying
- Supports aggregations for analytics

### 6. Dashboard Visualization
- Streamlit queries MongoDB in real-time
- Displays sentiment distribution, trends, top hashtags
- Auto-refreshes every few seconds

## 🛠️ Tech Stack

- **Apache Kafka**: Distributed streaming platform
- **Apache Spark**: Large-scale data processing
- **MongoDB**: NoSQL database
- **Streamlit**: Web dashboard framework
- **Docker**: Containerization
- **Python**: Primary programming language

## 📁 Project Structure

```
tweet-analysis/
├── consumer/
│   └── spark_consumer.py          # Spark streaming consumer
├── producer/
│   ├── config.py                   # Configuration
│   └── stream_simulator.py         # Kafka producer
├── dashboard/
│   └── app.py                      # Streamlit dashboard
├── utils/
│   ├── sentiment_analysis.py       # Sentiment analysis logic
│   └── database.py                 # MongoDB operations
├── data/
│   └── tweets_clean.json           # Tweet dataset
├── scripts/
├── docker-compose.yml              # Infrastructure services
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🧪 Testing

Monitor the pipeline:

1. **Check Kafka topics**
```bash
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

2. **Monitor Spark logs**
Watch the Spark consumer terminal for processing logs

3. **Check MongoDB data**
```bash
docker exec -it mongodb mongosh -u admin -p password
use twitter_analysis
db.tweets.countDocuments()
db.tweets.find().limit(5)
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Import Error: "pyspark.sql" could not be resolved

**Problem**: PySpark not installed in the current environment.

**Solution**:
```bash
# Activate virtual environment if using one
source .venv/bin/activate

# Install PySpark
pip install pyspark==3.3.0

# Verify installation
python -c "import pyspark; print(pyspark.__version__)"
```

#### 2. Module Import Errors (utils, config, etc.)

**Problem**: Python can't find project modules.

**Solution**:
```bash
# Set PYTHONPATH to project root
export PYTHONPATH=/path/to/tweet-analysis:$PYTHONPATH

# Or use module syntax for imports
python -m producer.stream_simulator
```

#### 3. Kafka Connection Refused

**Problem**: Kafka not ready or not running.

**Solution**:
```bash
# Check if Kafka container is running
docker ps | grep kafka

# Check Kafka logs
docker-compose logs kafka

# Restart services if needed
docker-compose restart kafka

# Ensure Kafka has fully started (wait 10-15 seconds)
sleep 15
```

#### 4. MongoDB Authentication Failed

**Problem**: Incorrect MongoDB credentials.

**Solution**:
```bash
# Check docker-compose.yml for credentials
# Default: admin/password

# Test connection
docker exec -it mongodb mongosh -u admin -p password

# Verify config.py has matching credentials
cat config.py | grep MONGO
```

#### 5. Spark Consumer Not Processing Data

**Problem**: Consumer started but no batches processed.

**Solution**:
```bash
# 1. Verify Kafka topic exists and has data
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# 2. Check consumer offset
docker exec -it kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list

# 3. Ensure producer is running and sending data
# Look for "📤 tweets sent" messages

# 4. Check Spark logs for errors
# Look in the Spark consumer terminal output
```

#### 6. Dashboard Not Loading

**Problem**: Streamlit not accessible on port 8501.

**Solution**:
```bash
# Check if Streamlit is running
lsof -i :8501

# Kill existing Streamlit process if needed
pkill -f streamlit

# Restart dashboard
streamlit run dashboard/app.py

# If port is in use, specify different port
streamlit run dashboard/app.py --server.port 8502
```

#### 7. Virtual Environment Issues

**Problem**: Packages not found even after installation.

**Solution**:
```bash
# Verify you're in the virtual environment
which python  # Should show .venv/bin/python

# If not, activate it
source .venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

### Performance Issues

#### Slow Processing

- **Reduce streaming rate**: Edit `config.py` and set `TWEETS_PER_SECOND = 10`
- **Increase batch interval**: In `spark_consumer.py`, change `processingTime='5 seconds'` to longer interval
- **Check system resources**: `htop` or `top` to monitor CPU/memory

#### Memory Issues

- Add Spark configuration in `spark_consumer.py`:
```python
.config("spark.executor.memory", "2g") \
.config("spark.driver.memory", "2g") \
```

### Logs and Monitoring

```bash
# View all Docker logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f kafka
docker-compose logs -f mongodb

# Monitor MongoDB data
docker exec -it mongodb mongosh -u admin -p password
use twitter_analysis
db.tweets.countDocuments()
db.tweets.find().sort({processing_timestamp: -1}).limit(5)

# Monitor Kafka topic
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic tweets_stream \
  --from-beginning \
  --max-messages 10
```

## 📝 License

This project is for educational purposes.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue in the repository.

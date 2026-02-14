# Twitter Sentiment Analysis Pipeline

A real-time big data pipeline for Twitter sentiment analysis using Kafka, Spark Streaming, MongoDB, and Streamlit.

## 🏗️ Architecture

```
Tweets Dataset → Kafka Producer → Kafka Broker → Spark Streaming → MongoDB → Streamlit Dashboard
```

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

1. **Start infrastructure services** (Kafka, Zookeeper, MongoDB)
```bash
docker-compose up -d
```

2. **Verify services are running**
```bash
docker ps
```
You should see: `kafka`, `zookeeper`, and `mongodb` containers running.

3. **Start the Spark consumer** (in a terminal)
```bash
export SPARK_HOME=/opt/spark
export PATH=$SPARK_HOME/bin:$PATH
export PYTHONPATH=$PWD:$PYTHONPATH

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 consumer/spark_consumer.py
```

4. **Start the Kafka producer** (in another terminal)
```bash
python -m producer.stream_simulator
```

5. **Launch the dashboard** (in another terminal)
```bash
streamlit run dashboard/app.py
```

The dashboard will be available at `http://localhost:8501`

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
- **Sentiment Analysis**: Analyzes tweet sentiment (Positive/Negative/Neutral)
- **Entity Extraction**: Extracts hashtags and mentions
- **Data Storage**: Stores processed tweets in MongoDB
- **Live Dashboard**: Real-time visualization with Streamlit
- **Scalable Architecture**: Built on industry-standard big data tools

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

### Kafka Connection Refused
```bash
# Ensure Kafka is fully started
docker-compose logs kafka

# Restart services if needed
docker-compose restart
```

### Module Import Errors
```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/tweet-analysis:$PYTHONPATH

# Or use module syntax
python -m producer.stream_simulator
```

### Spark Not Found
```bash
# Verify Spark installation
spark-submit --version

# Set environment variables
export SPARK_HOME=/opt/spark
export PATH=$SPARK_HOME/bin:$PATH
```

## 📝 License

This project is for educational purposes.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue in the repository.

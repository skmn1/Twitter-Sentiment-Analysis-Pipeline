# Kafka Configuration
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "tweets_stream"

# MongoDB Configuration
MONGO_URI = "mongodb://admin:password@localhost:27017/"
MONGO_DB = "twitter_analysis"
MONGO_COLLECTION = "tweets"

# Simulator Configuration
TWEETS_PER_SECOND = 50  # Injection speed
DATASET_PATH = "data/tweets_clean.json"
LOOP_DATASET = True  # Loop when reaching end of dataset
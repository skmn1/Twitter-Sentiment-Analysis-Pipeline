from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, current_timestamp, explode, split
from pyspark.sql.types import StructType, StructField, StringType, LongType, ArrayType
import sys
import logging

sys.path.append('..')
from utils.sentiment_analysis import analyze_sentiment, extract_hashtags, extract_mentions
from utils.database import MongoDatabase
from config import KAFKA_BROKER, KAFKA_TOPIC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Spark
spark = SparkSession.builder \
    .appName("TwitterSentimentAnalysis") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
logger.info("✅ Spark Session initialized")

# Tweet schema
tweet_schema = StructType([
    StructField("id", LongType(), True),
    StructField("text", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("user", StringType(), True),
    StructField("simulated_timestamp", StringType(), True)
])

# UDFs for processing
def get_sentiment(text):
    sentiment, score = analyze_sentiment(text)
    return sentiment

def get_score(text):
    sentiment, score = analyze_sentiment(text)
    return float(score)

def get_hashtags(text):
    return extract_hashtags(text)

def get_mentions(text):
    return extract_mentions(text)

sentiment_udf = udf(get_sentiment, StringType())
score_udf = udf(get_score, StringType())
hashtags_udf = udf(get_hashtags, ArrayType(StringType()))
mentions_udf = udf(get_mentions, ArrayType(StringType()))

# Read Kafka stream
logger.info(f"🔗 Connecting to Kafka: {KAFKA_BROKER}")
df_raw = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

logger.info("✅ Kafka stream connected")

# Parse JSON
df_parsed = df_raw.select(
    from_json(col("value").cast("string"), tweet_schema).alias("data")
).select("data.*")

# Enrich with analysis
df_enriched = df_parsed \
    .withColumn("sentiment", sentiment_udf(col("text"))) \
    .withColumn("sentiment_score", score_udf(col("text"))) \
    .withColumn("hashtags", hashtags_udf(col("text"))) \
    .withColumn("mentions", mentions_udf(col("text"))) \
    .withColumn("processing_timestamp", current_timestamp())

# Function to write to MongoDB
def write_batch_to_mongo(batch_df, batch_id):
    """Write each batch to MongoDB"""
    try:
        mongo_db = MongoDatabase()
        
        # Convert to list of dictionaries
        tweets = batch_df.collect()
        tweets_dict = [row.asDict() for row in tweets]
        
        # Batch insertion
        if tweets_dict:
            mongo_db.insert_many_tweets(tweets_dict)
            logger.info(f"✅ Batch {batch_id}: {len(tweets_dict)} tweets processed")
        
    except Exception as e:
        logger.error(f"❌ Batch {batch_id} error: {e}")

# Configure streaming to MongoDB
query = df_enriched \
    .writeStream \
    .foreachBatch(write_batch_to_mongo) \
    .outputMode("append") \
    .trigger(processingTime='5 seconds') \
    .start()

logger.info("🚀 Spark Consumer started - Waiting for data...")
logger.info("📊 Tweets will be processed in batches every 5 seconds")

# Periodic statistics
try:
    query.awaitTermination()
except KeyboardInterrupt:
    logger.info("\n⛔ Stopping Spark consumer")
    query.stop()
    spark.stop()
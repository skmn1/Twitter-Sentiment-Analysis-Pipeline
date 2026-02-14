from kafka import KafkaProducer
import json
import time
import logging
from datetime import datetime
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TweetStreamSimulator:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.tweet_count = 0
        logger.info("✅ Kafka Producer initialized")
    
    def load_dataset(self):
        """Load the tweet dataset"""
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            tweets = json.load(f)
        logger.info(f"📊 Dataset loaded: {len(tweets)} tweets")
        return tweets
    
    def simulate_stream(self):
        """Simulate a real-time tweet stream"""
        tweets = self.load_dataset()
        delay = 1.0 / TWEETS_PER_SECOND  # Delay between each tweet
        
        logger.info(f"🚀 Starting stream ({TWEETS_PER_SECOND} tweets/sec)")
        
        idx = 0
        while True:
            try:
                tweet = tweets[idx]
                
                # Add current timestamp to simulate real-time
                tweet['simulated_timestamp'] = datetime.now().isoformat()
                
                # Send to Kafka
                self.producer.send(KAFKA_TOPIC, value=tweet)
                
                self.tweet_count += 1
                
                # Log every 100 tweets
                if self.tweet_count % 100 == 0:
                    logger.info(f"📤 {self.tweet_count} tweets sent")
                
                # Delay to simulate realistic flow
                time.sleep(delay)
                
                # Handle end of dataset
                idx += 1
                if idx >= len(tweets):
                    if LOOP_DATASET:
                        logger.info("🔄 Looping dataset")
                        idx = 0
                    else:
                        logger.info("✅ End of dataset reached")
                        break
                        
            except KeyboardInterrupt:
                logger.info(f"\n⛔ Stopping producer. Total sent: {self.tweet_count}")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                time.sleep(1)
        
        self.producer.close()

def main():
    simulator = TweetStreamSimulator()
    simulator.simulate_stream()

if __name__ == "__main__":
    main()
from pymongo import MongoClient
from datetime import datetime
import logging
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

logger = logging.getLogger(__name__)

class MongoDatabase:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[MONGO_DB]
            self.collection = self.db[MONGO_COLLECTION]
            
            # Create indexes for performance
            self.collection.create_index("timestamp")
            self.collection.create_index("sentiment")
            
            logger.info("✅ MongoDB connection established")
        except Exception as e:
            logger.error(f"❌ MongoDB error: {e}")
    
    def insert_tweet(self, tweet_data):
        """Insert a tweet"""
        try:
            tweet_data['inserted_at'] = datetime.now()
            self.collection.insert_one(tweet_data)
        except Exception as e:
            logger.error(f"❌ Insertion error: {e}")
    
    def insert_many_tweets(self, tweets_list):
        """Insert multiple tweets (more performant)"""
        try:
            if tweets_list:
                for tweet in tweets_list:
                    tweet['inserted_at'] = datetime.now()
                self.collection.insert_many(tweets_list)
        except Exception as e:
            logger.error(f"❌ Batch insertion error: {e}")
    
    def get_stats(self):
        """General statistics"""
        total = self.collection.count_documents({})
        sentiments = self.collection.aggregate([
            {'$group': {'_id': '$sentiment', 'count': {'$sum': 1}}}
        ])
        return {
            'total': total,
            'sentiments': list(sentiments)
        }

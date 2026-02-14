from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Two analysis engines available
analyzer_vader = SentimentIntensityAnalyzer()

def clean_tweet(text):
    """Clean the text"""
    text = re.sub(r'http\S+', '', text)  # URLs
    text = re.sub(r'@\w+', '', text)     # Mentions
    text = re.sub(r'RT\s+', '', text)    # Retweets
    text = re.sub(r'#', '', text)        # # from hashtags
    text = re.sub(r'[^\w\s]', '', text)  # Punctuation
    return text.strip().lower()

def analyze_sentiment_textblob(text):
    """Analysis with TextBlob (simple)"""
    try:
        cleaned = clean_tweet(text)
        blob = TextBlob(cleaned)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive', polarity
        elif polarity < -0.1:
            return 'negative', polarity
        else:
            return 'neutral', polarity
    except:
        return 'neutral', 0.0

def analyze_sentiment_vader(text):
    """Analysis with VADER (better for social media)"""
    try:
        cleaned = clean_tweet(text)
        scores = analyzer_vader.polarity_scores(cleaned)
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return sentiment, compound
    except:
        return 'neutral', 0.0

def extract_hashtags(text):
    """Extract hashtags"""
    return re.findall(r'#\w+', text)

def extract_mentions(text):
    """Extract mentions"""
    return re.findall(r'@\w+', text)

# Main function (use VADER, more accurate)
def analyze_sentiment(text):
    return analyze_sentiment_vader(text)

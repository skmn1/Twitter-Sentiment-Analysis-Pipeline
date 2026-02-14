import pandas as pd
import json

# path to the dataset
dataset_path = 'data/training.1600000.processed.noemoticon.csv'  # Update this path to your dataset

# Load the dataset
df = pd.read_csv(dataset_path, header=None, names=['target', 'id', 'date', 'query', 'user', 'text'], encoding='latin-1')

print("=== Dataset Overview ===")
print(df.head())
print(f"\nTotal number of tweets: {len(df)}")
print(f"\nAvailable columns: {df.columns.tolist()}")
print(f"\nMissing values:\n{df.isnull().sum()}")

# Clean the data
df = df.dropna(subset=['text'])  # Remove empty tweets
df = df[df['text'].str.len() > 10]  # Minimum 10 characters
df = df.drop_duplicates(subset=['text'])  # Remove duplicates

print(f"\nAfter cleaning: {len(df)} tweets")

# Convert to JSON format for Kafka
def prepare_tweet(row):
    return {
        'id': int(row.get('id', 0)),
        'text': str(row['text']),
        'created_at': str(row.get('date', '2024-01-01')),
        'user': str(row.get('user', 'anonymous'))
    }

# Save cleaned dataset
tweets_clean = [prepare_tweet(row) for _, row in df.iterrows()]

with open('tweets_clean.json', 'w', encoding='utf-8') as f:
    json.dump(tweets_clean, f, ensure_ascii=False, indent=2)

print(f"\n✅ Cleaned dataset saved: tweets_clean.json")
print(f"📊 Ready for Kafka injection")
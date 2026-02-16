# 🎓 Twitter Sentiment Analysis Pipeline - Interactive Learning Tool

> Master the Big Data Pipeline through flashcards, quiz questions, and practical scenarios

---

## 📚 Table of Contents
- [Flashcards](#flashcards)
  - [Beginner Level](#beginner-cards)
  - [Intermediate Level](#intermediate-cards)
  - [Advanced Level](#advanced-cards)
- [Quiz Questions](#quiz-questions)
  - [Multiple Choice](#multiple-choice-questions)
  - [True/False](#truefalse-questions)
  - [Scenario-Based](#scenario-based-questions)
  - [Code Comprehension](#code-comprehension-questions)
  - [Sequencing/Ordering](#sequencing-questions)
- [Answer Key](#answer-key)
- [Scoring Guide](#scoring-guide)

---

# 🧠 Flashcards

## Beginner Cards

### Card 1: Kafka Fundamentals
**Question**: What is Apache Kafka and what is its primary role in this pipeline?

> <details>
> <summary>Answer</summary>
> Apache Kafka is a distributed, fault-tolerant message broker that acts as a streaming platform. In this pipeline, it serves as the transport layer between the producer (stream simulator) and consumer (Spark), decoupling them and ensuring no tweets are lost even if the consumer temporarily stops.
> </details>

---

### Card 2: VADER Sentiment Analysis
**Question**: What does VADER stand for and why was it chosen over other sentiment analysis tools?

> <details>
> <summary>Answer</summary>
> VADER = Valence Aware Dictionary and sEntiment Reasoner. It was chosen because:
> - Optimized specifically for social media text
> - Fast processing (<1ms per tweet, no ML model training required)
> - Native emoji/emoticon support
> - Handles internet slang and informal language
> - 78.4% accuracy on the dataset, best balance of speed/accuracy for real-time processing
> </details>

---

### Card 3: MongoDB's Role
**Question**: What is MongoDB and why is it used instead of a traditional SQL database?

> <details>
> <summary>Answer</summary>
> MongoDB is a NoSQL document database. It's used because:
> - Flexible schema: Can adapt when tweet structure changes
> - Fast aggregation queries for dashboard analytics
> - Horizontal scalability for handling millions of tweets
> - JSON-native format matches our data structure
> - Suitable for real-time data ingestion and retrieval
> </details>

---

### Card 4: The Three Layers of Processing
**Question**: Name the three main processing layers in the pipeline and describe what each does.

> <details>
> <summary>Answer</summary>
> 1. **Ingestion Layer**: Stream Simulator reads tweets from JSON file and sends them to Kafka at 50 tweets/sec
> 2. **Processing Layer**: Spark Streaming consumes messages, applies VADER sentiment analysis, extracts hashtags/mentions
> 3. **Storage Layer**: MongoDB stores enriched tweets for fast queries
> </details>

---

### Card 5: Real-Time vs Batch Processing
**Question**: Why is Spark Streaming better than batch processing for a sentiment analysis pipeline?

> <details>
> <summary>Answer</summary>
> Spark Streaming provides:
> - **Near real-time processing**: Processes tweets in micro-batches every ~5 seconds
> - **Lower latency**: Users see sentiment results almost immediately
> - **Continuous operation**: No scheduled batch windows, continuous data flow
> - **Dashboard freshness**: Dashboard can auto-refresh with latest data
> - **Responsiveness**: Can react to trends as they emerge
> </details>

---

### Card 6: Data Cleaning Pipeline
**Question**: What were the main data quality issues found in the raw Sentiment140 dataset and how were they fixed?

> <details>
> <summary>Answer</summary>
> Issues and fixes:
> - **Exact duplicates (21,373)**: Removed, keeping first occurrence
> - **Tweets too short (<10 chars)**: Filtered out (insufficient context for analysis)
> - **HTML entities**: Decoded (e.g., `&amp;` → `&`)
> - **Encoding issues**: Normalized UTF-8
> - **Whitespace**: Normalized (multiple spaces → single space)
> - **Result**: 1,578,438 clean tweets (98.65% retention rate)
> </details>

---

### Card 7: Stream Simulator Purpose
**Question**: What does the stream simulator do and why is it separate from the actual data source in production?

> <details>
> <summary>Answer</summary>
> The stream simulator:
> - Reads from the cleaned JSON dataset file
> - Publishes tweets to Kafka at a configurable rate (default 50 tweets/sec)
> - Simulates real-time Twitter stream for development/testing
> 
> In production, the actual Twitter API would replace this, but the simulator allows:
> - Consistent/reproducible testing
> - No dependency on live Twitter API during development
> - No authentication/rate limit concerns
> - Cost-free development environment
> </details>

---

### Card 8: Sentiment Scoring Thresholds
**Question**: What are the threshold values for classifying a tweet as positive, negative, or neutral in VADER?

> <details>
> <summary>Answer</summary>
> VADER uses the "compound" score (range -1.0 to +1.0):
> - **Positive**: compound >= 0.05
> - **Negative**: compound <= -0.05
> - **Neutral**: -0.05 < compound < 0.05
> 
> Example: "Good" (0.35) = Positive, "GOOD!!!" (0.68) = Positive (emphasis recognized), "Not good" (-0.43) = Negative
> </details>

---

### Card 9: Docker Compose Services
**Question**: List the three main services defined in docker-compose.yml and their purposes.

> <details>
> <summary>Answer</summary>
> 1. **Zookeeper** (port 2181): Coordinates Kafka brokers, maintains cluster metadata
> 2. **Kafka** (port 9092): Message broker for tweet streaming, topic: `tweets_stream`
> 3. **MongoDB** (port 27017): NoSQL database stores enriched tweets, database: `twitter_analysis`
> </details>

---

### Card 10: Entity Extraction
**Question**: What are the two main types of entities extracted from tweets and how?

> <details>
> <summary>Answer</summary>
> 1. **Hashtags**: Extracted using regex pattern `r'#(\w+)'`
>    - Example: "Love this #coffee" → hashtags: ["coffee"]
> 
> 2. **Mentions**: Extracted using regex pattern `r'@(\w+)'`
>    - Example: "Thanks @twitter for the great service" → mentions: ["twitter"]
> 
> These entities enable topical analysis and trend identification
> </details>

---

## Intermediate Cards

### Card 11: Kafka-Spark Integration
**Question**: Explain how Spark Streaming reads data from Kafka. What format does the data arrive in and how is it processed?

> <details>
> <summary>Answer</summary>
> Spark connects to Kafka broker (localhost:9092) and subscribes to topic `tweets_stream`. 
> 
> Data flow:
> - Kafka stores messages as JSON strings
> - Spark reads in micro-batches (default 5-second windows)
> - Each batch is parsed: `df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").load()`
> - Messages are deserialized from JSON
> - Each tweet becomes a row in a Spark DataFrame
> - Transformations (sentiment analysis) applied to distributed computation
> </details>

---

### Card 12: Spark DataFrame Transformations
**Question**: What transformations does Spark apply to each tweet after consuming from Kafka?

> <details>
> <summary>Answer</summary>
> 1. **Parse JSON**: Extract original tweet object from Kafka message
> 2. **Sentiment analysis**: Apply VADER to text field → returns sentiment (positive/negative/neutral) + compound score
> 3. **Hashtag extraction**: Regex pattern matching on text → list of hashtags
> 4. **Mention extraction**: Regex pattern matching on text → list of mentions
> 5. **Timestamp addition**: Add `processing_timestamp` when tweet was processed
> 6. **Data enrichment**: Create new columns with extracted features
> 7. **Batch write**: Write enriched DataFrame to MongoDB collection
> </details>

---

### Card 13: MongoDB Indexing Strategy
**Question**: Why should the MongoDB collection be indexed? What fields should have indexes?

> <details>
> <summary>Answer</summary>
> **Index necessity**: Dashboard queries run repeatedly on full collection; indexes prevent full table scans
> 
> **Recommended indexes**:
> - `sentiment`: Frequently filtered by sentiment type in dashboard queries
> - `processing_timestamp`: Used for time-range queries and sorting
> - `hashtags`: Array field for filtering tweets by specific hashtags
> - `created_at`: Historical queries by tweet creation time
> 
> **Command**: 
> ```
> db.tweets.createIndex({ "sentiment": 1 })
> db.tweets.createIndex({ "processing_timestamp": -1 })
> db.tweets.createIndex({ "hashtags": 1 })
> ```
> </details>

---

### Card 14: Streaming Micro-Batches
**Question**: What is a micro-batch in Spark Streaming? Why is 5-second window chosen?

> <details>
> <summary>Answer</summary>
> **Micro-batch**: A collection of incoming messages processed together within a time window (5 seconds default)
> 
> **Why 5 seconds?**
> - **Latency balance**: 5s window = ~5s delay from tweet to dashboard (acceptable for Twitter trends)
> - **Processing efficiency**: Groups 50 tweets/sec × 5 sec = 250 tweets/batch (good batch size)
> - **MongoDB throughput**: 50+ inserts/second is manageable for network
> - **Resource usage**: Larger batches = more efficient Spark job execution
> - **Dashboard refresh**: Streamlit typically refreshes every 5-10 seconds anyway
> 
> Trade-off: Smaller windows = lower delay but less efficient; larger windows = higher throughput but more delay
> </details>

---

### Card 15: VADER Linguistic Features
**Question**: Give examples of how VADER handles linguistic nuance in social media text that simple sentiment approaches miss.

> <details>
> <summary>Answer</summary>
> 1. **Capitalization** ("good" vs "GOOD"): Recognizes emphasis, scores GOOD higher
> 2. **Punctuation** ("good!" vs "good"): Exclamation marks boost positive sentiment
> 3. **Emojis** ("love this 😍" vs "love this"): Emoji adds positive weight
> 4. **Negation** ("good" vs "not good"): Flips sentiment direction
> 5. **Intensifiers** ("very good" vs "good"): Boosts magnitude
> 6. **Sarcasm handling** (limited): "Oh great, another bug" scores as positive (known limitation)
> 7. **Multiple modifiers** ("LOVE THIS!!!! 😍" vs "love this"): Compounds positivity
> 
> Example scores:
> - "good" → 0.35
> - "GOOD!" → 0.64
> - "Not good" → -0.43
> - "I love this so much!!! 😍" → 0.84
> </details>

---

### Card 16: Data Flow Enrichment Pipeline
**Question**: Trace a single tweet through the entire pipeline from JSON file to MongoDB, listing all transformations.

> <details>
> <summary>Answer</summary>
> 1. **JSON file**: `{"id": 123, "text": "Love this #coffee!", "user": "@john"}`
> 2. **Stream Simulator**: Reads file, publishes to Kafka topic `tweets_stream`
> 3. **Kafka**: Stores message as serialized JSON, ready for consumption
> 4. **Spark Consumer**: 
>    - Reads micro-batch from Kafka
>    - Parses JSON: extracts fields
>    - **VADER Sentiment**: "Love this #coffee!" → sentiment="Positive", score=0.76
>    - **Extract Hashtags**: `#coffee` → hashtags=["coffee"]
>    - **Extract Mentions**: No mentions → mentions=[]
>    - **Add Timestamp**: processing_timestamp="2026-02-15T10:30:45Z"
> 5. **Enriched Tweet** (in DataFrame):
>    ```json
>    {
>      "id": 123,
>      "text": "Love this #coffee!",
>      "sentiment": "Positive",
>      "sentiment_score": 0.76,
>      "hashtags": ["coffee"],
>      "mentions": [],
>      "processing_timestamp": "2026-02-15T10:30:45Z"
>    }
>    ```
> 6. **MongoDB**: Batch write to `twitter_analysis.tweets` collection
> 7. **Dashboard**: Streamlit queries MongoDB, displays in real-time visualization
> </details>

---

### Card 17: Fault Tolerance Mechanisms
**Question**: How does the pipeline handle failures? What happens if Kafka goes down or Spark crashes?

> <details>
> <summary>Answer</summary>
> **Kafka failure handling**:
> - **Replication**: Kafka broker (in this setup) stores all messages
> - **Consumer offset**: Spark tracks which messages were processed
> - **Recovery**: When Spark reconnects, it resumes from last processed offset
> - **Data not lost**: If Spark crashes mid-processing, tweets remain in Kafka queue
> 
> **Spark failure handling**:
> - **Checkpoint directory**: Spark writes metadata about processed batches
> - **Automatic recovery**: Spark can restart and resume processing
> - **Exactly-once semantics**: With proper configuration, each tweet processed exactly once
> 
> **MongoDB failure handling**:
> - **Connection retry**: Spark can retry failed writes
> - **In-memory buffering**: Processed tweets held temporarily if MongoDB unavailable
> 
> **Limitations**:
> - Producer (stream simulator) failure → no new tweets entering pipeline
> - Kafka deletion: If messages deleted from Kafka topic, permanently lost
> - No persistent queue between producers and Kafka
> </details>

---

### Card 18: Streamlit Dashboard Architecture
**Question**: How does the Streamlit dashboard fetch and display real-time data from MongoDB?

> <details>
> <summary>Answer</summary>
> **Architecture**:
> 1. **MongoDB Connection**: Dashboard establishes connection to MongoDB at startup
> 2. **Aggregation Queries**: Uses MongoDB aggregation pipeline for analytics:
>    - `db.tweets.aggregate([{$group: {_id: "$sentiment", count: {$sum: 1}}}])`
>    - Counts by sentiment, extracts hashtags, calculates statistics
> 3. **Auto-refresh**: Streamlit re-runs entire script every 5-10 seconds (configurable)
> 4. **Query execution**: Each refresh runs fresh MongoDB queries on latest data
> 5. **Data plotting**: Results plotted with Plotly for interactive charts
> 6. **Responsive design**: Charts adapt to screen size (desktop vs mobile)
> 
> **Performance considerations**:
> - Indexes prevent full collection scans
> - Aggregation pipeline computed on MongoDB server, not fetched to Python
> - Limiting result sets: "Max tweets to load" parameter controls document count
> - Caching with `@st.cache_data` for expensive computations
> </details>

---

### Card 19: Mobile Responsiveness Design
**Question**: Explain the dual-view system (desktop vs mobile) in the dashboard. What are the key differences?

> <details>
> <summary>Answer</summary>
> **Desktop View**:
> - Multi-column layouts with side-by-side metrics
> - 5-column metric row showing all KPIs simultaneously
> - Tabbed interface (Overview, Temporal, Hashtags, Details)
> - Large data table, word clouds, advanced statistics
> 
> **Mobile View**:
> - Single-column vertical layout for scrolling
> - Card-based metrics in responsive grids
> - 44x44px touch targets (WCAG compliant)
> - Stacked charts for small screens
> - Pagination with Previous/Next buttons
> - Collapsible sections to reduce scrolling
> 
> **Key mobile optimizations**:
> - **Zero horizontal scrolling**: All content fits viewport
> - **Touch-friendly controls**: No hover interactions
> - **Performance tuning**: Fewer data points, lazy rendering
> - **Viewport responsive**: Adapts to iPhone (375px), iPad (768px), desktop (1920px+)
> 
> **User selects view**: "📊 Dashboard View" selector at top, preference persists during session
> </details>

---

### Card 20: VADER Accuracy Limitations
**Question**: What are the known limitations of VADER sentiment analysis? When would you need to upgrade to more sophisticated models?

> <details>
> <summary>Answer</summary>
> **Known Limitations**:
> 1. **Sarcasm/Irony**: ❌ Scored literally
>    - "Oh great, another bug" → Positive (should be negative)
>    - Too context-dependent for lexicon approach
> 
> 2. **Context Dependency**: Limited multi-sentence understanding
>    - Can't track topic shifts within a tweet
> 
> 3. **Slang Evolution**: Trained on 2014 data
>    - Modern slang (2025+) may not be recognized
>    - New emojis/abbreviations missed
> 
> 4. **Domain Specificity**: General-purpose tool
>    - Not tuned for financial tweets, tech industry, medical topics
> 
> **When to upgrade**:
> - **High accuracy needed**: Sarcasm detection → BERT/FastText models
> - **Domain-specific**: FinBERT for finance, BioBERT for biotech
> - **Latency acceptable**: GPU inference (50-100ms) → allows training-based models
> - **Complex reasoning**: Context-aware → Transformer models (BERT, RoBERTa)
> 
> **Current accuracy**: 78.4% agreement with original Sentiment140 labels (acceptable for trend analysis)
> </details>

---

## Advanced Cards

### Card 21: Distributed Computing Concepts
**Question**: Explain how Spark Streaming achieves parallelism in processing tweets. What role do partitions play?

> <details>
> <summary>Answer</summary>
> **Parallelism mechanisms**:
> 1. **Kafka topic partitions**: Tweet stream divided across 3 partitions (configurable)
>    - Each partition can be processed independently
>    - Multiple Spark executor tasks process different partitions simultaneously
> 
> 2. **Spark DataFrame partitions**: Micro-batch data split into partitions
>    - Default: one task per partition
>    - Example: 250 tweets in batch × 3 partitions = 3 tasks (each processes ~84 tweets)
> 
> 3. **Executor parallelism**: Each Spark executor runs multiple tasks concurrently
>    - Default in local mode: 4 parallel tasks
>    - Cluster mode: scales across multiple machines
> 
> **Performance impact**:
> - More partitions → better parallelism (up to number of cores)
> - Too many partitions → overhead, task scheduling bottleneck
> - Ideal partition count: number of CPU cores
> 
> **Sentiment analysis parallelization**:
> ```python
> # Each partition processed in parallel
> df.withColumn("sentiment", udf_vader_sentiment(col("text")))
> # 3 tasks run simultaneously on 3 partitions
> ```
> </details>

---

### Card 22: Spark UDFs and Performance
**Question**: What is a Spark UDF (User Defined Function) and what performance implications does it have for sentiment analysis?

> <details>
> <summary>Answer</summary>
> **UDF definition**: Custom function applied to each row in a DataFrame
> 
> **VADER sentiment as UDF**:
> ```python
> from pyspark.sql.functions import col, udf
> from pyspark.sql.types import StringType, DoubleType
> 
> def vader_sentiment(text):
>     analyzer = SentimentIntensityAnalyzer()
>     scores = analyzer.polarity_scores(text)
>     return "Positive" if scores['compound'] >= 0.05 else "Negative"
> 
> sentiment_udf = udf(vader_sentiment, StringType())
> df = df.withColumn("sentiment", sentiment_udf(col("text")))
> ```
> 
> **Performance implications**:
> - **Row-at-a-time processing**: UDFs can't leverage Catalyst optimizer
> - **JVM overhead**: Python UDFs require Java-Python serialization (expensive)
> - **Slow**: 250 tweets × 1ms VADER = 250ms per batch in single executor
> - **Mitigation**: Use Pandas UDF (vectorized) for batch processing:
>   ```python
>   @pandas_udf(StringType())  # Processes multiple rows at once
>   def vader_sentiment_pandas(texts):
>       # Process entire batch, not one at a time
>   ```
> - **Result**: 10-100x faster than row-at-a-time approach
> </details>

---

### Card 23: State Management in Streaming
**Question**: Explain stateful operations in Spark Streaming. How would you track running sentiment statistics?

> <details>
> <summary>Answer</summary>
> **Stateful operations**: Operations that maintain state across micro-batches
> 
> **Example - Running sentiment statistics**:
> ```python
> # Group by sentiment, count running totals
> from pyspark.sql.functions import count, window
> 
> streaming_agg = df \
>     .withWatermark("processing_timestamp", "10 minutes") \
>     .groupBy("sentiment") \
>     .agg(count("*").alias("count"))
> 
> # State maintained across batches:
> # Batch 1: Positive=100, Negative=50
> # Batch 2: Positive=250 (previously 100 + new 150), Negative=120
> ```
> 
> **State management challenges**:
> - **Memory consumption**: State grows unbounded unless cleaned
> - **Watermarking**: Drops old states beyond watermark (e.g., >10 min old)
> - **Fault tolerance**: State must be checkpointed to recover after failures
> 
> **Current pipeline limitation**: 
> - Spark consumer doesn't use stateful operations, just batch writes
> - Could enhance with running statistics for trend detection
> </details>

---

### Card 24: MongoDB Aggregation Pipeline
**Question**: Write a MongoDB aggregation query to find the top 5 hashtags by frequency and their average sentiment score.

> <details>
> <summary>Answer</summary>
> ```javascript
> db.tweets.aggregate([
>   // Stage 1: Unwind hashtags array (one document per hashtag)
>   { $unwind: "$hashtags" },
>   
>   // Stage 2: Group by hashtag, calculate stats
>   { 
>     $group: {
>       _id: "$hashtags",
>       count: { $sum: 1 },
>       avg_sentiment: { 
>         $avg: { 
>           $cond: [
>             { $eq: ["$sentiment", "Positive"] }, 
>             1, 
>             { $cond: [{ $eq: ["$sentiment", "Negative"] }, -1, 0] }
>           ] 
>         } 
>       }
>     }
>   },
>   
>   // Stage 3: Sort by count descending
>   { $sort: { count: -1 } },
>   
>   // Stage 4: Limit to top 5
>   { $limit: 5 },
>   
>   // Stage 5: Rename fields for clarity
>   { 
>     $project: { 
>       hashtag: "$_id",
>       frequency: "$count",
>       avg_sentiment_score: "$avg_sentiment",
>       _id: 0
>     } 
>   }
> ])
> ```
> 
> **Result example**:
> ```
> { hashtag: "love", frequency: 1850, avg_sentiment_score: 0.82 }
> { hashtag: "coffee", frequency: 1240, avg_sentiment_score: 0.71 }
> ```
> </details>

---

### Card 25: Handling Late/Out-of-Order Data
**Question**: In a real streaming system, tweets may arrive out of order. How should the pipeline handle them?

> <details>
> <summary>Answer</summary>
> **Challenge**: Tweet created at 10:00 AM but arrives at 10:05 AM (5 min delay)
> 
> **Current approach**: Process in order received (ignores creation time)
> - Simple but incorrect for time-series analysis
> - Dashboard shows processing order, not tweet creation order
> 
> **Better approach - Event Time Processing**:
> ```python
> # Use tweet creation time, not processing time
> df = df.withWatermark("created_at", "10 minutes")  # Allow 10 min late arrivals
> 
> df.groupBy(
>   window("created_at", "5 minutes")  # Group by creation time, not processing time
> ).agg(count("*").alias("tweets_per_5min"))
> ```
> 
> **Watermark strategy**:
> - **Watermark = 10 minutes**: Accept tweets up to 10 min late
> - **Too low (1 min)**: Miss legitimate delayed tweets
> - **Too high (1 hour)**: Hold state in memory too long
> - **Trade-off**: Accuracy vs memory/latency
> 
> **Current limitation**: Pipeline uses `processing_timestamp`, not `created_at`
> - Could enhance for more accurate temporal analysis
> </details>

---

### Card 26: Backpressure and Rate Limiting
**Question**: What is backpressure in streaming systems? How does the producer rate limit prevent overwhelming the system?

> <details>
> <summary>Answer</summary>
> **Backpressure**: Situation where downstream system can't keep up with upstream producer
> 
> **Example scenario**:
> - Producer: 100 tweets/sec
> - Processing: 30 tweets/sec (sentiment analysis is slow)
> - Result: Queue grows unbounded → eventual system crash
> 
> **Solution - Rate limiting**.
> Stream simulator uses configurable rate:
> ```python
> TWEETS_PER_SECOND = 50  # Limit to 50 tweets/second
> time.sleep(1.0 / TWEETS_PER_SECOND)  # 20ms delay between tweets
> ```
> 
> **Why 50 tweets/sec?**
> - 50 tweets × 1ms sentiment analysis = 50ms processing
> - 5-second micro-batch = 250 tweets, easily processed
> - Allows headroom for temporary slowdowns
> 
> **Monitoring backpressure**:
> - Check Kafka topic lag: `kafka-consumer-groups --describe --group spark-consumer`
> - If lag growing: Downstream is slower than upstream
> - If lag stable/shrinking: System is balanced
> 
> **Advanced mitigation**:
> - Adaptive batching: Larger batches when lag high
> - Scaling: Add more Spark executors
> - Caching: Store intermediate results to avoid recomputation
> </details>

---

### Card 27: Schema Evolution and Data Versioning
**Question**: How should the pipeline handle schema changes? Example: What if we want to add a "language" field to sentiment analysis?

> <details>
> <summary>Answer</summary>
> **Challenge**: Existing tweets in MongoDB don't have `language` field
> 
> **Handling strategy**:
> 1. **Backward compatibility**: New tweets have language, old tweets don't
> 
> 2. **MongoDB approach** (schema-flexible):
>    ```python
>    # New tweets always include language
>    enriched_tweet = {
>      "id": 123,
>      "text": "...",
>      "sentiment": "Positive",
>      "language": "en",  # New field
>      "language_detected": True
>    }
>    
>    # Dashboards handle null gracefully
>    db.tweets.find({"language": {$exists: true}}).count()
>    ```
> 
> 3. **Data migration options**:
>    - **Option A (immediate)**: Backfill old tweets
>      ```javascript
>      db.tweets.updateMany(
>        {language: {$exists: false}},
>        [{$set: {language: "en", language_detected: false}}]
>      )
>      ```
>    - **Option B (lazy)**: Handle nulls in queries
>      ```javascript
>      db.tweets.aggregate([
>        {$addFields: {lang: {$ifNull: ["$language", "unknown"]}}}
>      ])
>      ```
> 
> 4. **Version management**:
>    - Add metadata: `schema_version: 2`
>    - Track which version created the document
>    - Enables A/B testing different schemas
> </details>

---

### Card 28: Cost Optimization for Big Data
**Question**: If this pipeline scaled to 1 billion tweets/day, what would be the bottlenecks and how would you optimize for cost?

> <details>
> <summary>Answer</summary>
> **Scaling scenario**: 1B tweets/day = ~11,600 tweets/second (vs current 50 tweets/sec)
> 
> **Bottlenecks**:
> 1. **Sentiment analysis**: 11,600 tweets/sec × 1ms = 11.6 seconds of CPU per second (need 12 parallel cores minimum)
> 2. **MongoDB writes**: 11,600 writes/sec exceeds single server capacity
> 3. **Network I/O**: Kafka broker, Spark, MongoDB all competing for network
> 4. **Storage**: 1B tweets × 500 bytes = 500 GB disk required
> 
> **Cost optimization strategies**:
> 1. **Batching**: Increase micro-batch window from 5s to 30s
>    - 11,600 × 30 = 348,000 tweets per batch
>    - Fewer, larger Spark jobs = more efficient
>    - Trade-off: 30s delay vs 5s (acceptable for trend analysis)
> 
> 2. **Sampling**: Process 1-in-10 tweets for real-time dashboard
>    - 1,160 tweets/sec = manageable on cheap hardware
>    - Store full data stream for batch analysis later
> 
> 3. **Tiering**: Hot/cold storage
>    - **Hot tier**: Recent tweets (last 24h) in MongoDB
>    - **Cold tier**: Historical tweets (>24h) in S3 (cheaper)
>    - Dashboard queries hot tier only
> 
> 4. **Aggregation at source**: Pre-aggregate before MongoDB
>    - Don't store individual tweets, only 5-min summaries
>    - "5 tweets from 10:00-10:05, 3 positive, 2 negative"
>    - Reduces storage 300x, improves query speed
> 
> 5. **Cloud infrastructure**:
>    - AWS Kinesis instead of self-managed Kafka
>    - DynamoDB autoscaling instead of MongoDB
>    - S3 for long-term storage
> </details>

---

### Card 29: Testing and Validation in Production
**Question**: How would you validate that the sentiment analysis is working correctly in a production environment with millions of tweets?

> <details>
> <summary>Answer</summary>
> **Validation approaches**:
> 
> 1. **Sampling and manual review**:
>    ```python
>    # Daily: Random sample 100 tweets, manual check
>    manual_labels = ["positive", "negative", "neutral"]
>    predicted_sentiments = get_predictions(sample_tweets)
>    accuracy = (manual_labels == predicted_sentiments).mean()
>    # Alert if accuracy < 75%
>    ```
> 
> 2. **Sanity checks**:
>    - Count tweets by sentiment → Should be roughly balanced
>    - Check emotional words → "love/great/amazing" should be mostly positive
>    - Check negative words → "hate/bad/worst" should be mostly negative
> 
>    ```sql
>    -- Monitor accuracy by word
>    SELECT word, 
>           COUNT(*) as count,
>           SUM(CASE WHEN sentiment="Positive" THEN 1 ELSE 0 END) 
>             / COUNT(*) as positive_rate
>    FROM tweets_with_words
>    WHERE word IN ('love', 'great', 'hate', 'bad')
>    GROUP BY word
>    ```
> 
> 3. **Temporal monitoring**:
>    - Plot sentiment distribution over time
>    - Sudden shifts suggest processing bug or data quality issue
>    - Baseline: Previous 30 days' distributions should be similar
> 
> 4. **Comparative validation**:
>    - A/B test: Run VADER + alternative model on same sample
>    - Use human ratings as ground truth
>    - Track metrics over time: `accuracy_30day_trend`
> 
> 5. **Automated alerts**:
>    ```python
>    accuracy_current = calculate_accuracy()
>    accuracy_baseline = get_baseline_accuracy()  # Previous 7 days average
>    
>    if accuracy_current < accuracy_baseline * 0.95:  # >5% drop
>        send_alert("Sentiment analysis accuracy dropped!")
>    ```
> </details>

---

### Card 30: Real-Time Anomaly Detection
**Question**: How could you detect anomalies in the sentiment stream? Example: Unusual sentiment spike during normal hours.

> <details>
> <summary>Answer</summary>
> **Anomaly scenarios**:
> - 95% positive tweets (vs normal 40-50%)
> - Sudden topic shift (new hashtags appear)
> - Hashtag goes viral (frequency spikes 10x)
> - Spam detection (many bot accounts)
> 
> **Detection approach - Statistical baseline**:
> ```python
> from pyspark.sql.window import Window
> 
> # Calculate 1-hour rolling average
> window_spec = Window.partitionBy().orderBy("processing_timestamp") \
>     .rangeBetween(-3600, 0)  # 1-hour window
> 
> df.withColumn(
>     "positive_rate_rolling", 
>     avg(col("is_positive")).over(window_spec)
> ).withColumn(
>     "is_anomaly",
>     col("positive_rate_rolling") > 0.65  # Normal: 40-50%
> )
> ```
> 
> **Detection approach - Hashtag frequency**:
> ```python
> # Track hashtag counts over time
> top_hashtags = df.groupBy("hashtags", window("processing_timestamp", "1 minute")) \
>     .agg(count("*").alias("count"))
> 
> # Detect if count > 2σ (2 standard deviations) from mean
> # Normal behavior: steady frequency
> # Anomaly: sudden spike
> ```
> 
> **Response actions**:
> - Flag anomalous tweets in MongoDB
> - Alert dashboard (visual indicator)
> - Manual review for spam/bot activity
> - Automatic filtering if confidence high
> 
> **Machine learning approach**:
> - Isolation Forest: Unsupervised anomaly detection
> - One-class SVM: Learn "normal" distribution
> - LSTM: Detect sequence anomalies over time
> </details>

---

### Card 31: Security Considerations
**Question**: What security vulnerabilities exist in this pipeline and how would you address them?

> <details>
> <summary>Answer</summary>
> **Vulnerabilities**:
> 
> 1. **MongoDB authentication**:
>    - ❌ Current: Hardcoded credentials in config.py
>    - ✅ Fix: Environment variables, Docker secrets
>    ```python
>    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
>    ```
> 
> 2. **Kafka security**:
>    - ❌ Current: No authentication, plain TCP
>    - ✅ Fix: Enable SASL/SCRAM authentication, TLS encryption
> 
> 3. **Data privacy**:
>    - ❌ Current: Full tweets stored, including user mentions
>    - ✅ Fix: Anonymize personally identifiable information
>    ```python
>    tweet_text = re.sub(r'@\w+', '@user', tweet_text)  # Remove handles
>    ```
> 
> 4. **Spark job injection**:
>    - ❌ Current: User input in SQL queries not validated
>    - ✅ Fix: Use parameterized queries, input validation
> 
> 5. **Network exposure**:
>    - ❌ Current: Services exposed to public
>    - ✅ Fix: Use VPC, firewall rules, network segmentation
>    ```yaml
>    # docker-compose.yml
>    services:
>      kafka:
>        ports: []  # Don't expose to host
>        networks:
>          - internal  # Private network only
>    ```
> 
> 6. **Audit logging**:
>    - ❌ Current: Limited logging
>    - ✅ Fix: Log all data access, API calls, modifications
> 
> **Compliance**:
> - GDPR: Right to be forgotten (Spark can't delete processed data)
> - Data retention: Delete old tweets after 90 days
> </details>

---

### Card 32: Docker Network Communication
**Question**: Explain how the services communicate inside the Docker Compose network. Why not expose Kafka/MongoDB to the host?

> <details>
> <summary>Answer</summary>
> **Docker Compose networking**:
> - Automatic network created: `tweet-analysis_default`
> - Each service gets internal DNS name: `kafka`, `mongodb`, `zookeeper`
> 
> **Internal communication** (inside containers):
> ```python
> # Spark consumer running in Docker
> spark.readStream \
>     .format("kafka") \
>     .option("kafka.bootstrap.servers", "kafka:9092") \  # Internal DNS
>     .load()
> 
> # MongoDB connection from Spark
> mongoClient = MongoClient("mongodb://admin:password@mongodb:27017")
> ```
> 
> **Port mapping**:
> - `ports: ["9092:9092"]`: 
>   - Host can connect: `localhost:9092`
>   - Container can connect: `kafka:9092` (internal)
> 
> **Don't expose Kafka/MongoDB**:
> 1. **Security**: Prevents external connections, reduces attack surface
> 2. **Isolation**: Containers isolated from host and external networks
> 3. **Flexibility**: Change internal ports without affecting host
> 4. **Cleanliness**: Only expose what's needed (in this case: strictly for development)
> 
> **Production approach** (different):
> ```yaml
> services:
>   kafka:
>     ports: []  # Don't publish ports
>     networks:
>       - internal  # Private network only
>   
>   mongodb:
>     ports: []
>     networks:
>       - internal
>   
>   spark:  # Runs outside Docker, in cluster
>     networks:
>       - internal  # Can still reach Kafka/MongoDB
> ```
> </details>

---

### Card 33: Schema Registry Pattern
**Question**: In a production system with multiple data sources, how would you manage schema evolution across teams?

> <details>
> <summary>Answer</summary>
> **Challenge**: 
> - Team A produces tweets with `{sentiment, hashtags}`
> - Team B wants to add `language` field
> - Team C consumes data expecting original schema → breaks
> 
> **Solution - Schema Registry**:
> 
> 1. **Central schema repository** (e.g., Confluent Schema Registry):
>    ```json
>    // Version 1 of tweet schema
>    {
>      "type": "record",
>      "name": "Tweet",
>      "fields": [
>        {"name": "id", "type": "long"},
>        {"name": "text", "type": "string"},
>        {"name": "sentiment", "type": "string"},
>        {"name": "hashtags", "type": {"type": "array", "items": "string"}}
>      ]
>    }
>    
>    // Version 2 - Added language field
>    {
>      ...
>      {"name": "language", "type": ["null", "string"], "default": null}
>    }
>    ```
> 
> 2. **Backward compatibility**:
>    - New field has `default` value
>    - Old consumers can ignore new fields
>    - Old producers using v1 still work
> 
> 3. **Version enforcement**:
>    - Producer serializes with v2
>    - Old consumers reading v2 get sensible defaults
>    - Breaking changes (removing fields) rejected by registry
> 
> 4. **Kafka integration**:
>    ```python
>    # Producer automatically validates against registry
>    producer = KafkaProducer(
>        value_serializer=AvroSerializer(schema_registry_client)
>    )
>    producer.send("tweets", value=enriched_tweet)  # Validates schema v2
>    
>    # Consumer automatically deserializes
>    consumer = KafkaConsumer(
>        value_deserializer=AvroDeserializer(schema_registry_client)
>    )
>    ```
> </details>

---

### Card 34: Exactly-Once Semantics
**Question**: What does "exactly-once" processing mean? How do you ensure tweets aren't processed twice or missed?

> <details>
> <summary>Answer</summary>
> **Delivery semantics**:
> 1. **At-most-once**: May be skipped (if Spark crashes after processing but before confirmation)
> 2. **At-least-once**: May be duplicated (if Spark crashes before writing confirmation to Kafka)
> 3. **Exactly-once**: ✅ Processed exactly once, even after failures
> 
> **Exactly-once implementation**:
> 
> 1. **Kafka offset management**:
>    ```python
>    # Spark tracks offset position
>    df.select("*") \
>        .writeStream \
>        .option("checkpointLocation", "/path/to/checkpoint") \
>        .option("kafka.bootstrap.servers", "kafka:9092") \
>        .start()
>    
>    # Checkpoint directory stores: 
>    # - Last processed offset from Kafka
>    # - Processing metadata
>    ```
> 
> 2. **Atomic writes to sink**:
>    - Spark processes a batch
>    - Writes results to MongoDB atomically
>    - Updates Kafka offset atomically (or not at all on failure)
> 
> 3. **Idempotent MongoDB writes**:
>    ```python
>    # Use tweet ID as unique key
>    db.tweets.updateOne(
>        {"_id": tweet_id},  # Unique identifier
>        {"$set": enriched_tweet},
>        upsert=True  # Insert if not exists, update if does
>    )
>    
>    # If duplicate arrives: idempotent operation (no duplicate side effects)
>    ```
> 
> 4. **Recovery**:
>    - Spark crashes after processing batch 5
>    - On restart, checkpoint shows last completed: batch 4
>    - Reprocesses batch 5 (idempotent due to upsert)
>    - No data loss, no duplicates
> 
> **Tradeoff**: 
> - Exactly-once guarantees slightly slower (atomic writes)
> - At-least-once is faster but requires deduplication logic
> </details>

---

### Card 35: Time Zone Handling
**Question**: The pipeline processes tweets from global sources but stores timestamps. How should time zones be handled?

> <details>
> <summary>Answer</summary>
> **Challenge**: 
> - Tweet created at "2am London time" = "9pm New York time"
> - Dashboard shows "2am", user in NY confused
> 
> **Solution - Store as UTC**:
> 
> 1. **During ingestion**:
>    ```python
>    from datetime import datetime, timezone
>    
>    # Always convert to UTC for storage
>    utc_timestamp = datetime.now(timezone.utc)
>    enriched_tweet["processing_timestamp"] = utc_timestamp.isoformat()
>    # Result: "2026-02-15T10:30:45Z"  (Z = UTC)
>    ```
> 
> 2. **In MongoDB**:
>    ```json
>    {
>      "processing_timestamp": ISODate("2026-02-15T10:30:45Z"),
>      "created_at": ISODate("2009-04-06T22:19:45Z")
>    }
>    ```
> 
> 3. **Dashboard display** (convert back to user's timezone):
>    ```python
>    import pytz
>    
>    # Server timezone: UTC
>    utc_time = tweet["processing_timestamp"]
>    
>    # Convert to user's timezone for display
>    user_tz = pytz.timezone("America/New_York")
>    user_time = utc_time.astimezone(user_tz)
>    # Result: "2:30 PM EST"
>    ```
> 
> 4. **MongoDB queries**:
>    ```javascript
>    // Query by UTC time, not local time
>    db.tweets.find({
>      processing_timestamp: {
>        $gte: ISODate("2026-02-15T00:00:00Z"),
>        $lt: ISODate("2026-02-16T00:00:00Z")
>      }
>    })
>    ```
> 
> **Best practice**: Store all timestamps UTC, convert to user timezone only for display
> </details>

---

---

# 📝 Quiz Questions

## Multiple Choice Questions

### MC 1 (Beginner):
**Question**: What is the primary role of Apache Kafka in this Twitter sentiment analysis pipeline?
- a) Performs sentiment analysis on tweets
- b) Stores processed tweets in a database
- c) Acts as a distributed message broker between producer and consumer
- d) Visualizes real-time sentiment data

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) Acts as a distributed message broker between producer and consumer**
> 
> **Explanation**: Kafka decouples the producer (stream simulator) from the consumer (Spark), ensuring fault tolerance and reliable message delivery. Options a, b, and d are handled by VADER, MongoDB, and Streamlit respectively.
> </details>

---

### MC 2 (Beginner):
**Question**: Which of the following is NOT a benefit of using VADER for sentiment analysis?
- a) Works well with social media text (emojis, slang, abbreviations)
- b) Requires no training data (lexicon-based approach)
- c) Handles sarcasm and irony perfectly
- d) Processes tweets faster than 1ms per tweet

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) Handles sarcasm and irony perfectly**
> 
> **Explanation**: Sarcasm and irony detection is a known limitation of VADER. The phrase "Oh great, another bug" would be scored as positive (literally), but should be negative (sarcasm). This is due to the lexicon-based approach's inability to understand context deeply. Understanding this limitation is crucial for real-world implementation.
> </details>

---

### MC 3 (Beginner):
**Question**: What does the Sentiment140 dataset contain?
- a) 1.6 million tweets from 2009 with binary sentiment labels (positive/negative)
- b) 1.6 million tweets from 2020 with three sentiment classes
- c) 800,000 tweets with neutral sentiment pre-labeled
- d) Real-time tweet stream directly from Twitter API

> <details>
> <summary>Answer</summary>
> **Correct Answer: a) 1.6 million tweets from 2009 with binary sentiment labels (positive/negative)**
> 
> **Explanation**: The README specifies 1.6M tweets from April-June 2009, with 50% negative (target=0) and 50% positive (target=4). There was no neutral class in the original dataset (VADER detected neutral sentiment in ~12.9% during analysis). The dataset is historical, not a real-time stream.
> </details>

---

### MC 4 (Beginner):
**Question**: What are the three main services orchestrated by docker-compose.yml?
- a) Producer, Consumer, Dashboard
- b) Zookeeper, Kafka, MongoDB
- c) Python, Java, Node.js
- d) Spark, Hadoop, HBase

> <details>
> <summary>Answer</summary>
> **Correct Answer: b) Zookeeper, Kafka, MongoDB**
> 
> **Explanation**: The docker-compose.yml file specifies three services: Zookeeper (Kafka coordination), Kafka (message broker), and MongoDB (data storage). Producer, Consumer, and Dashboard run outside Docker on the host machine.
> </details>

---

### MC 5 (Intermediate):
**Question**: In the spark_consumer.py, the text goes through several transformations. In what order do these occur?
- a) Sentiment analysis → Extract hashtags → Extract mentions → Store in MongoDB
- b) Extract hashtags → Sentiment analysis → Extract mentions → Store in MongoDB
- c) Parse JSON from Kafka → Sentiment analysis → Extract entities → Add timestamp → Store in MongoDB
- d) Store in MongoDB → Sentiment analysis → Extract entities → Parse JSON

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) Parse JSON from Kafka → Sentiment analysis → Extract entities → Add timestamp → Store in MongoDB**
> 
> **Explanation**: The logical order is: 1) Parse the incoming JSON message from Kafka, 2) Apply VADER to the text field, 3) Use regex to extract hashtags and mentions, 4) Add processing timestamp, 5) Write the enriched document to MongoDB. This order ensures the text is available for processing before being stored.
> </details>

---

### MC 6 (Intermediate):
**Question**: The stream simulator publishes 50 tweets per second. How many tweets are in a typical 5-second Spark micro-batch?
- a) 5-10 tweets
- b) 50 tweets
- c) 250 tweets
- d) 1,000 tweets

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) 250 tweets**
> 
> **Explanation**: 50 tweets/second × 5 seconds = 250 tweets per batch. This is a good batch size for processing efficiency. A 5-second micro-batch with 250 tweets provides a balance between latency (not too delayed) and efficiency (batching multiple records together).
> </details>

---

### MC 7 (Intermediate):
**Question**: What happens if a Spark executor crashes while processing a micro-batch?
- a) The tweets are permanently lost
- b) Tweets remain in Kafka; Spark resumes from the last processed offset on recovery
- c) The entire system shuts down
- d) Tweets are sent to a dead-letter queue

> <details>
> <summary>Answer</summary>
> **Correct Answer: b) Tweets remain in Kafka; Spark resumes from the last processed offset on recovery**
> 
> **Explanation**: Kafka maintains a queue of messages, and Spark tracks the offset (position) of processed messages. On failure, Spark checkpoints and can resume from this offset, ensuring no data is lost. This is the fault tolerance mechanism built into Kafka + Spark.
> </details>

---

### MC 8 (Intermediate):
**Question**: The dashboard shows sentiment distribution across thousands of tweets. Which MongoDB operation is most efficient for this query?
- a) Fetching all tweets and calculating in Python
- b) MongoDB aggregation pipeline with `$group` and `$count`
- c) Sequential loop querying one tweet at a time
- d) SQL query through a bridge layer

> <details>
> <summary>Answer</summary>
> **Correct Answer: b) MongoDB aggregation pipeline with `$group` and `$count`**
> 
> **Explanation**: The aggregation pipeline processes data on the MongoDB server side, much faster than fetching all documents to Python for processing. `$group` buckets tweets by sentiment, `$count` tallies them. This is a standard pattern for analytics and avoids transferring millions of documents over the network.
> </details>

---

### MC 9 (Advanced):
**Question**: To improve sentiment analysis accuracy for sarcasm detection (e.g., "Oh great, another bug"), which approach would be most effective?
- a) Increase VADER's detection thresholds
- b) Use a fine-tuned BERT model trained on sarcasm dataset
- c) Add more emoji support to VADER
- d) Increase the micro-batch window to 10 seconds

> <details>
> <summary>Answer</summary>
> **Correct Answer: b) Use a fine-tuned BERT model trained on sarcasm dataset**
> 
> **Explanation**: Sarcasm requires contextual understanding beyond lexicon matching. BERT and similar transformer models can learn these patterns from training examples. However, this trades latency (50-100ms per tweet) for accuracy. Option a (adjusting thresholds) won't help; sarcasm requires context, not just keyword detection. Options c and d are irrelevant to sarcasm detection.
> </details>

---

### MC 10 (Advanced):
**Question**: If the pipeline needs to scale to 1 million tweets per second (currently 50), which bottleneck would be hit first?
- a) Sentiment analysis CPU processing
- b) MongoDB write throughput
- c) Kafka topic partitions
- d) Network bandwidth between services

> <details>
> <summary>Answer</summary>
> **Correct Answer: b) MongoDB write throughput**
> 
> **Explanation**: At 1M tweets/sec, MongoDB single instance cannot sustain 1M writes/second. VADER can be parallelized across Spark executors (CPU, optiona a); Kafka can add partitions (option c); network can be upgraded (option d). But MongoDB requires sharding or a different architecture. Typically, databases are the first bottleneck in streaming systems.
> </details>

---

### MC 11 (Intermediate):
**Question**: The VADER sentiment score (compound) ranges from -1.0 to +1.0. What does a score of 0.00 indicate?
- a) Strongly positive sentiment
- b) Strongly negative sentiment
- c) Neutral sentiment
- d) Invalid tweet

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) Neutral sentiment**
> 
> **Explanation**: Compound score of 0 is in the neutral zone (-0.05 to +0.05). Example: "Going to work today" has compound ≈ 0.0. Scores > 0.05 are positive, scores < -0.05 are negative. The threshold of ±0.05 allows a small buffer around zero to classify mixed sentiment as neutral rather than slightly positive/negative.
> </details>

---

### MC 12 (Beginner):
**Question**: How many rows were removed during data cleaning?
- a) 189 tweets (length filter)
- b) 21,373 tweets (duplicates)
- c) 21,562 tweets (duplicates + length)
- d) 1,578,438 tweets (final dataset)

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) 21,562 tweets (duplicates + length)**
> 
> **Explanation**: 21,373 exact duplicate tweets were removed, and 189 tweets shorter than 10 characters were filtered. Total = 21,562 removed. The final retained dataset is 1,578,438 tweets (98.65% retention).
> </details>

---

### MC 13 (Advanced):
**Question**: A dashboard query shows 500ms response time on first request and 8ms on subsequent requests. What is the most likely explanation?
- a) MongoDB is caching query results
- b) Network is faster on repeat requests
- c) Streamlit is caching data with `@st.cache_data`
- d) Spark completed an additional batch between requests

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) Streamlit is caching data with `@st.cache_data`**
> 
> **Explanation**: The first request runs the MongoDB aggregation pipeline (500ms). Streamlit caches the result with a decorator. Second request retrieves from cache (8ms) without database query. After the cache timeout (60s default), the next request would be slow again. This is a Streamlit performance optimization pattern.
> </details>

---

### MC 14 (Intermediate):
**Question**: A tweet contains both positive and negative words: "Good product but bad customer service". How would VADER likely classify this?
- a) Positive (more positive words)
- b) Negative (more sentiment-bearing words)
- c) Neutral (mixed sentiment, compound close to 0)
- d) Error (conflicting signals)

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) Neutral (mixed sentiment, compound close to 0)**
> 
> **Explanation**: VADER calculates scores for all sentiment words and combines them. Positive ("Good") and negative ("bad") roughly cancel out, producing a compound score near 0 (e.g., 0.02). This falls in the neutral range (-0.05 to +0.05). VADER handles mixed sentiment gracefully rather than erroring.
> </details>

---

### MC 15 (Beginner):
**Question**: Where does the stream simulator read tweets from?
- a) Live Twitter API stream
- b) Kafka topic `tweets_stream`
- c) JSON file at `data/tweets_clean.json`
- d) MongoDB collection `tweets`

> <details>
> <summary>Answer</summary>
> **Correct Answer: c) JSON file at `data/tweets_clean.json`**
> 
> **Explanation**: The stream simulator is in `producer/stream_simulator.py` and reads from the local cleaned JSON dataset. It simulates real-time streaming by publishing tweets to Kafka at a configurable rate. This allows reproducible testing without live API dependency.
> </details>

---

## True/False Questions

### TF 1 (Beginner):
**Statement**: MongoDB is a relational database like PostgreSQL.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: FALSE**
> 
> MongoDB is a **NoSQL document database**, not a relational (SQL) database. It stores documents (JSON-like) rather than tables with rows and columns. For this pipeline, MongoDB's flexible schema is better suited for storing diverse tweet attributes.
> </details>

---

### TF 2 (Beginner):
**Statement**: VADER sentiment analysis requires a pre-trained machine learning model to be trained on the sentiment dataset before it can classify tweets.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: FALSE**
> 
> VADER is a **lexicon-based** approach; it uses a pre-built dictionary of sentiment-bearing words and rules. No training is required. It works immediately out-of-the-box, making it ideal for real-time applications where training latency is unacceptable.
> </details>

---

### TF 3 (Intermediate):
**Statement**: If Kafka crashes and loses all data in its topic, tweets can be recovered from the stream simulator.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: TRUE**
> 
> The stream simulator reads from the persistent JSON file on disk. If Kafka crashes, the data in Kafka's memory is lost, but the simulator can restart and re-read the file. However, the pipeline would need to handle replaying the dataset (may create duplicates in MongoDB if not handled). This highlights the importance of checkpoint management for exactly-once semantics.
> </details>

---

### TF 4 (Intermediate):
**Statement**: Spark Streaming processes tweets one at a time as they arrive from Kafka.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: FALSE**
> 
> Spark Streaming processes tweets in **micro-batches**. In this pipeline, a 5-second window collects ~250 tweets, then processes them together in a single batch. This is more efficient than one-by-one processing.
> </details>

---

### TF 5 (Beginner):
**Statement**: The sentiment score of 0.05 is classified as neutral by VADER.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: FALSE**
> 
> A compound score of 0.05 is exactly at the **positive threshold** and is classified as **positive** (compound >= 0.05). The neutral range is -0.05 < compound < 0.05. A score of 0.04 would be neutral, 0.05 is positive (though barely).
> </details>

---

### TF 6 (Intermediate):
**Statement**: The dashboard must directly query MongoDB for every metric displayed, so performance is bounded by Kafka throughput.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: FALSE**
> 
> Dashboard performance depends on **MongoDB query speed**, not directly on Kafka throughput. Kafka throughput affects how fast new data arrives in MongoDB, but cached or indexed queries respond quickly regardless of Kafka speed. With proper indexes, dashboard queries complete in milliseconds.
> </details>

---

### TF 7 (Advanced):
**Statement**: Exactly-once processing semantics guarantee that each tweet is processed and stored exactly once, even if systems crash.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: TRUE**
> 
> Exactly-once semantics mean: With proper configuration (checkpoint directories, idempotent operations), each tweet is processed and written exactly once. Recovery mechnisms ensure failures don't cause duplicates or losses. This requires atomic writes and offset tracking.
> </details>

---

### TF 8 (Intermediate):
**Statement**: Hashtags and mentions are extracted before sentiment analysis.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: FALSE**
> 
> The order doesn't matter because they operate on the raw text. Sentiment analysis reads the full text; hashtag/mention extraction uses regex on the same text. Both happen in parallel in the Spark transformation. The logical order is flexible; hashtags/mentions can be extracted before, after, or during sentiment analysis.
> </details>

---

### TF 9 (Beginner):
**Statement**: The Sentiment140 dataset contains real-time tweets collected from Twitter's live stream.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: FALSE**
> 
> The Sentiment140 dataset contains historical tweets from April-June 2009, manually labeled for sentiment. It's static, downloadable from Kaggle, and used for consistent testing. It's not a live stream; the stream simulator reproduces streaming behavior by reading the file iteratively.
> </details>

---

### TF 10 (Advanced):
**Statement**: Adding more Kafka topic partitions automatically improves the processing throughput of Spark Streaming.

> <details>
> <summary>Answer & Explanation</summary>
> **Answer: TRUE (with caveats)**
> 
> More partitions enable more parallel tasks in Spark. Each partition can be processed by a different executor, improving throughput. However, adding partitions beyond the number of available cores wastes resources. The ideal partition count equals number of CPU cores. Also, more partitions increase Kafka overhead.
> </details>

---

## Scenario-Based Questions

### Scenario 1 (Intermediate):
**Scenario**: You're monitoring the pipeline. You notice MongoDB has 5 million tweets, but the stream simulator claims to have sent 600 million messages to Kafka over the past 2 weeks. Tweet arrival rate looks normal in Kafka, but MongoDB insert rate is stuck around 100 tweets/sec.

**Question**: What is the likely bottleneck?

> <details>
> <summary>Answer</summary>
> **Root Cause**: MongoDB write throughput is bottlenecked. Kafka backlog is growing because Spark can't write to MongoDB fast enough.
>
> **Investigation steps**:
> 1. Check Kafka consumer lag: `kafka-consumer-groups --describe --group spark-group`
> 2. If lag is high (millions of messages): Spark is falling behind
> 3. Check Spark logs: Are there MongoDB connection timeouts?
> 4. Monitor MongoDB: `db.serverStatus().opcounters.insert` → should be ~250/sec (not 100/sec)
>
> **Solutions**:
> - **Increase Spark executors**: Add more parallel writers to MongoDB
> - **Increase batch interval**: 5 → 10 seconds, write 500 tweets/batch instead of 250
> - **Scout MongoDB**: Single instance can't sustain; shard the collection by tweet ID
> - **Write optimization**: Use bulk writes, disable durability temporarily if acceptable
> - **Connection pooling**: Increase MongoDB connection pool size
> </details>

---

### Scenario 2 (Advanced):
**Scenario**: Dashboard shows sentiment: 99% positive tweets. This is unusual (normally 40-50%). You suspect the sentiment analysis broke. How do you verify?

**Question**: What diagnostic steps would you take?

> <details>
> <summary>Answer</summary>
> **Diagnostic steps**:
>
> 1. **Manual spot check**:
>    ```python
>    # Query 10 random recent tweets from MongoDB
>    tweets = db.tweets.aggregate([{$sample: {size: 10}}])
>    for tweet in tweets:
>        print(f"Text: {tweet['text']}")
>        print(f"Labeled: {tweet['sentiment']}")
>        # Manually read: Does "Love this!!!" = Positive? Yes, correct.
>        # Does "Hate this" = Positive? NO, BUG DETECTED.
>    ```
>
> 2. **Check VADER directly**:
>    ```python
>    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
>    analyzer = SentimentIntensityAnalyzer()
>    
>    # Test known sentiments
>    test_cases = [
>        ("I love this!", "Positive"),
>        ("I hate this!", "Negative"),
>        ("Just going to work", "Neutral")
>    ]
>    
>    for text, expected in test_cases:
>        scores = analyzer.polarity_scores(text)
>        sentiment = "Positive" if scores['compound'] >= 0.05 else ...
>        assert sentiment == expected, f"Failed: {text}"
>    ```
>
> 3. **Check data pipeline**:
>    ```python
>    # Tail Spark logs for errors
>    tail -f logs/spark_consumer.log | grep -i "error\|exception"
>    
>    # Check if sentiment column exists in MongoDB
>    db.tweets.findOne() # View actual document structure
>    
>    # Check if column is being set
>    db.tweets.find({sentiment: {$exists: false}}).count()
>    ```
>
> 4. **Compare with original labels**:
>    ```python
>    # Original dataset has target field (0=negative, 4=positive)
>    # Compare with new analysis
>    df = pd.read_json("tweets_clean.json", lines=True)
>    df['original_sentiment'] = df['target'].map({0: 'Negative', 4: 'Positive'})
>    
>    df['agreement'] = (df['sentiment'] == df['original_sentiment'])
>    accuracy = df['agreement'].mean()  # Should be ~78%
>    ```
>
> 5. **Time-based analysis**:
>    - Did accuracy drop at a specific time?
>    - Check logs at that timestamp
>    - Did Spark restart? Did config change?
>
> **Possible root causes**:
> - Sentiment analysis code changed (regression bug)
> - VADER library broken (rare)
> - MongoDB storing wrong field (typo in field name)
> - Previous data corrupt (need to reload)
> </details>

---

### Scenario 3 (Intermediate):
**Scenario**: A hashtag #election goes viral and appears in 50,000 tweets within 10 minutes. The dashboard shows it correctly, but the database query takes 45 seconds instead of the usual 200ms.

**Question**: Why is the query slow and how would you fix it?

> <details>
> <summary>Answer</summary>
> **Root cause**: No index on the `hashtags` field in MongoDB.
>
> **Why it's slow**:
> - To find tweets with "#election", MongoDB scans every document
> - 5 million tweets × averaging 1.8 hashtags per tweet = full collection scan
> - Full collection scan: 45 seconds on a 5M document collection
>
> **Solution - Add index**:
> ```javascript
> db.tweets.createIndex({ "hashtags": 1 })
> ```
>
> **After index**:
> - MongoDB reads hashtag index (sorted list of all hashtags)
> - Finds documents with "#election" directly (not scanning all 5M)
> - Result: 200ms (+ index maintenance cost, negligible)
>
> **Prevention**:
> - Add indexes at startup for frequently queried fields
> - Monitor slow query logs: `db.setProfilingLevel(1)` 
> - Alert if query > 500ms
>
> **Index strategy** (for full production system):
> ```javascript
> db.tweets.createIndex({ "sentiment": 1 })
> db.tweets.createIndex({ "processing_timestamp": -1 })
> db.tweets.createIndex({ "hashtags": 1 })
> db.tweets.createIndex({ "user": 1 })
> ```
> </details>

---

### Scenario 4 (Beginner):
**Scenario**: A user tweets "That's terrible" at 10:00 AM. Producer picks it up and publishes to Kafka. By the time Spark processes it (5 seconds later) and writes to MongoDB, the timestamp says 10:00 AM. But when you query MongoDB, the tweet has `processing_timestamp: 10:05 AM`.

**Question**: Is this a bug? Explain what's happening.

> <details>
> <summary>Answer</summary>
> **No, not a bug.** Both timestamps are correct; they measure different things:
>
> - **Tweet created_at**: 10:00 AM (original tweet timestamp from dataset)
> - **Spark processing_timestamp**: 10:05 AM (when our system processed it)
> - **Kafka latency**: ~5 seconds (time in Kafka queue before processing)
>
> **Timeline**:
> 1. 10:00:00 - Tweet created (stored in `created_at` field)
> 2. 10:00:01 - Stream simulator publishes to Kafka
> 3. 10:00:05 - Spark micro-batch window closes, processes batch
> 4. 10:00:05 - VADER analyzes, extraction happens
> 5. 10:00:05 - Spark adds `processing_timestamp: 10:00:05`
> 6. 10:00:07 - MongoDB writes complete
>
> **Why have both timestamps?**
> - **created_at**: For temporal analysis (when was tweet created?)
> - **processing_timestamp**: For monitoring (when did system process it?)
>
> **Dashboard should use**:
> - `created_at` for trend analysis ("tweets per hour of creation")
> - `processing_timestamp` for system monitoring ("latency from creation to analysis")
> 
> **Potential issue**: If delay is >10 minutes, might indicate pipeline slowdown and warrant investigation.
> </details>

---

### Scenario 5 (Advanced):
**Scenario**: A sentiment analysis company wants to monetize your pipeline. They want to send their own tweets through your system and pay per tweet processed. You add a second producer that sends tweets to the same Kafka topic. Suddenly, MongoDB is getting throughput errors and the original free user's tweets are delayed.

**Question**: What architectural problem exists and how would you solve it?

> <details>
> <summary>Answer</summary>
> **Problem**: Single shared Kafka topic and single MongoDB collection
> - Both producers write to same queue, competing for bandwidth
> - No isolation or rate limiting
> - No way to prioritize or separate workloads
> - Single consumer bottleneck
>
> **Issues caused**:
> 1. **Capacity**: Kafka has fixed throughput; new producer overloads it
> 2. **Isolation**: One producer's data intermingled with another's
> 3. **Billing**: Can't track usage per producer
> 4. **SLA**: Can't guarantee latency for paying customer
>
> **Solutions**:
>
> **Option 1 - Separate Kafka topics** (Quick fix):
> ```yaml
> # New topic for paid customer
> Kafka topics:
>   - tweets_stream_free (original)
>   - tweets_stream_paid (new)
> 
> # Two Spark consumers
> Consumer 1: tweets_stream_free → MongoDB → Dashboard
> Consumer 2: tweets_stream_paid → separate_collection → separate_dashboard
> ```
> **Pros**: Simple, complete isolation
> **Cons**: Duplicated infrastructure
>
> **Option 2 - Multi-tenant MongoDB** (Better):
> ```python
> enriched_tweet = {
>   "tenant_id": "free_tier",  # New field
>   "id": 123,
>   "text": "...",
>   "sentiment": "Positive",
>   ...
> }
> 
> # Index for multi-tenancy
> db.tweets.createIndex({ "tenant_id": 1, "sentiment": 1 })
> 
> # Dashboard queries specific tenant
> db.tweets.find({"tenant_id": user.tenant_id})
> ```
> **Pros**: Shared infrastructure, cost-effective
> **Cons**: Need to handle tenant isolation, billing logic
>
> **Option 3 - Quota and rate limiting** (Production):
> ```python
> from ratelimit import limits, sleep_and_retry
> 
> @sleep_and_retry  # Rate limit per producer
> @limits(calls=50, period=1)  # 50 tweets/sec per producer
> def publish_to_kafka(tweet, producer_id):
>   # Calculate remaining quota
>   daily_limit = get_daily_limit(producer_id)
>   current_usage = get_usage(producer_id)
>   
>   if current_usage >= daily_limit:
>       raise QuotaExceeded()
>   
>   kafka_producer.send(topic, value=tweet)
> ```
> **Pros**: Fair allocation, cost control
> **Cons**: Complex, need usage tracking
>
> **Recommended**: **Option 3** (Quota + multi-tenant) for SaaS viability
> </details>

---

### Scenario 6 (Intermediate):
**Scenario**: The stream simulator runs fine locally. But when deployed to a cluster with 100 Spark executors, VADER sentiment analysis starts failing on 5% of tweets with "Module not found: vaderSentiment".

**Question**: What's wrong and how would you fix it?

> <details>
> <summary>Answer</summary>
> **Root Cause**: VADER library not installed on Spark executor nodes
> - Local dev: All requirements installed on your machine
> - Cluster: 100 executor JVMs each need Python with VADER
> - Some executors don't have the package → failures
>
> **Why 5% and not 100%?**
> - Tasks are distributed across 100 nodes
> - Some nodes have VADER (if developer worked on them), others don't
> - Random distribution causes ~5% to fail (unlucky data distribution)
>
> **Solutions**:
>
> **Option 1 - Package Python with Spark**:
> ```bash
> # Before submitting job to cluster
> spark-submit \
>   --py-files /path/to/requirements.txt \
>   --archives /path/to/python_env.tar.gz  # Pre-packaged Python environment
>   spark_consumer.py
> ```
>
> **Option 2 - Install on all nodes** (Ansible/Terraform):
> ```bash
> # Deploy script to all 100 nodes
> ansible all -m shell -a "pip install vaderSentiment"
> ```
>
> **Option 3 - Docker container** (Best practice):
> ```dockerfile
> # Dockerfile
> FROM pyspark:3.3
> RUN pip install vaderSentiment pymongo
> 
> # Build and push to all nodes
> docker build -t spark-consumer:1.0 .
> ```
>
> **Option 4 - Spark dependency management**:
> ```python
> # In spark_consumer.py
> spark = SparkSession.builder \
>   .config("spark.jars.packages", 
>           "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
>   .config("spark.python.executable", "/usr/bin/python3") \
>   .config("spark.python.worker.reuse", True) \
>   .getOrCreate()
> 
> # Note: This handles Scala/Java packages, not Python packages
> # For Python dependencies, use Option 1-3
> ```
>
> **Best practice**: Use Docker for guaranteed consistency across 100 nodes
> </details>

---

### Scenario 7 (Advanced):
**Scenario**: Your sentiment analysis model is trained on 2009 tweets. It's now 2026. Modern tweets use new slang (e.g., "lowkey", "slay", "it's giving"), new emoji, and references to memes. VADER's accuracy has dropped from 78% to 62%. You need to improve it without completely rewriting the system.

**Question**: Propose a solution that maintains real-time performance while improving accuracy.

> <details>
> <summary>Answer</summary>
> **Problem**: 
> - New slang/emoji not in VADER's 2014 lexicon
> - Training a full BERT model would be 50-100ms latency (too slow for real-time)
> - Can't wait to retrain; need improvement now
>
> **Proposed solution - Hybrid approach**:
>
> **Phase 1 - Quick wins** (Days, minimal latency impact):
> ```python
> # Update VADER's lexicon with 2026 slang
> custom_lexicon = {
>     "lowkey": -0.4,      # Negative/dismissive
>     "slay": 0.8,         # Strongly positive
>     "it's giving": 0.6,  # Positive vibe
>     "no cap": 0.5,       # Positive emphasis
>     "fr fr": 0.4,        # Casual positive
> }
> 
> analyzer = SentimentIntensityAnalyzer()
> analyzer.lexicon.update(custom_lexicon)  # Extend lexicon
> 
> def analyze_sentiment_v2(text):
>     scores = analyzer.polarity_scores(text)
>     return scores['compound']
> ```
> **Cost**: ~1-2% latency increase (still <2ms), 62% → 68% accuracy
>
> **Phase 2 - Ensemble approach** (Weeks):
> ```python
> # Combine VADER (fast) with lightweight model (faster BERT)
> def ensemble_sentiment(text):
>     # Fast: VADER (1ms)
>     vader_score = vader_analyzer.polarity_scores(text)['compound']
>     
>     # Medium: Distilled BERT (10ms, much smaller than full BERT)
>     # Model distilled from teacher BERT, 10x smaller
>     bert_input = tokenizer(text, return_tensors="pt")
>     with torch.no_grad():
>         output = distilled_bert(**bert_input)
>     bert_score = output.logits.softmax(dim=-1)[0, -1].item()  # Positive logits
>     
>     # Weighted ensemble: Trust VADER 70%, BERT 30%
>     combined = 0.7 * vader_score + 0.3 * (bert_score * 2 - 1)  # Rescale BERT
>     
>     return "Positive" if combined >= 0.05 else ...
> ```
> **Cost**: ~12ms latency (slightly slower, still acceptable for 5s batches), 68% → 75% accuracy
> **Trade-off**: Process 250 tweets × 12ms = 3 seconds (under 5s window)
>
> **Phase 3 - Online learning** (Months):
> ```python
> # User corrections: "This was classified as Positive but I meant Negative"
> corrections = []
> 
> # Periodically retrain lightweight model on corrections
> if len(corrections) > 1000:
>     retrain_distilled_bert(corrections)
>     accuracy improve further
> ```
>
> **Implementation roadmap**:
> 1. Update VADER lexicon immediately (Days)
>   - Deploy in Spark consumer, minimal change
>   - Monitor accuracy improvement
> 2. Integrate distilled BERT if accuracy still insufficient (Weeks)
>   - Test on small % of traffic (1% A/B test)
>   - Roll out if latency acceptable
> 3. Gather user feedback (Ongoing)
>   - Improve with actual use cases
>
> **Advantages over full rewrite**:
> - Incremental changes, low risk
> - Maintains real-time performance (critical requirement)
> - Applicable at any scale
> - Easy to rollback if something breaks
> </details>

---

## Code Comprehension Questions

### Code 1 (Intermediate):
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, schema_of_json

spark = SparkSession.builder \
    .appName("TweetSentimentAnalysis") \
    .getOrCreate()

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "tweets_stream") \
    .option("startingOffsets", "latest") \
    .load()

# Kafka messages come as raw JSON in value column
schema = '{"id": "long", "text": "string", "user": "string"}'
tweets_df = df.select(from_json(col("value"), schema).alias("tweet")) \
    .select("tweet.*")
```

**Question**: What does `.option("startingOffsets", "latest")` do? How would the behavior change with `"earliest"`?

> <details>
> <summary>Answer</summary>
> **"latest"**:
> - Spark starts consuming from the **newest messages** in Kafka
> - Ignores all historical messages (processed before Spark started)
> - Use case: Real-time dashboard (don't care about past data)
> - On Spark restart: Resumes from checkpoint (if exists), otherwise latest again
> - Useful for: Fresh start, live data only
>
> **"earliest"**:
> - Spark starts consuming from the **oldest message** in Kafka
> - Processes the entire Kafka backlog from day 1
> - Use case: Reprocessing entire dataset, quality checks
> - On Spark restart: Resumes from checkpoint, not re-reading from beginning
> - Useful for: Backfill, full reprocessing after model change
>
> **Trade-off**:
> - "latest": Fast startup (no backlog), but miss historical context
> - "earliest": Slow startup (process backlog), but capture all data
>
> **Example**:
> - Kafka has messages from hours 1-10
> - Spark starts at hour 11 with "latest": Processes hour 11+ only
> - Spark starts at hour 11 with "earliest": Processes hours 1-10, then hour 11+
>
> **Current pipeline**: Uses "latest" (appropriate for streaming demo)
> </details>

---

### Code 2 (Beginner):
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# Test
print(analyze_sentiment("LOVE THIS!!!"))  # Output?
```

**Question**: What would the output be for "LOVE THIS!!!" and why?

> <details>
> <summary>Answer</summary>
> **Output**: "Positive"
>
> **Why**:
> 1. VADER analyzes "LOVE THIS!!!"
> 2. Components:
>    - "LOVE": Strong positive word (base 0.65)
>    - "THIS": Neutral (0)
>    - ALL CAPS: Emphasis multiplier (×1.5)
>    - "!!!": Punctuation emphasis (×1.2)
> 3. Compound score: ~0.85 (strongly positive, after combining factors)
> 4. Decision: 0.85 >= 0.05 → "Positive" ✓
>
> **Comparison**:
> - "Love this" → compound ≈ 0.65 → Positive
> - "LOVE THIS" → compound ≈ 0.80 → Positive (emphasis)
> - "LOVE THIS!!!" → compound ≈ 0.85 → Positive (emphasis + punctuation)
> - "love this" → compound ≈ 0.45 → Positive (lowercase less emphatic)
>
> **Key insight**: VADER recognizes linguistic cues beyond just word meanings
> </details>

---

### Code 3 (Advanced):
```python
from pyspark.sql.functions import col, udf, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

sentiment_schema = StructType([
    StructField("sentiment", StringType()),
    StructField("score", DoubleType())
])

def vader_udf(text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    
    sentiment = "Positive" if compound >= 0.05 else ("Negative" if compound <= -0.05 else "Neutral")
    return (sentiment, compound)

sentiment_udf = udf(vader_udf, sentiment_schema)

# In Spark consumer
enriched_df = tweets_df.withColumn(
    "sentiment_info",
    sentiment_udf(col("text"))
).select(
    "id",
    "text",
    "user",
    col("sentiment_info.sentiment"),
    col("sentiment_info.score")
)
```

**Question**: What is the difference between this UDF and calling VADER directly in Python? What's the Performance implication?

> <details>
> <summary>Answer</summary>
> **UDF vs Direct Python**:
>
> **UDF (above code)**:
> - Spark creates a Python UDF
> - Spark applies to each row in DataFrame
> - Result is integrated back into Spark
> - Returns structured output (sentiment_info with both fields)
>
> **Direct Python**:
> ```python
> tweets_list = tweets_df.collect()  # Loads all data into driver memory
> for tweet in tweets_list:
>     scores = analyzer.polarity_scores(tweet['text'])  # Process one by one
>     # Result outside Spark, can't parallelize
> ```
>
> **Performance implications**:
>
> | Aspect | UDF | Direct Python |
> |--------|-----|----------------|
> | **Parallelization** | ✅ Across 100 executors | ❌ Single driver |
> | **Execution** | Distributed | Single machine |
> | **250 tweets** | 250ms / N_executors | 250ms (no speedup) |
> | **Memory** | Distributed across executors | All data on driver (crashes >100GB) |
> | **Latency** | 250ms ÷ 4 cores = 62ms | 250ms |
>
> **Trade-offs for this code**:
> - Python UDFs have **serialization overhead** (JVM ↔ Python JSON conversion)
> - **Solution**: Use **Pandas UDF** for vectorization
> ```python
> from pyspark.sql.functions import pandas_udf
> 
> @pandas_udf(sentiment_schema)
> def vader_pandas_udf(texts: pd.Series) -> pd.DataFrame:
>    # Process entire batch at once, not row-by-row
>    results = [vader_udf(text) for text in texts]
>    return pd.DataFrame(results)
> ```
> - Pandas UDF: **10-100x faster** than row-at-a-time Python UDF
> - Still distributes across executors
>
> **Recommendation for 250 tweets/batch**: Use Pandas UDF to avoid serialization bottleneck
> </details>

---

### Code 4 (Intermediate):
```python
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://admin:password@localhost:27017/")
db = client["twitter_analysis"]
collection = db["tweets"]

# Ensure unique constraint on tweet ID
collection.create_index("id", unique=True)

def insert_enriched_tweets(tweets):
    for tweet in tweets:
        try:
            collection.insert_one(tweet)
        except DuplicateKeyError:
            # Tweet already exists, skip silently
            pass
```

**Question**: This code handles duplicates, but the approach has a flaw. What is it and how would you improve it?

> <details>
> <summary>Answer</summary>
> **Flaw**:
> 1. **One-by-one inserts** (insert_one per tweet):
>    - 250 tweets × 3 network round-trips each = 750 network calls
>    - **Very slow**: Network latency dominates (ms per call)
>    - MongoDB not designed for this pattern
>
> 2. **DuplicateKeyError handling** is good but inefficient:
>    - Retry mechanism requires individual handling
>    - Better to prevent duplicates before inserting
>
> **Improvement 1 - Bulk insert**:
> ```python
> def insert_enriched_tweets(tweets):
>     try:
>         collection.insert_many(tweets, ordered=False)
>     except DuplicateKeyError:
>         # Batch insert failed due to duplicate
>         # Fallback: Insert individually to skip duplicates
>         for tweet in tweets:
>             try:
>                 collection.insert_one(tweet)
>             except DuplicateKeyError:
>                 pass
> ```
> - **insert_many()**: Single network call for all tweets
> - **ordered=False**: Continue on duplicate (don't stop)
> - Fallback handles partial duplicates
> - Result: 250 inserts in ~10ms (vs 750ms with insert_one)
>
> **Improvement 2 - Upsert for idempotency**:
> ```python
> def insert_enriched_tweets_idempotent(tweets):
>     # Idempotent: Can re-send same tweets without duplicates
>     operations = [
>         UpdateOne(
>             {"_id": tweet["id"]},  # Match by ID
>             {"$set": tweet},       # Set full document
>             upsert=True            # Insert if not exists
>         )
>         for tweet in tweets
>     ]
>     collection.bulk_write(operations)
> ```
> - **bulk_write()**: Efficient batch operation
> - **UpdateOne with upsert**: Creates if missing, updates if exists
> - **Idempotent**: Safe to re-send same tweets (won't create duplicates)
> - **Exactly-once semantics**: Guaranteed with this approach
> - Result: Same performance (10ms) with guaranteed correctness
>
> **Improvement 3 - Spark DataFrame write**:
> ```python
> # In Spark, use native MongoDB connector (best for distributed writes)
> enriched_df.write \
>     .format("mongodb") \
>     .mode("upsert") \
>     .option("uri", "mongodb://admin:password@localhost:27017/") \
>     .option("database", "twitter_analysis") \
>     .option("collection", "tweets") \
>     .save()
> ```
> - Spark handles distribution, batching, and retries
> - Leverages Spark's optimization (not Python loops)
> - Scales automatically (100x executors = 100x parallel writes)
>
> **Recommended**: Use Spark's MongoDB connector + **Improvement 2** as fallback
> </details>

---

### Code 5 (Beginner):
```python
import json
import time
import random

with open("data/tweets_clean.json", "r") as f:
    tweets = [json.loads(line) for line in f]

kafka_producer.send("tweets_stream", value=tweets[0])  # Send first tweet

TWEETS_PER_SECOND = 50

for tweet in tweets:
    kafka_producer.send("tweets_stream", value=tweet)
    time.sleep(1.0 / TWEETS_PER_SECOND)  # Delay between tweets
```

**Question**: What does the delay `time.sleep(1.0 / TWEETS_PER_SECOND)` achieve? Calculate the approximate delay per tweet.

> <details>
> <summary>Answer</summary>
> **Purpose**: Rate limiting - controls the streaming speed to simulate real-time data
>
> **Calculation**:
> - TWEETS_PER_SECOND = 50
> - Delay = 1.0 / 50 = **0.02 seconds = 20 milliseconds**
> - So: One tweet sent every 20ms
>
> **Why this rate?**
> - 50 tweets/sec × 5-sec batch window = 250 tweets/batch
> - 250 tweets × 1ms VADER analysis = 250ms processing
> - 250ms << 5 seconds, so system has headroom (can handle 10x this rate)
> - Feels like "real-time" streaming from user perspective
> - Prevents overwhelming development machine
>
> **Without delay** (no time.sleep):
> - All 1.5M tweets published to Kafka instantly
> - Kafka would store them all
> - Spark would process in huge batches
> - MongoDB would be flooded
> - Dashboard wouldn't show gradual trends (all data present immediately)
> - Not representative of real streaming
>
> **Effects of changing delay**:
> - Delay = 0.01s: 100 tweets/sec (5x faster)
> - Delay = 0.1s: 10 tweets/sec (5x slower)
> - Delay = 0: All tweets instantly (unrealistic)
>
> **Recommendation**: Keep at 50 tweets/sec for development; adjust for load testing
> </details>

---

## Sequencing Questions

### Seq 1 (Intermediate):
**Question**: Arrange these steps in the correct order for deploying the pipeline:

1. Start Spark consumer (monitor logs)
2. Start Streamlit dashboard
3. Start stream simulator
4. Create virtual environment and install dependencies
5. Start Docker infrastructure (Kafka, MongoDB, Zookeeper)
6. Verify Kafka topic is created
7. Configure MongoDB indexes for performance

---

> <details>
> <summary>Answer</summary>
> **Correct order**:
>
> 1. **Create virtual environment and install dependencies**
>    - `python3 -m venv .venv source .venv/bin/activate`
>    - `pip install -r requirements.txt`
>    - Requirement: Must have PySpark, vaderSentiment, pymongo, streamlit
>
> 2. **Start Docker infrastructure** (Kafka, MongoDB, Zookeeper)
>    - `docker-compose up -d`
>    - Wait 15 seconds for services to be ready
>    - Requirement: Services must be running before producers/consumers
>
> 3. **Verify Kafka topic is created** (Optional but recommended)
>    - `docker exec kafka kafka-topics --list --bootstrap-server localhost:9092`
>    - Ensure `tweets_stream` topic exists (auto-created on first publish or manually)
>
> 4. **Configure MongoDB indexes**
>    - ```
>      docker exec mongodb mongosh
>      use twitter_analysis
>      db.tweets.createIndex({sentiment: 1})
>      db.tweets.createIndex({processing_timestamp: -1})
>      ```
>    - Improves dashboard query performance later
>
> 5. **Start Spark consumer** (in Terminal 1)
>    - `python consumer/spark_consumer.py`
>    - Waits for Kafka messages (none yet)
>    - Requirement: Must be running before producer sends data
>
> 6. **Start stream simulator / producer** (in Terminal 2)
>    - `python -m producer.stream_simulator`
>    - Now tweets start flowing: stream_simulator → Kafka → Spark → MongoDB
>
> 7. **Start Streamlit dashboard** (in Terminal 3)
>    - `streamlit run dashboard/app.py`
>    - Opens http://localhost:8501
>    - Connects to MongoDB, displays real-time data
>
> **Why this order?**
> - ⚠️ Dependencies first (needed for everything)
> - ⚠️ Infrastructure before services (can't connect if not running)
> - 📊 Indexes before producer (improves performance when data arrives)
> - 📥 Consumer before producer (ready to receive)
> - 📤 Producer sends data (starts the flow)
> - 🖥️ Dashboard last (displays what's already processed)
> 
> **What breaks if order is wrong?**
> - Producer before consumer: Tweets queue in Kafka but nothing processes them
> - Dashboard before MongoDB: Can't query, crashes
> - Forgot indexes: Dashboard queries slow as data arrives
> </details>

---

### Seq 2 (Advanced):
**Question**: A tweet goes through the system with potential failures at each stage. Order these recovery steps from "do first" to "do last" when the pipeline fails:

1. Check Spark consumer logs for errors
2. Check if MongoDB has write failures
3. Check Kafka consumer group lag
4. Restart Spark consumer
5. Restart stream simulator
6. Check if services are running (docker ps)
7. Verify network connectivity between containers
8. Flush Kafka topic and restart

---

> <details>
> <summary>Answer</summary>
> **Correct recovery order** (troubleshoot narrowly before broad actions):
>
> 1. **Check if services are running** (`docker ps`)
>    - Most common issue: Services crashed
>    - If Kafka/MongoDB not running, everything fails
>    - Quick command, solves 50% of issues
>
> 2. **Check Spark consumer logs**
>    - `tail -f logs/spark_consumer.log`
>    - Reveals if Spark is processing or erroring
>    - Tells you if it's an application bug
>
> 3. **Check Kafka consumer group lag**
>    - `kafka-consumer-groups --describe --group spark-group --bootstrap-server localhost:9092`
>    - If lag is growing: Spark can't keep up
>    - If lag stable but no data: Producer not sending
>    - Indicates if Kafka side is working
>
> 4. **Verify network connectivity between containers**
>    - `docker exec spark ping kafka` (inside Docker network)
>    - `docker network inspect tweet-analysis_default`
>    - If containers can't see each other, app fails mysteriously
>
> 5. **Check if MongoDB has write failures**
>    - `docker logs mongodb | tail`
>    - Check Spark logs for "MongoException"
>    - If MongoDB can't write, Spark keeps retrying and falls behind
>
> 6. **Restart Spark consumer**
>    - `pkill -f spark_consumer.py`
>    - `python consumer/spark_consumer.py`
>    - Often clears transient connection issues
>    - Has checkpoint recovery mechanism
>
> 7. **Restart stream simulator**
>    - `pkill -f stream_simulator.py`
>    - `python -m producer.stream_simulator`
>    - Usually not the cause (but try if others don't work)
>
> 8. **Flush Kafka topic and restart** (Last resort)
>    - `kafka-topics --delete --topic tweets_stream`
>    - `docker-compose restart kafka`
>    - Wipes all queued messages (data loss!)
>    - Only if completely stuck
>
> **Why this order?**
> - Start with quick checks (doesn't change anything)
> - Move to application logs (reveals root cause)
> - Try soft restarts (restart services gracefully)
> - Avoid nuking data until necessary
>
> **Example troubleshooting**:
> - Issue: Dashboard shows no tweets
> - Step 1: `docker ps` → MongoDB running ✓, Kafka running ✓
> - Step 2: Spark logs → "Connection refused on localhost:9092"
> - **Root cause**: Spark connecting to localhost instead of kafka hostname
> - Fix: Change config from localhost:9092 to kafka:9092 (Docker DNS)
> </details>

---

---

# 📊 Answer Key

**Quick lookup for all answers:**

| Question | Type | Answer |
|----------|------|--------|
| Card 1 | Flashcard | Apache Kafka is the message broker |
| Card 2 | Flashcard | VADER = lexicon-based, fast, social media optimized |
| ... | ... | (See detailed answers in each card above) |
| MC 1 | Multiple Choice | c) Message broker |
| MC 2 | Multiple Choice | c) Handles sarcasm perfectly (FALSE) |
| MC 3 | Multiple Choice | a) 1.6M tweets from 2009 |
| ... | ... | (See detailed answers in each card above) |
| TF 1 | True/False | FALSE - MongoDB is NoSQL |
| TF 2 | True/False | FALSE - VADER needs no training |
| ... | ... | (See detailed answers in each card above) |
| Scenario 1 | Scenario | MongoDB write throughput bottlenecked |
| Scenario 2 | Scenario | Manual review → MongoDB query → VADER test → Compare labels |
| ... | ... | (See detailed answers in each card above) |
| Seq 1 | Sequencing | 4→5→6→7→1→3→2 (setup dependencies to dashboard) |
| Seq 2 | Sequencing | 6→2→3→7→5→4→1 (diagnose before restarting) |

---

# 🎯 Scoring Guide

## Self-Assessment Rubric

### Flashcards (0-35 points)

**Scoring approach**: Use flashcards for self-study. Try to answer before revealing, then assess:

- **Perfect answer**: Explains concept correctly with examples → 1 point
- **Mostly correct**: Right idea but missing nuance → 0.75 points
- **Partially correct**: Some understanding but incomplete → 0.5 points
- **Incorrect**: Misunderstood concept → 0 points

**Example**:
- **Card 2 (VADER)**: You answer "VADER is a sentiment tool that works fast"
  - Missing: Why it was chosen, specifics on speed/accuracy, social media optimization
  - Score: 0.5 points (correct but incomplete)
- **Better answer** [reveals spoiler]: "VADER is lexicon-based, optimized for social media, works in <1ms, no training required, chosen over BERT due to speed/accuracy balance"
  - Score: 1 point (complete and accurate)

**Maximum flashcard score**: 35 × 1 = **35 points**

---

### Quiz Questions (0-100 points)

**Scoring approach**: Track your answers, then score:

#### Multiple Choice (MC 1-15): 15 points
- Correct answer: 1 point each
- Incorrect answer: 0 points
- Partial credit (reasonable alternative): 0.5 points

#### True/False (TF 1-10): 10 points
- Correct answer: 1 point each
- Incorrect answer: 0 points
- No partial credit

#### Scenario Questions (Scenario 1-7): 35 points
- Identifies root cause: 1 point
- Proposes investigation steps: 1.5 points
- Suggests multiple solutions: 1.5 points
- Explains trade-offs: 1 point
- **Per scenario**: 5 points

#### Code Comprehension (Code 1-5): 25 points
- Correct explanation: 3 points
- Identifies performance implication: 1 point
- Suggests improvement: 1 point
- **Per question**: 5 points

#### Sequencing (Seq 1-2): 15 points
- Correct full order: 7 points each
- Partial credit (+3 sequencing errors): 4 points
- Explains reasoning: +1 bonus per question

---

## Difficulty Calibration

### Beginner Level (40% of exam)
- **Cards**: 1-10 (basic concepts)
- **Questions**: MC 1, 3, 15; TF 1, 2, 9
- **Expected score**: 90%+ (should be comfortable here)
- **Time**: 20 minutes

### Intermediate Level (35% of exam)
- **Cards**: 11-20 (architecture, implementation)
- **Questions**: MC 2, 4, 5, 6, 7, 8, 14; TF 3, 4, 6, 8; Scenario 1-2
- **Expected score**: 70-80% (requires self-study)
- **Time**: 45 minutes

### Advanced Level (25% of exam)
- **Cards**: 21-35 (distributed systems, optimization, production)
- **Questions**: MC 9, 10, 11, 13; TF 5, 7, 10; Scenario 3-7; Code 1-5; Seq 1-2
- **Expected score**: 60-75% (requires deep understanding)
- **Time**: 60 minutes

---

## Performance Bands

### Pathway to Mastery

| Score Band | Interpretation | Next Steps |
|-----------|-----------------|-----------|
| **90-100%** | 🟢 **Expert** - Ready for technical interview | Review advanced scenarios for edge cases |
| **80-89%** | 🟢 **Proficient** - Strong understanding | Focus on advanced cards and scenarios |
| **70-79%** | 🟡 **Intermediate** - Good grasp but gaps | Reread architecture section in README |
| **60-69%** | 🟡 **Developing** - Foundational knowledge | Focus on intermediate cards and multiple choice |
| **Below 60%** | 🔴 **Beginning** - Review fundamentals | Start with beginner cards, build up |

---

## Technical Interview Preparation

**Questions likely in a real technical interview:**

1. **Architecture**: "Explain the 3-layer architecture of the pipeline" → Use Card 4
2. **Fault Tolerance**: "What happens if Kafka crashes?" → Use Card 17
3. **Performance**: "Why is the second dashboard request faster?" → Use MC 13
4. **Real-world**: "You need to scale 1M tweets/sec—what breaks first?" → Use MC 10
5. **Troubleshooting**: "Sentiment analysis accuracy dropped—how do you debug?" → Use Scenario 2
6. **Design**: "Scale this system to 1B tweets/day" → Use Card 28
7. **Code**: "What's wrong with this MongoDB code?" → Use Code 4
8. **Trade-offs**: "VADER vs BERT—which is better?" → Use Card 20

---

## Study Recommendations

### 1-Hour Session
- **15 min**: Beginner cards (1-10)
- **30 min**: Multiple choice and True/False (MC 1-10, TF 1-5)
- **15 min**: Review answers, identify weak areas

### 3-Hour Session
- **30 min**: Beginner + Intermediate cards (1-20)
- **45 min**: All multiple choice + True/False questions
- **60 min**: Scenario-based questions (pick 2-3)
- **30 min**: Review and identify gaps
- **15 min**: Quick code review (Code 1-2)

### 8-Hour Deep Dive
- **2 hours**: All flashcards (depth-first reading)
- **2 hours**: All multiple choice + True/False
- **2 hours**: All scenario-based questions
- **1 hour**: Code comprehension (Code 1-5)
- **1 hour**: Sequencing questions with detailed explanations

---

## Self-Evaluation Questions

After taking the quiz, ask yourself:

1. **Could you explain the pipeline to a friend without looking at notes?**
   - If no → Review cards and architecture fundamentals
   
2. **Can you identify when VADER would fail?**
   - If no → Review Card 15 and 20, MC 2
   
3. **Could you troubleshoot a real production issue?**
   - If no → Review Scenarios 2-7 more carefully
   
4. **Do you understand the trade-offs between technologies?**
   - If no → Review Cards 21-28, advanced scenarios
   
5. **Could you handle a follow-up question during an interview?**
   - If no → Practice explaining "why" not just "what"

---

## Continuous Learning Path

### Week 1: Foundations
- [ ] Read all beginner cards (1-10)
- [ ] Answer MC 1-7, TF 1-5
- [ ] Understand basic concepts

### Week 2: Architecture
- [ ] Understand all 3 layers (Card 4)
- [ ] Learn data flow (Card 16)
- [ ] Answer MC 5, 6, 7
- [ ] Work through Scenario 1

### Week 3: Production Concerns
- [ ] Learn fault tolerance (Card 17)
- [ ] Understand scaling (Card 28)
- [ ] Answer advanced scenario questions
- [ ] Review code examples (Code 1-5)

### Week 4: Interview Prep
- [ ] Do mock interviews (explain pipeline in 5 min)
- [ ] Practice troubleshooting (follow Scenario 2 steps)
- [ ] Answer random questions to test depth
- [ ] Prepare 3 deep-dive stories (project, challenge, learning)

---

End of Learning Tool. Good luck with your studies! 🚀


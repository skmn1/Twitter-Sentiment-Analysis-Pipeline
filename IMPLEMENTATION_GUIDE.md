# 🎓 Big Data Pipeline - Complete Implementation Guide

[![Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white)](https://kafka.apache.org/)
[![Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white)](https://spark.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)

> A production-ready big data pipeline processing 864,000 vessel positions in real-time with sub-100ms API response times.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Understanding Data Flow](#-understanding-data-flow)
- [Implementation Steps](#-implementation-steps)
  - [Step 1: Generate Data](#step-1-generate-your-data-day-1)
  - [Step 2: Start Infrastructure](#step-2-start-the-infrastructure-day-2)
  - [Step 3: Create Kafka Topics](#step-3-create-kafka-topics-day-2)
  - [Step 4: Build Kafka Producer](#step-4-build-kafka-producer-day-3-4)
  - [Step 5: Data Cleaning Job](#step-5-build-spark-consumer---part-a-data-cleaning-job-day-5-7)
  - [Step 6: Enrichment Job](#step-6-build-spark-consumer---part-b-enrichment-job-day-8-10)
  - [Step 7: Aggregation Job](#step-7-build-spark-consumer---part-c-aggregation-job-day-11-12)
  - [Step 8: Build REST API](#step-8-build-rest-api-day-13-15)
  - [Step 9: Deploy Everything](#step-9-deploy-everything-day-16-18)
- [Complete Data Journey](#-complete-data-journey)
- [Mental Model](#-mental-model---5-core-rules)
- [Quick Reference](#-quick-reference-cheat-sheet)

---

## 🎯 Overview

### What We're Building

A system that transforms raw data into actionable insights through automated processing:

```
RAW DATA → INGESTION → PROCESSING → STORAGE → SERVING
(Files)     (Kafka)      (Spark)      (Iceberg)   (API)
```

### Real-World Analogy

Think of it as a **restaurant kitchen**:
- 📦 Raw ingredients arrive (**data ingestion**)
- 👨‍🍳 Chefs prepare them (**data processing**)
- 🗄️ Organized in storage (**data lake**)
- 🍽️ Served to customers (**API serving**)

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────┐     ┌────────────┐     ┌──────────┐     ┌─────────┐
│   CSV File  │ --> │  Kafka   │ --> │   Spark    │ --> │ Iceberg  │ --> │   API   │
│  Generator  │     │ Producer │     │ Processing │     │   Lake   │     │ + Redis │
└─────────────┘     └──────────┘     └────────────┘     └──────────┘     └─────────┘
                                            │
                                            ├── Bronze (Raw)
                                            ├── Silver (Enriched)
                                            └── Gold (Aggregated)
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Transport** | Apache Kafka | Message streaming |
| **Processing Engine** | Apache Spark | Data transformation |
| **Data Lake** | Apache Iceberg | Table format |
| **Object Storage** | MinIO (S3) | File storage |
| **Catalog** | PostgreSQL | Metadata management |
| **Cache** | Redis | Fast data access |
| **API** | FastAPI (Python) | RESTful endpoints |
| **Orchestration** | Docker/Kubernetes | Container management |

---

## 📚 Understanding Data Flow

### The 5 Stages Every Data Pipeline Goes Through

#### Stage 1 - RAW DATA
```json
{
  "mmsi": "123456",
  "lat": 48.8,
  "lon": 2.3,
  "speed": 12.5,
  "time": "2024-01-15T10:00:00"
}
```
**Like:** Raw ingredients with dirt and skin

#### Stage 2 - INGESTION (Kafka)
Data gets transported to processing.  
**Like:** Delivery truck brings ingredients to restaurant

#### Stage 3 - PROCESSING (Spark)
Data is cleaned and enriched.  
**Like:** Peel onions, cut vegetables, mix ingredients

#### Stage 4 - STORAGE (Iceberg)
Organized storage for easy retrieval.  
**Like:** Labeled containers in the fridge

#### Stage 5 - SERVING (API)
Deliver to customers quickly.  
**Like:** Waiter brings food to table

---

## 🚀 Implementation Steps

### Step 1: Generate Your Data (Day 1)

**Objective:** Create the raw material you'll work with

**Why:** You need data before you can process it!

#### Actions

```bash
# Run the data generator
python3 data-generation/generate_ais_data.py
```

#### Output

```csv
mmsi,timestamp,latitude,longitude,speed,vessel_name
123456,2024-01-15T10:00:00,48.8,2.3,12.5,OCEAN STAR
123456,2024-01-15T10:05:00,48.81,2.31,12.3,OCEAN STAR
...
```

**Result:** 864,000 vessel positions ready for processing

**⏱️ Time:** 2 minutes  
**📊 Output:** `ais_data.csv` file

---

### Step 2: Start the Infrastructure (Day 2)

**Objective:** Turn on all the "machines" that will process data

**Why:** You need the kitchen equipment before you can cook!

#### Actions

```bash
docker-compose up -d
```

#### What Happens Behind the Scenes

1. **Zookeeper** (Port 2181)
   - Boots up and coordinates Kafka
   - ✅ "Ready to coordinate!"

2. **Kafka** (Port 9092)
   - Connects to Zookeeper
   - Creates empty topics
   - ✅ "Ready to receive messages!"

3. **Spark Master** (Port 7077, 8080)
   - Starts management service
   - Opens web UI: http://localhost:8080
   - ✅ "Ready to manage workers!"

4. **Spark Worker**
   - Registers with Master
   - Allocates 4GB memory, 2 CPU cores
   - ✅ "Ready to work!"

5. **PostgreSQL** (Port 5432)
   - Creates `iceberg_catalog` database
   - ✅ "Ready to store metadata!"

6. **MinIO** (Ports 9000, 9001)
   - Creates object storage
   - ✅ "Ready to store files!"

7. **Redis** (Port 6379)
   - Loads into memory
   - ✅ "Ready to cache data!"

#### Verification

```bash
docker-compose ps

# You should see 7 services "Up"
```

**⏱️ Time:** 2 minutes to start  
**✅ Output:** All services running and ready

---

### Step 3: Create Kafka Topics (Day 2)

**Objective:** Create "mailboxes" where data will be sent

**Why:** Kafka needs to know where to put incoming messages

#### Create Topics

```bash
# Create AIS raw data topic
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic ais_raw \
  --partitions 3 \
  --replication-factor 1

# Create weather stream topic
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic weather_stream \
  --partitions 3 \
  --replication-factor 1

# Create port events topic
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic port_events \
  --partitions 3 \
  --replication-factor 1
```

#### Topic Structure

```
Topic: ais_raw
├── Partition 0 (empty)
├── Partition 1 (empty)
└── Partition 2 (empty)
```

**Why 3 partitions?**
- Allows 3 consumers to read simultaneously
- Parallel processing = faster throughput

#### Verification

```bash
docker exec -it kafka kafka-topics --list \
  --bootstrap-server localhost:9092

# Output:
# ais_raw
# weather_stream
# port_events
```

**⏱️ Time:** 30 seconds per topic  
**✅ Output:** Empty topics ready to receive data

---

### Step 4: Build Kafka Producer (Day 3-4)

**Objective:** Write code that sends data to Kafka

**Why:** Someone needs to put mail in the mailbox!

#### Producer Responsibilities

1. Read data from CSV file
2. Send each record to Kafka
3. Maintain controlled speed (50 records/second)

#### Implementation

```scala
object AISStreamProducer {
  def main(args: Array[String]): Unit = {
    // Step 1: Connect to Kafka
    val producer = new KafkaProducer[String, String](
      Map(
        "bootstrap.servers" -> "localhost:9092",
        "key.serializer" -> "org.apache.kafka.common.serialization.StringSerializer",
        "value.serializer" -> "org.apache.kafka.common.serialization.StringSerializer"
      )
    )
    
    // Step 2: Read CSV file
    val data = Source.fromFile("ais_data.csv").getLines()
    
    // Step 3: Loop through each record
    data.foreach { line =>
      // Step 4: Convert to JSON
      val record = parseCSV(line)
      val json = convertToJSON(record)
      
      // Step 5: Send to Kafka topic
      val kafkaRecord = new ProducerRecord[String, String](
        "ais_raw",    // topic
        record.mmsi,  // key
        json          // value
      )
      
      producer.send(kafkaRecord)
      
      // Step 6: Control rate (50 records/second)
      Thread.sleep(20)
    }
    
    producer.close()
  }
}
```

#### Runtime Behavior

```
Second 0: Send 50 records → Kafka stores them
Second 1: Send 50 records → Kafka stores them
Second 2: Send 50 records → Kafka stores them
...
```

#### Kafka's Perspective

```
Topic: ais_raw
Partition 0: [msg1, msg2, msg3, ...]
Partition 1: [msg4, msg5, msg6, ...]
Partition 2: [msg7, msg8, msg9, ...]
```

#### Run the Producer

```bash
sbt "runMain producer.AISStreamProducer"
```

#### Console Output

```
📤 Sent record 100 to Kafka
📤 Sent record 200 to Kafka
📤 Sent record 300 to Kafka
...
```

**⏱️ Time:** 1-2 days to code and test  
**✅ Output:** Data flowing into Kafka continuously

---

### Step 5: Build Spark Consumer - Part A (Data Cleaning Job) (Day 5-7)

**Objective:** Read from Kafka and clean the data

**Why:** Raw data is messy - we need to validate and clean it!

#### Consumer Responsibilities

1. Read messages from Kafka
2. Validate data quality
3. Remove bad records
4. Save to Bronze layer

#### Implementation

```scala
object DataCleaningJob {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("AIS Data Cleaning")
      .master("spark://localhost:7077")
      .getOrCreate()
    
    import spark.implicits._
    
    // Step 1: Connect to Kafka
    val kafkaDF = spark
      .readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "localhost:9092")
      .option("subscribe", "ais_raw")
      .option("startingOffsets", "earliest")
      .load()
    
    // Step 2: Parse JSON
    val schema = StructType(Seq(
      StructField("mmsi", StringType),
      StructField("timestamp", TimestampType),
      StructField("latitude", DoubleType),
      StructField("longitude", DoubleType),
      StructField("speed", DoubleType),
      StructField("vessel_name", StringType)
    ))
    
    val parsedDF = kafkaDF
      .select(from_json(col("value").cast("string"), schema).as("data"))
      .select("data.*")
    
    // Step 3: Clean the data
    val cleanedDF = parsedDF
      // Remove duplicates
      .dropDuplicates("mmsi", "timestamp")
      
      // Validate coordinates
      .filter(col("latitude").between(-90, 90))
      .filter(col("longitude").between(-180, 180))
      
      // Validate speed
      .filter(col("speed") >= 0 && col("speed") <= 100)
      
      // Add quality flag
      .withColumn("is_valid", lit(true))
      .withColumn("processing_date", current_date())
    
    // Step 4: Write to Iceberg (Bronze layer)
    val query = cleanedDF
      .writeStream
      .format("iceberg")
      .outputMode("append")
      .option("path", "s3://datalake/bronze/ais_raw")
      .option("checkpointLocation", "/tmp/checkpoint/bronze")
      .trigger(Trigger.ProcessingTime("5 seconds"))
      .start()
    
    query.awaitTermination()
  }
}
```

#### Processing Flow

```
Input: 250 records
  ↓
Remove duplicates: 248 records (2 duplicates)
  ↓
Validate latitude: 247 records (1 invalid)
  ↓
Validate longitude: 247 records (all valid)
  ↓
Validate speed: 245 records (2 impossible speeds)
  ↓
Output: 245 clean records → Bronze layer
```

#### What Happens Physically

1. **Spark processes micro-batch** (every 5 seconds)
   ```
   Batch 1: Process 245 records
   Batch 2: Process 238 records
   Batch 3: Process 251 records
   ```

2. **Spark writes to MinIO**
   ```
   /bronze/ais_raw/
   ├── part-00001.parquet (245 records)
   ├── part-00002.parquet (238 records)
   └── part-00003.parquet (251 records)
   ```

3. **Spark updates PostgreSQL catalog**
   ```sql
   INSERT INTO iceberg_catalog.tables VALUES
   ('bronze.ais_raw', 'parquet', '/bronze/ais_raw/', ...);
   ```

#### Run the Job

```bash
spark-submit \
  --class com.maritime.processing.DataCleaningJob \
  --master spark://localhost:7077 \
  --packages org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.3.0 \
  target/scala-2.12/maritime-platform.jar
```

#### Console Output

```
✅ Batch 0: Processed 245 records
✅ Batch 1: Processed 238 records
✅ Batch 2: Processed 251 records
```

**⏱️ Time:** 2-3 days to code and test  
**✅ Output:** Clean data in Bronze layer (Iceberg table)

---

### Step 6: Build Spark Consumer - Part B (Enrichment Job) (Day 8-10)

**Objective:** Add context and additional information to cleaned data

**Why:** Raw positions aren't useful alone - we need business context!

#### Enrichment Process

**Input (Bronze layer):**
```json
{
  "mmsi": "123456",
  "lat": 48.8,
  "lon": 2.3,
  "speed": 12.5
}
```

**Output (Silver layer):**
```json
{
  "mmsi": "123456",
  "lat": 48.8,
  "lon": 2.3,
  "speed": 12.5,
  "nearest_port": "ROTTERDAM",
  "distance_to_port": 351,
  "sea_temperature": 18.5,
  "wind_speed": 15,
  "speed_category": "CRUISING",
  "time_in_zone": 2.3,
  "is_potential_fishing": false
}
```

#### Implementation

```scala
object EnrichmentJob {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("AIS Data Enrichment")
      .master("spark://localhost:7077")
      .getOrCreate()
    
    import spark.implicits._
    
    // Step 1: Read from Bronze layer
    val vesselData = spark.read
      .format("iceberg")
      .load("s3://datalake/bronze/ais_raw")
    
    // Step 2: Load reference data
    val weatherData = spark.read
      .format("iceberg")
      .load("s3://datalake/bronze/weather_raw")
    
    val portData = spark.read
      .format("json")
      .load("data/ports_reference.json")
    
    // Step 3: Join with weather data
    val withWeather = vesselData
      .withColumn("lat_grid", round(col("latitude"), 0))
      .withColumn("lon_grid", round(col("longitude"), 0))
      .join(
        weatherData,
        Seq("lat_grid", "lon_grid"),
        "left"
      )
      .select(
        vesselData.columns.map(col) ++
        Seq(col("temperature"), col("wind_speed")): _*
      )
    
    // Step 4: Calculate distance to nearest port
    val withPorts = withWeather
      .crossJoin(portData)
      .withColumn("distance", 
        haversineDistance(
          col("latitude"), col("longitude"),
          col("port_lat"), col("port_lon")
        )
      )
      .withColumn("rank",
        row_number().over(
          Window.partitionBy("mmsi", "timestamp")
            .orderBy("distance")
        )
      )
      .filter(col("rank") === 1)
      .select(
        withWeather.columns.map(col) ++
        Seq(
          col("port_name").as("nearest_port"),
          col("distance").as("distance_to_port")
        ): _*
      )
    
    // Step 5: Add derived features
    val enriched = withPorts
      // Speed category
      .withColumn("speed_category",
        when(col("speed") === 0, "STOPPED")
          .when(col("speed") < 5, "SLOW")
          .when(col("speed") < 15, "CRUISING")
          .otherwise("FAST")
      )
      
      // Time in zone
      .withColumn("time_in_zone",
        (unix_timestamp(col("timestamp")) - 
         lag(unix_timestamp(col("timestamp")), 1)
           .over(Window.partitionBy("mmsi").orderBy("timestamp"))
        ) / 3600.0
      )
      
      // Potential fishing activity
      .withColumn("is_potential_fishing",
        col("speed").between(2, 5) && col("time_in_zone") > 1.0
      )
    
    // Step 6: Write to Silver layer
    enriched
      .write
      .format("iceberg")
      .mode("append")
      .save("s3://datalake/silver/vessels_enriched")
  }
  
  // Haversine distance formula
  def haversineDistance(
    lat1: Column, lon1: Column,
    lat2: Column, lon2: Column
  ): Column = {
    val R = 6371 // Earth's radius in km
    
    val dLat = radians(lat2 - lat1)
    val dLon = radians(lon2 - lon1)
    
    val a = sin(dLat / 2) * sin(dLat / 2) +
            cos(radians(lat1)) * cos(radians(lat2)) *
            sin(dLon / 2) * sin(dLon / 2)
    
    val c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    R * c
  }
}
```

#### Enrichment Examples

**Weather Join:**
```
Vessel: lat=48.756 → rounded to 49, lon=2.341 → rounded to 2
Weather grid: lat=49, lon=2 → temp=18.5°C, wind=15 knots
Result: vessel + temperature=18.5, wind=15
```

**Nearest Port Calculation:**
```
For vessel at (48.8, 2.3):

Distances to all ports:
  ROTTERDAM (51.9, 4.5)  → 351 km
  SINGAPORE (1.3, 103.8) → 10,234 km
  SHANGHAI (31.2, 121.5) → 9,456 km

Result: nearest_port=ROTTERDAM, distance=351
```

**Derived Features:**
```
Input:
  speed: 3.2 knots
  time_in_zone: 1.5 hours

Calculations:
  speed_category: SLOW (3.2 < 5)
  is_potential_fishing: TRUE (slow speed + long duration)
```

**⏱️ Time:** 2-3 days to code and test  
**✅ Output:** Enriched data in Silver layer with 8+ new fields

---

### Step 7: Build Spark Consumer - Part C (Aggregation Job) (Day 11-12)

**Objective:** Summarize data for analytics and reporting

**Why:** Users want insights, not individual records!

#### Aggregation Process

**Input:** 864,000 individual vessel positions  
**Output:** Daily statistics and summaries

#### Implementation

```scala
object AggregationJob {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("AIS Data Aggregation")
      .master("spark://localhost:7077")
      .getOrCreate()
    
    import spark.implicits._
    
    // Read from Silver layer
    val enrichedData = spark.read
      .format("iceberg")
      .load("s3://datalake/silver/vessels_enriched")
    
    // Daily statistics by vessel type
    val dailyStats = enrichedData
      .withColumn("date", to_date(col("timestamp")))
      .groupBy("date", "vessel_type")
      .agg(
        count("*").as("total_positions"),
        avg("speed").as("avg_speed"),
        max("speed").as("max_speed"),
        min("speed").as("min_speed"),
        countDistinct("mmsi").as("unique_vessels"),
        sum(when(col("is_potential_fishing"), 1).otherwise(0))
          .as("fishing_activities"),
        avg("distance_to_port").as("avg_distance_to_port")
      )
    
    // Port activity statistics
    val portStats = enrichedData
      .groupBy("nearest_port")
      .agg(
        countDistinct("mmsi").as("unique_vessels"),
        count("*").as("total_visits"),
        avg("speed").as("avg_approach_speed")
      )
    
    // Hourly traffic patterns
    val hourlyTraffic = enrichedData
      .withColumn("hour", hour(col("timestamp")))
      .groupBy("hour")
      .agg(
        count("*").as("position_count"),
        countDistinct("mmsi").as("active_vessels")
      )
    
    // Write to Gold layer
    dailyStats
      .write
      .format("iceberg")
      .mode("overwrite")
      .partitionBy("date")
      .save("s3://datalake/gold/daily_statistics")
    
    portStats
      .write
      .format("iceberg")
      .mode("overwrite")
      .save("s3://datalake/gold/port_statistics")
    
    hourlyTraffic
      .write
      .format("iceberg")
      .mode("overwrite")
      .save("s3://datalake/gold/hourly_traffic")
  }
}
```

#### Example Output

**Daily Statistics:**
```
date       | vessel_type | total_pos | avg_speed | unique_vessels | fishing_acts
2024-01-15 | Cargo       | 145,230   | 15.3      | 45             | 0
2024-01-15 | Fishing     | 89,450    | 6.2       | 28             | 1,234
2024-01-15 | Tanker      | 67,890    | 12.8      | 19             | 0
```

**Transformation:**
```
864,000 individual records
  ↓ GROUP BY date, vessel_type
  ↓ AGGREGATE metrics
  ↓
15 summary rows (5 vessel types × 3 days)
```

**⏱️ Time:** 1-2 days to code and test  
**✅ Output:** Aggregated insights in Gold layer

---

### Step 8: Build REST API (Day 13-15)

**Objective:** Create web endpoints to serve the processed data

**Why:** Make data accessible to applications and end users

#### API Architecture

```
User/App → HTTP Request → FastAPI → Redis (cache) → Iceberg → JSON Response
                                          ↓ miss
                                      PostgreSQL + MinIO
```

#### Implementation

```python
# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
from trino.dbapi import connect
from typing import List, Optional
from datetime import datetime, date

app = FastAPI(title="Maritime Data API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Trino/Iceberg connection
def get_trino_connection():
    return connect(
        host='localhost',
        port=8080,
        user='trino',
        catalog='iceberg',
        schema='silver'
    )

@app.get("/")
def read_root():
    return {
        "service": "Maritime Data API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/v1/vessels/current")
async def get_current_vessels(limit: int = 100):
    """Get current vessel positions with caching"""
    
    cache_key = f"vessels:current:{limit}"
    
    # Step 1: Check Redis cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return {
            "data": json.loads(cached_data),
            "cached": True,
            "count": len(json.loads(cached_data))
        }
    
    # Step 2: Query Iceberg if cache miss
    conn = get_trino_connection()
    cursor = conn.cursor()
    
    query = f"""
        SELECT 
            mmsi,
            vessel_name,
            latitude,
            longitude,
            speed,
            nearest_port,
            distance_to_port,
            speed_category,
            timestamp
        FROM vessels_enriched
        WHERE processing_date = CURRENT_DATE
        ORDER BY timestamp DESC
        LIMIT {limit}
    """
    
    cursor.execute(query)
    results = [
        {
            "mmsi": row[0],
            "vessel_name": row[1],
            "latitude": row[2],
            "longitude": row[3],
            "speed": row[4],
            "nearest_port": row[5],
            "distance_to_port": row[6],
            "speed_category": row[7],
            "timestamp": row[8].isoformat()
        }
        for row in cursor.fetchall()
    ]
    
    # Step 3: Cache the results
    redis_client.setex(
        cache_key,
        60,  # Expire after 60 seconds
        json.dumps(results)
    )
    
    return {
        "data": results,
        "cached": False,
        "count": len(results)
    }

@app.get("/api/v1/vessels/{mmsi}/history")
async def get_vessel_history(mmsi: str, days: int = 7):
    """Get historical positions for a specific vessel"""
    
    conn = get_trino_connection()
    cursor = conn.cursor()
    
    query = f"""
        SELECT 
            timestamp,
            latitude,
            longitude,
            speed,
            nearest_port,
            distance_to_port
        FROM vessels_enriched
        WHERE mmsi = '{mmsi}'
          AND timestamp >= CURRENT_DATE - INTERVAL '{days}' DAY
        ORDER BY timestamp DESC
    """
    
    cursor.execute(query)
    results = [
        {
            "timestamp": row[0].isoformat(),
            "latitude": row[1],
            "longitude": row[2],
            "speed": row[3],
            "nearest_port": row[4],
            "distance_to_port": row[5]
        }
        for row in cursor.fetchall()
    ]
    
    return {
        "mmsi": mmsi,
        "history": results,
        "count": len(results)
    }

@app.get("/api/v1/statistics/daily")
async def get_daily_statistics(target_date: Optional[date] = None):
    """Get daily aggregated statistics"""
    
    if not target_date:
        target_date = datetime.now().date()
    
    cache_key = f"stats:daily:{target_date}"
    
    # Check cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Query Gold layer
    conn = get_trino_connection()
    cursor = conn.cursor()
    
    query = f"""
        SELECT 
            vessel_type,
            total_positions,
            avg_speed,
            unique_vessels,
            fishing_activities
        FROM iceberg.gold.daily_statistics
        WHERE date = DATE '{target_date}'
    """
    
    cursor.execute(query)
    results = [
        {
            "vessel_type": row[0],
            "total_positions": row[1],
            "avg_speed": row[2],
            "unique_vessels": row[3],
            "fishing_activities": row[4]
        }
        for row in cursor.fetchall()
    ]
    
    # Cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(results))
    
    return {
        "date": target_date.isoformat(),
        "statistics": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Request Flow Example

```
1. User Request:
   GET http://localhost:8000/api/v1/vessels/current

2. API receives request (t=2ms)

3. Check Redis cache (t=5ms)
   ❌ Cache MISS

4. Query Iceberg via Trino (t=10ms to t=497ms)
   - Read PostgreSQL catalog
   - Fetch data from MinIO
   - Execute SQL query

5. Cache result in Redis (t=500ms)

6. Return JSON to user (t=503ms)

Next identical request:
   ✅ Cache HIT - Returns in 8ms (62x faster!)
```

#### Run the API

```bash
cd serving-api

# Install dependencies
pip install fastapi uvicorn redis trino

# Start server
uvicorn app.main:app --reload --port 8000
```

#### Test Endpoints

```bash
# Current vessels
curl http://localhost:8000/api/v1/vessels/current?limit=10

# Vessel history
curl http://localhost:8000/api/v1/vessels/367123456/history?days=7

# Daily statistics
curl http://localhost:8000/api/v1/statistics/daily
```

#### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**⏱️ Time:** 2-3 days to code and test  
**✅ Output:** Working REST API with sub-100ms response times (cached)

---

### Step 9: Deploy Everything (Day 16-18)

**Objective:** Deploy to production using Kubernetes

**Why:** Prove it works end-to-end in a production-like environment

#### Kubernetes Deployment Structure

```
k8s/
├── namespace.yaml
├── kafka/
│   ├── zookeeper-deployment.yaml
│   ├── kafka-deployment.yaml
│   └── kafka-service.yaml
├── spark/
│   ├── spark-master-deployment.yaml
│   ├── spark-worker-deployment.yaml
│   └── spark-service.yaml
├── storage/
│   ├── postgresql-deployment.yaml
│   ├── minio-deployment.yaml
│   └── redis-deployment.yaml
└── api/
    ├── api-deployment.yaml
    └── api-service.yaml
```

#### Example Deployment: API Service

```yaml
# k8s/api/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maritime-api
  namespace: maritime
spec:
  replicas: 2
  selector:
    matchLabels:
      app: maritime-api
  template:
    metadata:
      labels:
        app: maritime-api
    spec:
      containers:
      - name: api
        image: maritime-platform/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: redis-service
        - name: REDIS_PORT
          value: "6379"
        - name: ICEBERG_CATALOG_URI
          value: postgresql://postgres-service:5432/iceberg_catalog
        - name: MINIO_ENDPOINT
          value: minio-service:9000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: maritime-api-service
  namespace: maritime
spec:
  selector:
    app: maritime-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### Deployment Steps

```bash
# 1. Create namespace
kubectl create namespace maritime

# 2. Deploy storage layer
kubectl apply -f k8s/storage/

# 3. Wait for storage to be ready
kubectl wait --for=condition=ready pod -l app=postgresql -n maritime --timeout=300s
kubectl wait --for=condition=ready pod -l app=minio -n maritime --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n maritime --timeout=300s

# 4. Deploy Kafka
kubectl apply -f k8s/kafka/

# 5. Wait for Kafka
kubectl wait --for=condition=ready pod -l app=kafka -n maritime --timeout=300s

# 6. Deploy Spark
kubectl apply -f k8s/spark/

# 7. Deploy API
kubectl apply -f k8s/api/

# 8. Verify all pods are running
kubectl get pods -n maritime

# 9. Get API external IP
kubectl get service maritime-api-service -n maritime
```

#### Expected Output

```bash
$ kubectl get pods -n maritime

NAME                              READY   STATUS    RESTARTS   AGE
kafka-0                           1/1     Running   0          5m
kafka-1                           1/1     Running   0          5m
kafka-2                           1/1     Running   0          5m
spark-master-0                    1/1     Running   0          4m
spark-worker-0                    1/1     Running   0          4m
spark-worker-1                    1/1     Running   0          4m
spark-worker-2                    1/1     Running   0          4m
postgresql-0                      1/1     Running   0          6m
minio-0                           1/1     Running   0          6m
redis-0                           1/1     Running   0          6m
maritime-api-5d6f8b9c-abc12      1/1     Running   0          3m
maritime-api-5d6f8b9c-xyz89      1/1     Running   0          3m
```

#### Test Production Deployment

```bash
# Get API endpoint
EXTERNAL_IP=$(kubectl get service maritime-api-service -n maritime -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test API
curl http://$EXTERNAL_IP/api/v1/vessels/current

# Expected response:
# {
#   "data": [...],
#   "count": 100,
#   "cached": false
# }
```

#### Monitoring

```bash
# View logs
kubectl logs -f deployment/maritime-api -n maritime

# Check resource usage
kubectl top pods -n maritime

# Scale API
kubectl scale deployment maritime-api --replicas=4 -n maritime
```

**⏱️ Time:** 2-3 days to configure and deploy  
**✅ Output:** Production-ready system running on Kubernetes

---

## 📊 Complete Data Journey

### Following ONE Vessel Position Through the Entire Pipeline

#### **t=0 minutes: Data Generation**
```json
{
  "mmsi": "367123456",
  "timestamp": "2024-01-15T10:00:00",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "speed": 12.5,
  "vessel_name": "OCEAN STAR",
  "vessel_type": "Cargo"
}
```
📍 **Status:** CSV file on disk

---

#### **t=1 minute: Kafka Producer**
```scala
producer.send(topic = "ais_raw", value = json)
```
📍 **Status:** Kafka topic `ais_raw`, Partition 1, Offset 12,345

---

#### **t=1m 5s: Spark Reads**
```scala
val batch = kafka.readBatch()  // 300 records
```
📍 **Status:** Loaded into Spark memory

---

#### **t=1m 6s: Data Cleaning**
```
✅ Latitude: 48.8566 (valid)
✅ Longitude: 2.3522 (valid)
✅ Speed: 12.5 (valid)
✅ No duplicates
→ CLEAN
```
📍 **Status:** Validated in Spark

---

#### **t=1m 7s: Write to Bronze**
```
MinIO: /bronze/ais_raw/part-00123.parquet
PostgreSQL: Catalog entry created
```
📍 **Status:** Permanently stored in Bronze layer

---

#### **t=5 minutes: Enrichment**
```json
{
  ...original_fields...,
  "temperature": 18.5,
  "wind_speed": 15.2,
  "nearest_port": "ROTTERDAM",
  "distance_to_port": 351,
  "speed_category": "CRUISING",
  "is_potential_fishing": false
}
```
📍 **Status:** Enriched in Silver layer

---

#### **t=10 minutes: Aggregation**
```json
{
  "date": "2024-01-15",
  "vessel_type": "Cargo",
  "avg_speed": 13.2,  // ← Our 12.5 contributed
  "total_positions": 145230,
  "unique_vessels": 45
}
```
📍 **Status:** Aggregated in Gold layer

---

#### **t=15 minutes: API Query**
```bash
curl http://localhost:8000/api/v1/vessels/367123456/history
```

**Response (8ms):**
```json
{
  "mmsi": "367123456",
  "history": [
    {
      "timestamp": "2024-01-15T10:00:00",
      "latitude": 48.8566,
      "longitude": 2.3522,
      "speed": 12.5,
      "nearest_port": "ROTTERDAM",
      "distance_to_port": 351
    }
  ]
}
```
📍 **Status:** Delivered to end user! 🎉

---

## 🎯 Mental Model - 5 Core Rules

### Rule 1: Data Flows in One Direction

```
CSV → Kafka → Spark → Iceberg → API → User
```
☝️ Like water flowing downhill - never backwards

---

### Rule 2: Each Layer Has a Job

| Component | Role | Analogy |
|-----------|------|---------|
| **Kafka** | Transport | Delivery truck |
| **Spark** | Transform | Factory |
| **Iceberg** | Store | Warehouse |
| **Redis** | Cache | Express shelf |
| **API** | Serve | Store clerk |

---

### Rule 3: Bronze → Silver → Gold

| Layer | State | Analogy |
|-------|-------|---------|
| **Bronze** | Raw | Kitchen ingredients with dirt |
| **Silver** | Clean | Washed and prepared |
| **Gold** | Ready | Cooked dishes ready to serve |

**Key principle:** Never delete Bronze! It's your source of truth.

---

### Rule 4: Every Service Needs Its Friend

```
Kafka ←→ Zookeeper (coordination)
Spark Worker ←→ Spark Master (task distribution)
Iceberg ←→ PostgreSQL + MinIO (metadata + data)
API ←→ Redis + Iceberg (cache + storage)
```

---

### Rule 5: Always Think: "What If It Fails?"

| Failure | Impact | Recovery |
|---------|--------|----------|
| Producer crashes | ✅ Kafka keeps messages | Restart, continue from offset |
| Spark crashes | ✅ Kafka keeps messages | Restart, read from checkpoint |
| API crashes | ✅ Data in Iceberg | Restart, re-query |
| Redis crashes | ⚠️ Slower (no cache) | System works, queries Iceberg |

**Design principle:** Build for failure, not just success.

---

## 🚀 Quick Reference Cheat Sheet

### Pipeline Stages

```
1. Generate/Get Data
   ↓ Files on disk
   
2. Ingest to Kafka
   ↓ Messages in topics
   
3. Process with Spark
   ↓ Clean → Enrich → Aggregate
   
4. Store in Data Lake (Iceberg)
   ↓ Organized in Bronze/Silver/Gold
   
5. Serve via API
   ↓ Fast queries with Redis cache
   
6. Deploy to Production
   ↓ Docker/Kubernetes
```

### Essential Commands

```bash
# Start infrastructure
docker-compose up -d

# Create Kafka topic
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic ais_raw --partitions 3

# Submit Spark job
spark-submit \
  --class com.maritime.processing.DataCleaningJob \
  --master spark://localhost:7077 \
  target/scala-2.12/maritime-platform.jar

# Start API
uvicorn app.main:app --reload --port 8000

# Deploy to Kubernetes
kubectl apply -f k8s/

# Check status
kubectl get pods -n maritime
```

### Technology Quick Reference

| What | Tool | Port |
|------|------|------|
| Message Queue | Kafka | 9092 |
| Processing | Spark Master | 7077, 8080 |
| Catalog | PostgreSQL | 5432 |
| Storage | MinIO | 9000, 9001 |
| Cache | Redis | 6379 |
| API | FastAPI | 8000 |

---

## 📝 The Elevator Pitch

When someone asks **"How does your pipeline work?"**, say:

> "I built a Big Data pipeline that processes maritime vessel tracking data in real-time.
>
> **Data flows through five stages:**
> 1. **Kafka** streams 864,000 vessel positions
> 2. **Spark** processes them in three layers: Bronze (raw), Silver (enriched), Gold (aggregated)
> 3. **Iceberg** stores everything in a data lake with full history
> 4. **Redis** caches popular queries
> 5. **FastAPI** serves data with sub-100ms response times
>
> The entire system runs in **Docker** containers, can be deployed to **Kubernetes**, and handles failures gracefully with checkpointing and automatic restarts.
>
> **The result?** A production-ready platform processing streaming data at scale with enterprise-grade reliability."

---

## 🎓 Learning Path

### Week 1: Foundation
- [ ] Understand data flow concept
- [ ] Set up Docker environment
- [ ] Run data generator
- [ ] Start all services

### Week 2: Streaming
- [ ] Create Kafka topics
- [ ] Build producer
- [ ] Test message flow
- [ ] Monitor with Kafka tools

### Week 3: Processing
- [ ] Build cleaning job (Bronze)
- [ ] Build enrichment job (Silver)
- [ ] Build aggregation job (Gold)
- [ ] Understand Iceberg tables

### Week 4: Serving
- [ ] Build REST API
- [ ] Implement Redis caching
- [ ] Add monitoring
- [ ] Load testing

### Week 5: Production
- [ ] Create Kubernetes manifests
- [ ] Deploy to cluster
- [ ] Set up monitoring
- [ ] Document everything

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Apache Kafka, Spark, Iceberg communities
- Maritime AIS data standards
- Open source contributors

---

**Built with ❤️ for learning Big Data Engineering**

*Remember: The best way to learn is to build. Start small, iterate, and scale!*
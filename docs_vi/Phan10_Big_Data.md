# Phần 10: Big Data Processing (Xử lý Dữ liệu lớn)

Tài liệu này bổ sung các kiến thức về xử lý dữ liệu quy mô lớn, các thuật toán và hệ thống Big Data.

---

## 10.1. Big Data Algorithms (Thuật toán Dữ liệu lớn)

### 10.1.1. ⭐ TopK Problem (Bài toán Top K)

**Vấn đề**: Tìm K phần tử lớn nhất (hoặc nhỏ nhất) trong dataset cực lớn (không thể load hết vào memory).

**Ví dụ**: Tìm 10 sản phẩm bán chạy nhất từ 1 tỷ đơn hàng.

#### Solution 1: Min Heap (K nhỏ)

**Cơ chế:**
- Duyệt qua dataset
- Dùng **Min Heap** kích thước K
- Nếu phần tử mới > min heap → Thay thế min
- Kết quả: Heap chứa K phần tử lớn nhất

**Time Complexity**: O(n log K)
**Space Complexity**: O(K)

**Code:**
```java
public List<Integer> findTopK(int[] nums, int k) {
    PriorityQueue<Integer> minHeap = new PriorityQueue<>();
    
    for (int num : nums) {
        if (minHeap.size() < k) {
            minHeap.offer(num);
        } else if (num > minHeap.peek()) {
            minHeap.poll();
            minHeap.offer(num);
        }
    }
    
    return new ArrayList<>(minHeap);
}
```

#### Solution 2: QuickSelect (K lớn)

**Cơ chế:**
- Dùng **QuickSelect** (biến thể QuickSort)
- Partition để tìm phần tử thứ K
- **Time Complexity**: O(n) average, O(n²) worst case

#### Solution 3: Distributed (K rất lớn)

**Cơ chế:**
- Chia dataset thành nhiều chunks
- Mỗi chunk tìm Top K local
- Merge các Top K local → Top K global

---

### 10.1.2. ⭐ Massive Data Processing Problems

#### Problem 1: Tìm số không trùng lặp (Find Unique Numbers)

**Vấn đề**: Có 2.5 tỷ số nguyên, tìm các số chỉ xuất hiện 1 lần. Memory chỉ có 2GB.

**Solution: BitMap**
- Dùng **2 bits** để đếm: 00 (0 lần), 01 (1 lần), 10 (2+ lần)
- 2.5 tỷ số × 2 bits = 5 tỷ bits ≈ **625 MB** ✅

**Code:**
```java
public class BitMapCounter {
    private byte[] bitmap;  // 2 bits per number
    
    public void add(int num) {
        int index = num / 4;
        int offset = (num % 4) * 2;
        int count = (bitmap[index] >> offset) & 0x03;
        
        if (count < 2) {
            count++;
            bitmap[index] = (byte) ((bitmap[index] & ~(0x03 << offset)) | (count << offset));
        }
    }
    
    public boolean isUnique(int num) {
        int index = num / 4;
        int offset = (num % 4) * 2;
        int count = (bitmap[index] >> offset) & 0x03;
        return count == 1;
    }
}
```

#### Problem 2: Tìm Median (Trung vị)

**Vấn đề**: Tìm median của 10 tỷ số. Memory: 1GB.

**Solution: Bucket + Counting**
1. Chia range thành buckets (ví dụ: 0-999, 1000-1999, ...)
2. Đếm số lượng trong mỗi bucket
3. Tìm bucket chứa median
4. Sort bucket đó → Tìm median

**Alternative: Distributed**
- Chia data thành N machines
- Mỗi machine tìm median local
- Merge medians → Global median

#### Problem 3: Tìm Top IP Addresses

**Vấn đề**: Có 10 tỷ log entries, mỗi entry có IP. Tìm 100 IP xuất hiện nhiều nhất.

**Solution: Hash + Min Heap**
1. **Hash IP → Hash value** (giảm memory)
2. **Count frequency** (HashMap)
3. **Min Heap** kích thước 100 để giữ Top 100

**Distributed Solution:**
1. Hash IP → Route đến N machines
2. Mỗi machine đếm frequency local
3. Merge Top 100 từ mỗi machine → Global Top 100

#### Problem 4: Tìm Hot Queries (Truy vấn nóng)

**Vấn đề**: Tìm 10 từ khóa tìm kiếm phổ biến nhất từ 1 tỷ queries. Memory: 100MB.

**Solution: Hash + Heap (giống Top IP)**

**Optimization:**
- Dùng **Trie** để compress queries (nếu queries có prefix chung)
- **Sampling**: Chỉ xử lý 10% data (statistical approach)

#### Problem 5: Tìm Common URLs

**Vấn đề**: Có 2 files, mỗi file chứa 10 tỷ URLs. Tìm URLs xuất hiện trong cả 2 files.

**Solution: Hash + Partition**
1. Hash URL → Route đến N partitions
2. URLs cùng hash → cùng partition
3. Tìm intersection trong mỗi partition
4. Union kết quả

**Memory-efficient:**
- Chỉ load 1 partition vào memory mỗi lần
- Process từng partition

---

## 10.2. Big Data Systems (Hệ thống Dữ liệu lớn)

### 10.2.1. ⭐ Hadoop Ecosystem

**Hadoop** là framework xử lý Big Data phân tán.

**Core Components:**

**1. HDFS (Hadoop Distributed File System)**
- **Distributed storage**: Chia file thành blocks, replicate 3 lần
- **Fault tolerance**: Node chết → Dùng replica
- **Scalability**: Thêm nodes để tăng capacity

**Architecture:**
- **NameNode**: Quản lý metadata (file → blocks mapping)
- **DataNode**: Lưu trữ data blocks

**2. MapReduce**
- **Programming model** để xử lý data song song
- **Map**: Transform data (key-value pairs)
- **Reduce**: Aggregate results

**Example: Word Count**
```java
// Map: (line) → (word, 1)
public void map(String line, Context context) {
    String[] words = line.split(" ");
    for (String word : words) {
        context.write(word, 1);
    }
}

// Reduce: (word, [1,1,1,...]) → (word, count)
public void reduce(String word, Iterable<Integer> values, Context context) {
    int sum = 0;
    for (int value : values) {
        sum += value;
    }
    context.write(word, sum);
}
```

**3. YARN (Yet Another Resource Negotiator)**
- **Resource Manager**: Quản lý cluster resources
- **Node Manager**: Quản lý resources trên mỗi node
- **Application Master**: Quản lý từng application

**Hadoop Limitations:**
- ❌ **Batch processing only** (không real-time)
- ❌ **Disk I/O** (chậm hơn Spark in-memory)
- ❌ **Complex programming model**

### 10.2.2. ⭐ Apache Spark

**Spark** là engine xử lý Big Data **in-memory**, nhanh hơn Hadoop 10-100 lần.

**Key Features:**
- **In-Memory Computing**: Cache data trong RAM
- **Unified Engine**: Batch, Streaming, ML, Graph processing
- **Lazy Evaluation**: Chỉ execute khi cần (optimization)

**Core Concepts:**

**1. RDD (Resilient Distributed Dataset)**
- **Immutable** distributed collection
- **Fault-tolerant**: Tự động recover khi node chết

**2. DataFrame / Dataset**
- **Structured data** với schema
- **Optimization**: Catalyst optimizer, Tungsten execution engine

**3. Spark Operations:**
- **Transformations**: `map`, `filter`, `join` (lazy)
- **Actions**: `count`, `collect`, `save` (trigger execution)

**Example:**
```scala
val df = spark.read.json("hdfs://data/users.json")
val result = df
  .filter($"age" > 18)
  .groupBy($"city")
  .agg(count("*").as("count"))
  .orderBy($"count".desc)

result.show()
```

**Spark vs Hadoop:**

| Tiêu chí | Hadoop MapReduce | Spark |
|----------|------------------|-------|
| **Processing** | Batch only | Batch + Streaming |
| **Speed** | Chậm (Disk I/O) | Nhanh (Memory) |
| **Fault Tolerance** | Recompute | RDD lineage |
| **Memory** | Ít | Nhiều (caching) |
| **Use Case** | Historical data analysis | Real-time + Batch |

### 10.2.3. ⭐ Kafka (Stream Processing)

**Kafka** là **distributed streaming platform**.

**Use Cases:**
1. **Message Queue**: Decouple producers và consumers
2. **Event Streaming**: Real-time event processing
3. **Log Aggregation**: Collect logs từ nhiều services

**Core Concepts:**

**1. Topics & Partitions**
- **Topic**: Category/feed name
- **Partition**: Topic được chia thành partitions (parallelism)
- **Replication**: Mỗi partition có N replicas (fault tolerance)

**2. Producers & Consumers**
- **Producer**: Gửi messages vào topic
- **Consumer**: Đọc messages từ topic
- **Consumer Group**: Nhiều consumers cùng group → Load balancing

**3. Kafka Streams**
- **Stream processing** library
- Process data in real-time
- **Windowing**: Tumbling, Hopping, Sliding windows

**Example:**
```java
StreamsBuilder builder = new StreamsBuilder();
KStream<String, String> source = builder.stream("input-topic");

source
    .filter((key, value) -> value.length() > 10)
    .mapValues(value -> value.toUpperCase())
    .to("output-topic");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

### 10.2.4. ⭐ Flink (Real-time Stream Processing)

**Apache Flink** là **stream processing engine** mạnh mẽ.

**Key Features:**
- **True Streaming**: Process data as it arrives (không cần micro-batches)
- **Low Latency**: Sub-second latency
- **Exactly-Once Semantics**: Đảm bảo mỗi message xử lý đúng 1 lần
- **State Management**: Maintain state cho complex operations

**Flink vs Spark Streaming:**

| Tiêu chí | Spark Streaming | Flink |
|----------|----------------|-------|
| **Model** | Micro-batch | True streaming |
| **Latency** | Seconds | Milliseconds |
| **State** | Limited | Rich state API |
| **Exactly-Once** | Complex | Built-in |
| **Use Case** | Near real-time | Real-time critical |

**Flink Example:**
```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

DataStream<Event> events = env.addSource(new KafkaSource<>("topic"));

events
    .keyBy(Event::getUserId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new CountAggregateFunction())
    .addSink(new KafkaSink<>("output-topic"));

env.execute("Event Processing");
```

---

## 10.3. Data Processing Patterns (Mẫu xử lý dữ liệu)

### 10.3.1. Lambda Architecture

**Lambda Architecture** kết hợp **batch processing** và **stream processing**.

**3 Layers:**

1. **Batch Layer** (Hadoop/Spark)
   - Xử lý toàn bộ historical data
   - **Accuracy**: 100% accurate
   - **Latency**: Cao (vài giờ)

2. **Speed Layer** (Kafka Streams/Flink)
   - Xử lý real-time data
   - **Latency**: Thấp (vài giây)
   - **Accuracy**: Có thể có lỗi nhỏ

3. **Serving Layer**
   - Merge batch view + real-time view
   - Serve queries

**Example:**
- **Batch**: Tính tổng doanh thu hôm qua (chính xác 100%)
- **Speed**: Tính tổng doanh thu hôm nay (real-time, có thể thiếu vài transactions)
- **Query**: Batch + Speed = Tổng doanh thu

**Limitations:**
- ❌ **Complexity**: Phải maintain 2 systems
- ❌ **Code duplication**: Logic phải viết 2 lần (batch + stream)

### 10.3.2. Kappa Architecture

**Kappa Architecture** chỉ dùng **stream processing** cho cả batch và real-time.

**Cơ chế:**
- **Single stream processing system** (Kafka + Flink)
- **Replay**: Để tính lại historical data, replay từ đầu stream

**Ưu điểm:**
- ✅ **Simplicity**: Chỉ 1 system
- ✅ **Code reuse**: Logic chỉ viết 1 lần

**Nhược điểm:**
- ❌ **Storage**: Cần lưu toàn bộ stream (tốn storage)
- ❌ **Replay cost**: Replay toàn bộ stream tốn thời gian

---

## 10.4. Search Engines (Công cụ Tìm kiếm)

### 10.4.1. Elasticsearch (Đã có trong Part 3)

Xem lại **Phần 3.5: Elasticsearch** trong `Phan3_Database_Storage.md`.

**Tóm tắt:**
- **Inverted Index**: Term → Documents mapping
- **Full-text search**: Relevance scoring (BM25)
- **Distributed**: Sharding, Replication
- **Real-time**: Near real-time indexing

### 10.4.2. Solr vs Elasticsearch

| Tiêu chí | Solr | Elasticsearch |
|----------|------|---------------|
| **Maturity** | Lâu đời hơn | Trẻ hơn, phát triển nhanh |
| **API** | XML/JSON | JSON only |
| **Use Case** | Enterprise search | Log analytics, APM |
| **Community** | Smaller | Larger (Elastic company) |

---

## Tổng kết Phần 10: Big Data

Đã hoàn thành **Phần 10: Big Data Processing** với nội dung thực tế:

✅ **10.1. Big Data Algorithms**:
- **TopK Problem**: Min Heap, QuickSelect, Distributed
- **Massive Data Problems**: Unique numbers (BitMap), Median, Top IP, Hot queries, Common URLs

✅ **10.2. Big Data Systems**:
- **Hadoop**: HDFS, MapReduce, YARN
- **Spark**: In-memory computing, RDD, DataFrame
- **Kafka**: Stream processing, Topics, Partitions
- **Flink**: True streaming, Low latency

✅ **10.3. Data Processing Patterns**:
- **Lambda Architecture**: Batch + Speed layers
- **Kappa Architecture**: Stream-only

✅ **10.4. Search Engines**: Elasticsearch overview (chi tiết ở Part 3)

**Tổng cộng: ~500 lines** kiến thức Big Data algorithms và systems!

---

*Kết thúc Phần 10 - Big Data Processing*

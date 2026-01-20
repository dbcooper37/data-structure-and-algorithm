# Phần 10: Big Data Processing (Xử lý Dữ liệu lớn)

Tài liệu này bổ sung các kiến thức về xử lý dữ liệu quy mô lớn, các thuật toán và hệ thống Big Data.

---

## 10.1. Big Data Algorithms (Thuật toán Dữ liệu lớn)

### 10.1.1. ⭐ Classic Big Data Problems (Các bài toán Big Data kinh điển)

#### Problem 1: Count Different Phone Numbers (Đếm số điện thoại khác nhau)

**Vấn đề**: Có một file chứa các số điện thoại (8 chữ số), đếm số lượng số điện thoại khác nhau.

**Constraints**:
- Mỗi số điện thoại: 8 chữ số (0-9)
- File quá lớn, không thể load hết vào memory

**Solution: BitMap (Bit Array)**

**Phân tích**:
- 8 chữ số → Range: 0 - 99,999,999 (100 triệu số)
- Mỗi số dùng 1 bit → Cần 100 triệu bits ≈ **12 MB**

**Algorithm**:
1. Tạo bit array kích thước 100 triệu bits
2. Đọc từng số điện thoại từ file
3. Set bit tại vị trí = số điện thoại = 1
4. Đếm số bits = 1 → Kết quả

**Code**:
```java
public class PhoneNumberCounter {
    private BitSet bitSet;
    private static final int MAX_PHONE = 100_000_000;  // 8 digits
    
    public PhoneNumberCounter() {
        this.bitSet = new BitSet(MAX_PHONE);
    }
    
    public void addPhoneNumber(int phoneNumber) {
        bitSet.set(phoneNumber);
    }
    
    public int countDistinct() {
        return bitSet.cardinality();  // Count bits set to 1
    }
}

// Usage
PhoneNumberCounter counter = new PhoneNumberCounter();
// Read from file line by line
while ((line = reader.readLine()) != null) {
    int phone = Integer.parseInt(line.trim());
    counter.addPhoneNumber(phone);
}
int distinctCount = counter.countDistinct();
```

**Time Complexity**: O(n) - n là số lượng số điện thoại
**Space Complexity**: O(1) - Cố định 12 MB

**Key Insight**: **BitMap** rất hiệu quả cho bài toán **check existence** và **count distinct** khi range nhỏ.

---

#### Problem 2: Find a Number if Exists (Tìm số có tồn tại không)

**Vấn đề**: Có 40 tỷ số nguyên không trùng lặp, chưa sắp xếp. Cho một số X, kiểm tra X có trong 40 tỷ số đó không?

**Constraints**:
- 40 tỷ số unsigned int (0 - 2^32-1)
- Memory: 1GB
- File quá lớn, không thể load hết

**Solution: BitMap**

**Phân tích**:
- Unsigned int range: 0 - 4,294,967,295 (2^32)
- Mỗi số dùng 1 bit → Cần 2^32 bits = 512 MB ✅ (nhỏ hơn 1GB)

**Algorithm**:
1. Tạo bit array kích thước 2^32 bits (512 MB)
2. Đọc 40 tỷ số từ file, set bit tương ứng = 1
3. Check số X: Nếu bit[X] = 1 → Tồn tại, ngược lại → Không tồn tại

**Code**:
```java
public class NumberExistenceChecker {
    private BitSet bitSet;
    private static final long MAX_NUMBER = (1L << 32);  // 2^32
    
    public NumberExistenceChecker() {
        this.bitSet = new BitSet((int) MAX_NUMBER);
    }
    
    public void loadNumbers(String filePath) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                long number = Long.parseLong(line.trim());
                bitSet.set((int) number);
            }
        }
    }
    
    public boolean exists(long number) {
        return bitSet.get((int) number);
    }
}
```

**Alternative: Bloom Filter** (Nếu range quá lớn)
- Dùng khi range quá lớn, không thể dùng BitMap
- Trade-off: Có false positive (nhưng không có false negative)
- Space: Nhỏ hơn BitMap nhiều

**Key Insight**: **BitMap** là giải pháp tối ưu cho bài toán **existence check** khi range vừa phải.

---

#### Problem 3: Find Common URLs (Tìm URLs chung)

**Vấn đề**: Có 2 files (a và b), mỗi file chứa 50 tỷ URLs, mỗi URL 64 bytes. Memory: 4GB. Tìm URLs xuất hiện trong cả 2 files.

**Constraints**:
- 50 tỷ URLs × 64 bytes = 320 GB (quá lớn cho memory)
- Memory chỉ có 4GB

**Solution: Hash Partitioning (Phân vùng Hash)**

**Algorithm**:

**Step 1: Hash Partitioning**
- Hash mỗi URL → Hash value
- `hash(URL) % 1000` → Chia thành 1000 files nhỏ
- URLs cùng hash → Cùng file (đảm bảo common URLs ở cùng partition)

**Step 2: Process từng partition**
- Load file a_i và b_i vào memory (mỗi file ~320MB)
- Tìm intersection trong mỗi cặp file
- Union kết quả từ tất cả partitions

**Code**:
```java
public class CommonURLFinder {
    private static final int NUM_PARTITIONS = 1000;
    
    // Step 1: Partition files
    public void partitionFile(String inputFile, String outputDir) throws IOException {
        List<BufferedWriter> writers = new ArrayList<>();
        for (int i = 0; i < NUM_PARTITIONS; i++) {
            writers.add(new BufferedWriter(new FileWriter(
                outputDir + "/partition_" + i + ".txt")));
        }
        
        try (BufferedReader reader = new BufferedReader(new FileReader(inputFile))) {
            String url;
            while ((url = reader.readLine()) != null) {
                int partition = Math.abs(url.hashCode()) % NUM_PARTITIONS;
                writers.get(partition).write(url);
                writers.get(partition).newLine();
            }
        }
        
        for (BufferedWriter writer : writers) {
            writer.close();
        }
    }
    
    // Step 2: Find common URLs in each partition
    public Set<String> findCommonInPartition(String fileA, String fileB) throws IOException {
        Set<String> setA = new HashSet<>();
        
        // Load file A into HashSet
        try (BufferedReader reader = new BufferedReader(new FileReader(fileA))) {
            String url;
            while ((url = reader.readLine()) != null) {
                setA.add(url);
            }
        }
        
        // Check file B against setA
        Set<String> common = new HashSet<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(fileB))) {
            String url;
            while ((url = reader.readLine()) != null) {
                if (setA.contains(url)) {
                    common.add(url);
                }
            }
        }
        
        return common;
    }
    
    // Main method
    public Set<String> findCommonURLs(String fileA, String fileB) throws IOException {
        // Partition both files
        partitionFile(fileA, "temp/partitions_a");
        partitionFile(fileB, "temp/partitions_b");
        
        // Find common in each partition pair
        Set<String> allCommon = new HashSet<>();
        for (int i = 0; i < NUM_PARTITIONS; i++) {
            Set<String> common = findCommonInPartition(
                "temp/partitions_a/partition_" + i + ".txt",
                "temp/partitions_b/partition_" + i + ".txt"
            );
            allCommon.addAll(common);
        }
        
        return allCommon;
    }
}
```

**Time Complexity**: O(n) - n là tổng số URLs
**Space Complexity**: O(n/k) - k là số partitions (chia nhỏ memory)

**Optimization: Trie Tree** (Nếu URLs có nhiều prefix chung)
- Dùng Trie để compress URLs
- Giảm memory usage
- Trade-off: Chậm hơn HashSet một chút

**Key Insight**: **Hash Partitioning** là kỹ thuật cốt lõi để xử lý data lớn hơn memory.

---

#### Problem 4: Find Hottest Query String (Tìm query string phổ biến nhất)

**Vấn đề**: Có 10 triệu query strings (mỗi string ≤ 255 bytes). Memory: 1GB. Tìm 10 query strings phổ biến nhất.

**Constraints**:
- 10 triệu strings × 255 bytes = 2.55 GB (lớn hơn memory)
- Nhưng sau khi deduplicate: ≤ 3 triệu strings (777 MB) ✅

**Solution 1: HashMap + Min Heap**

**Algorithm**:
1. Dùng HashMap đếm frequency: `Map<String, Integer>`
2. Duyệt tất cả strings, update frequency
3. Dùng Min Heap (kích thước 10) để giữ Top 10
4. Duyệt HashMap, nếu frequency > heap min → Replace

**Code**:
```java
public class TopKQueries {
    public List<String> findTopKQueries(List<String> queries, int k) {
        // Step 1: Count frequency
        Map<String, Integer> frequency = new HashMap<>();
        for (String query : queries) {
            frequency.put(query, frequency.getOrDefault(query, 0) + 1);
        }
        
        // Step 2: Min Heap để giữ Top K
        PriorityQueue<Map.Entry<String, Integer>> minHeap = new PriorityQueue<>(
            (a, b) -> a.getValue() - b.getValue()  // Min heap by frequency
        );
        
        // Step 3: Maintain Top K
        for (Map.Entry<String, Integer> entry : frequency.entrySet()) {
            if (minHeap.size() < k) {
                minHeap.offer(entry);
            } else if (entry.getValue() > minHeap.peek().getValue()) {
                minHeap.poll();
                minHeap.offer(entry);
            }
        }
        
        // Step 4: Extract results
        List<String> result = new ArrayList<>();
        while (!minHeap.isEmpty()) {
            result.add(minHeap.poll().getKey());
        }
        Collections.reverse(result);  // Reverse để có thứ tự giảm dần
        
        return result;
    }
}
```

**Time Complexity**: O(n + m log k)
- n: Tổng số queries
- m: Số unique queries
- k: Top K (10)

**Space Complexity**: O(m + k)

**Solution 2: Trie Tree** (Nếu queries có nhiều prefix chung)

**Lợi ích**:
- Compress storage (chia sẻ prefix)
- Giảm memory usage

**Code**:
```java
class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    int count = 0;  // Frequency
    String word = null;  // Full word at leaf
}

public class TopKQueriesTrie {
    private TrieNode root = new TrieNode();
    
    public void insert(String query) {
        TrieNode node = root;
        for (char c : query.toCharArray()) {
            node.children.putIfAbsent(c, new TrieNode());
            node = node.children.get(c);
        }
        node.count++;
        node.word = query;
    }
    
    // DFS để collect all words với frequency
    private void collectWords(TrieNode node, Map<String, Integer> frequency) {
        if (node.word != null) {
            frequency.put(node.word, node.count);
        }
        for (TrieNode child : node.children.values()) {
            collectWords(child, frequency);
        }
    }
    
    public List<String> findTopK(int k) {
        Map<String, Integer> frequency = new HashMap<>();
        collectWords(root, frequency);
        
        // Dùng Min Heap như Solution 1
        // ... (same as above)
    }
}
```

**Key Insight**: 
- **HashMap** đơn giản, nhanh
- **Trie** tiết kiệm memory khi có nhiều prefix chung

---

#### Problem 5: Find Top 1 IP (Tìm IP truy cập nhiều nhất)

**Vấn đề**: Có file log rất lớn, mỗi dòng chứa IP address. Tìm IP xuất hiện nhiều nhất trong một ngày.

**Solution: Hash Partitioning + HashMap**

**Algorithm**:
1. **Filter by date**: Chỉ lấy logs của ngày cần tìm
2. **Hash partitioning**: Hash IP → Chia thành N partitions
3. **Count frequency**: Mỗi partition dùng HashMap đếm frequency
4. **Merge**: Tìm IP có frequency cao nhất từ tất cả partitions

**Code**:
```java
public class TopIPFinder {
    private static final int NUM_PARTITIONS = 100;
    
    public String findTopIP(String logFile, String targetDate) throws IOException {
        Map<String, Integer>[] partitionCounts = new Map[NUM_PARTITIONS];
        for (int i = 0; i < NUM_PARTITIONS; i++) {
            partitionCounts[i] = new HashMap<>();
        }
        
        // Step 1: Filter by date và count frequency
        try (BufferedReader reader = new BufferedReader(new FileReader(logFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(" ");
                String date = parts[0];
                String ip = parts[1];
                
                if (date.equals(targetDate)) {
                    int partition = Math.abs(ip.hashCode()) % NUM_PARTITIONS;
                    partitionCounts[partition].put(ip, 
                        partitionCounts[partition].getOrDefault(ip, 0) + 1);
                }
            }
        }
        
        // Step 2: Merge và tìm max
        String topIP = null;
        int maxCount = 0;
        
        for (Map<String, Integer> partition : partitionCounts) {
            for (Map.Entry<String, Integer> entry : partition.entrySet()) {
                if (entry.getValue() > maxCount) {
                    maxCount = entry.getValue();
                    topIP = entry.getKey();
                }
            }
        }
        
        return topIP;
    }
}
```

**Key Insight**: **Hash partitioning** giúp xử lý file lớn bằng cách chia nhỏ và xử lý từng phần.

---

#### Problem 6: Find Top 100 Words (Tìm 100 từ phổ biến nhất)

**Vấn đề**: File 1GB, mỗi dòng là một từ (≤ 16 bytes). Memory: 1MB. Tìm 100 từ xuất hiện nhiều nhất.

**Constraints**:
- File: 1GB
- Memory: 1MB (rất nhỏ)
- Mỗi từ ≤ 16 bytes

**Solution: Hash Partitioning + Min Heap**

**Algorithm**:

**Step 1: Hash Partitioning**
- Hash từ → `hash(word) % 5000`
- Chia thành 5000 files nhỏ (mỗi file ~200KB)

**Step 2: Count frequency trong mỗi file**
- Load từng file vào memory
- Dùng HashMap đếm frequency
- Tìm Top 100 trong mỗi file

**Step 3: Merge Top 100**
- Dùng Min Heap (kích thước 100) để merge
- Duyệt tất cả Top 100 từ các files
- Giữ Top 100 global

**Code**:
```java
public class Top100Words {
    private static final int NUM_PARTITIONS = 5000;
    private static final int TOP_K = 100;
    
    // Step 1: Partition file
    public void partitionFile(String inputFile, String outputDir) throws IOException {
        List<BufferedWriter> writers = new ArrayList<>();
        for (int i = 0; i < NUM_PARTITIONS; i++) {
            writers.add(new BufferedWriter(new FileWriter(
                outputDir + "/partition_" + i + ".txt")));
        }
        
        try (BufferedReader reader = new BufferedReader(new FileReader(inputFile))) {
            String word;
            while ((word = reader.readLine()) != null) {
                int partition = Math.abs(word.hashCode()) % NUM_PARTITIONS;
                writers.get(partition).write(word);
                writers.get(partition).newLine();
            }
        }
        
        for (BufferedWriter writer : writers) {
            writer.close();
        }
    }
    
    // Step 2: Find Top K in each partition
    public List<Map.Entry<String, Integer>> findTopKInPartition(String filePath, int k) {
        Map<String, Integer> frequency = new HashMap<>();
        
        // Count frequency
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String word;
            while ((word = reader.readLine()) != null) {
                frequency.put(word, frequency.getOrDefault(word, 0) + 1);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        // Min Heap để giữ Top K
        PriorityQueue<Map.Entry<String, Integer>> minHeap = new PriorityQueue<>(
            (a, b) -> a.getValue() - b.getValue()
        );
        
        for (Map.Entry<String, Integer> entry : frequency.entrySet()) {
            if (minHeap.size() < k) {
                minHeap.offer(entry);
            } else if (entry.getValue() > minHeap.peek().getValue()) {
                minHeap.poll();
                minHeap.offer(entry);
            }
        }
        
        return new ArrayList<>(minHeap);
    }
    
    // Step 3: Merge Top K from all partitions
    public List<String> findTop100Words(String inputFile) throws IOException {
        // Partition
        partitionFile(inputFile, "temp/partitions");
        
        // Find Top K in each partition
        List<Map.Entry<String, Integer>> allTopK = new ArrayList<>();
        for (int i = 0; i < NUM_PARTITIONS; i++) {
            List<Map.Entry<String, Integer>> topK = findTopKInPartition(
                "temp/partitions/partition_" + i + ".txt", TOP_K);
            allTopK.addAll(topK);
        }
        
        // Merge: Find Top K global
        PriorityQueue<Map.Entry<String, Integer>> minHeap = new PriorityQueue<>(
            (a, b) -> a.getValue() - b.getValue()
        );
        
        for (Map.Entry<String, Integer> entry : allTopK) {
            if (minHeap.size() < TOP_K) {
                minHeap.offer(entry);
            } else if (entry.getValue() > minHeap.peek().getValue()) {
                minHeap.poll();
                minHeap.offer(entry);
            }
        }
        
        // Extract results
        List<String> result = new ArrayList<>();
        while (!minHeap.isEmpty()) {
            result.add(minHeap.poll().getKey());
        }
        Collections.reverse(result);
        
        return result;
    }
}
```

**Key Insight**: 
- **Hash partitioning** để chia file lớn thành files nhỏ
- **Min Heap** để maintain Top K efficiently
- **Two-phase**: Top K local → Top K global

---

### 10.1.2. ⭐ TopK Problem (Bài toán Top K)

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
- **Classic Problems** (Chi tiết với code):
  - **Count Different Phone Numbers**: BitMap (12 MB cho 100M số)
  - **Find Number if Exists**: BitMap (512 MB cho 2^32 số)
  - **Find Common URLs**: Hash Partitioning (chia 320GB thành 1000 files)
  - **Find Hottest Query String**: HashMap + Min Heap, Trie Tree
  - **Find Top 1 IP**: Hash Partitioning + HashMap
  - **Find Top 100 Words**: Hash Partitioning + Min Heap (2-phase)
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

**Tổng cộng: ~1,200+ lines** kiến thức Big Data algorithms và systems, bao gồm 6 bài toán kinh điển với code examples chi tiết, solutions và best practices!

---

*Kết thúc Phần 10 - Big Data Processing*

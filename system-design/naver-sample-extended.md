# Advanced System Design Solutions (11-20) - NAVER Interview

> Comprehensive system design solutions for NAVER interview preparation  
> Covering 10 essential large-scale systems

## Table of Contents

1. [Q11: Autocomplete System](#11-design-an-autocomplete-system-naver-search-suggestions)
2. [Q12: Payment Processing](#12-design-a-payment-processing-system-naver-pay)
3. [Q13: Distributed Cache](#13-design-a-distributed-cache-system)
4. [Q14: Rate Limiter](#14-design-a-rate-limiter-for-apis)
5. [Q15: Video Transcoding](#15-design-a-video-transcoding-system)
6. [Q16: Collaborative Editing](#16-design-a-collaborative-editing-system)
7. [Q17: Commenting System](#17-design-a-commenting-and-review-system-webtoon-comments--naver-shopping-reviews)
8. [Q18: Location-Based Service](#18-design-a-location-based-service-naver-maps)
9. [Q19: Ad Serving](#19-design-an-ad-serving-system-naver-ads)
10. [Q20: ML Model Serving](#20-design-a-machine-learning-model-serving-system-naver-ai-recs)

---

## 11. Design an Autocomplete System (NAVER Search Suggestions)

### Requirements
- 1 tỷ queries/ngày
- Personalized suggestions based on user history
- Trending terms support
- Sub-100ms latency
- Multilingual input (Korean, English, etc.)

### High-Level Architecture

```
[User Input]
      ↓
[CDN Edge Cache]
      ↓
[API Gateway + Load Balancer]
      ↓
[Autocomplete Service Cluster]
      ↓
   ┌──┴────────┬────────┐
   ↓           ↓        ↓
[Trie Cache] [Trending] [Personalization]
(Redis)      Service    Service (ML)
   ↓           ↓        ↓
[Persistent DB (MySQL)]
   ↓
[Query Analytics (Kafka)]
```

### Core Components

**1. Data Structures - Trie (Prefix Tree)**

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.frequency = 0
        self.suggestions = []  # Top 10 suggestions cached at node
        
class AutocompleteTrie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word, frequency):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end_of_word = True
        node.frequency = frequency
        
        # Update suggestions cache at each node
        self._update_suggestions_cache(word)
    
    def search_prefix(self, prefix, limit=10):
        node = self.root
        
        # Navigate to prefix node
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Return cached suggestions at this node
        if node.suggestions:
            return node.suggestions[:limit]
        
        # Otherwise, DFS to collect suggestions
        return self._collect_suggestions(node, prefix, limit)
    
    def _collect_suggestions(self, node, prefix, limit):
        suggestions = []
        
        if node.is_end_of_word:
            suggestions.append((prefix, node.frequency))
        
        # DFS through children
        for char, child_node in node.children.items():
            suggestions.extend(
                self._collect_suggestions(child_node, prefix + char, limit)
            )
        
        # Sort by frequency and return top N
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [word for word, freq in suggestions[:limit]]
    
    def _update_suggestions_cache(self, word):
        # Cache top suggestions at each prefix node
        node = self.root
        for i in range(len(word)):
            prefix = word[:i+1]
            char = word[i].lower()
            
            if char in node.children:
                node = node.children[char]
                # Recalculate top suggestions for this node
                node.suggestions = self._collect_suggestions(node, prefix, 10)
```

**2. Autocomplete Service Implementation**

```python
from flask import Flask, request, jsonify
import redis
import json

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    prefix = request.args.get('q', '').strip()
    user_id = request.args.get('user_id')
    language = request.args.get('lang', 'ko')
    
    if len(prefix) < 2:
        return jsonify([])
    
    # 1. Check cache
    cache_key = f"autocomplete:{language}:{prefix}"
    cached = redis_client.get(cache_key)
    
    if cached:
        suggestions = json.loads(cached)
        return jsonify(suggestions)
    
    # 2. Get base suggestions from trie
    base_suggestions = get_trie_suggestions(prefix, language)
    
    # 3. Mix with trending
    trending = get_trending_suggestions(prefix, language)
    
    # 4. Add personalized if user logged in
    if user_id:
        personalized = get_personalized_suggestions(user_id, prefix)
        base_suggestions = merge_suggestions(base_suggestions, personalized, trending)
    else:
        base_suggestions = merge_suggestions(base_suggestions, trending)
    
    # 5. Cache result
    redis_client.setex(cache_key, 300, json.dumps(base_suggestions))  # 5 min TTL
    
    # 6. Log query for analytics
    log_query(user_id, prefix, language)
    
    return jsonify(base_suggestions)

def get_trie_suggestions(prefix, language):
    # Query from Redis trie or fallback to DB
    trie_key = f"trie:{language}"
    
    # In production, trie is loaded in memory
    # For demo, query from sorted set
    suggestions = redis_client.zrevrangebyscore(
        f"suggestions:{language}:{prefix}",
        '+inf', '-inf',
        start=0, num=10,
        withscores=False
    )
    
    return suggestions

def get_trending_suggestions(prefix, language):
    # Get trending queries from last 24 hours
    trending_key = f"trending:{language}:{get_current_hour()}"
    
    trending = redis_client.zrevrange(trending_key, 0, 9, withscores=True)
    
    # Filter by prefix
    filtered = [
        query for query, score in trending 
        if query.lower().startswith(prefix.lower())
    ]
    
    return filtered[:3]

def get_personalized_suggestions(user_id, prefix):
    # Get user's search history
    history_key = f"user_history:{user_id}"
    
    history = redis_client.zrevrange(history_key, 0, 99)
    
    # Filter by prefix
    matches = [
        query for query in history 
        if query.lower().startswith(prefix.lower())
    ]
    
    return matches[:3]

def merge_suggestions(base, personalized=None, trending=None):
    # Merge with weights
    result = []
    
    # Add personalized first (higher priority)
    if personalized:
        result.extend(personalized[:2])
    
    # Add base suggestions
    result.extend(base[:7])
    
    # Add trending
    if trending:
        result.extend(trending[:1])
    
    # Deduplicate while preserving order
    seen = set()
    unique_result = []
    for item in result:
        if item not in seen:
            seen.add(item)
            unique_result.append(item)
    
    return unique_result[:10]

def log_query(user_id, query, language):
    # Async log to Kafka for analytics
    event = {
        'user_id': user_id,
        'query': query,
        'language': language,
        'timestamp': time.time()
    }
    
    # In production: kafka_producer.send('autocomplete_queries', event)
    pass
```

**3. Trending Calculation (Streaming)**

```python
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

def calculate_trending_queries(spark_context):
    ssc = StreamingContext(spark_context, 60)  # 60 second batches
    
    # Consume from Kafka
    kafka_stream = KafkaUtils.createStream(
        ssc,
        'zookeeper:2181',
        'trending-consumer-group',
        {'autocomplete_queries': 1}
    )
    
    # Extract queries
    queries = kafka_stream.map(lambda x: json.loads(x[1]))
    
    # Count queries per language per window
    query_counts = queries \
        .map(lambda x: ((x['language'], x['query']), 1)) \
        .reduceByKey(lambda a, b: a + b) \
        .transform(lambda rdd: rdd.sortBy(lambda x: x[1], ascending=False))
    
    # Update Redis with trending
    def update_trending(rdd):
        for (language, query), count in rdd.take(100):
            redis_client.zadd(
                f"trending:{language}:{get_current_hour()}",
                {query: count}
            )
            # Set expiry
            redis_client.expire(f"trending:{language}:{get_current_hour()}", 7200)
    
    query_counts.foreachRDD(update_trending)
    
    ssc.start()
    ssc.awaitTermination()
```

**4. Multilingual Support**

```python
import unicodedata

def normalize_text(text, language):
    # Unicode normalization
    text = unicodedata.normalize('NFKC', text)
    
    # Language-specific processing
    if language == 'ko':
        # Korean: Separate Hangul into components
        return decompose_hangul(text)
    elif language == 'ja':
        # Japanese: Handle Hiragana/Katakana
        return normalize_japanese(text)
    else:
        return text.lower()

def decompose_hangul(text):
    # Decompose Korean syllables for better matching
    # Example: "한글" -> "ㅎㅏㄴㄱㅡㄹ"
    result = []
    for char in text:
        if 0xAC00 <= ord(char) <= 0xD7A3:
            # Decompose Hangul syllable
            decomposed = unicodedata.decomposition(char)
            result.append(decomposed)
        else:
            result.append(char)
    return ''.join(result)
```

**5. Fuzzy Matching**

```python
from fuzzywuzzy import fuzz

def fuzzy_autocomplete(prefix, candidates, threshold=80):
    matches = []
    
    for candidate in candidates:
        # Calculate similarity
        similarity = fuzz.partial_ratio(prefix.lower(), candidate.lower())
        
        if similarity >= threshold:
            matches.append({
                'text': candidate,
                'similarity': similarity
            })
    
    # Sort by similarity
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    
    return [m['text'] for m in matches[:10]]

# Typo correction using edit distance
def suggest_corrections(query, dictionary, max_distance=2):
    from Levenshtein import distance
    
    corrections = []
    
    for word in dictionary:
        dist = distance(query.lower(), word.lower())
        if dist <= max_distance:
            corrections.append((word, dist))
    
    # Sort by distance
    corrections.sort(key=lambda x: x[1])
    
    return [word for word, dist in corrections[:5]]
```

**6. Personalization with ML**

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class PersonalizedAutocomplete:
    def __init__(self):
        self.user_profiles = {}
        self.vectorizer = TfidfVectorizer(max_features=1000)
    
    def build_user_profile(self, user_id):
        # Get user's search history
        history = get_user_search_history(user_id, limit=1000)
        
        if not history:
            return None
        
        # Create TF-IDF profile
        profile_vector = self.vectorizer.fit_transform(history)
        avg_vector = profile_vector.mean(axis=0)
        
        self.user_profiles[user_id] = avg_vector
        return avg_vector
    
    def get_personalized_suggestions(self, user_id, candidates):
        # Get user profile
        if user_id not in self.user_profiles:
            self.build_user_profile(user_id)
        
        user_profile = self.user_profiles.get(user_id)
        
        if user_profile is None:
            return candidates  # No personalization
        
        # Vectorize candidates
        candidate_vectors = self.vectorizer.transform(candidates)
        
        # Calculate similarity
        similarities = cosine_similarity(user_profile, candidate_vectors)[0]
        
        # Sort by similarity
        ranked = sorted(
            zip(candidates, similarities),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [cand for cand, score in ranked]
```

**7. Database Schema**

```sql
-- Query statistics table
CREATE TABLE query_stats (
    query_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    query_text VARCHAR(500) NOT NULL,
    language VARCHAR(10),
    frequency BIGINT DEFAULT 1,
    last_searched TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_query_lang (query_text, language),
    INDEX idx_frequency (frequency DESC)
);

-- User search history
CREATE TABLE user_search_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    query_text VARCHAR(500),
    language VARCHAR(10),
    clicked_position INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_time (user_id, timestamp DESC)
);

-- Trending queries (materialized view)
CREATE TABLE trending_queries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    query_text VARCHAR(500),
    language VARCHAR(10),
    score FLOAT,
    hour_bucket TIMESTAMP,
    
    INDEX idx_lang_hour (language, hour_bucket),
    INDEX idx_score (score DESC)
);
```

**8. Building and Updating Trie**

```python
def build_trie_from_db():
    # Batch job: Build trie from query statistics
    trie = AutocompleteTrie()
    
    # Get top 10M queries
    queries = db.execute("""
        SELECT query_text, frequency, language
        FROM query_stats
        WHERE frequency > 10
        ORDER BY frequency DESC
        LIMIT 10000000
    """)
    
    # Group by language
    tries_by_lang = {}
    
    for query in queries:
        lang = query['language']
        
        if lang not in tries_by_lang:
            tries_by_lang[lang] = AutocompleteTrie()
        
        tries_by_lang[lang].insert(query['query_text'], query['frequency'])
    
    # Serialize and save to Redis
    for lang, trie in tries_by_lang.items():
        serialized = pickle.dumps(trie)
        redis_client.set(f"trie:{lang}", serialized)
    
    return tries_by_lang

# Incremental update
def update_trie_incremental(query, language, frequency_delta=1):
    # Get trie from Redis
    trie_data = redis_client.get(f"trie:{language}")
    
    if trie_data:
        trie = pickle.loads(trie_data)
    else:
        trie = AutocompleteTrie()
    
    # Update with new query
    trie.insert(query, frequency_delta)
    
    # Save back to Redis
    redis_client.set(f"trie:{language}", pickle.dumps(trie))
```

**9. Load Balancing & Geo-Distribution**

```python
# GeoDNS routing
geo_routing = {
    'KR': 'seoul.autocomplete.naver.com',
    'JP': 'tokyo.autocomplete.naver.com',
    'US': 'us-west.autocomplete.naver.com',
    'EU': 'frankfurt.autocomplete.naver.com'
}

# Consistent hashing for cache distribution
class ConsistentHash:
    def __init__(self, nodes, replicas=3):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        
        for node in nodes:
            self.add_node(node)
    
    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)
        
        self.sorted_keys.sort()
    
    def get_node(self, key):
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        
        # Find first node >= hash
        for node_key in self.sorted_keys:
            if node_key >= hash_key:
                return self.ring[node_key]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
```

**10. Performance Optimization**

```python
# Compression for trie storage
import zlib

def compress_trie(trie):
    serialized = pickle.dumps(trie)
    compressed = zlib.compress(serialized, level=9)
    
    compression_ratio = len(compressed) / len(serialized)
    print(f"Compression ratio: {compression_ratio:.2%}")
    
    return compressed

def decompress_trie(compressed_data):
    decompressed = zlib.decompress(compressed_data)
    trie = pickle.loads(decompressed)
    return trie

# Memory-efficient trie using arrays
class CompactTrie:
    def __init__(self):
        self.nodes = []  # Array of nodes
        self.children_arrays = []  # Array of children indices
        self.root_index = 0
    
    # Implementation uses arrays instead of dicts
    # Reduces memory overhead significantly
```

**11. Monitoring & Metrics**

```python
metrics = {
    "autocomplete_latency_ms": Histogram("autocomplete_latency_milliseconds"),
    "cache_hit_rate": Gauge("cache_hit_rate_percentage"),
    "trie_size_mb": Gauge("trie_memory_size_megabytes"),
    "queries_per_second": Counter("autocomplete_queries_total")
}

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = (time.time() - request.start_time) * 1000
    metrics["autocomplete_latency_ms"].observe(latency)
    metrics["queries_per_second"].inc()
    
    return response
```

---

## 12. Design a Payment Processing System (NAVER Pay)

### Requirements
- 150 triệu users
- 100M transactions/ngày
- Multiple currencies support
- Fraud detection
- Idempotency for retries
- 99.999% availability (5 minutes downtime/năm)

### High-Level Architecture

```
[Client Apps]
      ↓
[API Gateway + Rate Limiter]
      ↓
[Payment Orchestrator]
      ↓
   ┌──┴────────┬─────────┬────────┐
   ↓           ↓         ↓        ↓
[Fraud    [Currency] [Ledger] [Notification]
Detection] Exchange]  Service] Service
   ↓           ↓         ↓
[Payment Providers]
(Stripe, Bank APIs, Card Networks)
   ↓
[Transaction DB (Sharded PostgreSQL)]
   ↓
[Audit Log (Append-only)]
```

### Core Components

**1. Payment Request Schema**

```python
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class PaymentRequest:
    idempotency_key: str  # Client-generated unique key
    user_id: int
    amount: Decimal
    currency: str  # ISO 4217 (USD, KRW, JPY)
    payment_method: PaymentMethod
    payment_details: dict  # Card number, CVV, etc.
    merchant_id: int
    order_id: str
    description: str
    callback_url: str
    metadata: dict
```

**2. Payment Orchestrator**

```python
from fastapi import FastAPI, HTTPException
import redis
import hashlib

app = FastAPI()
redis_client = redis.Redis(host='localhost', decode_responses=True)

@app.post("/api/v1/payments")
async def create_payment(payment_request: PaymentRequest):
    # 1. Idempotency check
    idempotency_result = check_idempotency(payment_request.idempotency_key)
    if idempotency_result:
        return idempotency_result
    
    # 2. Validate request
    validate_payment_request(payment_request)
    
    # 3. Fraud detection
    fraud_score = await check_fraud(payment_request)
    if fraud_score > 0.8:
        return {
            "status": "rejected",
            "reason": "fraud_detected",
            "fraud_score": fraud_score
        }
    
    # 4. Currency conversion if needed
    if payment_request.currency != get_merchant_currency(payment_request.merchant_id):
        payment_request.amount = await convert_currency(
            payment_request.amount,
            payment_request.currency,
            get_merchant_currency(payment_request.merchant_id)
        )
    
    # 5. Create payment record
    payment_id = create_payment_record(payment_request)
    
    # 6. Process payment with provider
    try:
        result = await process_with_provider(payment_request, payment_id)
        
        # 7. Update ledger (double-entry bookkeeping)
        await update_ledger(payment_id, result)
        
        # 8. Send notification
        await send_payment_notification(payment_request.user_id, payment_id, result)
        
        # 9. Store result for idempotency
        store_idempotency_result(payment_request.idempotency_key, result)
        
        return result
        
    except ProviderError as e:
        # Handle payment failure
        mark_payment_failed(payment_id, str(e))
        raise HTTPException(status_code=500, detail="Payment processing failed")

def check_idempotency(key):
    # Check if we've seen this request before
    cached_result = redis_client.get(f"idempotency:{key}")
    
    if cached_result:
        return json.loads(cached_result)
    
    return None

def store_idempotency_result(key, result):
    # Store result for 24 hours
    redis_client.setex(
        f"idempotency:{key}",
        86400,
        json.dumps(result)
    )
```

**3. Fraud Detection System**

```python
class FraudDetector:
    def __init__(self):
        self.ml_model = load_fraud_model()
        self.rules = load_fraud_rules()
    
    async def check_fraud(self, payment_request):
        # Rule-based checks
        rule_score = self.check_rules(payment_request)
        
        # ML-based scoring
        ml_score = self.check_ml_model(payment_request)
        
        # Combine scores
        final_score = 0.4 * rule_score + 0.6 * ml_score
        
        # Log for review if suspicious
        if final_score > 0.5:
            await log_suspicious_transaction(payment_request, final_score)
        
        return final_score
    
    def check_rules(self, payment_request):
        score = 0.0
        
        # Rule 1: Large transaction from new account
        account_age = get_account_age(payment_request.user_id)
        if account_age < 7 and payment_request.amount > 1000000:
            score += 0.3
        
        # Rule 2: Multiple transactions in short time
        recent_transactions = get_recent_transactions(
            payment_request.user_id,
            minutes=30
        )
        if len(recent_transactions) > 5:
            score += 0.2
        
        # Rule 3: Unusual location
        user_location = get_user_location(payment_request.user_id)
        transaction_location = payment_request.metadata.get('location')
        
        if distance(user_location, transaction_location) > 1000:  # km
            score += 0.15
        
        # Rule 4: High-risk merchant category
        merchant_category = get_merchant_category(payment_request.merchant_id)
        if merchant_category in HIGH_RISK_CATEGORIES:
            score += 0.1
        
        # Rule 5: Blacklisted card/account
        if is_blacklisted(payment_request.payment_details):
            score = 1.0
        
        return min(score, 1.0)
    
    def check_ml_model(self, payment_request):
        # Extract features
        features = extract_fraud_features(payment_request)
        
        # Model prediction
        fraud_probability = self.ml_model.predict_proba(features)[0][1]
        
        return fraud_probability

def extract_fraud_features(payment_request):
    features = {
        'amount': float(payment_request.amount),
        'amount_log': np.log1p(float(payment_request.amount)),
        'hour_of_day': datetime.now().hour,
        'day_of_week': datetime.now().weekday(),
        'account_age_days': get_account_age(payment_request.user_id),
        'previous_transactions_count': get_transaction_count(payment_request.user_id),
        'average_transaction_amount': get_avg_transaction(payment_request.user_id),
        'device_type': payment_request.metadata.get('device_type', 'unknown'),
        'is_vpn': payment_request.metadata.get('is_vpn', False),
        'payment_method_age_days': get_payment_method_age(payment_request.payment_details),
        'merchant_risk_score': get_merchant_risk_score(payment_request.merchant_id)
    }
    
    return pd.DataFrame([features])
```

**4. Double-Entry Ledger System**

```python
# Database schema
"""
CREATE TABLE ledger_entries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    account_id BIGINT NOT NULL,
    debit DECIMAL(20, 2),
    credit DECIMAL(20, 2),
    balance DECIMAL(20, 2),
    currency VARCHAR(3),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_account_time (account_id, created_at),
    INDEX idx_transaction (transaction_id)
);

CREATE TABLE accounts (
    account_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    account_type ENUM('user_wallet', 'merchant', 'system', 'escrow'),
    currency VARCHAR(3),
    balance DECIMAL(20, 2) DEFAULT 0,
    
    INDEX idx_user (user_id)
);
"""

class LedgerService:
    def __init__(self, db):
        self.db = db
    
    async def record_payment(self, payment_id, amount, currency, from_account, to_account):
        # Start transaction
        async with self.db.transaction():
            # Debit from payer
            await self.create_entry(
                transaction_id=payment_id,
                account_id=from_account,
                debit=amount,
                credit=0,
                currency=currency,
                description=f"Payment {payment_id}"
            )
            
            # Credit to merchant
            await self.create_entry(
                transaction_id=payment_id,
                account_id=to_account,
                debit=0,
                credit=amount,
                currency=currency,
                description=f"Payment {payment_id}"
            )
            
            # Update account balances
            await self.update_balance(from_account, -amount)
            await self.update_balance(to_account, amount)
    
    async def create_entry(self, transaction_id, account_id, debit, credit, currency, description):
        # Get current balance
        current_balance = await self.get_balance(account_id)
        new_balance = current_balance - debit + credit
        
        await self.db.execute("""
            INSERT INTO ledger_entries
            (transaction_id, account_id, debit, credit, balance, currency, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, transaction_id, account_id, debit, credit, new_balance, currency, description)
        
        return new_balance
    
    async def update_balance(self, account_id, amount_delta):
        await self.db.execute("""
            UPDATE accounts
            SET balance = balance + ?
            WHERE account_id = ?
        """, amount_delta, account_id)
    
    async def get_balance(self, account_id):
        result = await self.db.execute("""
            SELECT balance FROM accounts WHERE account_id = ?
        """, account_id)
        
        return result['balance'] if result else 0
```

**5. Payment Provider Integration**

```python
class PaymentProvider(ABC):
    @abstractmethod
    async def charge(self, payment_request):
        pass
    
    @abstractmethod
    async def refund(self, payment_id, amount):
        pass

class StripeProvider(PaymentProvider):
    def __init__(self, api_key):
        self.stripe = stripe
        self.stripe.api_key = api_key
    
    async def charge(self, payment_request):
        try:
            # Create payment intent
            intent = await self.stripe.PaymentIntent.create_async(
                amount=int(payment_request.amount * 100),  # Convert to cents
                currency=payment_request.currency.lower(),
                payment_method=payment_request.payment_details['payment_method_id'],
                confirm=True,
                description=payment_request.description,
                metadata={
                    'order_id': payment_request.order_id,
                    'user_id': str(payment_request.user_id)
                }
            )
            
            return {
                'provider_transaction_id': intent.id,
                'status': 'completed' if intent.status == 'succeeded' else 'failed',
                'amount': payment_request.amount,
                'currency': payment_request.currency
            }
            
        except stripe.error.CardError as e:
            # Card declined
            return {
                'status': 'failed',
                'error_code': e.code,
                'error_message': str(e)
            }
        
        except Exception as e:
            # Other errors
            raise ProviderError(f"Stripe error: {str(e)}")
    
    async def refund(self, payment_id, amount):
        intent_id = get_provider_transaction_id(payment_id)
        
        refund = await self.stripe.Refund.create_async(
            payment_intent=intent_id,
            amount=int(amount * 100)
        )
        
        return refund

# Provider factory
class PaymentProviderFactory:
    providers = {
        'stripe': StripeProvider,
        'bank_transfer': BankTransferProvider,
        'digital_wallet': DigitalWalletProvider
    }
    
    @classmethod
    def get_provider(cls, payment_method):
        provider_class = cls.providers.get(payment_method)
        if not provider_class:
            raise ValueError(f"Unsupported payment method: {payment_method}")
        
        return provider_class()
```

**6. Currency Exchange Service**

```python
class CurrencyExchangeService:
    def __init__(self):
        self.rates_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def convert(self, amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount
        
        # Get exchange rate
        rate = await self.get_rate(from_currency, to_currency)
        
        # Convert
        converted_amount = Decimal(str(amount)) * Decimal(str(rate))
        
        # Round to 2 decimal places
        return round(converted_amount, 2)
    
    async def get_rate(self, from_currency, to_currency):
        cache_key = f"{from_currency}_{to_currency}"
        
        # Check cache
        if cache_key in self.rates_cache:
            cached_rate, timestamp = self.rates_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_rate
        
        # Fetch from external API
        rate = await self.fetch_rate_from_api(from_currency, to_currency)
        
        # Cache
        self.rates_cache[cache_key] = (rate, time.time())
        
        # Store in Redis for sharing across instances
        redis_client.setex(
            f"exchange_rate:{cache_key}",
            self.cache_ttl,
            str(rate)
        )
        
        return rate
    
    async def fetch_rate_from_api(self, from_currency, to_currency):
        # Use external API (e.g., Open Exchange Rates)
        async with aiohttp.ClientSession() as session:
            url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}"
            
            async with session.get(url) as response:
                data = await response.json()
                return data['result']
```

**7. Transaction State Machine**

```python
class PaymentStateMachine:
    states = {
        'created': ['pending', 'cancelled'],
        'pending': ['processing', 'failed'],
        'processing': ['completed', 'failed'],
        'completed': ['refund_pending'],
        'refund_pending': ['refunded', 'refund_failed'],
        'refunded': [],
        'failed': [],
        'cancelled': []
    }
    
    def __init__(self, payment_id):
        self.payment_id = payment_id
        self.current_state = self.get_current_state()
    
    def transition(self, new_state):
        if new_state not in self.states.get(self.current_state, []):
            raise InvalidStateTransition(
                f"Cannot transition from {self.current_state} to {new_state}"
            )
        
        # Update database
        db.execute("""
            UPDATE payments
            SET status = ?, updated_at = NOW()
            WHERE payment_id = ?
        """, new_state, self.payment_id)
        
        # Log transition
        log_state_transition(self.payment_id, self.current_state, new_state)
        
        self.current_state = new_state
        
        return new_state
```

**8. Webhook Handling**

```python
@app.post("/api/v1/webhooks/stripe")
async def stripe_webhook(request: Request):
    # Verify signature
    signature = request.headers.get('Stripe-Signature')
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle event
    if event['type'] == 'payment_intent.succeeded':
        await handle_payment_success(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        await handle_payment_failure(event['data']['object'])
    elif event['type'] == 'charge.refunded':
        await handle_refund(event['data']['object'])
    
    return {'status': 'success'}

async def handle_payment_success(payment_intent):
    payment_id = payment_intent['metadata']['order_id']
    
    # Update payment status
    state_machine = PaymentStateMachine(payment_id)
    state_machine.transition('completed')
    
    # Send notification
    await send_payment_success_notification(payment_id)
    
    # Trigger order fulfillment
    await trigger_order_fulfillment(payment_id)
```

**9. Refund Processing**

```python
@app.post("/api/v1/payments/{payment_id}/refund")
async def refund_payment(payment_id: str, refund_amount: Decimal):
    # Get payment details
    payment = get_payment(payment_id)
    
    if payment['status'] != 'completed':
        raise HTTPException(400, "Payment not completed")
    
    # Validate refund amount
    if refund_amount > payment['amount']:
        raise HTTPException(400, "Refund amount exceeds payment amount")
    
    # Create refund record
    refund_id = create_refund_record(payment_id, refund_amount)
    
    try:
        # Process refund with provider
        provider = PaymentProviderFactory.get_provider(payment['payment_method'])
        refund_result = await provider.refund(payment_id, refund_amount)
        
        # Update ledger
        await ledger_service.record_refund(
            refund_id,
            refund_amount,
            payment['currency'],
            payment['merchant_account'],
            payment['user_account']
        )
        
        # Update state
        state_machine = PaymentStateMachine(payment_id)
        state_machine.transition('refunded')
        
        # Notify user
        await send_refund_notification(payment['user_id'], payment_id, refund_amount)
        
        return {
            'refund_id': refund_id,
            'status': 'refunded',
            'amount': refund_amount
        }
        
    except Exception as e:
        mark_refund_failed(refund_id, str(e))
        raise HTTPException(500, f"Refund failed: {str(e)}")
```

**10. High Availability & Disaster Recovery**

```python
# Multi-region setup
regions = {
    'primary': {
        'db': 'us-west-2-primary.rds.amazonaws.com',
        'redis': 'us-west-2-redis.cache.amazonaws.com'
    },
    'secondary': {
        'db': 'eu-west-1-secondary.rds.amazonaws.com',
        'redis': 'eu-west-1-redis.cache.amazonaws.com'
    }
}

# Circuit breaker for external services
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
            
            raise e

# Database sharding
def get_shard(user_id, num_shards=16):
    shard_id = user_id % num_shards
    return f"payment_db_shard_{shard_id}"

def get_db_connection(user_id):
    shard = get_shard(user_id)
    return db_pool.get_connection(shard)
```

**11. Compliance & Auditing**

```python
# PCI DSS Compliance: Never store full card numbers
def tokenize_card(card_number):
    # Use payment provider's tokenization
    token = stripe.Token.create(
        card={
            "number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc
        }
    )
    
    return token.id

# Audit logging
async def log_payment_event(event_type, payment_id, details):
    audit_entry = {
        'event_type': event_type,
        'payment_id': payment_id,
        'timestamp': datetime.now().isoformat(),
        'details': details,
        'ip_address': get_client_ip(),
        'user_agent': get_user_agent()
    }
    
    # Write to append-only audit log
    await audit_log_db.insert('audit_logs', audit_entry)
    
    # Also stream to Kafka for real-time monitoring
    kafka_producer.send('payment_audit_log', audit_entry)

# GDPR compliance: Data export
async def export_user_payment_data(user_id):
    payments = await db.query("""
        SELECT payment_id, amount, currency, status, created_at
        FROM payments
        WHERE user_id = ?
    """, user_id)
    
    # Anonymize sensitive data
    for payment in payments:
        payment['payment_method'] = "****"  # Redact
    
    return payments
```

---

## 13. Design a Distributed Cache System

### Requirements
- 300 triệu users
- 10 tỷ reads/ngày
- Eviction policies (LRU, LFU, TTL)
- Replication
- Consistency guarantees

### High-Level Architecture

```
[Application Servers]
      ↓
[Cache Client Library]
      ↓
[Load Balancer]
      ↓
[Cache Cluster]
   ┌──┴──────┬────┬────┐
   ↓         ↓    ↓    ↓
[Shard 1] [S2] [S3] [S4]
(Master+Slaves)
   ↓
[Persistence Layer]
(AOF/RDB Snapshots)
```

### Core Components

**1. Cache Architecture**

```python
# Redis Cluster configuration
redis_cluster_config = {
    'nodes': [
        {'host': 'node1', 'port': 7000},
        {'host': 'node2', 'port': 7001},
        {'host': 'node3', 'port': 7002},
        {'host': 'node4', 'port': 7003},
        {'host': 'node5', 'port': 7004},
        {'host': 'node6', 'port': 7005}
    ],
    'replicas': 2,  # Each master has 2 slaves
    'max_connections': 50,
    'socket_keepalive': True,
    'socket_connect_timeout': 5
}

from rediscluster import RedisCluster

cache_client = RedisCluster(
    startup_nodes=redis_cluster_config['nodes'],
    decode_responses=True,
    skip_full_coverage_check=True
)
```

**2. Cache Client Library**

```python
class CacheClient:
    def __init__(self, redis_cluster):
        self.redis = redis_cluster
        self.local_cache = {}  # L1 cache (in-memory)
        self.local_cache_size = 1000
        self.stats = {
            'hits': 0,
            'misses': 0,
            'l1_hits': 0,
            'l2_hits': 0
        }
    
    def get(self, key):
        # L1 cache (local memory)
        if key in self.local_cache:
            self.stats['l1_hits'] += 1
            self.stats['hits'] += 1
            return self.local_cache[key]
        
        # L2 cache (Redis cluster)
        value = self.redis.get(key)
        
        if value is not None:
            self.stats['l2_hits'] += 1
            self.stats['hits'] += 1
            
            # Populate L1 cache
            self.set_local(key, value)
            
            return value
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key, value, ttl=None):
        # Set in Redis
        if ttl:
            self.redis.setex(key, ttl, value)
        else:
            self.redis.set(key, value)
        
        # Set in local cache
        self.set_local(key, value)
    
    def set_local(self, key, value):
        # LRU eviction for local cache
        if len(self.local_cache) >= self.local_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.local_cache))
            del self.local_cache[oldest_key]
        
        self.local_cache[key] = value
    
    def delete(self, key):
        # Delete from Redis
        self.redis.delete(key)
        
        # Delete from local cache
        if key in self.local_cache:
            del self.local_cache[key]
    
    def get_stats(self):
        hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])
        return {
            **self.stats,
            'hit_rate': hit_rate
        }
```

**3. Eviction Policies**

```python
# LRU (Least Recently Used) Implementation
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.order = []  # Track access order
    
    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            # Update existing
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Evict least recently used
            lru_key = self.order.pop(0)
            del self.cache[lru_key]
        
        self.cache[key] = value
        self.order.append(key)

# LFU (Least Frequently Used) Implementation
class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.frequency = {}  # Track access frequency
        self.min_freq = 0
        self.freq_to_keys = collections.defaultdict(OrderedDict)
    
    def get(self, key):
        if key not in self.cache:
            return None
        
        # Update frequency
        freq = self.frequency[key]
        self.frequency[key] = freq + 1
        
        # Move to next frequency bucket
        del self.freq_to_keys[freq][key]
        if not self.freq_to_keys[freq]:
            del self.freq_to_keys[freq]
            if freq == self.min_freq:
                self.min_freq += 1
        
        self.freq_to_keys[freq + 1][key] = True
        
        return self.cache[key]
    
    def put(self, key, value):
        if self.capacity == 0:
            return
        
        if key in self.cache:
            # Update existing
            self.cache[key] = value
            self.get(key)
            return
        
        if len(self.cache) >= self.capacity:
            # Evict least frequently used
            evict_key = next(iter(self.freq_to_keys[self.min_freq]))
            del self.freq_to_keys[self.min_freq][evict_key]
            if not self.freq_to_keys[self.min_freq]:
                del self.freq_to_keys[self.min_freq]
            del self.cache[evict_key]
            del self.frequency[evict_key]
        
        # Add new key
        self.cache[key] = value
        self.frequency[key] = 1
        self.freq_to_keys[1][key] = True
        self.min_freq = 1

# TTL (Time To Live) with automatic expiration
# Redis handles this natively with EXPIRE command
def set_with_ttl(key, value, ttl_seconds):
    redis.setex(key, ttl_seconds, value)
```

**4. Cache Patterns**

```python
# Cache-Aside (Lazy Loading)
def get_user(user_id):
    # Try cache first
    cached_user = cache.get(f"user:{user_id}")
    if cached_user:
        return json.loads(cached_user)
    
    # Cache miss, query database
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    # Populate cache
    cache.set(f"user:{user_id}", json.dumps(user), ttl=3600)
    
    return user

# Write-Through
def update_user(user_id, data):
    # Update database
    db.execute("UPDATE users SET ... WHERE id = ?", data, user_id)
    
    # Update cache
    cache.set(f"user:{user_id}", json.dumps(data), ttl=3600)

# Write-Behind (Write-Back)
def update_user_async(user_id, data):
    # Update cache immediately
    cache.set(f"user:{user_id}", json.dumps(data), ttl=3600)
    
    # Queue DB update for later
    queue.enqueue('db_updates', {'user_id': user_id, 'data': data})

# Read-Through
class ReadThroughCache:
    def get(self, key, loader_func):
        # Check cache
        value = cache.get(key)
        if value:
            return value
        
        # Load from source
        value = loader_func()
        
        # Cache for next time
        cache.set(key, value)
        
        return value
```

**5. Cache Invalidation Strategies**

```python
# Time-based invalidation
def invalidate_after_time(key, ttl=3600):
    cache.expire(key, ttl)

# Event-based invalidation
def on_user_update(user_id):
    # Invalidate user cache
    cache.delete(f"user:{user_id}")
    
    # Invalidate related caches
    cache.delete(f"user_posts:{user_id}")
    cache.delete(f"user_friends:{user_id}")

# Cache stampede prevention (using locks)
def get_with_lock(key, loader_func, lock_timeout=10):
    # Try to get from cache
    value = cache.get(key)
    if value:
        return value
    
    # Acquire lock
    lock_key = f"lock:{key}"
    if cache.set(lock_key, "1", nx=True, ex=lock_timeout):
        try:
            # This thread loads data
            value = loader_func()
            cache.set(key, value, ex=3600)
            return value
        finally:
            cache.delete(lock_key)
    else:
        # Wait and retry
        time.sleep(0.1)
        return get_with_lock(key, loader_func, lock_timeout)
```

**6. Consistent Hashing**

```python
import hashlib

class ConsistentHashRing:
    def __init__(self, nodes, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        
        for node in nodes:
            self.add_node(node)
    
    def add_node(self, node):
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            self.ring[hash_key] = node
            self.sorted_keys.append(hash_key)
        
        self.sorted_keys.sort()
    
    def remove_node(self, node):
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            del self.ring[hash_key]
            self.sorted_keys.remove(hash_key)
    
    def get_node(self, key):
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        
        # Binary search for the first node >= hash_key
        index = bisect.bisect_right(self.sorted_keys, hash_key)
        
        # Wrap around to first node if necessary
        if index == len(self.sorted_keys):
            index = 0
        
        return self.ring[self.sorted_keys[index]]
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
```

Tôi đã tạo tài liệu chi tiết cho 3 câu hỏi đầu tiên (11-13) trong danh sách mở rộng. Tài liệu bao gồm:

**Câu 11 - Autocomplete System:**
- Trie data structure implementation
- Multilingual support (Korean, Japanese, English)
- Personalization với ML
- Trending queries với real-time processing
- Fuzzy matching & typo correction
- Caching strategies

**Câu 12 - Payment Processing System:**
- Payment orchestrator
- Fraud detection (rule-based + ML)
- Double-entry ledger system
- Multiple payment providers
- Currency exchange
- Idempotency handling
- PCI DSS compliance

**Câu 13 - Distributed Cache:**
- Cache client library với L1/L2 caching
- Eviction policies (LRU, LFU, TTL)
- Cache patterns (Cache-Aside, Write-Through, Write-Behind)
- Consistent hashing
- Cache invalidation strategies

---

## 14. Design a Rate Limiter for APIs

### Requirements
- 200 triệu users
- Enforce limits per user/IP (e.g., 1000 requests/min)
- Distributed across regions
- Handle bursts
- No single points of failure

### High-Level Architecture

```
[API Requests]
      ↓
[API Gateway]
      ↓
[Rate Limiter Middleware]
      ↓
[Redis Cluster] (for counters)
      ↓
[Backend Services]
```

### Core Components

**1. Token Bucket Algorithm**

```python
import time
import redis

class TokenBucket:
    def __init__(self, redis_client, capacity, refill_rate):
        self.redis = redis_client
        self.capacity = capacity  # Max tokens
        self.refill_rate = refill_rate  # Tokens per second
    
    def allow_request(self, key):
        now = time.time()
        
        # Lua script for atomic operation
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1])
        local last_refill = tonumber(bucket[2])
        
        if tokens == nil then
            tokens = capacity
            last_refill = now
        end
        
        -- Refill tokens based on time elapsed
        local time_elapsed = now - last_refill
        tokens = math.min(capacity, tokens + time_elapsed * refill_rate)
        
        local allowed = 0
        if tokens >= requested then
            tokens = tokens - requested
            allowed = 1
        end
        
        -- Update bucket
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)
        
        return allowed
        """
        
        result = self.redis.eval(
            lua_script,
            1,  # Number of keys
            key,
            self.capacity,
            self.refill_rate,
            now,
            1  # Request 1 token
        )
        
        return result == 1

# Usage
rate_limiter = TokenBucket(redis_client, capacity=100, refill_rate=10)  # 100 tokens, refill 10/sec

if rate_limiter.allow_request(f"user:{user_id}"):
    # Process request
    pass
else:
    # Return 429 Too Many Requests
    return {"error": "Rate limit exceeded"}
```

**2. Sliding Window Log**

```python
class SlidingWindowLog:
    def __init__(self, redis_client, max_requests, window_seconds):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def allow_request(self, key):
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        request_count = self.redis.zcard(key)
        
        if request_count < self.max_requests:
            # Add current request
            self.redis.zadd(key, {str(now): now})
            self.redis.expire(key, self.window_seconds)
            return True
        
        return False
```

**3. Sliding Window Counter**

```python
class SlidingWindowCounter:
    def __init__(self, redis_client, max_requests, window_seconds):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def allow_request(self, key):
        now = time.time()
        current_window = int(now // self.window_seconds)
        previous_window = current_window - 1
        
        # Keys for current and previous windows
        current_key = f"{key}:{current_window}"
        previous_key = f"{key}:{previous_window}"
        
        # Get counts
        current_count = int(self.redis.get(current_key) or 0)
        previous_count = int(self.redis.get(previous_key) or 0)
        
        # Calculate weight for previous window
        elapsed_time = now - (current_window * self.window_seconds)
        weight = 1 - (elapsed_time / self.window_seconds)
        
        # Weighted count
        estimated_count = current_count + (previous_count * weight)
        
        if estimated_count < self.max_requests:
            # Increment current window
            pipe = self.redis.pipeline()
            pipe.incr(current_key)
            pipe.expire(current_key, self.window_seconds * 2)
            pipe.execute()
            return True
        
        return False
```

**4. Fixed Window Counter**

```python
class FixedWindowCounter:
    def __init__(self, redis_client, max_requests, window_seconds):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def allow_request(self, key):
        now = int(time.time())
        window = now // self.window_seconds
        window_key = f"{key}:{window}"
        
        # Increment counter
        count = self.redis.incr(window_key)
        
        if count == 1:
            # Set expiration on first request
            self.redis.expire(window_key, self.window_seconds)
        
        return count <= self.max_requests
```

**5. Rate Limiter Middleware**

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# Configure rate limits
RATE_LIMITS = {
    'default': {'requests': 1000, 'window': 60},  # 1000 req/min
    'premium': {'requests': 10000, 'window': 60},  # 10000 req/min
    'internal': {'requests': float('inf'), 'window': 60}  # No limit
}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Get user tier
    user_id = request.headers.get('X-User-Id')
    user_tier = get_user_tier(user_id) or 'default'
    
    # Get rate limit config
    config = RATE_LIMITS.get(user_tier, RATE_LIMITS['default'])
    
    # Check rate limit
    rate_limiter = SlidingWindowCounter(
        redis_client,
        config['requests'],
        config['window']
    )
    
    key = f"rate_limit:{user_tier}:{user_id or request.client.host}"
    
    if not rate_limiter.allow_request(key):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "retry_after": config['window']
            },
            headers={
                "X-RateLimit-Limit": str(config['requests']),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(config['window'])
            }
        )
    
    # Get remaining requests
    remaining = get_remaining_requests(key, config)
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(config['requests'])
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + config['window'])
    
    return response
```

**6. Distributed Rate Limiting**

```python
class DistributedRateLimiter:
    def __init__(self, redis_cluster):
        self.redis = redis_cluster
    
    def allow_request(self, key, limit, window):
        # Use Redis Cluster for distributed rate limiting
        # Each node handles its shard of keys
        
        # Global rate limiting across all regions
        global_key = f"global:{key}"
        local_key = f"local:{get_region()}:{key}"
        
        # Check local first (faster)
        local_allowed = self.check_local_limit(local_key, limit * 0.7, window)
        
        if not local_allowed:
            return False
        
        # Check global (cross-region)
        global_allowed = self.check_global_limit(global_key, limit, window)
        
        return global_allowed
    
    def check_local_limit(self, key, limit, window):
        # Fast local check
        counter = FixedWindowCounter(self.redis, limit, window)
        return counter.allow_request(key)
    
    def check_global_limit(self, key, limit, window):
        # Slower global check with eventual consistency
        counter = SlidingWindowCounter(self.redis, limit, window)
        return counter.allow_request(key)
```

**7. Rate Limiting by IP, User, and API Key**

```python
def get_rate_limit_key(request):
    # Priority order
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api_key:{api_key}"
    
    user_id = request.headers.get('X-User-Id')
    if user_id:
        return f"user:{user_id}"
    
    # Fall back to IP
    ip = request.client.host
    return f"ip:{ip}"

def get_rate_limit_config(key):
    if key.startswith('api_key:'):
        # Check API key tier from database
        api_key = key.split(':', 1)[1]
        tier = get_api_key_tier(api_key)
        return API_KEY_LIMITS[tier]
    
    if key.startswith('user:'):
        user_id = key.split(':', 1)[1]
        tier = get_user_tier(user_id)
        return USER_LIMITS[tier]
    
    # IP-based (most restrictive)
    return IP_LIMITS['default']
```

**8. Graceful Degradation**

```python
@app.middleware("http")
async def adaptive_rate_limit(request: Request, call_next):
    # Monitor system load
    system_load = get_system_load()
    
    if system_load > 0.9:
        # Under heavy load, reduce limits by 50%
        scale_factor = 0.5
    elif system_load > 0.7:
        # Moderate load, reduce by 20%
        scale_factor = 0.8
    else:
        # Normal operation
        scale_factor = 1.0
    
    # Apply scaled rate limit
    config = get_rate_limit_config(request)
    adjusted_limit = int(config['requests'] * scale_factor)
    
    rate_limiter = TokenBucket(
        redis_client,
        capacity=adjusted_limit,
        refill_rate=adjusted_limit / config['window']
    )
    
    key = get_rate_limit_key(request)
    
    if not rate_limiter.allow_request(key):
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})
    
    return await call_next(request)
```

**9. Rate Limit Bypass for Critical Services**

```python
WHITELISTED_IPS = ['10.0.0.0/8', '172.16.0.0/12']
CRITICAL_ENDPOINTS = ['/health', '/metrics', '/webhook']

def should_bypass_rate_limit(request):
    # Check if IP is whitelisted
    client_ip = request.client.host
    for cidr in WHITELISTED_IPS:
        if ip_address_in_network(client_ip, cidr):
            return True
    
    # Check if endpoint is critical
    if request.url.path in CRITICAL_ENDPOINTS:
        return True
    
    # Check for admin role
    user_role = get_user_role(request)
    if user_role == 'admin':
        return True
    
    return False
```

**10. Monitoring & Alerts**

```python
import prometheus_client

rate_limit_requests = prometheus_client.Counter(
    'rate_limit_requests_total',
    'Total requests processed by rate limiter',
    ['status', 'tier']
)

rate_limit_exceeded = prometheus_client.Counter(
    'rate_limit_exceeded_total',
    'Total requests that exceeded rate limit',
    ['tier']
)

def monitor_rate_limit(key, allowed, tier):
    status = 'allowed' if allowed else 'blocked'
    rate_limit_requests.labels(status=status, tier=tier).inc()
    
    if not allowed:
        rate_limit_exceeded.labels(tier=tier).inc()
        
        # Alert if too many blocked requests
        if rate_limit_exceeded.labels(tier=tier)._value.get() > 1000:
            send_alert(f"High rate limit violations for tier {tier}")
```

---

## 15. Design a Video Transcoding System

### Requirements
- 1 triệu videos/ngày
- Multiple formats/resolutions
- Adaptive streaming (HLS/DASH)
- Cost-efficient storage

### High-Level Architecture

```
[User Upload]
      ↓
[Upload Service] → [S3 Raw Storage]
      ↓
[Message Queue (SQS/RabbitMQ)]
      ↓
[Transcoding Workers (Auto-scaling)]
      ↓
[FFmpeg Processing]
      ↓
[S3 Processed Storage] → [CDN]
```

### Core Components

**1. Upload Service**

```python
from fastapi import FastAPI, UploadFile, File
import boto3
import uuid

app = FastAPI()
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

@app.post("/api/v1/videos/upload")
async def upload_video(file: UploadFile = File(...), user_id: str = None):
    # Generate unique video ID
    video_id = str(uuid.uuid4())
    
    # Upload to S3
    s3_key = f"raw/{video_id}/{file.filename}"
    
    # Use multipart upload for large files
    s3_client.upload_fileobj(
        file.file,
        'video-raw-bucket',
        s3_key,
        ExtraArgs={
            'ContentType': file.content_type,
            'Metadata': {
                'user_id': user_id,
                'original_filename': file.filename
            }
        }
    )
    
    # Get video metadata
    metadata = await extract_metadata(s3_key)
    
    # Create transcoding job
    job = {
        'video_id': video_id,
        's3_key': s3_key,
        'user_id': user_id,
        'metadata': metadata,
        'profiles': ['1080p', '720p', '480p', '360p'],
        'priority': 'normal'
    }
    
    # Send to queue
    sqs_client.send_message(
        QueueUrl='transcoding-queue',
        MessageBody=json.dumps(job),
        MessageAttributes={
            'Priority': {'StringValue': 'normal', 'DataType': 'String'}
        }
    )
    
    return {
        'video_id': video_id,
        'status': 'processing',
        'estimated_time': estimate_processing_time(metadata)
    }

async def extract_metadata(s3_key):
    # Download file temporarily
    local_path = f"/tmp/{uuid.uuid4()}"
    s3_client.download_file('video-raw-bucket', s3_key, local_path)
    
    # Use ffprobe to get metadata
    result = subprocess.run([
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        local_path
    ], capture_output=True, text=True)
    
    metadata = json.loads(result.stdout)
    
    # Clean up
    os.remove(local_path)
    
    return {
        'duration': float(metadata['format']['duration']),
        'size': int(metadata['format']['size']),
        'bitrate': int(metadata['format']['bit_rate']),
        'video_codec': metadata['streams'][0]['codec_name'],
        'audio_codec': metadata['streams'][1]['codec_name'],
        'width': metadata['streams'][0]['width'],
        'height': metadata['streams'][0]['height'],
        'fps': eval(metadata['streams'][0]['r_frame_rate'])
    }
```

**2. Transcoding Worker**

```python
import ffmpeg
import concurrent.futures

class TranscodingWorker:
    def __init__(self):
        self.profiles = {
            '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k', 'audio_bitrate': '192k'},
            '720p': {'width': 1280, 'height': 720, 'bitrate': '2800k', 'audio_bitrate': '128k'},
            '480p': {'width': 854, 'height': 480, 'bitrate': '1400k', 'audio_bitrate': '128k'},
            '360p': {'width': 640, 'height': 360, 'bitrate': '800k', 'audio_bitrate': '96k'},
            '240p': {'width': 426, 'height': 240, 'bitrate': '400k', 'audio_bitrate': '64k'}
        }
    
    def process_job(self, job):
        video_id = job['video_id']
        s3_key = job['s3_key']
        
        # Download from S3
        input_path = f"/tmp/{video_id}_input.mp4"
        s3_client.download_file('video-raw-bucket', s3_key, input_path)
        
        # Transcode to multiple profiles in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for profile_name in job['profiles']:
                future = executor.submit(
                    self.transcode_profile,
                    input_path,
                    video_id,
                    profile_name
                )
                futures.append(future)
            
            # Wait for all to complete
            results = [f.result() for f in futures]
        
        # Generate HLS master playlist
        master_playlist = self.generate_master_playlist(video_id, results)
        
        # Upload master playlist
        s3_client.put_object(
            Bucket='video-processed-bucket',
            Key=f"{video_id}/master.m3u8",
            Body=master_playlist,
            ContentType='application/vnd.apple.mpegurl'
        )
        
        # Clean up
        os.remove(input_path)
        
        # Update database
        update_video_status(video_id, 'completed', results)
        
        return video_id
    
    def transcode_profile(self, input_path, video_id, profile_name):
        profile = self.profiles[profile_name]
        output_dir = f"/tmp/{video_id}/{profile_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = f"{output_dir}/index.m3u8"
        
        # FFmpeg command for HLS
        stream = ffmpeg.input(input_path)
        
        # Video processing
        video = stream.video.filter('scale', profile['width'], profile['height'])
        
        # Audio processing
        audio = stream.audio
        
        # Output to HLS
        output = ffmpeg.output(
            video, audio,
            output_path,
            format='hls',
            vcodec='libx264',
            video_bitrate=profile['bitrate'],
            acodec='aac',
            audio_bitrate=profile['audio_bitrate'],
            hls_time=6,  # 6-second segments
            hls_list_size=0,  # Keep all segments in playlist
            hls_segment_filename=f"{output_dir}/segment_%03d.ts",
            preset='medium',  # Encoding speed vs quality
            crf=23  # Quality (lower = better)
        )
        
        # Run transcoding
        ffmpeg.run(output, capture_stdout=True, capture_stderr=True)
        
        # Upload to S3
        self.upload_to_s3(output_dir, video_id, profile_name)
        
        # Clean up
        import shutil
        shutil.rmtree(output_dir)
        
        return {
            'profile': profile_name,
            'path': f"{video_id}/{profile_name}/index.m3u8",
            'resolution': f"{profile['width']}x{profile['height']}",
            'bitrate': profile['bitrate']
        }
    
    def upload_to_s3(self, directory, video_id, profile_name):
        # Upload all files in directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            s3_key = f"{video_id}/{profile_name}/{filename}"
            
            content_type = 'application/vnd.apple.mpegurl' if filename.endswith('.m3u8') else 'video/MP2T'
            
            s3_client.upload_file(
                file_path,
                'video-processed-bucket',
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
    
    def generate_master_playlist(self, video_id, results):
        playlist = "#EXTM3U\n#EXT-X-VERSION:3\n"
        
        for result in sorted(results, key=lambda x: int(x['bitrate'].rstrip('k')), reverse=True):
            bitrate_kbps = int(result['bitrate'].rstrip('k'))
            width, height = result['resolution'].split('x')
            
            playlist += f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate_kbps * 1000},RESOLUTION={width}x{height}\n"
            playlist += f"{result['profile']}/index.m3u8\n"
        
        return playlist
```

**3. Priority Queue Management**

```python
class PriorityQueue:
    def __init__(self):
        self.queues = {
            'high': [],
            'normal': [],
            'low': []
        }
    
    def enqueue(self, job, priority='normal'):
        self.queues[priority].append(job)
    
    def dequeue(self):
        # Process high priority first
        for priority in ['high', 'normal', 'low']:
            if self.queues[priority]:
                return self.queues[priority].pop(0)
        return None
    
    def get_queue_sizes(self):
        return {p: len(q) for p, q in self.queues.items()}

# Set priority based on user tier or video importance
def determine_priority(user_id, video_metadata):
    user_tier = get_user_tier(user_id)
    
    if user_tier == 'premium':
        return 'high'
    elif video_metadata['duration'] < 60:  # Short videos
        return 'high'
    else:
        return 'normal'
```

**4. Auto-scaling Workers**

```python
# Kubernetes HPA (Horizontal Pod Autoscaler) configuration
"""
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: transcoding-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: transcoding-worker
  minReplicas: 5
  maxReplicas: 100
  metrics:
  - type: External
    external:
      metric:
        name: sqs_queue_depth
      target:
        type: AverageValue
        averageValue: "10"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
"""

# EC2 Spot Instances for cost optimization
def request_spot_instances(count):
    ec2_client = boto3.client('ec2')
    
    response = ec2_client.request_spot_instances(
        InstanceCount=count,
        Type='persistent',
        LaunchSpecification={
            'ImageId': 'ami-transcoding-worker',
            'InstanceType': 'c5.4xlarge',  # Compute optimized
            'KeyName': 'transcoding-key',
            'UserData': get_worker_userdata(),
            'IamInstanceProfile': {
                'Name': 'transcoding-worker-role'
            }
        },
        SpotPrice='0.20'  # Max price per hour
    )
    
    return response
```

**5. Thumbnail Generation**

```python
def generate_thumbnails(video_path, video_id, count=5):
    # Get video duration
    duration = get_video_duration(video_path)
    
    # Generate thumbnails at intervals
    thumbnails = []
    for i in range(count):
        timestamp = (duration / (count + 1)) * (i + 1)
        
        output_path = f"/tmp/{video_id}_thumb_{i}.jpg"
        
        # Extract frame at timestamp
        stream = ffmpeg.input(video_path, ss=timestamp)
        stream = ffmpeg.output(
            stream,
            output_path,
            vframes=1,
            format='image2',
            vcodec='mjpeg',
            **{'q:v': 2}  # Quality
        )
        ffmpeg.run(stream, quiet=True)
        
        # Upload to S3
        s3_key = f"{video_id}/thumbnails/thumb_{i}.jpg"
        s3_client.upload_file(
            output_path,
            'video-processed-bucket',
            s3_key,
            ExtraArgs={'ContentType': 'image/jpeg'}
        )
        
        thumbnails.append(s3_key)
        os.remove(output_path)
    
    return thumbnails
```

**6. Storage Tiering**

```python
# S3 Lifecycle Policy
lifecycle_policy = {
    "Rules": [
        {
            "Id": "MoveRawToGlacier",
            "Status": "Enabled",
            "Prefix": "raw/",
            "Transitions": [
                {
                    "Days": 7,
                    "StorageClass": "GLACIER"
                }
            ]
        },
        {
            "Id": "MoveUnpopularToIA",
            "Status": "Enabled",
            "Prefix": "processed/",
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        },
        {
            "Id": "DeleteOldRaw",
            "Status": "Enabled",
            "Prefix": "raw/",
            "Expiration": {
                "Days": 365
            }
        }
    ]
}

s3_client.put_bucket_lifecycle_configuration(
    Bucket='video-storage',
    LifecycleConfiguration=lifecycle_policy
)
```

**7. Progress Tracking**

```python
class TranscodingProgress:
    def __init__(self, video_id):
        self.video_id = video_id
        self.redis = redis.Redis()
    
    def update_progress(self, profile, percentage):
        key = f"transcode_progress:{self.video_id}:{profile}"
        self.redis.set(key, percentage, ex=3600)
        
        # Calculate overall progress
        profiles = ['1080p', '720p', '480p', '360p']
        total_progress = sum(
            float(self.redis.get(f"transcode_progress:{self.video_id}:{p}") or 0)
            for p in profiles
        ) / len(profiles)
        
        self.redis.set(
            f"transcode_progress:{self.video_id}",
            total_progress,
            ex=3600
        )
        
        # Send websocket update to user
        send_progress_update(self.video_id, total_progress)
    
    def get_progress(self):
        return float(self.redis.get(f"transcode_progress:{self.video_id}") or 0)

# Use with FFmpeg progress callback
def transcode_with_progress(input_path, output_path, video_id, profile):
    progress_tracker = TranscodingProgress(video_id)
    
    # FFmpeg with progress
    process = (
        ffmpeg
        .input(input_path)
        .output(output_path, **output_options)
        .global_args('-progress', 'pipe:1')
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    
    # Parse progress
    for line in process.stdout:
        if b'out_time_ms=' in line:
            time_ms = int(line.decode().split('=')[1])
            percentage = (time_ms / (duration * 1000)) * 100
            progress_tracker.update_progress(profile, percentage)
    
    process.wait()
```

**8. Error Handling & Retry**

```python
import tenacity

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=60),
    retry=tenacity.retry_if_exception_type(TranscodingError)
)
def transcode_with_retry(job):
    try:
        return worker.process_job(job)
    except ffmpeg.Error as e:
        # Log error
        log_transcoding_error(job['video_id'], str(e))
        
        # Determine if retriable
        if 'Codec not found' in str(e):
            # Not retriable
            mark_job_failed(job['video_id'], 'unsupported_codec')
            raise NonRetriableError(str(e))
        else:
            # Retriable
            raise TranscodingError(str(e))
```

**9. CDN Integration**

```python
import boto3

cloudfront = boto3.client('cloudfront')

def create_cdn_distribution(video_id):
    response = cloudfront.create_distribution(
        DistributionConfig={
            'CallerReference': str(uuid.uuid4()),
            'Origins': {
                'Quantity': 1,
                'Items': [{
                    'Id': 's3-origin',
                    'DomainName': 'video-processed-bucket.s3.amazonaws.com',
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                }]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 's3-origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'AllowedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD']
                },
                'Compress': True,
                'MinTTL': 86400  # 24 hours
            },
            'Enabled': True
        }
    )
    
    cdn_url = response['Distribution']['DomainName']
    
    return f"https://{cdn_url}/{video_id}/master.m3u8"
```

**10. Analytics & Monitoring**

```python
metrics = {
    'transcoding_duration': Histogram('transcoding_duration_seconds'),
    'transcoding_failures': Counter('transcoding_failures_total'),
    'queue_depth': Gauge('transcoding_queue_depth'),
    'worker_utilization': Gauge('worker_cpu_utilization_percent')
}

def monitor_transcoding(video_id, start_time, end_time, status):
    duration = end_time - start_time
    metrics['transcoding_duration'].observe(duration)
    
    if status == 'failed':
        metrics['transcoding_failures'].inc()
    
    # Log to analytics
    log_analytics({
        'video_id': video_id,
        'duration_seconds': duration,
        'status': status,
        'timestamp': datetime.now().isoformat()
    })
```

---

## 16. Design a Collaborative Editing System

### Requirements
- 100 triệu users
- Up to 50 concurrent editors/document
- Conflict resolution
- Offline sync
- Version history

### High-Level Architecture

```
[Clients (Web/Mobile)]
      ↓
[WebSocket Gateway]
      ↓
[Operational Transform / CRDT Engine]
      ↓
[Document State Service]
      ↓
[Document DB (MongoDB/Firestore)]
      ↓
[Version History (S3/DynamoDB)]
```

### Core Components

**1. Operational Transformation (OT)**

```python
class Operation:
    def __init__(self, op_type, position, content, user_id):
        self.type = op_type  # 'insert', 'delete', 'retain'
        self.position = position
        self.content = content
        self.user_id = user_id
        self.timestamp = time.time()

class OperationalTransform:
    @staticmethod
    def transform(op1, op2):
        """
        Transform two concurrent operations so they can be applied in any order
        """
        if op1.type == 'insert' and op2.type == 'insert':
            if op1.position < op2.position:
                return op1, Operation(op2.type, op2.position + len(op1.content), op2.content, op2.user_id)
            elif op1.position > op2.position:
                return Operation(op1.type, op1.position + len(op2.content), op1.content, op1.user_id), op2
            else:
                # Same position, use user_id as tiebreaker
                if op1.user_id < op2.user_id:
                    return op1, Operation(op2.type, op2.position + len(op1.content), op2.content, op2.user_id)
                else:
                    return Operation(op1.type, op1.position + len(op2.content), op1.content, op1.user_id), op2
        
        elif op1.type == 'insert' and op2.type == 'delete':
            if op1.position <= op2.position:
                return op1, Operation(op2.type, op2.position + len(op1.content), op2.content, op2.user_id)
            elif op1.position > op2.position + len(op2.content):
                return Operation(op1.type, op1.position - len(op2.content), op1.content, op1.user_id), op2
            else:
                # Insert position is within delete range
                return op1, Operation(op2.type, op2.position, op2.content[:op1.position - op2.position] + op2.content[op1.position - op2.position:], op2.user_id)
        
        elif op1.type == 'delete' and op2.type == 'insert':
            # Symmetric to above
            op2_prime, op1_prime = OperationalTransform.transform(op2, op1)
            return op1_prime, op2_prime
        
        elif op1.type == 'delete' and op2.type == 'delete':
            if op1.position + len(op1.content) <= op2.position:
                return op1, Operation(op2.type, op2.position - len(op1.content), op2.content, op2.user_id)
            elif op2.position + len(op2.content) <= op1.position:
                return Operation(op1.type, op1.position - len(op2.content), op1.content, op1.user_id), op2
            else:
                # Overlapping deletes
                # Complex case: merge the deletes
                start = min(op1.position, op2.position)
                end = max(op1.position + len(op1.content), op2.position + len(op2.content))
                merged_content = ''  # Content to delete
                return Operation('delete', start, merged_content, op1.user_id), None
        
        return op1, op2

class Document:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.content = ""
        self.version = 0
        self.pending_ops = []
    
    def apply_operation(self, operation):
        if operation.type == 'insert':
            self.content = (
                self.content[:operation.position] +
                operation.content +
                self.content[operation.position:]
            )
        elif operation.type == 'delete':
            self.content = (
                self.content[:operation.position] +
                self.content[operation.position + len(operation.content):]
            )
        
        self.version += 1
        
        return self.content
```

**2. CRDT (Conflict-Free Replicated Data Type)**

```python
import uuid
from typing import Dict, List, Tuple

class LSeq:
    """
    CRDT for collaborative text editing
    Uses Logoot-style positioning
    """
    def __init__(self, site_id):
        self.site_id = site_id
        self.sequence = []  # List of (position_id, character)
        self.clock = 0
    
    def insert(self, index, char):
        self.clock += 1
        
        # Generate position between previous and next
        if index == 0:
            prev_pos = None
            next_pos = self.sequence[0][0] if self.sequence else None
        elif index >= len(self.sequence):
            prev_pos = self.sequence[-1][0] if self.sequence else None
            next_pos = None
        else:
            prev_pos = self.sequence[index - 1][0]
            next_pos = self.sequence[index][0]
        
        new_pos = self.generate_position(prev_pos, next_pos)
        
        # Insert into sequence
        self.sequence.insert(index, (new_pos, char))
        
        return {
            'type': 'insert',
            'position': new_pos,
            'char': char,
            'site_id': self.site_id,
            'clock': self.clock
        }
    
    def delete(self, index):
        self.clock += 1
        
        pos_id, char = self.sequence[index]
        del self.sequence[index]
        
        return {
            'type': 'delete',
            'position': pos_id,
            'site_id': self.site_id,
            'clock': self.clock
        }
    
    def apply_remote_operation(self, operation):
        if operation['type'] == 'insert':
            # Find insertion point
            pos = operation['position']
            index = self.find_index(pos)
            self.sequence.insert(index, (pos, operation['char']))
        
        elif operation['type'] == 'delete':
            # Find deletion point
            pos = operation['position']
            index = self.find_index(pos)
            if index < len(self.sequence) and self.sequence[index][0] == pos:
                del self.sequence[index]
    
    def generate_position(self, prev_pos, next_pos):
        """
        Generate unique position ID between prev and next
        """
        if prev_pos is None:
            base = [0]
        else:
            base = list(prev_pos)
        
        if next_pos is None:
            base.append(self.clock)
            base.append(self.site_id)
            return tuple(base)
        
        # Find first position where they differ
        for i in range(min(len(base), len(next_pos))):
            if base[i] < next_pos[i]:
                # Can insert between
                base.append(self.clock)
                base.append(self.site_id)
                return tuple(base)
        
        # Need to extend
        base.append(self.clock)
        base.append(self.site_id)
        return tuple(base)
    
    def find_index(self, pos_id):
        # Binary search
        left, right = 0, len(self.sequence)
        
        while left < right:
            mid = (left + right) // 2
            if self.sequence[mid][0] < pos_id:
                left = mid + 1
            else:
                right = mid
        
        return left
    
    def get_text(self):
        return ''.join(char for _, char in self.sequence)
```

**3. WebSocket Server**

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_documents: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, doc_id: str, user_id: str):
        await websocket.accept()
        
        if doc_id not in self.active_connections:
            self.active_connections[doc_id] = set()
        
        self.active_connections[doc_id].add(websocket)
        self.user_documents[websocket] = doc_id
        
        # Send current document state
        document = await load_document(doc_id)
        await websocket.send_json({
            'type': 'init',
            'content': document['content'],
            'version': document['version'],
            'collaborators': len(self.active_connections[doc_id])
        })
        
        # Notify other users
        await self.broadcast(doc_id, {
            'type': 'user_joined',
            'user_id': user_id
        }, exclude=websocket)
    
    def disconnect(self, websocket: WebSocket):
        doc_id = self.user_documents.get(websocket)
        
        if doc_id and doc_id in self.active_connections:
            self.active_connections[doc_id].discard(websocket)
            
            if not self.active_connections[doc_id]:
                del self.active_connections[doc_id]
        
        if websocket in self.user_documents:
            del self.user_documents[websocket]
    
    async def broadcast(self, doc_id: str, message: dict, exclude: WebSocket = None):
        if doc_id in self.active_connections:
            for connection in self.active_connections[doc_id]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except:
                        pass

manager = ConnectionManager()

@app.websocket("/ws/{doc_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str, user_id: str):
    await manager.connect(websocket, doc_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process operation
            if data['type'] == 'operation':
                operation = data['operation']
                
                # Apply to document
                await apply_operation(doc_id, operation)
                
                # Broadcast to other users
                await manager.broadcast(doc_id, {
                    'type': 'operation',
                    'operation': operation,
                    'user_id': user_id
                }, exclude=websocket)
            
            elif data['type'] == 'cursor':
                # Broadcast cursor position
                await manager.broadcast(doc_id, {
                    'type': 'cursor',
                    'user_id': user_id,
                    'position': data['position']
                }, exclude=websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
        await manager.broadcast(doc_id, {
            'type': 'user_left',
            'user_id': user_id
        })
```

**4. Document Storage**

```python
from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient('mongodb://localhost:27017')
db = mongo_client['collaborative_docs']

async def load_document(doc_id):
    document = await db.documents.find_one({'_id': doc_id})
    
    if not document:
        # Create new document
        document = {
            '_id': doc_id,
            'content': '',
            'version': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        await db.documents.insert_one(document)
    
    return document

async def apply_operation(doc_id, operation):
    # Get document
    document = await db.documents.find_one({'_id': doc_id})
    
    # Apply operation to content
    doc_obj = Document(doc_id)
    doc_obj.content = document['content']
    doc_obj.version = document['version']
    
    new_content = doc_obj.apply_operation(operation)
    
    # Update database
    await db.documents.update_one(
        {'_id': doc_id},
        {
            '$set': {
                'content': new_content,
                'version': doc_obj.version,
                'updated_at': datetime.now()
            }
        }
    )
    
    # Save to version history
    await db.versions.insert_one({
        'doc_id': doc_id,
        'version': doc_obj.version,
        'operation': operation,
        'content_snapshot': new_content if doc_obj.version % 10 == 0 else None,  # Full snapshot every 10 versions
        'timestamp': datetime.now()
    })
```

**5. Offline Sync**

```python
class OfflineQueue:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.queue = []
        self.last_synced_version = 0
    
    def add_operation(self, operation):
        # Add to local queue
        self.queue.append(operation)
        
        # Save to IndexedDB (client-side)
        save_to_indexeddb(self.doc_id, self.queue)
    
    async def sync(self):
        if not self.queue:
            return
        
        # Get current server version
        server_version = await get_server_version(self.doc_id)
        
        # Transform local operations against server operations
        if server_version > self.last_synced_version:
            server_ops = await get_operations_since(
                self.doc_id,
                self.last_synced_version
            )
            
            # Transform local operations
            for server_op in server_ops:
                for i, local_op in enumerate(self.queue):
                    local_op_prime, server_op_prime = OperationalTransform.transform(
                        local_op, server_op
                    )
                    self.queue[i] = local_op_prime
        
        # Send operations to server
        for operation in self.queue:
            await send_operation(self.doc_id, operation)
        
        # Clear queue
        self.queue = []
        self.last_synced_version = server_version + len(self.queue)
        
        save_to_indexeddb(self.doc_id, self.queue)
```

**6. Version History & Restore**

```python
async def get_version_history(doc_id, limit=50):
    versions = await db.versions.find(
        {'doc_id': doc_id}
    ).sort('version', -1).limit(limit).to_list(length=limit)
    
    return [
        {
            'version': v['version'],
            'timestamp': v['timestamp'],
            'user_id': v['operation'].get('user_id'),
            'operation_type': v['operation'].get('type')
        }
        for v in versions
    ]

async def restore_version(doc_id, target_version):
    # Get latest snapshot before# Advanced System Design Solutions (11-20) - NAVER Interview

## 17. Design a Commenting and Review System (WEBTOON Comments / NAVER Shopping Reviews)

### Requirements
- 150 triệu users
- 500M comments/ngày
- Threading support
- Real-time updates
- Content moderation & anti-spam
- Sorting: newest, popular, relevant

### High-Level Architecture

```
[Client Apps]
      ↓
[API Gateway + Rate Limiter]
      ↓
[Comment Service Cluster]
      ↓
   ┌──┴────────┬─────────┬────────┐
   ↓           ↓         ↓        ↓
[Write DB]  [Read DB]  [Search] [Moderation]
(Cassandra) (Replica)  (ES)     Service (ML)
   ↓           ↓         ↓
[Notification Service] ←→ [Pub/Sub (Kafka)]
      ↓
[CDN for static content]
```

### Core Components

**1. Comment Data Model**

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List

class CommentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELETED = "deleted"

@dataclass
class Comment:
    comment_id: str
    content_id: str  # Article/Product/Episode ID
    content_type: str  # webtoon, shopping, news
    parent_id: Optional[str]  # For threading
    user_id: int
    text: str
    status: CommentStatus
    likes: int
    dislikes: int
    reply_count: int
    depth: int  # Thread depth (max 3)
    created_at: datetime
    updated_at: datetime
    metadata: dict  # Device, IP, etc.
```

**2. Comment Service Implementation**

```python
from fastapi import FastAPI, HTTPException
from cassandra.cluster import Cluster
import redis
import uuid

app = FastAPI()
cassandra = Cluster(['cassandra-node1', 'cassandra-node2']).connect('comments')
redis_client = redis.Redis(host='redis-cluster', decode_responses=True)

@app.post("/api/v1/comments")
async def create_comment(content_id: str, user_id: int, text: str, parent_id: str = None):
    # 1. Rate limiting
    if not check_rate_limit(user_id):
        raise HTTPException(429, "Too many comments")
    
    # 2. Content moderation
    moderation_result = await moderate_content(text, user_id)
    if moderation_result['blocked']:
        raise HTTPException(400, f"Comment blocked: {moderation_result['reason']}")
    
    # 3. Spam detection
    if await is_spam(text, user_id):
        raise HTTPException(400, "Spam detected")
    
    # 4. Create comment
    comment_id = str(uuid.uuid4())
    depth = 0
    
    if parent_id:
        parent = await get_comment(parent_id)
        if parent['depth'] >= 3:
            raise HTTPException(400, "Max thread depth reached")
        depth = parent['depth'] + 1
    
    comment = {
        'comment_id': comment_id,
        'content_id': content_id,
        'parent_id': parent_id,
        'user_id': user_id,
        'text': text,
        'status': 'approved' if moderation_result['auto_approve'] else 'pending',
        'likes': 0,
        'dislikes': 0,
        'reply_count': 0,
        'depth': depth,
        'created_at': datetime.now()
    }
    
    # 5. Save to Cassandra
    await save_comment(comment)
    
    # 6. Update parent reply count
    if parent_id:
        await increment_reply_count(parent_id)
    
    # 7. Publish event for real-time updates
    await publish_comment_event(content_id, comment)
    
    # 8. Index for search
    await index_comment(comment)
    
    return comment

@app.get("/api/v1/comments/{content_id}")
async def get_comments(content_id: str, sort: str = "newest", page: int = 1, limit: int = 20):
    # Check cache first
    cache_key = f"comments:{content_id}:{sort}:{page}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query based on sort
    if sort == "newest":
        comments = await get_comments_by_time(content_id, page, limit)
    elif sort == "popular":
        comments = await get_comments_by_popularity(content_id, page, limit)
    elif sort == "relevant":
        comments = await get_comments_by_relevance(content_id, page, limit)
    
    # Fetch replies for each comment
    for comment in comments:
        comment['replies'] = await get_replies(comment['comment_id'], limit=3)
    
    # Cache for 1 minute
    redis_client.setex(cache_key, 60, json.dumps(comments))
    
    return comments
```

**3. Content Moderation System**

```python
from transformers import pipeline
import re

class ContentModerator:
    def __init__(self):
        self.toxic_classifier = pipeline("text-classification", model="unitary/toxic-bert")
        self.spam_patterns = self.load_spam_patterns()
        self.banned_words = self.load_banned_words()
    
    async def moderate(self, text: str, user_id: int) -> dict:
        result = {
            'blocked': False,
            'reason': None,
            'auto_approve': True,
            'flags': []
        }
        
        # 1. Check banned words
        if self.contains_banned_words(text):
            result['blocked'] = True
            result['reason'] = 'banned_words'
            return result
        
        # 2. Check spam patterns
        if self.matches_spam_pattern(text):
            result['blocked'] = True
            result['reason'] = 'spam_pattern'
            return result
        
        # 3. ML toxicity check
        toxicity_score = await self.check_toxicity(text)
        if toxicity_score > 0.9:
            result['blocked'] = True
            result['reason'] = 'toxic_content'
            return result
        elif toxicity_score > 0.7:
            result['auto_approve'] = False
            result['flags'].append('needs_review')
        
        # 4. Check user history
        user_trust_score = await self.get_user_trust_score(user_id)
        if user_trust_score < 0.3:
            result['auto_approve'] = False
            result['flags'].append('low_trust_user')
        
        return result
    
    async def check_toxicity(self, text: str) -> float:
        result = self.toxic_classifier(text)[0]
        return result['score'] if result['label'] == 'toxic' else 1 - result['score']
    
    def contains_banned_words(self, text: str) -> bool:
        text_lower = text.lower()
        for word in self.banned_words:
            if word in text_lower:
                return True
        return False
    
    def matches_spam_pattern(self, text: str) -> bool:
        for pattern in self.spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
```

**4. Spam Detection**

```python
class SpamDetector:
    def __init__(self):
        self.redis = redis.Redis()
    
    async def is_spam(self, text: str, user_id: int) -> bool:
        # 1. Duplicate content check
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if self.redis.exists(f"comment_hash:{text_hash}"):
            return True
        
        # 2. Rate-based spam (too many comments in short time)
        recent_count = self.redis.incr(f"user_comments:{user_id}:minute")
        if recent_count == 1:
            self.redis.expire(f"user_comments:{user_id}:minute", 60)
        if recent_count > 10:
            return True
        
        # 3. Repetitive content from same user
        similarity = await self.check_similarity_with_recent(user_id, text)
        if similarity > 0.8:
            return True
        
        # Mark this comment hash
        self.redis.setex(f"comment_hash:{text_hash}", 3600, "1")
        
        return False
    
    async def check_similarity_with_recent(self, user_id: int, text: str) -> float:
        recent_comments = self.redis.lrange(f"user_recent_comments:{user_id}", 0, 9)
        
        if not recent_comments:
            return 0
        
        from difflib import SequenceMatcher
        
        max_similarity = 0
        for prev_text in recent_comments:
            similarity = SequenceMatcher(None, text.lower(), prev_text.decode().lower()).ratio()
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
```

**5. Real-time Updates with WebSocket**

```python
from fastapi import WebSocket
import asyncio

class CommentWebSocketManager:
    def __init__(self):
        self.connections: dict[str, set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, content_id: str):
        await websocket.accept()
        if content_id not in self.connections:
            self.connections[content_id] = set()
        self.connections[content_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, content_id: str):
        if content_id in self.connections:
            self.connections[content_id].discard(websocket)
    
    async def broadcast_comment(self, content_id: str, comment: dict):
        if content_id in self.connections:
            message = json.dumps({
                'type': 'new_comment',
                'data': comment
            })
            for connection in self.connections[content_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass

ws_manager = CommentWebSocketManager()

@app.websocket("/ws/comments/{content_id}")
async def websocket_endpoint(websocket: WebSocket, content_id: str):
    await ws_manager.connect(websocket, content_id)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        ws_manager.disconnect(websocket, content_id)
```

**6. Threading & Nested Comments**

```python
# Cassandra schema for efficient threading
"""
CREATE TABLE comments_by_content (
    content_id UUID,
    created_at TIMESTAMP,
    comment_id UUID,
    parent_id UUID,
    user_id BIGINT,
    text TEXT,
    likes INT,
    depth INT,
    PRIMARY KEY ((content_id), created_at, comment_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

CREATE TABLE replies_by_parent (
    parent_id UUID,
    created_at TIMESTAMP,
    comment_id UUID,
    user_id BIGINT,
    text TEXT,
    likes INT,
    PRIMARY KEY ((parent_id), created_at, comment_id)
) WITH CLUSTERING ORDER BY (created_at DESC);
"""

async def get_threaded_comments(content_id: str, limit: int = 20):
    # Get top-level comments
    top_level = await cassandra.execute_async("""
        SELECT * FROM comments_by_content
        WHERE content_id = ? AND depth = 0
        ORDER BY created_at DESC
        LIMIT ?
    """, [content_id, limit])
    
    # Fetch replies for each
    result = []
    for comment in top_level:
        comment_dict = dict(comment)
        comment_dict['replies'] = await get_replies(comment['comment_id'], limit=5)
        result.append(comment_dict)
    
    return result

async def get_replies(parent_id: str, limit: int = 5):
    replies = await cassandra.execute_async("""
        SELECT * FROM replies_by_parent
        WHERE parent_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, [parent_id, limit])
    
    return list(replies)
```

**7. Like/Dislike System**

```python
@app.post("/api/v1/comments/{comment_id}/like")
async def like_comment(comment_id: str, user_id: int):
    # Prevent duplicate likes
    like_key = f"like:{comment_id}:{user_id}"
    
    if redis_client.exists(like_key):
        raise HTTPException(400, "Already liked")
    
    # Atomic increment
    await cassandra.execute_async("""
        UPDATE comments SET likes = likes + 1 WHERE comment_id = ?
    """, [comment_id])
    
    # Mark as liked
    redis_client.set(like_key, "1")
    
    # Invalidate cache
    await invalidate_comment_cache(comment_id)
    
    return {"success": True}
```

**8. Sorting Strategies**

```python
async def get_comments_by_popularity(content_id: str, page: int, limit: int):
    # Use materialized view or secondary index
    offset = (page - 1) * limit
    
    # Score = likes - dislikes + reply_count * 2
    comments = await cassandra.execute_async("""
        SELECT * FROM comments_by_content
        WHERE content_id = ?
    """, [content_id])
    
    # Sort by popularity score
    sorted_comments = sorted(
        comments,
        key=lambda c: c['likes'] - c['dislikes'] + c['reply_count'] * 2,
        reverse=True
    )
    
    return sorted_comments[offset:offset + limit]

async def get_comments_by_relevance(content_id: str, page: int, limit: int):
    # Use Elasticsearch for relevance scoring
    query = {
        "query": {
            "bool": {
                "must": [{"term": {"content_id": content_id}}],
                "should": [
                    {"range": {"likes": {"gte": 10}}},
                    {"term": {"is_verified_user": True}},
                    {"range": {"created_at": {"gte": "now-24h"}}}
                ]
            }
        },
        "from": (page - 1) * limit,
        "size": limit
    }
    
    result = await es.search(index="comments", body=query)
    return [hit['_source'] for hit in result['hits']['hits']]
```

**9. Fan-out for Popular Content**

```python
class CommentFanOut:
    def __init__(self):
        self.hot_content_threshold = 1000  # Comments per hour
    
    async def handle_new_comment(self, content_id: str, comment: dict):
        # Check if content is "hot"
        hourly_count = redis_client.incr(f"content_comments_hourly:{content_id}")
        if hourly_count == 1:
            redis_client.expire(f"content_comments_hourly:{content_id}", 3600)
        
        if hourly_count > self.hot_content_threshold:
            # Hot content: use fan-out on read
            await self.store_in_main_feed(content_id, comment)
        else:
            # Normal: fan-out on write
            await self.fan_out_to_subscribers(content_id, comment)
    
    async def fan_out_to_subscribers(self, content_id: str, comment: dict):
        # Get subscribers (users following this content)
        subscribers = await get_content_subscribers(content_id)
        
        # Push to each subscriber's notification feed
        for user_id in subscribers[:1000]:  # Limit fan-out
            await push_notification(user_id, {
                'type': 'new_comment',
                'content_id': content_id,
                'comment': comment
            })
```

**10. Monitoring & Analytics**

```python
comment_metrics = {
    'comments_created': Counter('comments_created_total'),
    'comments_moderated': Counter('comments_moderated_total', ['action']),
    'comment_latency': Histogram('comment_creation_latency_seconds'),
    'spam_detected': Counter('spam_comments_detected_total')
}

async def track_comment_analytics(content_id: str, comment: dict):
    # Real-time analytics
    analytics_event = {
        'content_id': content_id,
        'user_id': comment['user_id'],
        'timestamp': datetime.now().isoformat(),
        'text_length': len(comment['text']),
        'has_parent': comment['parent_id'] is not None
    }
    
    # Send to Kafka for processing
    await kafka_producer.send('comment_analytics', analytics_event)
    
    # Update content engagement score
    redis_client.zincrby('content_engagement', 1, content_id)
```

---

## 18. Design a Location-Based Service (NAVER Maps)

### Requirements
- 200 triệu users
- 1 tỷ queries/ngày
- Real-time location search
- Routing & navigation
- Nearby recommendations
- Geo-sharding

### High-Level Architecture

```
[Mobile/Web Clients]
      ↓
[CDN (Map Tiles)]
      ↓
[API Gateway + Load Balancer]
      ↓
   ┌──┴────────┬─────────┬────────┐
   ↓           ↓         ↓        ↓
[Location  [Routing   [POI      [Traffic
 Service]   Service]  Service]   Service]
   ↓           ↓         ↓        ↓
[GeoDB (PostGIS)] [Graph DB] [Elasticsearch]
   ↓
[Real-time Traffic Data (Kafka)]
```

### Core Components

**1. Geospatial Data Model**

```python
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum

class POICategory(Enum):
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    HOTEL = "hotel"
    GAS_STATION = "gas_station"
    HOSPITAL = "hospital"
    SHOPPING = "shopping"
    PARKING = "parking"

@dataclass
class Location:
    latitude: float
    longitude: float
    
    def to_point(self):
        return f"POINT({self.longitude} {self.latitude})"

@dataclass
class POI:
    poi_id: str
    name: str
    category: POICategory
    location: Location
    address: str
    phone: Optional[str]
    rating: float
    review_count: int
    price_level: int
    opening_hours: dict
    photos: List[str]
    tags: List[str]

@dataclass
class BoundingBox:
    min_lat: float
    min_lng: float
    max_lat: float
    max_lng: float
```

**2. PostGIS Database Schema**

```sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- POI table with spatial index
CREATE TABLE pois (
    poi_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    location GEOGRAPHY(POINT, 4326),
    address TEXT,
    phone VARCHAR(20),
    rating DECIMAL(2,1),
    review_count INT DEFAULT 0,
    price_level INT,
    opening_hours JSONB,
    photos TEXT[],
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Spatial index for fast geo queries
CREATE INDEX idx_pois_location ON pois USING GIST(location);
CREATE INDEX idx_pois_category ON pois(category);
CREATE INDEX idx_pois_rating ON pois(rating DESC);

-- Road network for routing
CREATE TABLE road_segments (
    segment_id UUID PRIMARY KEY,
    name VARCHAR(255),
    road_class VARCHAR(20),  -- highway, primary, secondary, residential
    start_point GEOGRAPHY(POINT, 4326),
    end_point GEOGRAPHY(POINT, 4326),
    geometry GEOGRAPHY(LINESTRING, 4326),
    length_meters FLOAT,
    speed_limit INT,
    one_way BOOLEAN DEFAULT FALSE,
    traffic_factor FLOAT DEFAULT 1.0
);

CREATE INDEX idx_roads_geometry ON road_segments USING GIST(geometry);
```

**3. Location Service**

```python
from fastapi import FastAPI
import asyncpg
from typing import List

app = FastAPI()

@app.get("/api/v1/search/nearby")
async def search_nearby(
    lat: float, 
    lng: float, 
    radius_m: int = 1000,
    category: str = None,
    limit: int = 20
):
    query = """
        SELECT poi_id, name, category, 
               ST_AsText(location) as location,
               ST_Distance(location, ST_MakePoint($1, $2)::geography) as distance,
               rating, review_count
        FROM pois
        WHERE ST_DWithin(location, ST_MakePoint($1, $2)::geography, $3)
    """
    
    params = [lng, lat, radius_m]
    
    if category:
        query += " AND category = $4"
        params.append(category)
    
    query += " ORDER BY distance LIMIT $" + str(len(params) + 1)
    params.append(limit)
    
    async with db_pool.acquire() as conn:
        results = await conn.fetch(query, *params)
    
    return [dict(r) for r in results]

@app.get("/api/v1/search/bbox")
async def search_in_bbox(
    min_lat: float,
    min_lng: float, 
    max_lat: float,
    max_lng: float,
    category: str = None
):
    query = """
        SELECT poi_id, name, category, ST_AsText(location) as location
        FROM pois
        WHERE location && ST_MakeEnvelope($1, $2, $3, $4, 4326)
    """
    
    if category:
        query += " AND category = $5"
        params = [min_lng, min_lat, max_lng, max_lat, category]
    else:
        params = [min_lng, min_lat, max_lng, max_lat]
    
    async with db_pool.acquire() as conn:
        results = await conn.fetch(query, *params)
    
    return [dict(r) for r in results]
```

**4. Geohash-based Sharding**

```python
import geohash2

class GeoShardManager:
    def __init__(self, precision=4):
        self.precision = precision  # 4 = ~39km x 20km cells
        self.shards = {}
    
    def get_shard(self, lat: float, lng: float) -> str:
        gh = geohash2.encode(lat, lng, precision=self.precision)
        return f"geo_shard_{gh}"
    
    def get_shards_for_radius(self, lat: float, lng: float, radius_km: float) -> List[str]:
        # Get center geohash
        center_gh = geohash2.encode(lat, lng, precision=self.precision)
        
        # Get neighbors to cover radius
        neighbors = geohash2.neighbors(center_gh)
        all_hashes = [center_gh] + neighbors
        
        return [f"geo_shard_{gh}" for gh in all_hashes]
    
    def route_query(self, lat: float, lng: float, radius_km: float):
        shards = self.get_shards_for_radius(lat, lng, radius_km)
        
        # Query all relevant shards in parallel
        return shards

# Usage
shard_manager = GeoShardManager(precision=4)
shards = shard_manager.get_shards_for_radius(37.5665, 126.9780, 5)  # Seoul
```

**5. Routing Service (Dijkstra/A*)**

```python
import heapq
from typing import Dict, Tuple

class RoutingEngine:
    def __init__(self):
        self.graph = {}  # node_id -> [(neighbor_id, distance, road_segment)]
    
    def load_road_network(self, road_segments):
        for segment in road_segments:
            start = segment['start_node']
            end = segment['end_node']
            weight = segment['length_meters'] / (segment['speed_limit'] * segment['traffic_factor'])
            
            if start not in self.graph:
                self.graph[start] = []
            self.graph[start].append((end, weight, segment['segment_id']))
            
            if not segment['one_way']:
                if end not in self.graph:
                    self.graph[end] = []
                self.graph[end].append((start, weight, segment['segment_id']))
    
    def find_route(self, start_node: str, end_node: str) -> dict:
        # A* algorithm
        distances = {start_node: 0}
        previous = {}
        segments_used = {}
        
        pq = [(0, start_node)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == end_node:
                break
            
            for neighbor, weight, segment_id in self.graph.get(current, []):
                if neighbor in visited:
                    continue
                
                distance = current_dist + weight
                
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    segments_used[neighbor] = segment_id
                    
                    # A* heuristic
                    priority = distance + self.heuristic(neighbor, end_node)
                    heapq.heappush(pq, (priority, neighbor))
        
        # Reconstruct path
        path = []
        current = end_node
        while current in previous:
            path.append(segments_used[current])
            current = previous[current]
        
        path.reverse()
        
        return {
            'segments': path,
            'total_time': distances.get(end_node, float('inf')),
            'distance': sum(self.get_segment_length(s) for s in path)
        }
    
    def heuristic(self, node1: str, node2: str) -> float:
        # Haversine distance as heuristic
        lat1, lng1 = self.get_node_coords(node1)
        lat2, lng2 = self.get_node_coords(node2)
        return haversine_distance(lat1, lng1, lat2, lng2) / 100  # Assume 100 km/h max
```

**6. Real-time Traffic Integration**

```python
from kafka import KafkaConsumer
import asyncio

class TrafficService:
    def __init__(self):
        self.traffic_data = {}  # segment_id -> traffic_factor
        self.consumer = KafkaConsumer(
            'traffic_updates',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    
    async def start_consuming(self):
        for message in self.consumer:
            data = message.value
            segment_id = data['segment_id']
            
            # Update traffic factor based on speed vs speed limit
            current_speed = data['avg_speed']
            speed_limit = data['speed_limit']
            
            traffic_factor = min(current_speed / speed_limit, 1.0)
            self.traffic_data[segment_id] = traffic_factor
            
            # Update routing graph
            await routing_engine.update_traffic(segment_id, traffic_factor)
    
    def get_traffic_factor(self, segment_id: str) -> float:
        return self.traffic_data.get(segment_id, 1.0)
    
    def get_traffic_conditions(self, bbox: BoundingBox) -> List[dict]:
        # Return traffic conditions for map visualization
        conditions = []
        
        for segment_id, factor in self.traffic_data.items():
            segment = get_segment(segment_id)
            if is_in_bbox(segment, bbox):
                conditions.append({
                    'segment_id': segment_id,
                    'traffic_level': self.classify_traffic(factor),
                    'factor': factor
                })
        
        return conditions
    
    def classify_traffic(self, factor: float) -> str:
        if factor >= 0.8:
            return 'free_flow'
        elif factor >= 0.5:
            return 'moderate'
        elif factor >= 0.3:
            return 'heavy'
        else:
            return 'congested'
```

**7. Map Tile Service**

```python
import math

class TileServer:
    def __init__(self, tile_storage):
        self.storage = tile_storage
    
    def lat_lng_to_tile(self, lat: float, lng: float, zoom: int) -> Tuple[int, int]:
        n = 2 ** zoom
        x = int((lng + 180) / 360 * n)
        lat_rad = math.radians(lat)
        y = int((1 - math.log(math.tan(lat_rad) + 1/math.cos(lat_rad)) / math.pi) / 2 * n)
        return x, y
    
    async def get_tile(self, z: int, x: int, y: int, style: str = 'default'):
        # Check cache first
        cache_key = f"tile:{style}:{z}:{x}:{y}"
        cached = await redis_client.get(cache_key)
        if cached:
            return cached
        
        # Generate or fetch tile
        tile = await self.generate_tile(z, x, y, style)
        
        # Cache for 24 hours
        await redis_client.setex(cache_key, 86400, tile)
        
        return tile
    
    async def generate_tile(self, z: int, x: int, y: int, style: str):
        # Get bounding box for tile
        bbox = self.tile_to_bbox(z, x, y)
        
        # Fetch features in bbox
        features = await self.fetch_features(bbox, z)
        
        # Render to PNG/Vector
        if style == 'vector':
            return self.render_vector_tile(features)
        else:
            return self.render_raster_tile(features, style)
```

**8. POI Search with Elasticsearch**

```python
from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch(['http://elasticsearch:9200'])

async def search_pois(
    query: str,
    lat: float = None,
    lng: float = None,
    radius_km: float = None,
    categories: List[str] = None
) -> List[dict]:
    
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["name^3", "address", "tags"]
                        }
                    }
                ],
                "filter": []
            }
        }
    }
    
    # Add geo filter if location provided
    if lat and lng:
        geo_filter = {
            "geo_distance": {
                "distance": f"{radius_km or 10}km",
                "location": {"lat": lat, "lon": lng}
            }
        }
        body["query"]["bool"]["filter"].append(geo_filter)
        
        # Add distance scoring
        body["sort"] = [
            {
                "_geo_distance": {
                    "location": {"lat": lat, "lon": lng},
                    "order": "asc",
                    "unit": "km"
                }
            },
            {"_score": "desc"}
        ]
    
    # Add category filter
    if categories:
        body["query"]["bool"]["filter"].append({
            "terms": {"category": categories}
        })
    
    result = await es.search(index="pois", body=body, size=20)
    
    return [hit["_source"] for hit in result["hits"]["hits"]]
```

**9. Privacy & Anonymization**

```python
import hashlib
from datetime import datetime

class LocationPrivacy:
    def __init__(self):
        self.noise_factor = 0.001  # ~100m noise
    
    def anonymize_location(self, lat: float, lng: float, user_id: str) -> Tuple[float, float]:
        # Add deterministic noise based on user hash
        user_hash = hashlib.md5(user_id.encode()).hexdigest()
        noise_lat = (int(user_hash[:8], 16) / 2**32 - 0.5) * self.noise_factor
        noise_lng = (int(user_hash[8:16], 16) / 2**32 - 0.5) * self.noise_factor
        
        return lat + noise_lat, lng + noise_lng
    
    def aggregate_location_data(self, locations: List[dict], grid_size: float = 0.01):
        # K-anonymity through aggregation
        grid = {}
        
        for loc in locations:
            grid_key = (
                round(loc['lat'] / grid_size) * grid_size,
                round(loc['lng'] / grid_size) * grid_size
            )
            
            if grid_key not in grid:
                grid[grid_key] = 0
            grid[grid_key] += 1
        
        # Only return cells with k >= 5 users
        return {k: v for k, v in grid.items() if v >= 5}
    
    def should_store_history(self, user_id: str) -> bool:
        # Check user privacy settings
        settings = get_user_privacy_settings(user_id)
        return settings.get('location_history_enabled', False)
```

**10. Caching & Performance**

```python
class LocationCache:
    def __init__(self):
        self.redis = redis.Redis()
        self.local_cache = {}  # L1 cache
    
    async def get_nearby_cached(self, lat: float, lng: float, radius: int):
        # Round to cache grid
        cache_lat = round(lat, 3)
        cache_lng = round(lng, 3)
        cache_key = f"nearby:{cache_lat}:{cache_lng}:{radius}"
        
        # L1 check
        if cache_key in self.local_cache:
            return self.local_cache[cache_key]
        
        # L2 check
        cached = self.redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            self.local_cache[cache_key] = data
            return data
        
        return None
    
    async def cache_nearby(self, lat: float, lng: float, radius: int, data: List[dict]):
        cache_lat = round(lat, 3)
        cache_lng = round(lng, 3)
        cache_key = f"nearby:{cache_lat}:{cache_lng}:{radius}"
        
        # Store in both L1 and L2
        self.local_cache[cache_key] = data
        self.redis.setex(cache_key, 300, json.dumps(data))  # 5 min TTL
    
    async def invalidate_area(self, lat: float, lng: float, radius_km: float):
        # Invalidate all cache keys in affected area
        pattern = f"nearby:{round(lat, 2)}*:{round(lng, 2)}*"
        keys = self.redis.keys(pattern)
        
        if keys:
            self.redis.delete(*keys)
```

---

## 19. Design an Ad Serving System (NAVER Ads)

### Requirements
- 300 triệu users
- 1 tỷ impressions/ngày
- Real-time bidding (RTB)
- Targeting (demographics, interests, context)
- Low latency (<50ms)
- Analytics & fraud prevention

### High-Level Architecture

```
[Publisher Page/App]
      ↓
[Ad Request]
      ↓
[CDN Edge (Ad Tag)]
      ↓
[Ad Server Cluster]
      ↓
   ┌──┴────────┬─────────┬────────┐
   ↓           ↓         ↓        ↓
[Targeting  [Auction   [Fraud   [Creative
 Engine]    Service]   Detection] Storage]
   ↓           ↓         ↓
[Demand-Side Platforms (DSPs)]
   ↓
[Analytics & Reporting (Kafka → BigQuery)]
```

### Core Components

**1. Ad Request & Response Schema**

```python
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class AdFormat(Enum):
    BANNER = "banner"
    NATIVE = "native"
    VIDEO = "video"
    INTERSTITIAL = "interstitial"

class DeviceType(Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"

@dataclass
class AdRequest:
    request_id: str
    publisher_id: str
    placement_id: str
    ad_format: AdFormat
    device_type: DeviceType
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    page_url: str
    page_keywords: List[str]
    geo: Dict[str, str]  # country, region, city
    timestamp: float

@dataclass
class AdResponse:
    request_id: str
    ad_id: str
    creative_url: str
    click_url: str
    impression_url: str
    bid_price: float
    advertiser_id: str
```

**2. Ad Server Implementation**

```python
from fastapi import FastAPI, Request
import asyncio
import time

app = FastAPI()

@app.post("/api/v1/ad/request")
async def serve_ad(ad_request: AdRequest):
    start_time = time.time()
    
    # 1. Fraud check (non-blocking)
    fraud_task = asyncio.create_task(check_fraud(ad_request))
    
    # 2. Get user targeting profile
    user_profile = await get_user_profile(ad_request.user_id)
    
    # 3. Get eligible campaigns
    eligible_campaigns = await get_eligible_campaigns(
        ad_request,
        user_profile
    )
    
    if not eligible_campaigns:
        return {"status": "no_fill"}
    
    # 4. Run auction
    winning_bid = await run_auction(eligible_campaigns, ad_request)
    
    # 5. Wait for fraud check
    fraud_result = await fraud_task
    if fraud_result['is_fraud']:
        log_fraud_event(ad_request, fraud_result)
        return {"status": "no_fill"}
    
    # 6. Build response
    response = build_ad_response(winning_bid, ad_request)
    
    # 7. Log impression event
    asyncio.create_task(log_impression(response, ad_request))
    
    latency = (time.time() - start_time) * 1000
    metrics.observe('ad_latency_ms', latency)
    
    return response

async def get_eligible_campaigns(ad_request: AdRequest, user_profile: dict):
    # Query campaigns matching:
    # - Publisher/placement
    # - Ad format
    # - Geo targeting
    # - Device targeting
    # - Budget constraints
    # - Frequency caps
    
    cache_key = f"campaigns:{ad_request.placement_id}:{ad_request.geo['country']}"
    cached = await redis.get(cache_key)
    
    if cached:
        campaigns = json.loads(cached)
    else:
        campaigns = await db.query("""
            SELECT * FROM campaigns c
            JOIN campaign_targeting ct ON c.campaign_id = ct.campaign_id
            WHERE ct.placement_id = ?
            AND ct.geo_country = ?
            AND c.status = 'active'
            AND c.daily_budget > c.daily_spent
        """, ad_request.placement_id, ad_request.geo['country'])
        
        await redis.setex(cache_key, 60, json.dumps(campaigns))
    
    # Filter by user targeting
    return [c for c in campaigns if matches_targeting(c, user_profile, ad_request)]
```

**3. Real-Time Bidding (RTB) Auction**

```python
class AuctionService:
    def __init__(self):
        self.dsp_endpoints = {
            'dsp1': 'https://dsp1.example.com/bid',
            'dsp2': 'https://dsp2.example.com/bid',
        }
        self.timeout_ms = 100
    
    async def run_auction(self, campaigns: List[dict], ad_request: AdRequest):
        # First-price or second-price auction
        
        # 1. Send bid requests to DSPs
        bid_request = self.build_bid_request(ad_request)
        
        tasks = []
        for dsp_id, endpoint in self.dsp_endpoints.items():
            task = asyncio.create_task(
                self.request_bid(dsp_id, endpoint, bid_request)
            )
            tasks.append(task)
        
        # Also add internal campaigns
        for campaign in campaigns:
            bid = self.calculate_internal_bid(campaign, ad_request)
            tasks.append(asyncio.coroutine(lambda: bid)())
        
        # Wait for bids with timeout
        done, pending = await asyncio.wait(
            tasks,
            timeout=self.timeout_ms / 1000
        )
        
        # Cancel pending
        for task in pending:
            task.cancel()
        
        # Collect bids
        bids = []
        for task in done:
            try:
                bid = task.result()
                if bid and bid['price'] > 0:
                    bids.append(bid)
            except:
                pass
        
        if not bids:
            return None
        
        # 2. Run second-price auction
        sorted_bids = sorted(bids, key=lambda x: x['price'], reverse=True)
        winner = sorted_bids[0]
        
        # Winner pays second-highest price + 0.01
        if len(sorted_bids) > 1:
            winner['clearing_price'] = sorted_bids[1]['price'] + 0.01
        else:
            winner['clearing_price'] = winner['price']
        
        return winner
    
    async def request_bid(self, dsp_id: str, endpoint: str, bid_request: dict):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=bid_request,
                    timeout=aiohttp.ClientTimeout(total=self.timeout_ms/1000)
                ) as response:
                    if response.status == 200:
                        bid = await response.json()
                        bid['dsp_id'] = dsp_id
                        return bid
        except:
            return None
```

**4. Targeting Engine**

```python
class TargetingEngine:
    def matches_targeting(self, campaign: dict, user_profile: dict, ad_request: AdRequest) -> bool:
        targeting = campaign['targeting']
        
        # Geo targeting
        if 'geo' in targeting:
            if not self.matches_geo(targeting['geo'], ad_request.geo):
                return False
        
        # Device targeting
        if 'devices' in targeting:
            if ad_request.device_type.value not in targeting['devices']:
                return False
        
        # Demographics
        if 'demographics' in targeting:
            if not self.matches_demographics(targeting['demographics'], user_profile):
                return False
        
        # Interest targeting
        if 'interests' in targeting:
            user_interests = user_profile.get('interests', [])
            if not any(i in user_interests for i in targeting['interests']):
                return False
        
        # Frequency cap
        if not self.check_frequency_cap(campaign, user_profile):
            return False
        
        # Time targeting
        if 'schedule' in targeting:
            if not self.matches_schedule(targeting['schedule'], ad_request.timestamp):
                return False
        
        return True
    
    def check_frequency_cap(self, campaign: dict, user_profile: dict) -> bool:
        user_id = user_profile.get('user_id')
        if not user_id:
            return True
        
        cap = campaign.get('frequency_cap', {})
        max_impressions = cap.get('max_impressions', float('inf'))
        time_window = cap.get('time_window_hours', 24)
        
        key = f"freq:{campaign['campaign_id']}:{user_id}"
        current = redis.get(key)
        
        if current and int(current) >= max_impressions:
            return False
        
        return True
    
    def increment_frequency(self, campaign_id: str, user_id: str):
        key = f"freq:{campaign_id}:{user_id}"
        redis.incr(key)
        redis.expire(key, 86400)  # 24 hour window
```

**5. Fraud Detection**

```python
class FraudDetector:
    def __init__(self):
        self.ml_model = load_fraud_model()
        self.ip_blacklist = self.load_blacklist('ips')
        self.user_agent_blacklist = self.load_blacklist('user_agents')
    
    async def check_fraud(self, ad_request: AdRequest) -> dict:
        score = 0.0
        reasons = []
        
        # 1. IP blacklist check
        if ad_request.ip_address in self.ip_blacklist:
            return {'is_fraud': True, 'reason': 'blacklisted_ip', 'score': 1.0}
        
        # 2. User agent validation
        if self.is_invalid_user_agent(ad_request.user_agent):
            score += 0.3
            reasons.append('invalid_ua')
        
        # 3. Data center IP detection
        if await self.is_datacenter_ip(ad_request.ip_address):
            score += 0.4
            reasons.append('datacenter_ip')
        
        # 4. Request rate analysis
        rate = await self.get_request_rate(ad_request.ip_address)
        if rate > 100:  # Requests per minute
            score += 0.3
            reasons.append('high_rate')
        
        # 5. ML-based fraud detection
        features = self.extract_features(ad_request)
        ml_score = self.ml_model.predict_proba(features)[0][1]
        score = max(score, ml_score)
        
        # 6. Click pattern analysis (for click fraud)
        if ad_request.user_id:
            click_pattern = await self.analyze_click_pattern(ad_request.user_id)
            if click_pattern['suspicious']:
                score += 0.2
                reasons.append('suspicious_clicks')
        
        return {
            'is_fraud': score > 0.7,
            'score': score,
            'reasons': reasons
        }
    
    def is_invalid_user_agent(self, user_agent: str) -> bool:
        if not user_agent or len(user_agent) < 10:
            return True
        if user_agent in self.user_agent_blacklist:
            return True
        # Check for known bot patterns
        bot_patterns = ['bot', 'crawler', 'spider', 'headless']
        return any(p in user_agent.lower() for p in bot_patterns)
```

**6. Analytics & Reporting**

```python
from kafka import KafkaProducer

class AdAnalytics:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    
    async def log_impression(self, ad_response: dict, ad_request: AdRequest):
        event = {
            'event_type': 'impression',
            'request_id': ad_request.request_id,
            'ad_id': ad_response['ad_id'],
            'campaign_id': ad_response['campaign_id'],
            'advertiser_id': ad_response['advertiser_id'],
            'publisher_id': ad_request.publisher_id,
            'user_id': ad_request.user_id,
            'timestamp': time.time(),
            'bid_price': ad_response['clearing_price'],
            'geo': ad_request.geo,
            'device': ad_request.device_type.value
        }
        
        self.producer.send('ad_events', event)
        
        # Update real-time counters
        await self.update_counters(event)
    
    async def log_click(self, request_id: str, ad_id: str, user_id: str):
        event = {
            'event_type': 'click',
            'request_id': request_id,
            'ad_id': ad_id,
            'user_id': user_id,
            'timestamp': time.time()
        }
        
        self.producer.send('ad_events', event)
        
        # Update CTR metrics
        await self.update_ctr(ad_id)
    
    async def update_counters(self, event: dict):
        # Real-time aggregations in Redis
        hour = datetime.now().strftime('%Y%m%d%H')
        
        redis.hincrby(f"impressions:{hour}", event['campaign_id'], 1)
        redis.hincrbyfloat(f"spend:{hour}", event['campaign_id'], event['bid_price'])
        
        # Publisher revenue
        redis.hincrbyfloat(f"revenue:{hour}", event['publisher_id'], event['bid_price'] * 0.7)
```

**7. Budget Management**

```python
class BudgetManager:
    def __init__(self):
        self.redis = redis.Redis()
    
    async def check_budget(self, campaign_id: str, bid_amount: float) -> bool:
        # Daily budget check
        daily_key = f"spend:daily:{campaign_id}:{today()}"
        daily_spent = float(self.redis.get(daily_key) or 0)
        
        campaign = await get_campaign(campaign_id)
        if daily_spent + bid_amount > campaign['daily_budget']:
            return False
        
        # Lifetime budget check
        lifetime_key = f"spend:lifetime:{campaign_id}"
        lifetime_spent = float(self.redis.get(lifetime_key) or 0)
        
        if lifetime_spent + bid_amount > campaign['lifetime_budget']:
            return False
        
        return True
    
    async def record_spend(self, campaign_id: str, amount: float):
        # Atomic update
        daily_key = f"spend:daily:{campaign_id}:{today()}"
        lifetime_key = f"spend:lifetime:{campaign_id}"
        
        pipe = self.redis.pipeline()
        pipe.incrbyfloat(daily_key, amount)
        pipe.expire(daily_key, 86400 * 2)  # Keep 2 days
        pipe.incrbyfloat(lifetime_key, amount)
        pipe.execute()
        
        # Check if campaign should be paused
        await self.check_budget_exhausted(campaign_id)
    
    async def check_budget_exhausted(self, campaign_id: str):
        if not await self.check_budget(campaign_id, 0):
            # Pause campaign
            await db.execute("""
                UPDATE campaigns SET status = 'budget_exhausted'
                WHERE campaign_id = ?
            """, campaign_id)
            
            # Invalidate campaign cache
            await self.invalidate_campaign_cache(campaign_id)
```

**8. A/B Testing for Ads**

```python
class AdExperiment:
    def __init__(self):
        self.experiments = {}
    
    def get_experiment_variant(self, experiment_id: str, user_id: str) -> str:
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return 'control'
        
        # Consistent hashing for user assignment
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100
        
        cumulative = 0
        for variant, percentage in experiment['variants'].items():
            cumulative += percentage
            if bucket < cumulative:
                return variant
        
        return 'control'
    
    def track_conversion(self, experiment_id: str, variant: str, conversion_type: str):
        key = f"experiment:{experiment_id}:{variant}:{conversion_type}"
        redis.incr(key)
    
    def get_experiment_results(self, experiment_id: str) -> dict:
        results = {}
        experiment = self.experiments[experiment_id]
        
        for variant in experiment['variants']:
            impressions = int(redis.get(f"experiment:{experiment_id}:{variant}:impression") or 0)
            clicks = int(redis.get(f"experiment:{experiment_id}:{variant}:click") or 0)
            conversions = int(redis.get(f"experiment:{experiment_id}:{variant}:conversion") or 0)
            
            results[variant] = {
                'impressions': impressions,
                'clicks': clicks,
                'conversions': conversions,
                'ctr': clicks / impressions if impressions > 0 else 0,
                'cvr': conversions / clicks if clicks > 0 else 0
            }
        
        return results
```

**9. High Availability & Performance**

```python
# Multi-region deployment with edge computing
class AdServerCluster:
    def __init__(self):
        self.regions = ['us-east', 'us-west', 'eu-west', 'ap-northeast']
        self.local_cache = LRUCache(maxsize=10000)
    
    async def get_ads_with_fallback(self, ad_request: AdRequest):
        # Try local region first
        try:
            return await self.serve_local(ad_request)
        except Exception as e:
            # Fallback to other regions
            for region in self.regions:
                if region != self.current_region:
                    try:
                        return await self.serve_from_region(region, ad_request)
                    except:
                        continue
            
            # Return house ad as last resort
            return self.get_house_ad(ad_request)
    
    def get_house_ad(self, ad_request: AdRequest):
        # Return fallback/house advertisement
        return {
            'ad_id': 'house_ad',
            'creative_url': '/static/house_ads/default.jpg',
            'click_url': '/',
            'bid_price': 0
        }

# Connection pooling for database
from asyncpg import create_pool

db_pool = await create_pool(
    host='db-primary.internal',
    min_size=10,
    max_size=100,
    command_timeout=60
)
```

**10. GDPR & Privacy Compliance**

```python
class AdPrivacy:
    def __init__(self):
        self.consent_manager = ConsentManager()
    
    async def process_ad_request(self, ad_request: AdRequest):
        # Check user consent
        if ad_request.user_id:
            consent = await self.consent_manager.get_consent(ad_request.user_id)
            
            if not consent.get('personalized_ads', False):
                # Serve contextual ads only
                return await self.serve_contextual_ads(ad_request)
        
        # Full personalized ads
        return await self.serve_personalized_ads(ad_request)
    
    def anonymize_user_id(self, user_id: str) -> str:
        # Hash user ID for privacy
        return hashlib.sha256(f"{user_id}:{SALT}".encode()).hexdigest()[:32]
    
    async def handle_data_deletion(self, user_id: str):
        # GDPR right to erasure
        await redis.delete(f"user_profile:{user_id}")
        await redis.delete(f"user_interests:{user_id}")
        
        # Delete from all frequency caps
        keys = redis.keys(f"freq:*:{user_id}")
        if keys:
            redis.delete(*keys)
        
        # Log deletion
        await audit_log.log('data_deletion', user_id)
```

---

## 20. Design a Machine Learning Model Serving System (NAVER AI Recs)

### Requirements
- 500M inferences/ngày
- Real-time predictions (<10ms p99)
- A/B testing for models
- Model updates without downtime
- Monitoring for model drift
- Feature store integration

### High-Level Architecture

```
[Client Request]
      ↓
[API Gateway]
      ↓
[Load Balancer]
      ↓
[Model Router]
      ↓
   ┌──┴────────┬─────────┬────────┐
   ↓           ↓         ↓        ↓
[Model A    [Model B   [Model C  [Shadow
 v1.0]       v1.1]      v2.0]    Models]
   ↓           ↓         ↓
[Feature Store (Redis/Feast)]
   ↓
[Model Registry (MLflow)]
   ↓
[Monitoring (Prometheus + Grafana)]
```

### Core Components

**1. Model Server Implementation**

```python
from fastapi import FastAPI, HTTPException
import numpy as np
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any

app = FastAPI()

@dataclass
class PredictionRequest:
    model_name: str
    model_version: str
    features: Dict[str, Any]
    user_id: str
    request_id: str

@dataclass
class PredictionResponse:
    request_id: str
    predictions: List[float]
    model_version: str
    latency_ms: float

class ModelServer:
    def __init__(self):
        self.models = {}  # {model_name: {version: model}}
        self.model_registry = ModelRegistry()
        self.feature_store = FeatureStore()
    
    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        start_time = time.time()
        
        # 1. Get model
        model = self.get_model(request.model_name, request.model_version)
        if not model:
            raise HTTPException(404, f"Model {request.model_name}:{request.model_version} not found")
        
        # 2. Enrich features from feature store
        enriched_features = await self.feature_store.get_features(
            request.user_id,
            request.features
        )
        
        # 3. Preprocess features
        input_tensor = model.preprocess(enriched_features)
        
        # 4. Run inference
        predictions = await model.predict(input_tensor)
        
        # 5. Post-process
        result = model.postprocess(predictions)
        
        latency = (time.time() - start_time) * 1000
        
        # 6. Log for monitoring
        asyncio.create_task(self.log_prediction(request, result, latency))
        
        return PredictionResponse(
            request_id=request.request_id,
            predictions=result,
            model_version=request.model_version,
            latency_ms=latency
        )
    
    def get_model(self, model_name: str, version: str):
        if model_name in self.models:
            if version in self.models[model_name]:
                return self.models[model_name][version]
            elif version == "latest":
                return self.models[model_name][max(self.models[model_name].keys())]
        return None
    
    async def load_model(self, model_name: str, version: str):
        # Download from model registry
        model_artifact = await self.model_registry.download(model_name, version)
        
        # Load model based on framework
        if model_artifact['framework'] == 'tensorflow':
            model = TensorFlowModel.load(model_artifact['path'])
        elif model_artifact['framework'] == 'pytorch':
            model = PyTorchModel.load(model_artifact['path'])
        elif model_artifact['framework'] == 'sklearn':
            model = SklearnModel.load(model_artifact['path'])
        
        # Register
        if model_name not in self.models:
            self.models[model_name] = {}
        self.models[model_name][version] = model
        
        return model

@app.post("/api/v1/predict")
async def predict(request: PredictionRequest):
    return await model_server.predict(request)
```

**2. Model Wrapper Classes**

```python
import tensorflow as tf
import torch
import joblib

class BaseModel:
    def __init__(self, model, config):
        self.model = model
        self.config = config
    
    def preprocess(self, features: dict) -> np.ndarray:
        raise NotImplementedError
    
    async def predict(self, input_tensor: np.ndarray) -> np.ndarray:
        raise NotImplementedError
    
    def postprocess(self, predictions: np.ndarray) -> List[float]:
        raise NotImplementedError

class TensorFlowModel(BaseModel):
    @classmethod
    def load(cls, path: str):
        model = tf.saved_model.load(path)
        config = json.load(open(f"{path}/config.json"))
        return cls(model, config)
    
    def preprocess(self, features: dict) -> tf.Tensor:
        # Convert features to tensor
        feature_order = self.config['feature_order']
        values = [features[f] for f in feature_order]
        return tf.constant([values], dtype=tf.float32)
    
    async def predict(self, input_tensor: tf.Tensor) -> np.ndarray:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.model.signatures['serving_default'](input_tensor)
        )
        return result['predictions'].numpy()
    
    def postprocess(self, predictions: np.ndarray) -> List[float]:
        return predictions[0].tolist()

class PyTorchModel(BaseModel):
    @classmethod
    def load(cls, path: str):
        model = torch.jit.load(f"{path}/model.pt")
        model.eval()
        config = json.load(open(f"{path}/config.json"))
        return cls(model, config)
    
    async def predict(self, input_tensor: torch.Tensor) -> np.ndarray:
        with torch.no_grad():
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.model(input_tensor)
            )
        return result.numpy()
```

**3. Feature Store Integration**

```python
import redis
from feast import FeatureStore as FeastStore

class FeatureStore:
    def __init__(self):
        self.redis = redis.Redis(host='redis-features', decode_responses=True)
        self.feast = FeastStore(repo_path="feature_repo")
    
    async def get_features(self, user_id: str, request_features: dict) -> dict:
        # Combine request features with stored features
        enriched = request_features.copy()
        
        # 1. Get user features from Redis (fast path)
        user_features = await self.get_user_features(user_id)
        enriched.update(user_features)
        
        # 2. Get real-time features (if needed)
        realtime_features = await self.get_realtime_features(user_id)
        enriched.update(realtime_features)
        
        return enriched
    
    async def get_user_features(self, user_id: str) -> dict:
        cache_key = f"user_features:{user_id}"
        cached = self.redis.hgetall(cache_key)
        
        if cached:
            return {k: float(v) for k, v in cached.items()}
        
        # Fallback to Feast
        features = self.feast.get_online_features(
            features=[
                "user_features:age",
                "user_features:purchase_count_30d",
                "user_features:avg_session_duration",
                "user_features:interests_embedding"
            ],
            entity_rows=[{"user_id": user_id}]
        ).to_dict()
        
        # Cache for future
        self.redis.hset(cache_key, mapping=features)
        self.redis.expire(cache_key, 3600)
        
        return features
    
    async def get_realtime_features(self, user_id: str) -> dict:
        # Get features computed in real-time
        return {
            'session_page_views': await self.get_session_page_views(user_id),
            'time_since_last_action': await self.get_time_since_last_action(user_id),
            'current_hour': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }
```

**4. Model Router for A/B Testing**

```python
class ModelRouter:
    def __init__(self):
        self.experiments = {}
        self.traffic_allocator = TrafficAllocator()
    
    def get_model_version(self, model_name: str, user_id: str, request_id: str) -> str:
        # Check if there's an active experiment
        experiment = self.experiments.get(model_name)
        
        if not experiment or not experiment['active']:
            return experiment.get('default_version', 'latest')
        
        # Consistent hashing for user assignment
        variant = self.traffic_allocator.get_variant(
            experiment['id'],
            user_id
        )
        
        return experiment['variants'][variant]['model_version']
    
    def create_experiment(self, experiment_config: dict):
        experiment_id = str(uuid.uuid4())
        
        self.experiments[experiment_config['model_name']] = {
            'id': experiment_id,
            'active': True,
            'default_version': experiment_config['control_version'],
            'variants': experiment_config['variants'],
            'start_time': time.time(),
            'metrics': {}
        }
        
        return experiment_id
    
    async def record_experiment_outcome(self, experiment_id: str, variant: str, metric: str, value: float):
        # Record for statistical analysis
        key = f"experiment:{experiment_id}:{variant}:{metric}"
        redis.lpush(key, value)
        redis.ltrim(key, 0, 99999)  # Keep last 100k observations
    
    def get_experiment_results(self, experiment_id: str) -> dict:
        experiment = self.get_experiment_by_id(experiment_id)
        results = {}
        
        for variant_name, variant_config in experiment['variants'].items():
            results[variant_name] = {
                'predictions': self.get_variant_stats(experiment_id, variant_name, 'prediction_count'),
                'avg_latency': self.get_variant_stats(experiment_id, variant_name, 'latency'),
                'conversion_rate': self.get_variant_stats(experiment_id, variant_name, 'conversion')
            }
        
        # Calculate statistical significance
        results['statistical_significance'] = self.calculate_significance(results)
        
        return results

class TrafficAllocator:
    def get_variant(self, experiment_id: str, user_id: str) -> str:
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100
        
        experiment = experiments[experiment_id]
        cumulative = 0
        
        for variant, config in experiment['variants'].items():
            cumulative += config['traffic_percentage']
            if bucket < cumulative:
                return variant
        
        return 'control'
```

**5. Blue-Green & Canary Deployments**

```python
class ModelDeployment:
    def __init__(self):
        self.kubernetes = KubernetesClient()
    
    async def blue_green_deploy(self, model_name: str, new_version: str):
        # 1. Deploy new version (green)
        await self.deploy_model_version(model_name, new_version, replicas=3)
        
        # 2. Wait for healthy
        await self.wait_for_healthy(model_name, new_version)
        
        # 3. Switch traffic
        await self.update_service_selector(model_name, new_version)
        
        # 4. Keep old version for rollback (5 min)
        await asyncio.sleep(300)
        
        # 5. If no errors, scale down old version
        old_version = await self.get_current_version(model_name)
        if not await self.has_errors(model_name, new_version):
            await self.scale_down(model_name, old_version)
        else:
            # Rollback
            await self.update_service_selector(model_name, old_version)
            raise DeploymentError("Errors detected, rolled back")
    
    async def canary_deploy(self, model_name: str, new_version: str, stages: List[int]):
        # Progressive rollout: [5, 25, 50, 100]
        for percentage in stages:
            # Update traffic split
            await self.update_traffic_split(model_name, {
                'stable': 100 - percentage,
                'canary': percentage
            }, new_version)
            
            # Wait and monitor
            await asyncio.sleep(300)  # 5 minutes per stage
            
            # Check metrics
            metrics = await self.get_canary_metrics(model_name, new_version)
            
            if metrics['error_rate'] > 0.01 or metrics['latency_p99'] > 50:
                # Rollback
                await self.rollback_canary(model_name)
                raise DeploymentError(f"Canary failed at {percentage}%")
        
        # Promote canary to stable
        await self.promote_canary(model_name, new_version)
    
    async def update_traffic_split(self, model_name: str, split: dict, canary_version: str):
        # Using Istio VirtualService
        virtual_service = {
            'apiVersion': 'networking.istio.io/v1beta1',
            'kind': 'VirtualService',
            'spec': {
                'http': [{
                    'route': [
                        {
                            'destination': {'host': f'{model_name}-stable'},
                            'weight': split['stable']
                        },
                        {
                            'destination': {'host': f'{model_name}-canary'},
                            'weight': split['canary']
                        }
                    ]
                }]
            }
        }
        
        await self.kubernetes.apply(virtual_service)
```

**6. Model Drift Detection**

```python
from scipy import stats

class DriftDetector:
    def __init__(self):
        self.baseline_distributions = {}
        self.alert_threshold = 0.05  # p-value threshold
    
    async def check_drift(self, model_name: str) -> dict:
        results = {
            'has_drift': False,
            'features': {},
            'predictions': {}
        }
        
        # Get recent predictions
        recent_predictions = await self.get_recent_predictions(model_name, hours=24)
        baseline_predictions = self.baseline_distributions.get(f"{model_name}_predictions")
        
        if baseline_predictions:
            # KS test for prediction distribution
            ks_stat, p_value = stats.ks_2samp(
                baseline_predictions,
                recent_predictions
            )
            
            results['predictions'] = {
                'ks_statistic': ks_stat,
                'p_value': p_value,
                'drift_detected': p_value < self.alert_threshold
            }
            
            if p_value < self.alert_threshold:
                results['has_drift'] = True
        
        # Check feature distributions
        for feature_name in self.get_monitored_features(model_name):
            drift = await self.check_feature_drift(model_name, feature_name)
            results['features'][feature_name] = drift
            
            if drift['drift_detected']:
                results['has_drift'] = True
        
        # Alert if drift detected
        if results['has_drift']:
            await self.send_drift_alert(model_name, results)
        
        return results
    
    async def check_feature_drift(self, model_name: str, feature_name: str) -> dict:
        recent = await self.get_recent_feature_values(model_name, feature_name)
        baseline = self.baseline_distributions.get(f"{model_name}_{feature_name}")
        
        if not baseline:
            return {'drift_detected': False, 'reason': 'no_baseline'}
        
        # Population Stability Index (PSI)
        psi = self.calculate_psi(baseline, recent)
        
        return {
            'psi': psi,
            'drift_detected': psi > 0.2,  # PSI > 0.2 indicates significant drift
            'severity': 'high' if psi > 0.25 else 'medium' if psi > 0.1 else 'low'
        }
    
    def calculate_psi(self, expected: List[float], actual: List[float], buckets: int = 10) -> float:
        # Bin the data
        breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
        
        expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
        actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
        
        # Avoid log(0)
        expected_percents = np.clip(expected_percents, 0.0001, 1)
        actual_percents = np.clip(actual_percents, 0.0001, 1)
        
        psi = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
        
        return psi
```

**7. Model Registry (MLflow Integration)**

```python
import mlflow
from mlflow.tracking import MlflowClient

class ModelRegistry:
    def __init__(self):
        self.client = MlflowClient()
        mlflow.set_tracking_uri("http://mlflow-server:5000")
    
    async def register_model(self, model_name: str, model_path: str, metrics: dict):
        # Log model to MLflow
        with mlflow.start_run():
            mlflow.log_metrics(metrics)
            
            model_uri = mlflow.register_model(
                model_uri=model_path,
                name=model_name
            )
            
            return model_uri
    
    async def promote_model(self, model_name: str, version: int, stage: str):
        # Stages: Staging, Production, Archived
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
    
    async def download(self, model_name: str, version: str) -> dict:
        if version == "latest":
            version = self.get_latest_version(model_name)
        
        model_version = self.client.get_model_version(model_name, version)
        
        # Download artifact
        local_path = mlflow.artifacts.download_artifacts(
            artifact_uri=model_version.source
        )
        
        return {
            'path': local_path,
            'framework': model_version.tags.get('framework', 'unknown'),
            'version': version
        }
    
    def get_latest_version(self, model_name: str) -> str:
        versions = self.client.get_latest_versions(model_name, stages=["Production"])
        if versions:
            return versions[0].version
        return "1"
```

**8. Auto-Scaling**

```python
class ModelAutoScaler:
    def __init__(self):
        self.metrics_client = PrometheusClient()
        self.kubernetes = KubernetesClient()
    
    async def check_scaling(self, model_name: str):
        # Get current metrics
        metrics = await self.get_model_metrics(model_name)
        
        current_replicas = await self.get_current_replicas(model_name)
        
        # Scale based on latency and request rate
        target_replicas = self.calculate_target_replicas(metrics, current_replicas)
        
        if target_replicas != current_replicas:
            await self.scale(model_name, target_replicas)
    
    def calculate_target_replicas(self, metrics: dict, current: int) -> int:
        # Target: p99 latency < 10ms, requests per replica < 100/s
        
        if metrics['latency_p99'] > 15:
            # Scale up
            return min(current + 2, 20)  # Max 20 replicas
        elif metrics['latency_p99'] < 5 and current > 2:
            # Scale down
            return max(current - 1, 2)  # Min 2 replicas
        
        # Scale based on request rate
        requests_per_replica = metrics['request_rate'] / current
        
        if requests_per_replica > 100:
            return min(int(current * 1.5), 20)
        elif requests_per_replica < 30 and current > 2:
            return max(current - 1, 2)
        
        return current
    
    async def scale(self, model_name: str, replicas: int):
        await self.kubernetes.scale_deployment(
            namespace='ml-serving',
            deployment=f'{model_name}-serving',
            replicas=replicas
        )
        
        # Log scaling event
        await self.log_scaling_event(model_name, replicas)
```

**9. Monitoring & Observability**

```python
from prometheus_client import Counter, Histogram, Gauge

class ModelMetrics:
    def __init__(self):
        self.prediction_count = Counter(
            'model_predictions_total',
            'Total predictions',
            ['model_name', 'version']
        )
        self.prediction_latency = Histogram(
            'model_prediction_latency_seconds',
            'Prediction latency',
            ['model_name', 'version'],
            buckets=[.001, .005, .01, .025, .05, .1, .25, .5, 1]
        )
        self.prediction_errors = Counter(
            'model_prediction_errors_total',
            'Prediction errors',
            ['model_name', 'version', 'error_type']
        )
        self.model_memory = Gauge(
            'model_memory_bytes',
            'Model memory usage',
            ['model_name', 'version']
        )
    
    def record_prediction(self, model_name: str, version: str, latency: float, success: bool):
        self.prediction_count.labels(model_name, version).inc()
        self.prediction_latency.labels(model_name, version).observe(latency)
        
        if not success:
            self.prediction_errors.labels(model_name, version, 'inference_error').inc()
    
    async def export_to_dashboard(self, model_name: str):
        return {
            'total_predictions': self.prediction_count.labels(model_name).get(),
            'avg_latency_ms': self.prediction_latency.labels(model_name).observe() * 1000,
            'error_rate': self.prediction_errors.labels(model_name).get() / 
                         max(self.prediction_count.labels(model_name).get(), 1),
            'memory_mb': self.model_memory.labels(model_name).get() / (1024 * 1024)
        }
```

**10. Batch Inference Pipeline**

```python
class BatchInference:
    def __init__(self):
        self.spark = SparkSession.builder.appName("BatchInference").getOrCreate()
    
    async def run_batch_predictions(self, model_name: str, input_path: str, output_path: str):
        # Load model
        model = await model_server.get_model(model_name, "latest")
        broadcast_model = self.spark.sparkContext.broadcast(model)
        
        # Load data
        df = self.spark.read.parquet(input_path)
        
        # Define UDF for predictions
        @udf(ArrayType(FloatType()))
        def predict_udf(features):
            return broadcast_model.value.predict(features).tolist()
        
        # Run predictions
        result_df = df.withColumn(
            "predictions",
            predict_udf(col("features"))
        )
        
        # Save results
        result_df.write.parquet(output_path, mode="overwrite")
        
        # Log metrics
        total_rows = result_df.count()
        await self.log_batch_job(model_name, total_rows)
        
        return {
            'status': 'completed',
            'rows_processed': total_rows,
            'output_path': output_path
        }
```

---

## Tổng kết

Tài liệu này đã hoàn thành 10 câu hỏi system design (11-20) cho phỏng vấn NAVER:

| # | Hệ thống | Highlights |
|---|----------|------------|
| 11 | Autocomplete | Trie, Redis caching, multilingual, personalization ML |
| 12 | Payment Processing | Fraud detection, idempotency, double-entry ledger, PCI DSS |
| 13 | Distributed Cache | LRU/LFU/TTL, consistent hashing, cache patterns |
| 14 | Rate Limiter | Token bucket, sliding window, distributed limiting |
| 15 | Video Transcoding | FFmpeg workers, HLS/DASH, auto-scaling, CDN |
| 16 | Collaborative Editing | OT/CRDT, WebSocket, conflict resolution, offline sync |
| 17 | Commenting System | Threading, moderation ML, spam detection, fan-out |
| 18 | Location-Based Service | PostGIS, geohash sharding, routing A*, traffic |
| 19 | Ad Serving | RTB auction, targeting, fraud detection, GDPR |
| 20 | ML Model Serving | A/B testing, canary deploy, drift detection, MLflow |
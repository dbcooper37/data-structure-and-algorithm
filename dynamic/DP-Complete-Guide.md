# DYNAMIC PROGRAMMING - COMPLETE GUIDE
## Từ Tư Duy → Pattern → Tối Ưu → Bài Tập

> 🎯 **File duy nhất** gộp tất cả: tư duy giải bài, pattern nhận dạng, kỹ thuật tối ưu nâng cao (CHT, SOS), và bài tập có hướng dẫn.

---

# MỤC LỤC TỔNG QUAN

## PHẦN I: TƯ DUY CĂN BẢN
- [1. Nhận diện bài DP](#1-nhận-diện-bài-dp)
- [2. Mô hình 4 câu hỏi](#2-mô-hình-4-câu-hỏi)
- [3. Pipeline 6 bước](#3-pipeline-6-bước)
- [4. Top-Down vs Bottom-Up](#4-top-down-vs-bottom-up)

## PHẦN II: PATTERN NHẬN DẠNG
- [5. Linear DP](#5-linear-dp)
- [6. 2D DP (LCS, Edit Distance)](#6-2d-dp)
- [7. Knapsack Family](#7-knapsack-family)
- [8. Subsequence DP (LIS)](#8-subsequence-dp)
- [9. State Machine DP](#9-state-machine-dp)
- [10. Interval DP](#10-interval-dp)
- [11. Tree DP](#11-tree-dp)
- [12. Bitmask DP](#12-bitmask-dp)
- [13. Digit DP](#13-digit-dp)

## PHẦN III: TỐI ƯU NÂNG CAO
- [14. D&C Optimization](#14-dc-optimization)
- [15. Knuth Optimization](#15-knuth-optimization)
- [16. Convex Hull Trick (CHT)](#16-convex-hull-trick-cht) 🆕
- [17. SOS DP (Sum Over Subsets)](#17-sos-dp-sum-over-subsets) 🆕

## PHẦN IV: BÀI TẬP CÓ HƯỚNG DẪN
- [18. Bài tập theo Pattern](#18-bài-tập-theo-pattern) 🆕
- [19. Lộ trình luyện tập 4 tuần](#19-lộ-trình-luyện-tập)

---

# PHẦN I: TƯ DUY CĂN BẢN

## 1. Nhận diện bài DP

### 1.1 Từ khóa gợi ý

```
┌─────────────────────────────────────────────────────────────┐
│  TỐI ƯU: "min/max/shortest/largest..."                     │
│  ĐẾM:    "số cách/number of ways..."                       │
│  KHẢ THI: "có thể/possible/can..."                         │
│  CẤU TRÚC CON: "dãy con/tập con/đường đi..."              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Checklist 3 tính chất

| Tính chất | Câu hỏi kiểm tra |
|-----------|------------------|
| **Optimal Substructure** | Lời giải tối ưu dùng lời giải con tối ưu? |
| **Overlapping Subproblems** | Vẽ cây đệ quy, có nhánh lặp? |
| **No After-effect** | Giá trị dp[i] có đổi khi tính dp[i+1]? |

### 1.3 Phân biệt DP vs các kỹ thuật khác

| Kỹ thuật | Đặc điểm |
|----------|----------|
| **Greedy** | Local optimal = Global optimal |
| **DP** | Cần xét TẤT CẢ trường hợp |
| **Divide & Conquer** | Subproblems KHÔNG chồng chéo |
| **Backtracking** | Liệt kê TẤT CẢ lời giải |

---

## 2. Mô hình 4 câu hỏi

Khi gặp bài DP, trả lời theo thứ tự:

### Q1: Trạng thái cuối cùng là gì?
```
Climbing Stairs: "Đứng ở bậc n"
Knapsack: "Đã xét n vật, túi tối đa W kg"
LCS: "Đã xét toàn bộ s và t"
```

### Q2: Trước đó có thể đứng ở đâu?
```
Climbing Stairs: Bậc n-1 (leo 1) hoặc bậc n-2 (leo 2)
Knapsack: (n-1 vật, w) hoặc (n-1 vật, w-weight[n])
```

### Q3: Chi phí/giá trị thay đổi thế nào?
```
Climbing Stairs: dp[n] = dp[n-1] + dp[n-2]
Knapsack: dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt] + val)
```

### Q4: Base case là gì?
```
Climbing Stairs: dp[0]=1, dp[1]=1
Knapsack: dp[0][w]=0, dp[i][0]=0
```

---

## 3. Pipeline 6 bước

```
1. Chọn "trục" chia giai đoạn (i, t, w, (l,r)...)
2. Định nghĩa state: dp[...] = ? (một câu rõ ràng)
3. Liệt kê CHOICES tại mỗi state
4. Viết TRANSITION (min/max/sum)
5. Xác định BASE CASES + invalid states
6. Xác định ORDER (state nào tính trước?)
```

---

## 4. Top-Down vs Bottom-Up

### Top-Down (Memoization)
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def dp(state):
    if base_case: return value
    return combine(dp(prev_state) for choice in choices)
```

### Bottom-Up (Tabulation)
```python
dp = [0] * (n+1)
dp[0] = base_value
for i in range(1, n+1):
    dp[i] = transition(dp[i-1], dp[i-2], ...)
```

**Quy tắc chọn:**
- Top-Down: dễ nghĩ, chỉ tính states cần thiết
- Bottom-Up: nhanh hơn, dễ tối ưu memory

---

# PHẦN II: PATTERN NHẬN DẠNG

## 5. Linear DP

**Dấu hiệu:** Bài tiến theo i, mỗi bước nhìn vài bước trước.

### Climbing Stairs
```python
# dp[i] = số cách leo đến bậc i
dp[i] = dp[i-1] + dp[i-2]
```

### House Robber
```python
# dp[i] = max tiền cướp được xét đến nhà i
dp[i] = max(dp[i-1], dp[i-2] + money[i])
```

### Maximum Subarray (Kadane)
```python
# dp[i] = max sum ending at i
dp[i] = max(nums[i], dp[i-1] + nums[i])
answer = max(dp)
```

---

## 6. 2D DP

**Dấu hiệu:** 2 chuỗi/mảng, prefix matching.

### LCS (Longest Common Subsequence)
```python
def lcs(s, t):
    n, m = len(s), len(t)
    dp = [[0]*(m+1) for _ in range(n+1)]
    
    for i in range(1, n+1):
        for j in range(1, m+1):
            if s[i-1] == t[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[n][m]
```

### Edit Distance
```python
def edit_distance(a, b):
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    
    for i in range(n+1): dp[i][0] = i
    for j in range(m+1): dp[0][j] = j
    
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[n][m]
```

---

## 7. Knapsack Family

### 7.1 0-1 Knapsack (mỗi vật 1 lần)
```python
# DUYỆT NGƯỢC để mỗi item chỉ dùng 1 lần
for i, (w, v) in enumerate(items):
    for cap in range(W, w-1, -1):
        dp[cap] = max(dp[cap], dp[cap-w] + v)
```

### 7.2 Unbounded Knapsack (vô hạn)
```python
# DUYỆT XUÔI để cho phép dùng lại
for w, v in items:
    for cap in range(w, W+1):
        dp[cap] = max(dp[cap], dp[cap-w] + v)
```

### 7.3 Coin Change (min coins)
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for w in range(coin, amount + 1):
            dp[w] = min(dp[w], dp[w-coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

### 7.4 Subset Sum (boolean)
```python
dp = [False] * (target + 1)
dp[0] = True
for x in nums:
    for w in range(target, x-1, -1):
        dp[w] = dp[w] or dp[w-x]
```

---

## 8. Subsequence DP

### LIS O(n²)
```python
def lis(nums):
    n = len(nums)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

### LIS O(n log n)
```python
from bisect import bisect_left

def lis_fast(nums):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```

---

## 9. State Machine DP

**Dấu hiệu:** "mua/bán", "cooldown", "tối đa k lần".

### Stock với Cooldown
```python
def stock_cooldown(prices):
    hold, sold, rest = -float('inf'), -float('inf'), 0
    for p in prices:
        prev_sold = sold
        sold = hold + p
        hold = max(hold, rest - p)
        rest = max(rest, prev_sold)
    return max(rest, sold)
```

### Stock với K transactions
```python
def stock_k(prices, k):
    if k >= len(prices) // 2:
        return sum(max(0, prices[i]-prices[i-1]) for i in range(1, len(prices)))
    
    hold = [-float('inf')] * (k+1)
    cash = [0] * (k+1)
    for p in prices:
        for t in range(1, k+1):
            hold[t] = max(hold[t], cash[t-1] - p)
            cash[t] = max(cash[t], hold[t] + p)
    return cash[k]
```

---

## 10. Interval DP

**Dấu hiệu:** Tối ưu trên đoạn [l,r], "ghép", "chia", "burst".

### Template Split/Merge
```python
for length in range(2, n+1):
    for l in range(n - length + 1):
        r = l + length - 1
        dp[l][r] = INF
        for k in range(l, r):
            dp[l][r] = min(dp[l][r], dp[l][k] + dp[k+1][r] + cost(l,r))
```

### Burst Balloons (Choose-last)
```python
def burst_balloons(nums):
    a = [1] + nums + [1]
    n = len(a)
    dp = [[0]*n for _ in range(n)]
    
    for length in range(2, n):
        for l in range(n - length):
            r = l + length
            for k in range(l+1, r):
                dp[l][r] = max(dp[l][r], dp[l][k] + dp[k][r] + a[l]*a[k]*a[r])
    return dp[0][n-1]
```

---

## 11. Tree DP

**Dấu hiệu:** Cấu trúc cây, chọn/bỏ node.

```python
def tree_dp(u, parent):
    dp0, dp1 = 0, value[u]  # không chọn u, chọn u
    for v in adj[u]:
        if v == parent: continue
        c0, c1 = tree_dp(v, u)
        dp0 += max(c0, c1)  # không chọn u → con tùy ý
        dp1 += c0           # chọn u → không chọn con
    return dp0, dp1
```

---

## 12. Bitmask DP

**Dấu hiệu:** n nhỏ (≤20), xét subset.

### TSP
```python
def tsp(dist):
    n = len(dist)
    dp = [[INF]*n for _ in range(1<<n)]
    dp[1][0] = 0
    
    for mask in range(1<<n):
        for u in range(n):
            if dp[mask][u] >= INF: continue
            for v in range(n):
                if mask & (1<<v): continue
                dp[mask|(1<<v)][v] = min(dp[mask|(1<<v)][v], dp[mask][u] + dist[u][v])
    
    return min(dp[(1<<n)-1][u] + dist[u][0] for u in range(n))
```

---

## 13. Digit DP

**Dấu hiệu:** Đếm số trong [L,R] thỏa điều kiện theo chữ số.

```python
from functools import lru_cache

def count_upto(x):
    digits = list(map(int, str(x)))
    n = len(digits)
    
    @lru_cache(maxsize=None)
    def dfs(pos, state, tight, started):
        if pos == n:
            return 1 if started and is_valid(state) else 0
        
        limit = digits[pos] if tight else 9
        res = 0
        for d in range(0, limit+1):
            nstarted = started or d != 0
            nstate = transition(state, d) if nstarted else state
            res += dfs(pos+1, nstate, tight and d==limit, nstarted)
        return res
    
    return dfs(0, initial_state, True, False)

# Answer = count_upto(R) - count_upto(L-1)
```

---

# PHẦN III: TỐI ƯU NÂNG CAO

## 14. D&C Optimization

**Áp dụng khi:** `dp[i][j] = min(dp[i-1][k] + C(k+1,j))` với `opt[i][j]` đơn điệu.

```python
def compute(l, r, optl, optr, dp_prev, dp_cur):
    if l > r: return
    mid = (l + r) // 2
    best_k, best_val = -1, INF
    
    for k in range(optl, min(mid, optr) + 1):
        val = dp_prev[k] + cost(k+1, mid)
        if val < best_val:
            best_val, best_k = val, k
    
    dp_cur[mid] = best_val
    compute(l, mid-1, optl, best_k, dp_prev, dp_cur)
    compute(mid+1, r, best_k, optr, dp_prev, dp_cur)
```

---

## 15. Knuth Optimization

**Áp dụng khi:** Interval DP với `opt[l][r-1] ≤ opt[l][r] ≤ opt[l+1][r]`

```python
for length in range(2, n+1):
    for l in range(n - length + 1):
        r = l + length - 1
        start, end = opt[l][r-1], opt[l+1][r]
        for k in range(start, end+1):
            val = dp[l][k] + dp[k+1][r] + cost(l,r)
            if val < dp[l][r]:
                dp[l][r], opt[l][r] = val, k
```

---

## 16. Convex Hull Trick (CHT)

**Áp dụng khi:** `dp[i] = min(dp[j] + b[j] * a[i])` với b[j] đơn điệu.

### Ý tưởng
- Mỗi j tạo đường thẳng: `y = b[j] * x + dp[j]`
- Query tại x = a[i]: tìm min y trên tập đường thẳng
- Duy trì **convex hull** (lower envelope)

### Template (b giảm dần, a tăng dần)
```python
class CHT:
    def __init__(self):
        self.lines = []  # list of (slope, intercept)
    
    def bad(self, l1, l2, l3):
        # l2 không cần thiết nếu giao điểm l1-l3 bên trái giao điểm l1-l2
        return (l3[1]-l1[1]) * (l1[0]-l2[0]) <= (l2[1]-l1[1]) * (l1[0]-l3[0])
    
    def add(self, m, c):
        # Thêm đường y = mx + c (m giảm dần)
        line = (m, c)
        while len(self.lines) >= 2 and self.bad(self.lines[-2], self.lines[-1], line):
            self.lines.pop()
        self.lines.append(line)
    
    def query(self, x):
        # Trả về min(mx + c) tại x (x tăng dần)
        while len(self.lines) >= 2:
            m1, c1 = self.lines[0]
            m2, c2 = self.lines[1]
            if m1 * x + c1 >= m2 * x + c2:
                self.lines.pop(0)
            else:
                break
        m, c = self.lines[0]
        return m * x + c

# Ví dụ: dp[i] = min(dp[j] + b[j] * a[i]) với b giảm, a tăng
def solve_cht(a, b, initial_dp):
    n = len(a)
    dp = [0] * n
    cht = CHT()
    
    for i in range(n):
        if i > 0:
            dp[i] = cht.query(a[i])
        else:
            dp[i] = initial_dp
        cht.add(b[i], dp[i])
    
    return dp
```

### Ví dụ bài toán: "Covered Walkway" (USACO)
```
Có n người đứng tại vị trí x[i].
Muốn xây mái che sao cho tổng cost nhỏ nhất.
Cost mái che từ i đến j = C + (x[j] - x[i])²

dp[i] = min(dp[j] + C + (x[i] - x[j])²)
      = min(dp[j] + x[j]² - 2*x[i]*x[j]) + x[i]² + C
      
Đặt b[j] = -2*x[j], c[j] = dp[j] + x[j]²
→ dp[i] = min(b[j]*x[i] + c[j]) + x[i]² + C
→ Dùng CHT!
```

### Khi nào KHÔNG dùng được CHT đơn giản?
- Nếu b[j] không đơn điệu → dùng **Li Chao Tree** hoặc CHT với binary search
- Nếu a[i] không đơn điệu → dùng binary search trong hull

---

## 17. SOS DP (Sum Over Subsets)

**Bài toán:** Với mỗi mask, tính tổng f[submask] cho mọi submask ⊆ mask.

### Brute Force: O(3^n)
```python
for mask in range(1<<n):
    for submask in all_submasks(mask):
        sos[mask] += f[submask]
```

### SOS DP: O(n * 2^n)
```python
def sos_dp(f, n):
    # sos[mask] = sum of f[submask] for all submask ⊆ mask
    sos = f.copy()
    
    for bit in range(n):
        for mask in range(1<<n):
            if mask & (1<<bit):
                sos[mask] += sos[mask ^ (1<<bit)]
    
    return sos
```

### Ý tưởng
- Xây dựng theo từng bit
- `sos[mask][bit]` = tổng f của các subset chỉ khác mask ở bit 0..bit-1
- Tiết kiệm từ O(3^n) xuống O(n * 2^n)

### Ví dụ 1: Đếm cặp (i,j) sao cho A[i] AND A[j] = 0
```python
def count_and_zero_pairs(arr):
    MAX_VAL = max(arr) + 1
    n = MAX_VAL.bit_length()
    
    # cnt[mask] = số phần tử = mask
    cnt = [0] * (1<<n)
    for x in arr:
        cnt[x] += 1
    
    # sos[mask] = số phần tử là subset của mask
    sos = sos_dp(cnt, n)
    
    # Với mỗi x, số phần tử y thỏa x AND y = 0
    # <=> y là subset của ~x (complement)
    result = 0
    for x in arr:
        complement = ((1<<n) - 1) ^ x
        result += sos[complement]
    
    return result // 2  # mỗi cặp đếm 2 lần
```

### Ví dụ 2: Tìm max(A[i] + A[j]) với A[i] OR A[j] = A[i] + A[j] (tức AND = 0)
```python
def max_sum_disjoint_bits(arr):
    MAX_VAL = max(arr) + 1
    n = MAX_VAL.bit_length()
    
    # best[mask] = giá trị lớn nhất trong các số là subset của mask
    best = [-float('inf')] * (1<<n)
    for x in arr:
        best[x] = max(best[x], x)
    
    # SOS để tìm max thay vì sum
    for bit in range(n):
        for mask in range(1<<n):
            if mask & (1<<bit):
                best[mask] = max(best[mask], best[mask ^ (1<<bit)])
    
    result = 0
    for x in arr:
        complement = ((1<<n) - 1) ^ x
        if best[complement] > -float('inf'):
            result = max(result, x + best[complement])
    
    return result
```

### Superset SOS (ngược lại)
```python
def superset_sos(f, n):
    # sos[mask] = sum of f[supermask] for all supermask ⊇ mask
    sos = f.copy()
    
    for bit in range(n):
        for mask in range((1<<n)-1, -1, -1):
            if not (mask & (1<<bit)):
                sos[mask] += sos[mask | (1<<bit)]
    
    return sos
```

---

# PHẦN IV: BÀI TẬP CÓ HƯỚNG DẪN

## 18. Bài tập theo Pattern

### 18.1 Linear DP

| # | Bài | Độ khó | Gợi ý |
|---|-----|--------|-------|
| 1 | [LC 70. Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) | Easy | dp[i] = dp[i-1] + dp[i-2] |
| 2 | [LC 198. House Robber](https://leetcode.com/problems/house-robber/) | Medium | dp[i] = max(dp[i-1], dp[i-2] + nums[i]) |
| 3 | [LC 213. House Robber II](https://leetcode.com/problems/house-robber-ii/) | Medium | Chia 2 case: bỏ nhà đầu hoặc bỏ nhà cuối |
| 4 | [LC 53. Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) | Medium | Kadane's algorithm |
| 5 | [LC 152. Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/) | Medium | Track cả max và min (vì âm * âm = dương) |

<details>
<summary><b>Lời giải House Robber II</b></summary>

```python
def rob(nums):
    if len(nums) == 1:
        return nums[0]
    
    def rob_linear(arr):
        if not arr: return 0
        if len(arr) == 1: return arr[0]
        dp = [0] * len(arr)
        dp[0] = arr[0]
        dp[1] = max(arr[0], arr[1])
        for i in range(2, len(arr)):
            dp[i] = max(dp[i-1], dp[i-2] + arr[i])
        return dp[-1]
    
    # Case 1: bỏ nhà cuối (nums[0..n-2])
    # Case 2: bỏ nhà đầu (nums[1..n-1])
    return max(rob_linear(nums[:-1]), rob_linear(nums[1:]))
```
</details>

---

### 18.2 Knapsack

| # | Bài | Độ khó | Gợi ý |
|---|-----|--------|-------|
| 1 | [LC 416. Partition Equal Subset Sum](https://leetcode.com/problems/partition-equal-subset-sum/) | Medium | Subset sum với target = sum/2 |
| 2 | [LC 494. Target Sum](https://leetcode.com/problems/target-sum/) | Medium | dp[sum] = số cách đạt sum |
| 3 | [LC 322. Coin Change](https://leetcode.com/problems/coin-change/) | Medium | Unbounded knapsack, min coins |
| 4 | [LC 518. Coin Change 2](https://leetcode.com/problems/coin-change-2/) | Medium | Đếm số cách, duyệt coin ngoài |
| 5 | [LC 474. Ones and Zeroes](https://leetcode.com/problems/ones-and-zeroes/) | Medium | 2D knapsack (m zeros, n ones) |

<details>
<summary><b>Lời giải Target Sum</b></summary>

```python
def findTargetSumWays(nums, target):
    total = sum(nums)
    # P - N = target, P + N = total
    # => P = (target + total) / 2
    if (target + total) % 2 or abs(target) > total:
        return 0
    
    P = (target + total) // 2
    dp = [0] * (P + 1)
    dp[0] = 1
    
    for x in nums:
        for w in range(P, x-1, -1):  # 0-1 knapsack
            dp[w] += dp[w-x]
    
    return dp[P]
```
</details>

---

### 18.3 Subsequence

| # | Bài | Độ khó | Gợi ý |
|---|-----|--------|-------|
| 1 | [LC 300. LIS](https://leetcode.com/problems/longest-increasing-subsequence/) | Medium | dp[i] = LIS ending at i |
| 2 | [LC 1143. LCS](https://leetcode.com/problems/longest-common-subsequence/) | Medium | 2D DP chuẩn |
| 3 | [LC 516. Longest Palindromic Subsequence](https://leetcode.com/problems/longest-palindromic-subsequence/) | Medium | LCS(s, reverse(s)) |
| 4 | [LC 72. Edit Distance](https://leetcode.com/problems/edit-distance/) | Hard | 3 operations: insert, delete, replace |
| 5 | [LC 583. Delete Operation for Two Strings](https://leetcode.com/problems/delete-operation-for-two-strings/) | Medium | m + n - 2 * LCS |

<details>
<summary><b>Lời giải Palindromic Subsequence</b></summary>

```python
def longestPalindromeSubseq(s):
    # LPS(s) = LCS(s, reverse(s))
    t = s[::-1]
    n = len(s)
    dp = [[0]*(n+1) for _ in range(n+1)]
    
    for i in range(1, n+1):
        for j in range(1, n+1):
            if s[i-1] == t[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[n][n]
```
</details>

---

### 18.4 Interval DP

| # | Bài | Độ khó | Gợi ý |
|---|-----|--------|-------|
| 1 | [LC 312. Burst Balloons](https://leetcode.com/problems/burst-balloons/) | Hard | Choose-last (balloon cuối cùng trong đoạn) |
| 2 | [LC 1039. Minimum Score Triangulation](https://leetcode.com/problems/minimum-score-triangulation-of-polygon/) | Medium | Chọn đỉnh k làm tam giác với l, r |
| 3 | [LC 87. Scramble String](https://leetcode.com/problems/scramble-string/) | Hard | dp[l1][l2][len] |
| 4 | [LC 1000. Minimum Cost to Merge Stones](https://leetcode.com/problems/minimum-cost-to-merge-stones/) | Hard | Gộp K viên mỗi lần |

---

### 18.5 State Machine

| # | Bài | Độ khó | Gợi ý |
|---|-----|--------|-------|
| 1 | [LC 121. Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Easy | Track min so far |
| 2 | [LC 122. ... (Unlimited transactions)](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) | Medium | Greedy: mua mọi uptrend |
| 3 | [LC 123. ... (At most 2 transactions)](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/) | Hard | dp[trans][hold/cash] |
| 4 | [LC 309. ... with Cooldown](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/) | Medium | 3 states: hold, sold, rest |
| 5 | [LC 714. ... with Transaction Fee](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/) | Medium | hold[i] = max(hold[i-1], cash[i-1] - price - fee) |

---

### 18.6 Bitmask DP

| # | Bài | Độ khó | Gợi ý |
|---|-----|--------|-------|
| 1 | [LC 1879. Minimum XOR Sum of Two Arrays](https://leetcode.com/problems/minimum-xor-sum-of-two-arrays/) | Hard | dp[mask] = min XOR sum dùng subset mask của B |
| 2 | [LC 847. Shortest Path Visiting All Nodes](https://leetcode.com/problems/shortest-path-visiting-all-nodes/) | Hard | BFS + bitmask |
| 3 | [LC 1125. Smallest Sufficient Team](https://leetcode.com/problems/smallest-sufficient-team/) | Hard | dp[mask] = min team size cần để cover mask skills |
| 4 | [LC 943. Find the Shortest Superstring](https://leetcode.com/problems/find-the-shortest-superstring/) | Hard | TSP-like |

---

### 18.7 Digit DP

| # | Bài | Độ khó | Gợi ý |
|---|-----|--------|-------|
| 1 | [LC 233. Number of Digit One](https://leetcode.com/problems/number-of-digit-one/) | Hard | Đếm số lần xuất hiện digit 1 |
| 2 | [LC 357. Count Numbers with Unique Digits](https://leetcode.com/problems/count-numbers-with-unique-digits/) | Medium | mask 10-bit cho digits đã dùng |
| 3 | [LC 600. Non-negative Integers without Consecutive Ones](https://leetcode.com/problems/non-negative-integers-without-consecutive-ones/) | Hard | Binary representation |
| 4 | [LC 902. Numbers At Most N Given Digit Set](https://leetcode.com/problems/numbers-at-most-n-given-digit-set/) | Hard | Chỉ dùng digits cho trước |

---

### 18.8 Advanced (CHT, SOS, D&C)

| # | Bài | Độ khó | Kỹ thuật |
|---|-----|--------|----------|
| 1 | [CF 319C - Kalila and Dimna](https://codeforces.com/contest/319/problem/C) | Hard | CHT |
| 2 | [CF 455E - Function](https://codeforces.com/problemset/problem/455/E) | Hard | D&C Optimization |
| 3 | [CF 165E - Compatible Numbers](https://codeforces.com/contest/165/problem/E) | Medium | SOS DP |
| 4 | [CF 449D - Jzzhu and Numbers](https://codeforces.com/contest/449/problem/D) | Hard | SOS DP + Inclusion-Exclusion |
| 5 | [USACO - Covered Walkway](http://www.usaco.org/index.php?page=viewproblem2&cpid=239) | Hard | CHT |

---

## 19. Lộ trình luyện tập

### Tuần 1: Nền tảng
```
□ Fibonacci, Climbing Stairs (warm-up)
□ House Robber I, II
□ Maximum Subarray
□ Unique Paths I, II
□ Min Path Sum
```

### Tuần 2: Knapsack & Subsequence
```
□ Coin Change I, II
□ Partition Equal Subset Sum
□ Target Sum
□ LIS (O(n²) và O(n log n))
□ LCS
□ Edit Distance
```

### Tuần 3: String & Advanced Patterns
```
□ Word Break I, II
□ Palindrome Partitioning II
□ Regular Expression Matching
□ Stock problems (tất cả variants)
□ Burst Balloons
```

### Tuần 4: Competition Level
```
□ House Robber III (Tree DP)
□ TSP (Bitmask DP)
□ Digit DP problems
□ 1-2 bài CHT/SOS nếu đủ thời gian
```

---

# APPENDIX: QUICK REFERENCE

## Checklist khi code DP

```
□ dp[...] có nghĩa 1 câu rõ ràng?
□ Transition đã xét ĐỦ choices?
□ Base case đủ? (n=0, empty, etc.)
□ Invalid state → INF/-INF/0?
□ Loop order đúng? (đặc biệt knapsack 1D)
□ Index off-by-one?
□ Overflow? (INF + cost)
□ Quên mod? (đếm số cách)
```

## Pattern → Template nhanh

| Pattern | State | Transition |
|---------|-------|------------|
| Linear | dp[i] | dp[i] = f(dp[i-1], dp[i-2]) |
| 2D | dp[i][j] | So sánh s[i], t[j] |
| 0-1 Knapsack | dp[w] | Duyệt ngược w |
| Unbounded | dp[w] | Duyệt xuôi w |
| LIS | dp[i] = ending at i | dp[i] = max(dp[j]+1) for j<i, a[j]<a[i] |
| Interval | dp[l][r] | Duyệt k ∈ [l,r] |
| Bitmask | dp[mask] | dp[mask|bit] = f(dp[mask]) |
| State Machine | dp[i][state] | Transition theo state |

---

*Tổng hợp từ C.md, DP-Thinking-Methodology.md, DP-Full-Guide.md, DP-Thinking-Extended.md*

*Cập nhật: 30/12/2024*

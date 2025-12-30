# DYNAMIC PROGRAMMING (DP) — FULL GUIDE
## Từ Cách Nghĩ → Template → Pattern → Tối ưu

> Mục tiêu: Đây là **một file “đủ dùng từ cơ bản đến nâng cao”** theo hướng thực chiến: đọc đề → nhận dạng → định nghĩa state → viết transition → chọn order → tối ưu.
>
> Gợi ý: nếu bạn muốn tài liệu kiểu “bách khoa”, xem `C.md`. File này ưu tiên **tư duy + khuôn mẫu + checklist** để làm bài nhanh và đúng.

---

# MỤC LỤC

## 0. Mở đầu
- [DP là gì (1 câu)](#0-dp-là-gì-1-câu)
- [Khi nào nghĩ tới DP](#khi-nào-nghĩ-tới-dp)

## 1. Framework giải DP (xương sống)
- [3 tính chất cần có](#1-3-tính-chất-cần-có)
- [Pipeline 6 bước](#2-pipeline-6-bước)
- [Top-down vs Bottom-up](#3-top-down-vs-bottom-up)
- [Checklist trước khi code](#4-checklist-trước-khi-code)

## 2. Template nền tảng
- [Template Top-down (memo)](#21-template-top-down-memo)
- [Template Bottom-up (tabulation)](#22-template-bottom-up-tabulation)
- [Tối ưu bộ nhớ (rolling / 1D)](#23-tối-ưu-bộ-nhớ-rolling--1d)
- [Cách ước lượng độ phức tạp DP](#24-cách-ước-lượng-độ-phức-tạp-dp)
- [Reconstruction: lấy lại lời giải](#25-reconstruction-lấy-lại-lời-giải)

## 3. Pattern nhận dạng nhanh
- [Linear DP (1D)](#31-linear-dp-1d)
- [2D DP (2 chuỗi / 2 chiều)](#32-2d-dp-2-chuỗi--2-chiều)
- [Knapsack family](#33-knapsack-family)
- [Subsequence DP (LIS/LCS)](#34-subsequence-dp-lislcs)
- [State machine DP (stock, cooldown, transaction)](#35-state-machine-dp-stock-cooldown-transaction)
- [Interval DP](#36-interval-dp)
- [Worked-through: Burst Balloons (Choose-last)](#ví-dụ-worked-through-burst-balloons-choose-last)
- [Tree DP](#37-tree-dp)
- [Bitmask DP](#38-bitmask-dp)
- [Profile / Broken profile DP](#39-profile--broken-profile-dp)
- [Digit DP](#310-digit-dp)
- [Worked-through: Digit DP adjacency bitmask](#ví-dụ-worked-through-digit-dp-adjacency-bitmask)

## 4. Tối ưu hoá DP (khi TLE)
- [Tư duy tối ưu: đổi state / giảm chiều](#41-tư-duy-tối-ưu-đổi-state--giảm-chiều)
- [Divide & Conquer DP Optimization](#42-divide--conquer-dp-optimization)
- [Knuth Optimization](#43-knuth-optimization)

## 5. Debug & verify
- [10 lỗi DP hay gặp](#51-10-lỗi-dp-hay-gặp)
- [Cách tự test](#52-cách-tự-test)

---

## 0. DP là gì (1 câu)

DP là kỹ thuật giải bài toán bằng cách **chia thành subproblem**, mỗi subproblem được mô tả bằng **state**, và ta **lưu kết quả** để không tính lại.

## Khi nào nghĩ tới DP

Thường đề có các cụm:
- **Tối ưu**: min / max / shortest / largest
- **Đếm số cách**: number of ways
- **Khả thi**: can / possible / exists
- Có “quyết định theo bước” (thời gian, vị trí, số lượng, prefix)

---

# 1. Framework giải DP (xương sống)

## 1. 3 tính chất cần có

1) **Optimal substructure**: lời giải lớn xây từ lời giải con.
2) **Overlapping subproblems**: subproblem bị lặp lại.
3) **No after-effect**: khi state đã xác định, tương lai không làm thay đổi giá trị state đó.

Nếu (3) không rõ → thường phải **mở rộng state** (thêm thông tin: mask, last, cooldown, …).

## 2. Pipeline 6 bước

1) **Chọn “trục” chia giai đoạn**: theo i (vị trí), t (thời gian), w (capacity), (l,r) (khoảng)…
2) **Định nghĩa state**: `dp[...]` nghĩa là gì? (một câu, rõ ràng)
3) **Liệt kê choice** tại state đó.
4) **Viết transition** (min/max/sum/or) dựa trên choice.
5) **Base case + invalid state**.
6) **Order / direction**: trạng thái nào phải có trước? (bottom-up) / memo key gì? (top-down)

## 3. Top-down vs Bottom-up

- **Top-down** (memo): dễ nghĩ theo đệ quy, chỉ tính state cần thiết; chú ý stack.
- **Bottom-up** (tabulation): nhanh, rõ order, dễ tối ưu memory.

Thực chiến: thường **viết top-down để đúng**, rồi chuyển bottom-up để tối ưu.

## 4. Checklist trước khi code

- `dp[state]` có nghĩa rõ 1 câu chưa?
- Transition đã xét **đủ choice** chưa?
- Base case đủ chưa? (n=0, empty, start=false…)
- Invalid state xử lý thế nào? (INF / -INF / 0)
- Order có hợp lý? (đặc biệt knapsack 1D)

---

# 2. Template nền tảng

## 2.1 Template Top-down (memo)

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def f(state1, state2, ...):
    # base
    if ...:
        return ...

    ans = ...  # INF / 0 / -INF
    for choice in choices:
        ans = combine(ans, f(next_state(...)))
    return ans
```

**Gợi ý**: memo key chỉ gồm các tham số “định danh subproblem”. Tránh nhét biến “tạm” không cần thiết vào state.

## 2.2 Template Bottom-up (tabulation)

```python
# Khởi tạo dp với kích thước phù hợp
# Điền base
# Loop theo thứ tự đảm bảo phụ thuộc đã có
for ...:
    for ...:
        dp[...] = transition(...)
```

## 2.3 Tối ưu bộ nhớ (rolling / 1D)

- Nếu `dp[i][*]` chỉ phụ thuộc `dp[i-1][*]` → giữ 2 hàng (`prev`, `cur`).
- Nếu phụ thuộc cùng hàng và hàng trước → có thể 1D nhưng phải đúng **direction**.

## 2.4 Cách ước lượng độ phức tạp DP

Quy tắc nhanh:

$$\text{Time} \approx (\#\text{subproblems}) \times (\text{work per transition})$$

Ví dụ:
- Fibonacci: n subproblems, mỗi state O(1) → O(n)
- LCS: n*m subproblems, mỗi state O(1) → O(nm)
- Interval DP naïve: O(n^2) state, mỗi state duyệt k (O(n)) → O(n^3)

Khi thấy:
- O(n^3) thường chỉ sống được khi n ~ 400 trở xuống (tùy constant)
- O(2^n * n) chỉ sống được khi n ~ 20-22

## 2.5 Reconstruction: lấy lại lời giải

Nhiều bài không chỉ cần giá trị tối ưu mà cần **truy vết** (lấy các lựa chọn).

2 cách phổ biến:

1) **Lưu parent/choice** khi update dp
- Ví dụ LIS O(n^2): lưu `parent[i] = j` khi dp[i] được cập nhật từ j.

2) **Backtrack từ dp table**
- Ví dụ LCS: từ `dp[n][m]` đi ngược theo quy tắc so sánh `dp[i-1][j]` / `dp[i][j-1]`.

Mẹo:
- Nếu DP là min/max: nên lưu `choice[state]` = lựa chọn tạo ra giá trị tốt nhất.
- Nếu DP là đếm số cách: reconstruction thường không cần (vì số lượng lời giải quá lớn).

---

# 3. Pattern nhận dạng nhanh

## 3.1 Linear DP (1D)

Dấu hiệu: bài tiến theo i, mỗi bước nhìn vài bước trước.

Ví dụ:
- Fibonacci, Climbing stairs
- House robber

Template:
```python
dp = [0]*(n+1)
# base
for i in range(...):
    dp[i] = combine(dp[i-1], dp[i-2], ...)
```

Ví dụ 1 (Climbing Stairs):
- State: `dp[i]` = số cách lên bậc i
- Transition: `dp[i] = dp[i-1] + dp[i-2]`
- Base: `dp[0]=1, dp[1]=1`

Ví dụ 2 (House Robber):
- State: `dp[i]` = max tiền trong prefix [0..i]
- Transition: `dp[i] = max(dp[i-1], dp[i-2] + a[i])`
- Base: `dp[-1]=0, dp[0]=a[0]`

## 3.2 2D DP (2 chuỗi / 2 chiều)

Dấu hiệu: so sánh 2 chuỗi/2 mảng, prefix.

- LCS: `dp[i][j]` = LCS của s[:i], t[:j]
- Edit distance: `dp[i][j]` = min ops

Order: tăng i, tăng j.

### LCS template (kèm truy vết)

```python
def lcs(s: str, t: str) -> str:
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # reconstruct
    i, j = n, m
    out = []
    while i > 0 and j > 0:
        if s[i - 1] == t[j - 1]:
            out.append(s[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return ''.join(reversed(out))
```

### Edit distance template

```python
def edit_distance(a: str, b: str) -> int:
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],     # delete
                    dp[i][j - 1],     # insert
                    dp[i - 1][j - 1], # replace
                )
    return dp[n][m]
```

## 3.3 Knapsack family

### 3.3.1 0-1 Knapsack

State 2D:
- `dp[i][w]` = best dùng i items đầu, capacity w.

Transition:
- không chọn i
- chọn i (nếu đủ capacity)

1D tối ưu:
```python
for each item (wi, vi):
    for w in range(W, wi-1, -1):  # DUYỆT NGƯỢC
        dp[w] = max(dp[w], dp[w-wi] + vi)
```

**Tại sao phải ngược?** để mỗi item chỉ được dùng 1 lần.

### 3.3.2 Unbounded / Complete Knapsack

1D:
```python
for each item (wi, vi):
    for w in range(wi, W+1):  # DUYỆT XUÔI
        dp[w] = max(dp[w], dp[w-wi] + vi)
```

**Tại sao xuôi?** để cho phép dùng lại item vừa cập nhật.

### 3.3.2b Coin Change (đếm số cách) — khác với “max value”

Coin change hay có 2 phiên bản:

1) **Đếm số cách** để tạo sum W (thường mod M)
- State: `dp[w]` = số cách tạo w
- Base: `dp[0]=1`
- Transition (unbounded): `dp[w] += dp[w-coin]`
- Direction: duyệt w xuôi để không phân biệt thứ tự (combination)

```python
def coin_change_ways(coins, W, MOD=None):
    dp = [0] * (W + 1)
    dp[0] = 1
    for c in coins:
        for w in range(c, W + 1):
            dp[w] += dp[w - c]
            if MOD:
                dp[w] %= MOD
    return dp[W]
```

2) **Min số coin** để tạo W
- State: `dp[w]` = min coins tạo w
- Base: `dp[0]=0`, còn lại INF

```python
def coin_change_min(coins, W):
    INF = 10**30
    dp = [INF] * (W + 1)
    dp[0] = 0
    for c in coins:
        for w in range(c, W + 1):
            dp[w] = min(dp[w], dp[w - c] + 1)
    return dp[W] if dp[W] < INF else -1
```

### 3.3.3 Subset sum / boolean knapsack

`dp[w]` là True/False:
```python
dp = [False]*(W+1)

dp[0] = True
for x in nums:
    for w in range(W, x-1, -1):
        dp[w] = dp[w] or dp[w-x]
```

### 3.3.4 Multiple knapsack (mỗi item có count)

Nếu item i có thể dùng tối đa `cnt[i]` lần.

Cách đơn giản nhất (nhưng có thể chậm): tách thành 0-1 bằng **binary splitting**:
- cnt = 13 → 1,2,4,6 (tổng 13)

```python
def multiple_knapsack(items, W):
    # items: list of (weight, value, count)
    packs = []
    for w, v, c in items:
        k = 1
        while k <= c:
            packs.append((w * k, v * k))
            c -= k
            k <<= 1
        if c:
            packs.append((w * c, v * c))

    dp = [0] * (W + 1)
    for ww, vv in packs:
        for cap in range(W, ww - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - ww] + vv)
    return dp[W]
```

## 3.4 Subsequence DP (LIS/LCS)

### LIS (O(n^2))

`dp[i]` = LIS kết thúc tại i.
```python
dp[i] = 1 + max(dp[j]) for j<i and a[j] < a[i]
```

Template O(n^2) + reconstruct:
```python
def lis_n2(a):
    n = len(a)
    dp = [1] * n
    parent = [-1] * n

    best_end = 0
    for i in range(n):
        for j in range(i):
            if a[j] < a[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                parent[i] = j
        if dp[i] > dp[best_end]:
            best_end = i

    seq = []
    cur = best_end
    while cur != -1:
        seq.append(a[cur])
        cur = parent[cur]
    seq.reverse()
    return dp[best_end], seq
```

### LIS (O(n log n)) — đổi state

`tails[len]` = giá trị nhỏ nhất có thể làm tail của LIS độ dài len.
Update bằng binary search.

Template (chỉ lấy độ dài):
```python
from bisect import bisect_left

def lis_nlogn_len(a):
    tails = []
    for x in a:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```

Ghi chú: reconstruct trong O(n log n) cần thêm mảng `pos[]/parent[]` (chi tiết hơn, nhưng ý tưởng vẫn là lưu “tail index”).

## 3.5 State machine DP (stock, cooldown, transaction)

Dấu hiệu: đề có “mua/bán”, “cooldown”, “tối đa k lần”, “phí giao dịch”.

State thường là:
- ngày i
- đang giữ/không giữ
- số giao dịch đã dùng

Ví dụ dạng chung:
```python
hold[i] = max(hold[i-1], cash[i-1] - price[i])
cash[i] = max(cash[i-1], hold[i-1] + price[i] - fee)
```

### Biến thể 1: cooldown 1 ngày

State thường tách thành 3:
- `hold`: đang giữ
- `sold`: vừa bán hôm nay
- `rest`: không giữ và không vừa bán

```python
def stock_cooldown(prices):
    if not prices:
        return 0

    hold = -10**30
    sold = -10**30
    rest = 0

    for p in prices:
        prev_sold = sold
        sold = hold + p
        hold = max(hold, rest - p)
        rest = max(rest, prev_sold)

    return max(rest, sold)
```

### Biến thể 2: tối đa k transactions

Ý tưởng: `dp[trans][state]` với state ∈ {hold, cash}. Tối ưu theo ngày.

```python
def stock_k_transactions(prices, k):
    if not prices or k == 0:
        return 0

    # nếu k lớn, tương đương unlimited
    if k >= len(prices) // 2:
        profit = 0
        for i in range(1, len(prices)):
            profit += max(0, prices[i] - prices[i - 1])
        return profit

    INF = 10**30
    hold = [-INF] * (k + 1)
    cash = [0] * (k + 1)

    for p in prices:
        for t in range(1, k + 1):
            hold[t] = max(hold[t], cash[t - 1] - p)
            cash[t] = max(cash[t], hold[t] + p)

    return cash[k]
```

## 3.6 Interval DP

Dấu hiệu: bài hỏi tối ưu trên đoạn [l,r], “ghép”, “chia”, “burst”, “matrix chain”.

### Archetype A: Split / Merge
```python
for length in range(2, n+1):
    for l in range(0, n-length+1):
        r = l+length-1
        dp[l][r] = INF
        for k in range(l, r):
            dp[l][r] = min(dp[l][r], dp[l][k] + dp[k+1][r] + cost(l,r))
```

Gợi ý implement:
- Luôn xác định rõ: `cost(l,r)` có phụ thuộc k không?
- Base: `dp[i][i] = 0` hoặc theo đề.
- INF lớn và cẩn thận overflow.

### Archetype B: Choose-last

Chọn phần tử k là “cái làm cuối” trong [l,r] để tách 2 bên độc lập:
```python
dp[l][r] = max(dp[l][k-1] + gain(l,k,r) + dp[k+1][r])
```

### Ví dụ worked-through: Burst Balloons (Choose-last)

Mô tả bài (LeetCode 312 – ý tưởng):
- Có mảng `nums`.
- Khi burst balloon i, coins nhận được = `nums[left] * nums[i] * nums[right]` (left/right là balloon gần nhất còn sống).
- Mục tiêu: max total coins.

**Vì sao phải choose-last?**

Nếu bạn chọn balloon burst “đầu tiên” trong đoạn [l..r], 2 phía vẫn dính nhau vì hàng xóm thay đổi.
Nếu chọn balloon k là **burst cuối cùng** trong đoạn, thì tại thời điểm đó hàng xóm của k chắc chắn là biên đoạn → 2 phía độc lập.

**Chuẩn hoá input**

Thêm 2 balloon ảo giá trị 1 ở hai đầu:
`a = [1] + nums + [1]`

**Định nghĩa DP (open interval)**

- `dp[l][r]` = max coins khi burst hết balloon trong **khoảng mở** (l, r), tức là chỉ burst các chỉ số `l+1..r-1`.
- Base: nếu `r = l + 1` ⇒ khoảng rỗng ⇒ `dp[l][r] = 0`.

**Transition**

Chọn k là balloon burst cuối cùng trong (l, r):

$$ dp[l][r] = \max_{k \in (l,r)} \big( dp[l][k] + dp[k][r] + a[l]\cdot a[k]\cdot a[r] \big) $$

**Order**

Duyệt theo độ dài đoạn (r - l) tăng dần.

**Ví dụ nhỏ**

nums = [3, 1, 5]
→ a = [1, 3, 1, 5, 1]

Các đoạn dài 2 (r=l+2): chỉ có 1 k.
- dp[0][2] = 1*3*1 = 3
- dp[1][3] = 3*1*5 = 15
- dp[2][4] = 1*5*1 = 5

Đoạn dài 3:
- dp[0][3]: k∈{1,2}
    - k=1: dp[0][1]+dp[1][3]+1*3*5 = 0+15+15 = 30
    - k=2: dp[0][2]+dp[2][3]+1*1*5 = 3+0+5 = 8
    => dp[0][3] = 30

- dp[1][4]: k∈{2,3}
    - k=2: dp[1][2]+dp[2][4]+3*1*1 = 0+5+3 = 8
    - k=3: dp[1][3]+dp[3][4]+3*5*1 = 15+0+15 = 30
    => dp[1][4] = 30

Đoạn dài 4:
- dp[0][4]: k∈{1,2,3}
    - k=1: dp[0][1]+dp[1][4]+1*3*1 = 0+30+3 = 33
    - k=2: dp[0][2]+dp[2][4]+1*1*1 = 3+5+1 = 9
    - k=3: dp[0][3]+dp[3][4]+1*5*1 = 30+0+5 = 35
    => dp[0][4] = 35

**Code**

```python
def burst_balloons(nums):
        a = [1] + nums + [1]
        n = len(a)
        dp = [[0] * n for _ in range(n)]

        # length là khoảng cách (r-l)
        for length in range(2, n):
                for l in range(0, n - length):
                        r = l + length
                        best = 0
                        for k in range(l + 1, r):
                                best = max(best, dp[l][k] + dp[k][r] + a[l] * a[k] * a[r])
                        dp[l][r] = best

        return dp[0][n - 1]

# ví dụ:
# print(burst_balloons([3,1,5]))  # 35
```

### Ví dụ worked-through: Matrix Chain Multiplication (Split/Merge)

Bài toán (kinh điển): có dãy ma trận A1..An, kích thước:
- A1: p0 x p1
- A2: p1 x p2
- ...
- An: p(n-1) x pn

Hỏi: nhân theo thứ tự nào để **ít phép nhân scalar nhất**.

**Ví dụ**: p = [10, 30, 5, 60] ⇒ n=3
- A1: 10x30
- A2: 30x5
- A3: 5x60

**Định nghĩa DP**
- `dp[i][j]` = min cost nhân Ai..Aj (1-indexed)
- Base: `dp[i][i] = 0`

**Transition**
Chọn k là chỗ “cắt”:

$$ dp[i][j] = \min_{k=i..j-1} \big( dp[i][k] + dp[k+1][j] + p_{i-1}\cdot p_k \cdot p_j \big) $$

**Order**: theo length tăng dần.

**Tính tay ra bảng dp cho ví dụ**

Length = 2:
- dp[1][2] = 10*30*5 = 1500
- dp[2][3] = 30*5*60 = 9000

Length = 3:
- dp[1][3] = min(
  - k=1: dp[1][1]+dp[2][3]+10*30*60 = 0 + 9000 + 18000 = 27000
  - k=2: dp[1][2]+dp[3][3]+10*5*60  = 1500 + 0 + 3000  = 4500
  ) = 4500

**Bảng dp (tam giác trên)**
```
      j=1    2      3
i=1   0    1500   4500
  2         0     9000
  3                0
```

**Code (kèm truy vết ngoặc)**

```python
def matrix_chain_order(p):
    # p length = n+1
    n = len(p) - 1
    INF = 10**30
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    cut = [[-1] * (n + 1) for _ in range(n + 1)]

    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            dp[i][j] = INF
            for k in range(i, j):
                val = dp[i][k] + dp[k + 1][j] + p[i - 1] * p[k] * p[j]
                if val < dp[i][j]:
                    dp[i][j] = val
                    cut[i][j] = k

    def build(i, j):
        if i == j:
            return f"A{i}"
        k = cut[i][j]
        return f"({build(i, k)} x {build(k + 1, j)})"

    return dp[1][n], build(1, n)

# ví dụ:
# print(matrix_chain_order([10,30,5,60]))  # (4500, '(A1 x (A2 x A3))')
```

---

## 3.7 Tree DP

Dấu hiệu: cấu trúc cây, chọn/bỏ node, đường đi, subtree.

Thường có 2 trạng thái:
- `dp[u][0]`: không chọn u
- `dp[u][1]`: chọn u

Template:
```python
def dfs(u, parent):
    dp0, dp1 = 0, value[u]
    for v in adj[u]:
        if v == parent: continue
        c0, c1 = dfs(v, u)
        dp0 += max(c0, c1)
        dp1 += c0
    return dp0, dp1
```

Bẫy hay gặp:
- Quên parent → loop vô hạn.
- Tree DP nhiều bài cần “gộp con” theo kiểu knapsack (subtree size) → complexity tăng nhanh, cần cẩn thận.

## 3.8 Bitmask DP

Dấu hiệu: n nhỏ (≤ 20), cần xét subset.

Ví dụ TSP:
- `dp[mask][i]` = cost min đi qua subset mask và kết thúc tại i.

Template TSP (O(2^n * n^2)):

```python
def tsp(dist):
    n = len(dist)
    INF = 10**30
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0  # start at 0

    for mask in range(1 << n):
        for u in range(n):
            if dp[mask][u] >= INF:
                continue
            if ((mask >> u) & 1) == 0:
                continue
            for v in range(n):
                if (mask >> v) & 1:
                    continue
                nmask = mask | (1 << v)
                dp[nmask][v] = min(dp[nmask][v], dp[mask][u] + dist[u][v])

    full = (1 << n) - 1
    ans = INF
    for u in range(n):
        ans = min(ans, dp[full][u] + dist[u][0])
    return ans
```

## 3.9 Profile / Broken profile DP

Dấu hiệu: tiling / grid placement, chuyển theo từng row.

State:
- `dp[row][mask]`.
- “gen transition” để sinh `next_mask` bằng cách fill dần từng cột.

Skeleton (domino tiling):
```python
def profile_dp(R, C):
    dp = {0: 1}

    for _row in range(R):
        ndp = {}

        def gen(col, mask, next_mask, ways):
            if col == C:
                ndp[next_mask] = ndp.get(next_mask, 0) + ways
                return
            if (mask >> col) & 1:
                gen(col+1, mask, next_mask, ways)
                return

            # horizontal
            if col+1 < C and ((mask >> (col+1)) & 1) == 0:
                gen(col+2, mask, next_mask, ways)

            # vertical
            gen(col+1, mask, next_mask | (1<<col), ways)

        for mask, ways in dp.items():
            gen(0, mask, 0, ways)

        dp = ndp

    return dp.get(0, 0)
```

### Ví dụ worked-through: domino tiling 2x3

Mục tiêu: đếm số cách lát domino 2x1 phủ kín bảng 2 hàng, 3 cột.

**Encode mask**
- Duyệt theo từng row.
- `mask` có C bit.
- Bit col=1 nghĩa là ô ở cột đó của **row hiện tại** đã bị “chiếm sẵn” (do domino dọc từ row trước).

Với C=3, mask là 3-bit: từ 000 đến 111.

**Khởi tạo**
- row=0: dp = {000: 1}

**Row 0, mask=000**
Ta fill 3 cột:
- Nếu đặt 3 domino dọc (mỗi cột 1 domino dọc) ⇒ next_mask=111 (vì row1 sẽ bị chiếm sẵn cả 3 cột)
- Nếu đặt 1 domino ngang ở (col0-col1) + 1 domino dọc ở col2 ⇒ next_mask=100
- Nếu đặt 1 domino dọc col0 + 1 domino ngang (col1-col2) ⇒ next_mask=001

Vậy sau row0:
- dp1[111] += 1
- dp1[100] += 1
- dp1[001] += 1

**Row 1 xử lý từng mask**

Row1, mask=111: tất cả ô đã chiếm sẵn ⇒ gen kết thúc row ⇒ next_mask=000.

Row1, mask=100: col2 bị chiếm sẵn; còn col0-col1 trống ⇒ chỉ có thể đặt 1 domino ngang ⇒ next_mask=000.

Row1, mask=001: col0 bị chiếm sẵn; còn col1-col2 trống ⇒ đặt 1 domino ngang ⇒ next_mask=000.

Sau row1:
- dp2[000] = 3

**Kết luận**: số cách lát 2x3 là `dp cuối ở mask=000` = **3**.

Gợi ý debug nhanh:
- In ra dp sau mỗi row.
- Với C nhỏ (≤5), có thể in nhị phân mask để nhìn trực quan.

## 3.10 Digit DP

Dấu hiệu: đếm số trong [L..R] thỏa điều kiện theo chữ số.

Chiến lược:
- Viết `f(x)` đếm trong [0..x]
- Trả lời: `f(R) - f(L-1)`

Template:
```python
from functools import lru_cache

def solve_upto(x: int) -> int:
    if x < 0:
        return 0
    digits = list(map(int, str(x)))
    n = len(digits)

    @lru_cache(maxsize=None)
    def dfs(pos: int, state: int, tight: bool, started: bool) -> int:
        if pos == n:
            return 1 if started and is_good_terminal_state(state) else 0

        limit = digits[pos] if tight else 9
        res = 0
        for d in range(0, limit + 1):
            ns = state
            nstarted = started or (d != 0)
            if nstarted:
                ns = transition_state(state, d)
            res += dfs(pos+1, ns, tight and (d == limit), nstarted)
        return res

    return dfs(0, initial_state(), True, False)
```

Bẫy:
- leading zero (started)
- terminal condition: có tính số 0 không?

### Ví dụ worked-through: đếm số trong [0..x] có tổng chữ số % 3 == 0

Đây là bài digit DP tối giản để nắm cơ chế `pos/state/tight/started`.

**Ý nghĩa state**
- `state` = `sum_digits_mod3` (0,1,2)

**Terminal**
- Khi pos == n:
  - Nếu started=False: nghĩa là “chưa đặt chữ số nào” (số 0). Tùy đề: có tính 0 hay không.
  - Ở đây ta **tính cả số 0** như một số hợp lệ (tổng chữ số = 0, chia hết 3).

**Code hoàn chỉnh**

```python
from functools import lru_cache

def count_sum_digits_mod3_upto(x: int) -> int:
    if x < 0:
        return 0

    digits = list(map(int, str(x)))
    n = len(digits)

    @lru_cache(maxsize=None)
    def dfs(pos: int, mod: int, tight: bool, started: bool) -> int:
        if pos == n:
            if not started:
                # số 0
                return 1
            return 1 if mod == 0 else 0

        limit = digits[pos] if tight else 9
        res = 0

        for d in range(0, limit + 1):
            ntight = tight and (d == limit)
            if not started and d == 0:
                # vẫn chưa bắt đầu, không cộng vào sum
                res += dfs(pos + 1, mod, ntight, False)
            else:
                res += dfs(pos + 1, (mod + d) % 3, ntight, True)
        return res

    return dfs(0, 0, True, False)

def count_sum_digits_mod3(L: int, R: int) -> int:
    return count_sum_digits_mod3_upto(R) - count_sum_digits_mod3_upto(L - 1)
```

**Mini sanity check**
- x=20, các số có tổng chữ số %3==0: 0,3,6,9,12,15,18 (7 số)
- Bạn có thể test: `count_sum_digits_mod3_upto(20)` phải ra 7.

---

### Ví dụ worked-through: Digit DP adjacency bitmask

Bài mẫu (để thấy đủ “adjacency + bitmask” trong state):

Đếm số trong [L..R] thỏa:
1) **Mọi chữ số đều khác nhau** (dùng `mask` 10-bit để đánh dấu chữ số đã dùng).
2) **Không có 2 chữ số kề nhau chênh lệch 1** (adjacency constraint: $|d_i - d_{i-1}| \ne 1$).

Lưu ý:
- Leading zeros không tính là “dùng chữ số 0”.
- `include_zero`: có tính số 0 hay không.

**State**
- `pos`: vị trí digit
- `prev`: chữ số trước đó (0..9) hoặc sentinel 10 khi chưa có digit trước
- `mask`: bitmask chữ số đã dùng
- `tight`: còn bị giới hạn bởi x không
- `started`: đã bắt đầu tạo số chưa

Complexity xấp xỉ: len * 11 * 1024 * 2 * 2 (rất ổn).

**Code**

```python
from functools import lru_cache

def count_adjacent_not1_and_unique_upto(x: int, include_zero: bool = False) -> int:
    if x < 0:
        return 0

    digits = list(map(int, str(x)))
    n = len(digits)
    NO_PREV = 10

    @lru_cache(maxsize=None)
    def dfs(pos: int, prev: int, mask: int, tight: bool, started: bool) -> int:
        if pos == n:
            if started:
                return 1
            return 1 if include_zero else 0

        limit = digits[pos] if tight else 9
        res = 0

        for d in range(0, limit + 1):
            ntight = tight and (d == limit)

            if not started and d == 0:
                # chưa bắt đầu, bỏ qua digit này
                res += dfs(pos + 1, NO_PREV, mask, ntight, False)
                continue

            # adjacency constraint
            if prev != NO_PREV and abs(d - prev) == 1:
                continue

            # unique digits constraint via mask
            if (mask >> d) & 1:
                continue

            res += dfs(pos + 1, d, mask | (1 << d), ntight, True)

        return res

    return dfs(0, NO_PREV, 0, True, False)

def count_adjacent_not1_and_unique(L: int, R: int, include_zero: bool = False) -> int:
    return (
        count_adjacent_not1_and_unique_upto(R, include_zero)
        - count_adjacent_not1_and_unique_upto(L - 1, include_zero)
    )
```

**Cách tự verify nhanh**
- Viết brute force cho R nhỏ (vd 10000) rồi so sánh với digit-DP.
- Debug bằng cách in vài số đầu tiên thỏa điều kiện.

---

---

# 4. Tối ưu hoá DP (khi TLE)

## 4.1 Tư duy tối ưu: đổi state / giảm chiều

Khi DP đang O(n^2) hoặc O(n^3):
1) **Đổi state**: ví dụ LIS `dp ending` → `tails`.
2) **Giảm chiều**: 2D → rolling / 1D (cẩn thận direction).
3) Tìm cấu trúc đặc biệt của transition (min over k).

Checklist nhanh khi TLE:
- DP đang là **min/max over k** không? Nếu có, thử nghĩ tới D&C / Knuth.
- DP có tính chất “đơn điệu” không? (opt tăng dần)
- Có thể precompute `cost()` bằng prefix sum để O(1) không?
- Có thể thay 2D bằng 1D/rolling không?

## 4.2 Divide & Conquer DP Optimization

Áp dụng cho dạng:

$$ dp[i][j] = \min_{k \le j} (dp[i-1][k] + C(k+1, j)) $$

Nếu `opt[i][j]` đơn điệu theo j, ta dùng compute(mid) để thu hẹp k.

Skeleton:
```python
INF = 10**30

def compute(l, r, optl, optr, dp_prev, dp_cur):
    if l > r:
        return
    mid = (l + r) // 2

    best_k = -1
    best_val = INF

    for k in range(optl, min(mid, optr) + 1):
        val = dp_prev[k] + cost(k + 1, mid)
        if val < best_val:
            best_val = val
            best_k = k

    dp_cur[mid] = best_val
    compute(l, mid - 1, optl, best_k, dp_prev, dp_cur)
    compute(mid + 1, r, best_k, optr, dp_prev, dp_cur)
```

### Cách dùng “đúng bài” (full flow)

Với dạng DP nhiều lớp (i = 1..K):
- `dp_prev[j]`: đáp án cho lớp i-1 tại vị trí j
- `dp_cur[j]`: đáp án cho lớp i tại vị trí j

Pseudo flow:
```python
def solve(n, K):
    dp_prev = [INF] * (n + 1)
    dp_prev[0] = 0

    for i in range(1, K + 1):
        dp_cur = [INF] * (n + 1)

        # compute dp_cur[1..n] (hoặc [0..n] tùy bài)
        compute(1, n, 0, n - 1, dp_prev, dp_cur)

        dp_prev = dp_cur

    return dp_prev[n]
```

### Bài mẫu “form chuẩn” (không ràng buộc cost cụ thể)

Nhiều bài partition/prefix DP có form:

$$ dp[i][j] = \min_{k < j} (dp[i-1][k] + C(k+1, j)) $$

Trong đó `C(l,r)` thường tính O(1) nhờ prefix sums / prefix squares / precompute.

**Quan trọng**: D&C optimization chỉ đúng nếu bạn chứng minh (hoặc biết) rằng:
- `opt[i][j] <= opt[i][j+1]` (điểm tối ưu đơn điệu)

Nếu không chắc điều này: dùng D&C có thể ra sai.

### Checklist “đủ điều kiện” trước khi áp dụng

- Recurrence đúng form `min over k` và k-range là prefix.
- Cost `C(l,r)` không phụ thuộc vào i (hoặc phụ thuộc theo kiểu vẫn giữ monotonic).
- Có proof / reference / nghiệm nhỏ xác nhận `opt` đơn điệu.
- n lớn khiến O(K*n^2) TLE, nhưng O(K*n*logn) hoặc O(K*n) là cần thiết.

Checklist trước khi dùng:
- transition đúng “min over k”
- có cơ sở cho tính đơn điệu `opt` (thường do tính chất cost)

## 4.3 Knuth Optimization

Áp dụng cho interval DP dạng:

$$ dp[l][r] = \min_{k \in [l..r]} (dp[l][k] + dp[k][r]) + C(l,r) $$

Khi thỏa:

$$ opt[l][r-1] \le opt[l][r] \le opt[l+1][r] $$

Ta giới hạn k từ `opt[l][r-1]..opt[l+1][r]`.

Template:
```python
for length in range(2, n + 1):
    for l in range(0, n - length + 1):
        r = l + length - 1
        dp[l][r] = INF

        start = opt[l][r - 1]
        end = opt[l + 1][r]
        for k in range(start, end + 1):
            val = dp[l][k] + dp[k][r] + cost(l, r)
            if val < dp[l][r]:
                dp[l][r] = val
                opt[l][r] = k
```

### Ví dụ DP gốc: “merge intervals” kiểu Merge Stones

Bài kiểu:
- Có mảng a[0..n-1].
- Gộp các đoạn, cost gộp đoạn [l..r] là `sum(l,r)`.
- Muốn min cost gộp toàn bộ.

DP cơ bản:

$$ dp[l][r] = \min_{k \in [l..r-1]} (dp[l][k] + dp[k+1][r]) + sum(l,r) $$

Đây là đúng form để *có khả năng* áp dụng Knuth (tùy điều kiện cost, cần chứng minh opt-monotonicity).

### Implementation đầy đủ (Knuth template + prefix sum)

```python
def merge_cost_knuth(a):
    n = len(a)
    if n == 0:
        return 0

    INF = 10**30
    prefix = [0]
    for x in a:
        prefix.append(prefix[-1] + x)

    def sum_lr(l, r):
        return prefix[r + 1] - prefix[l]

    dp = [[0] * n for _ in range(n)]
    opt = [[0] * n for _ in range(n)]

    for i in range(n):
        opt[i][i] = i

    for length in range(2, n + 1):
        for l in range(0, n - length + 1):
            r = l + length - 1
            dp[l][r] = INF

            # phạm vi k thu hẹp nhờ Knuth
            start = opt[l][r - 1]
            end = opt[l + 1][r]
            if start > end:
                start, end = end, start

            for k in range(start, end + 1):
                val = dp[l][k] + dp[k + 1][r] + sum_lr(l, r)
                if val < dp[l][r]:
                    dp[l][r] = val
                    opt[l][r] = k

    return dp[0][n - 1]
```

### Nếu Knuth không áp dụng được thì sao?

- Quay về O(n^3) (n nhỏ) hoặc tìm tối ưu khác.
- Có bài merge-cost có thể dùng Huffman/greedy (nhưng đó là bài khác — điều kiện khác).

Ghi chú: nếu không chắc điều kiện của bài, **đừng dùng Knuth**.

---

# 5. Debug & verify

## 5.1 10 lỗi DP hay gặp

1) Sai nghĩa `dp[...]` (không viết được 1 câu rõ ràng)
2) Thiếu case trong transition
3) Sai base case (đặc biệt dp[0], empty)
4) Sai xử lý invalid state (INF/-INF/0)
5) Sai loop order
6) Sai direction (0-1 vs unbounded knapsack)
7) Index off-by-one (0-index vs 1-index)
8) Memo key thiếu/thừa biến (top-down)
9) Overflow (đặc biệt INF + cost)
10) Quên mod (đếm số cách)

## 5.2 Cách tự test

- Test nhỏ tính tay được.
- In bảng dp với n nhỏ.
- Nếu có thể: brute force cho n nhỏ để so sánh.

Mẹo kiểm lỗi nhanh:
- Với DP tối ưu: so sánh với brute force ở n<=10.
- Với DP đếm: so sánh bằng backtracking ở n nhỏ.
- In dp theo “lớp” (i, length, row) để thấy pattern.

---

# Kết

Nếu bạn muốn, mình có thể tạo thêm 1 file riêng dạng **“DP 1-page cheat sheet”** chỉ gồm checklist + template ngắn (để ôn trước contest).
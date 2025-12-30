# DYNAMIC PROGRAMMING (DP) — MASTER GUIDE (VI)
## Từ tư duy → template → pattern → tối ưu → bài tập (kèm ví dụ worked-through)

> Mục tiêu: 1 tài liệu duy nhất để bạn đi từ **nhận diện** → **định nghĩa state** → **transition** → **order** → **tối ưu** → **debug**.
>
> Ghi chú: Nội dung được **gộp và khử trùng lặp** từ các tài liệu DP hiện có trong repo này (xem mục “Nguồn trong repo”). Các link tham khảo trong `source.txt` được giữ ở phần cuối.

---

# MỤC LỤC

## 0. Mở đầu
- [DP là gì (1 câu)](#0-dp-là-gì-1-câu)
- [Khi nào nghĩ tới DP](#khi-nào-nghĩ-tới-dp)
- [DP vs Greedy vs D&C vs Backtracking](#dp-vs-greedy-vs-dc-vs-backtracking)

## 1. Framework tư duy giải DP
- [3 tính chất cần có](#1-3-tính-chất-cần-có)
- [Backward thinking](#backward-thinking)
- [Mô hình 4 câu hỏi](#mô-hình-4-câu-hỏi)
- [Pipeline 6 bước](#pipeline-6-bước)
- [Template tư duy 7 bước (chi tiết)](#template-tư-duy-7-bước-chi-tiết)
- [Từ đệ quy đến DP (5 bước)](#từ-đệ-quy-đến-dp-5-bước)

## 2. Template code nền tảng
- [Top-down (memoization)](#top-down-memoization)
- [Bottom-up (tabulation)](#bottom-up-tabulation)
- [Ước lượng độ phức tạp DP](#ước-lượng-độ-phức-tạp-dp)
- [Tối ưu bộ nhớ (rolling/1D)](#tối-ưu-bộ-nhớ-rolling1d)
- [Reconstruction (truy vết lời giải)](#reconstruction-truy-vết-lời-giải)

## 3. Pattern nhận dạng nhanh (kèm template + ví dụ)
- [3.0 Case studies (end-to-end)](#30-case-studies-end-to-end)
- [3.1 Linear DP (1D)](#31-linear-dp-1d)
- [3.2 Grid DP (2D lưới)](#32-grid-dp-2d-lưới)
- [3.3 2-sequence DP (LCS / Edit Distance)](#33-2-sequence-dp-lcs--edit-distance)
- [3.4 Knapsack family](#34-knapsack-family)
- [3.5 Subsequence DP (LIS)](#35-subsequence-dp-lis)
- [3.6 Boolean DP (Word Break)](#36-boolean-dp-word-break)
- [3.7 State machine DP (stock, cooldown, k transactions)](#37-state-machine-dp-stock-cooldown-k-transactions)
- [3.8 Interval DP (Split/Merge, Choose-last)](#38-interval-dp-splitmerge-choose-last)
- [3.9 Tree DP](#39-tree-dp)
- [3.10 Bitmask DP](#310-bitmask-dp)
- [3.11 Profile / Broken profile DP (tiling)](#311-profile--broken-profile-dp-tiling)
- [3.12 Digit DP](#312-digit-dp)
- [3.13 Probability DP](#313-probability-dp)

## 4. Tối ưu hoá DP (khi TLE)
- [Đổi state / giảm chiều](#đổi-state--giảm-chiều)
- [Divide & Conquer DP Optimization](#divide--conquer-dp-optimization)
- [Knuth Optimization](#knuth-optimization)
- [Convex Hull Trick (CHT)](#convex-hull-trick-cht)
- [SOS DP (Sum Over Subsets)](#sos-dp-sum-over-subsets)

## 5. Debug & verify
- [Checklist trước khi code](#checklist-trước-khi-code)
- [Sai lầm thường gặp](#sai-lầm-thường-gặp)
- [Cách tự test](#cách-tự-test)

## 6. Bài tập & lộ trình
- [Bài tập theo pattern](#bài-tập-theo-pattern)
- [Lộ trình 4 tuần](#lộ-trình-4-tuần)

---

# 0. Mở đầu

## 0. DP là gì (1 câu)

DP là kỹ thuật giải bài toán bằng cách **chia thành subproblem**, mô tả mỗi subproblem bằng **state**, và **lưu kết quả** để tránh tính lại.

## Khi nào nghĩ tới DP

Thường đề có các cụm:
- **Tối ưu**: min / max / shortest / largest
- **Đếm số cách**: number of ways
- **Khả thi**: can / possible / exists
- Có “quyết định theo bước”: i (vị trí), t (thời gian), prefix, capacity…

## DP vs Greedy vs D&C vs Backtracking

| Kỹ thuật | Khi nào dùng | Dấu hiệu | Ghi chú |
|---|---|---|---|
| Greedy | Local optimal = global optimal | có thể chứng minh lựa chọn tối ưu cục bộ | nếu không chứng minh được, dễ sai |
| DP | cần xét nhiều case nhưng có thể gom state | subproblem chồng chéo | thường “tối ưu/đếm/khả thi” |
| Divide & Conquer | subproblem độc lập | ít/không chồng chéo | merge sort, quick sort |
| Backtracking | liệt kê lời giải | n nhỏ, cần all solutions | thường kết hợp pruning |

---

# 1. Framework tư duy giải DP

## 1. 3 tính chất cần có

1) **Optimal substructure**: lời giải lớn xây từ lời giải con.
2) **Overlapping subproblems**: subproblem bị lặp lại.
3) **No after-effect** (Markov property): state đã xác định thì tương lai không làm đổi giá trị state đó.

Nếu (3) không rõ → thường phải **mở rộng state** (thêm thông tin: mask, last, cooldown…).

## Backward thinking

Tư duy dễ nhất khi làm DP:

- Forward (khó): “bắt đầu từ 0, làm sao để tới n?” → cây quyết định phình nhanh.
- Backward (dễ): “để đứng ở trạng thái cuối, tôi phải đến từ đâu?” → ra công thức chuyển ngay.

Ví dụ Climbing Stairs:
- Để lên bậc n, trước đó phải ở n-1 hoặc n-2
- `ways(n) = ways(n-1) + ways(n-2)`

## Mô hình 4 câu hỏi

Khi gặp bài DP, trả lời theo thứ tự:

1) Trạng thái cuối cùng là gì?
2) Trước đó có thể đứng ở đâu? (prev states)
3) Chi phí/giá trị thay đổi thế nào? (transition)
4) Base case là gì?

## Pipeline 6 bước

1) Chọn “trục” chia giai đoạn: i, t, w, (l,r)…
2) Định nghĩa state: `dp[...]` nghĩa là gì? (1 câu rõ ràng)
3) Liệt kê **choices** tại state.
4) Viết transition (min/max/sum/or).
5) Base case + invalid state.
6) Order/direction: phụ thuộc gì thì tính trước.

## Template tư duy 7 bước (chi tiết)

1) Xác định loại output: tối ưu / đếm / khả thi / truy vết.
2) Vẽ ví dụ nhỏ bằng tay.
3) Backward thinking: “để đến cuối cần gì?”
4) Định nghĩa state rõ ràng.
5) Liệt kê lựa chọn → viết phương trình chuyển.
6) Base cases.
7) Thứ tự tính + kết quả ở đâu.

## Từ đệ quy đến DP (5 bước)

Đây là cách “đi từ ý tưởng đến code” nhanh và chắc nhất:

1) Viết **đệ quy thuần** (brute force) theo đúng định nghĩa bài toán.
2) Nhìn xem đệ quy đang phụ thuộc vào những tham số nào → đó là **state**.
3) Thêm **memoization** (cache theo state) → top-down DP.
4) Nếu cần tối ưu tốc độ/stack → chuyển sang **bottom-up** với thứ tự tính hợp lệ.
5) Tối ưu không gian (rolling/1D), truy vết (nếu cần).

Mẹo kiểm tra nhanh “state có đủ chưa?”
- Nếu state đã cố định mà bạn vẫn phải biết thêm “quá khứ” để quyết định bước tiếp → state đang thiếu thông tin.
- Cách sửa: thêm biến vào state (ví dụ: `prev`, `mask`, `cooldown`, `k`...).

---

# 2. Template code nền tảng

## Top-down (memoization)

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

## Bottom-up (tabulation)

```python
# Khởi tạo dp
# Điền base
# Loop theo thứ tự đảm bảo phụ thuộc đã có
for ...:
    for ...:
        dp[...] = transition(...)
```

## Ước lượng độ phức tạp DP

Quy tắc nhanh:

Time ≈ (số subproblems) × (work mỗi transition)

Ví dụ:
- LCS: O(nm) states, O(1) transition → O(nm)
- Interval DP naïve: O(n^2) states, mỗi state duyệt k O(n) → O(n^3)
- Bitmask DP: O(2^n × n^2) (TSP) → n ~ 20 là giới hạn thực tế

## Tối ưu bộ nhớ (rolling/1D)

- Nếu `dp[i][*]` chỉ phụ thuộc `dp[i-1][*]` → giữ 2 hàng.
- Nếu chuyển được 2D → 1D: cực kỳ chú ý **direction** (0-1 knapsack phải duyệt ngược).

## Reconstruction (truy vết lời giải)

2 cách phổ biến:

1) Lưu `parent/choice` khi update dp.
2) Backtrack trực tiếp từ dp-table (ví dụ LCS).

---

# 3. Pattern nhận dạng nhanh (kèm template + ví dụ)

## 3.0 Case studies (end-to-end)

Phần này đi theo format cố định để bạn bắt chước khi gặp bài mới:

1) Ý tưởng/backward thinking
2) Định nghĩa state (1 câu)
3) Liệt kê choices
4) Transition
5) Base + invalid states
6) Order
7) Complexity
8) Code + mini-verify

---

### Case 1: Coin Change (min coins)

**Bài toán:** cho `coins[]`, `amount`. Tìm số xu ít nhất để tạo `amount`, không được thì -1.

**Ý tưởng:** đứng ở số tiền `x` (trạng thái cuối của subproblem), bước trước đó phải là `x - coin`.

**State:** `dp[x]` = số xu ít nhất để tạo ra `x`.

**Choices:** chọn một `coin` để dùng ở bước cuối.

**Transition:**

`dp[x] = min(dp[x - coin] + 1)` với mọi `coin <= x`.

**Base/invalid:**
- `dp[0] = 0`
- `dp[x] = +inf` nếu chưa thể tạo.

**Order:** tăng dần `x` từ 1..amount (bottom-up).

**Complexity:** O(amount * len(coins)), memory O(amount).

**Code:**

```python
def coinChange(coins, amount):
    INF = 10**30
    dp = [INF] * (amount + 1)
    dp[0] = 0

    for x in range(1, amount + 1):
        best = INF
        for c in coins:
            if x >= c and dp[x - c] != INF:
                best = min(best, dp[x - c] + 1)
        dp[x] = best

    return -1 if dp[amount] == INF else dp[amount]
```

**Mini-verify:** `coins=[1,2,5], amount=11` → 3 (5+5+1).

**Worked-through (điền mảng dp cho coins=[1,2,5], amount=11)**

Ta điền `dp[x]` từ 0 → 11:

```
dp[0]=0

dp[1]=1   (1)
dp[2]=1   (2)
dp[3]=2   (1+2)
dp[4]=2   (2+2)
dp[5]=1   (5)
dp[6]=2   (5+1)
dp[7]=2   (5+2)
dp[8]=3   (5+2+1)
dp[9]=3   (5+2+2)
dp[10]=2  (5+5)
dp[11]=3  (5+5+1)
```

Ghi chú thực chiến:
- `dp[x]` là min, nên khởi tạo INF và chỉ update khi `dp[x-c]` đã hữu hạn.
- Nếu đề yêu cầu “đếm số cách”, bạn sẽ đổi `min` → `sum`, và base `dp[0]=1`.

---

### Case 2: LIS (Longest Increasing Subsequence)

**Bài toán:** mảng `nums`, tìm độ dài dãy con tăng dần dài nhất (không cần liên tiếp).

**Ý tưởng:** nếu chỉ dùng `dp[i]=LIS trong prefix` thì thiếu thông tin “phần tử cuối”. Cách đúng: cố định **điểm kết thúc**.

**State:** `dp[i]` = độ dài LIS **kết thúc tại i**.

**Choices:** chọn `j < i` làm vị trí ngay trước i trong LIS.

**Transition:** nếu `nums[j] < nums[i]` thì `dp[i] = max(dp[i], dp[j] + 1)`.

**Base:** `dp[i] = 1` (mỗi phần tử tự tạo LIS độ dài 1).

**Order:** tăng i từ 0..n-1, bên trong duyệt j < i.

**Complexity:** O(n^2), memory O(n).

**Code O(n^2):**

```python
def lengthOfLIS(nums):
    n = len(nums)
    if n == 0:
        return 0
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

**Tối ưu ý tưởng (n log n):** dùng `tails[len]` là “giá trị nhỏ nhất có thể của phần tử cuối” cho subsequence dài `len+1`.

**Worked-through (dp ending at i)**

Ví dụ: `nums = [10, 9, 2, 5, 3, 7, 101, 18]`

- Khởi tạo `dp = [1,1,1,1,1,1,1,1]`
- Khi i=3 (nums[i]=5): nhìn j=2 (2<5) ⇒ dp[3]=dp[2]+1=2
- Khi i=5 (7): có thể nối sau 2,5,3 ⇒ dp[5]=3
- Khi i=6 (101): nối sau 7 ⇒ dp[6]=4
- Khi i=7 (18): nối sau 7 ⇒ dp[7]=4

Kết quả `max(dp)=4`.

---

### Case 3: 0-1 Knapsack (tối ưu giá trị)

**Bài toán:** n vật, mỗi vật (w,v), túi sức chứa W. Mỗi vật chọn 0/1. Max tổng value.

**Ý tưởng/backward:** xét vật i, chỉ có 2 lựa chọn: không lấy i hoặc lấy i (nếu đủ chỗ).

**State (2D kinh điển):** `dp[i][cap]` = max value khi xét i vật đầu với capacity `cap`.

**Transition:**
- Không lấy: `dp[i][cap] = dp[i-1][cap]`
- Lấy: `dp[i][cap] = max(dp[i][cap], dp[i-1][cap-w[i]] + v[i])`

**Base:** `dp[0][*]=0`.

**Tối ưu 1D:** `dp[cap]` và duyệt `cap` **ngược** để tránh dùng một vật nhiều lần.

**Code 1D:**

```python
def knapsack01(weights, values, W):
    dp = [0] * (W + 1)
    for w, v in zip(weights, values):
        for cap in range(W, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[W]
```

**Mini-verify direction:** nếu duyệt xuôi, bạn vô tình cho phép “lấy lại” cùng vật → biến thành unbounded.

**Worked-through (vì sao phải duyệt ngược)**

Ví dụ cực nhỏ:
- `weights=[2]`, `values=[3]`, `W=4`

Nếu duyệt **xuôi** `cap=2..4`:
- cap=2: dp[2] = max(dp[2], dp[0]+3) = 3
- cap=4: dp[4] = max(dp[4], dp[2]+3) = 6  ❌ (dùng 1 vật 2 lần)

Nếu duyệt **ngược** `cap=4..2`:
- cap=4: dp[4] = max(dp[4], dp[2]+3) = 3  ✅ (dp[2] lúc này vẫn là 0)
- cap=2: dp[2] = 3

Mẹo nhớ:
- 0-1 knapsack: duyệt ngược
- unbounded knapsack: duyệt xuôi

---

### Case 4: Edit Distance (Levenshtein)

**Bài toán:** biến `word1` thành `word2` với số thao tác ít nhất (insert/delete/replace).

**Ý tưởng/backward:** nhìn ký tự cuối: hoặc khớp nhau (không tốn) hoặc phải dùng 1 trong 3 thao tác để xử lý mismatch.

**State:** `dp[i][j]` = min ops để biến `word1[:i]` thành `word2[:j]`.

**Base:**
- `dp[i][0] = i` (xóa i ký tự)
- `dp[0][j] = j` (chèn j ký tự)

**Transition:**
- Nếu `word1[i-1] == word2[j-1]` ⇒ `dp[i][j] = dp[i-1][j-1]`
- Ngược lại:
  - Insert: `1 + dp[i][j-1]`
  - Delete: `1 + dp[i-1][j]`
  - Replace: `1 + dp[i-1][j-1]`

**Order:** tăng i, tăng j.

**Complexity:** O(mn), memory O(mn) (có thể rolling xuống O(min(m,n))).

**Code:**

```python
def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i][j - 1],      # insert
                    dp[i - 1][j],      # delete
                    dp[i - 1][j - 1],  # replace
                )

    return dp[m][n]
```

**Worked-through (bảng dp cho “horse” → “ros”)**

Hàng là prefix của `word1`, cột là prefix của `word2`:

```
      ''  r  o  s
''     0  1  2  3
h      1  1  2  3
o      2  2  1  2
r      3  2  2  2
s      4  3  3  2
e      5  4  4  3
```

Kết quả: `dp[5][3] = 3`.

**Mini-verify:** `minDistance("horse", "ros") == 3`.

---

### Case 5: Word Break (boolean DP)

**Bài toán:** `s`, `wordDict`. Kiểm tra s có thể tách thành các từ trong dict hay không.

**Ý tưởng/backward:** để prefix `s[:i]` tách được, phải tồn tại j < i sao cho prefix `s[:j]` tách được và đoạn `s[j:i]` là một từ.

**State:** `dp[i]` = True nếu `s[:i]` tách được.

**Base:** `dp[0]=True` (xâu rỗng).

**Transition:**

`dp[i] = any(dp[j] and s[j:i] in dict for j in [0..i))`

**Complexity:** O(n^2) substring checks (thực tế cần `set` để lookup O(1)).

**Code:**

```python
def wordBreak(s, wordDict):
    n = len(s)
    word_set = set(wordDict)
    dp = [False] * (n + 1)
    dp[0] = True

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break

    return dp[n]
```

**Worked-through (s = "leetcode", dict = {"leet","code"})**

Ta đánh dấu `dp[i]` là tách được `s[:i]`:

- dp[0]=True (xâu rỗng)
- i=4: có j=0 sao cho dp[0]=True và s[0:4]="leet" ∈ dict ⇒ dp[4]=True
- i=8: có j=4 sao cho dp[4]=True và s[4:8]="code" ∈ dict ⇒ dp[8]=True

Kết luận: dp[8]=True.

**Mini-verify:** `wordBreak("leetcode", ["leet","code"]) == True`.

---

## 3.1 Linear DP (1D)

Dấu hiệu: tiến theo i, mỗi bước nhìn vài bước trước.

### Ví dụ: Climbing Stairs
- State: `dp[i]` = số cách lên bậc i
- Transition: `dp[i] = dp[i-1] + dp[i-2]`
- Base: `dp[0]=1, dp[1]=1`

### Ví dụ: House Robber
- State: `dp[i]` = max tiền trong prefix [0..i]
- Transition: `dp[i] = max(dp[i-1], dp[i-2] + a[i])`

### Ví dụ: Maximum Subarray (Kadane)
- State: `dp[i]` = max sum kết thúc tại i
- Transition: `dp[i] = max(a[i], dp[i-1] + a[i])`

---

## 3.2 Grid DP (2D lưới)

Dấu hiệu: đường đi trên lưới, chỉ đi xuống/phải.

### Ví dụ: Unique Paths II (có chướng ngại)

```python
def uniquePathsWithObstacles(grid):
    m, n = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[m-1][n-1] == 1:
        return 0

    dp = [[0] * n for _ in range(m)]
    dp[0][0] = 1

    for j in range(1, n):
        if grid[0][j] == 0:
            dp[0][j] = dp[0][j-1]

    for i in range(1, m):
        if grid[i][0] == 0:
            dp[i][0] = dp[i-1][0]

    for i in range(1, m):
        for j in range(1, n):
            if grid[i][j] == 0:
                dp[i][j] = dp[i-1][j] + dp[i][j-1]

    return dp[m-1][n-1]
```

---

## 3.3 2-sequence DP (LCS / Edit Distance)

Dấu hiệu: 2 chuỗi/mảng, prefix.

### LCS (kèm truy vết)

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

### Edit Distance

```python
def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i][j-1],
                    dp[i-1][j],
                    dp[i-1][j-1]
                )

    return dp[m][n]
```

---

## 3.4 Knapsack family

### 0-1 Knapsack (mỗi vật 1 lần, 1D)

```python
for w, v in items:
    for cap in range(W, w-1, -1):
        dp[cap] = max(dp[cap], dp[cap-w] + v)
```

### Unbounded Knapsack (vô hạn, 1D)

```python
for w, v in items:
    for cap in range(w, W+1):
        dp[cap] = max(dp[cap], dp[cap-w] + v)
```

### Coin Change (min coins)

```python
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if i >= coin and dp[i-coin] != float('inf'):
                dp[i] = min(dp[i], dp[i-coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

---

## 3.5 Subsequence DP (LIS)

### LIS O(n^2)

```python
def lengthOfLIS(nums):
    n = len(nums)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp) if nums else 0
```

### LIS length O(n log n) (tails)

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

---

## 3.6 Boolean DP (Word Break)

```python
def wordBreak(s, wordDict):
    n = len(s)
    word_set = set(wordDict)
    dp = [False] * (n + 1)
    dp[0] = True

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break

    return dp[n]
```

---

## 3.7 State machine DP (stock, cooldown, k transactions)

Dấu hiệu: “mua/bán”, “cooldown”, “tối đa k lần”, “phí giao dịch”.

### Cooldown 1 ngày

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

### Tối đa k transactions

```python
def stock_k_transactions(prices, k):
    if not prices or k == 0:
        return 0

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

---

## 3.8 Interval DP (Split/Merge, Choose-last)

Dấu hiệu: tối ưu trên đoạn [l,r], “ghép/chia”, “burst”, “matrix chain”.

### Archetype A: Split/Merge

```python
for length in range(2, n+1):
    for l in range(0, n-length+1):
        r = l+length-1
        dp[l][r] = INF
        for k in range(l, r):
            dp[l][r] = min(dp[l][r], dp[l][k] + dp[k+1][r] + cost(l,r))
```

### Archetype B: Choose-last (Burst Balloons)

**Ý tưởng cốt lõi:** chọn k là **phần tử làm cuối** trong (l,r) để 2 phía độc lập.

- Chuẩn hoá: `a = [1] + nums + [1]`
- State: `dp[l][r]` = max coins khi burst hết balloon trong **khoảng mở** (l,r)
- Base: `dp[l][l+1]=0`

Transition:

`dp[l][r] = max(dp[l][k] + dp[k][r] + a[l]*a[k]*a[r])` với `k in (l,r)`

Code:

```python
def burst_balloons(nums):
    a = [1] + nums + [1]
    n = len(a)
    dp = [[0] * n for _ in range(n)]

    for length in range(2, n):
        for l in range(0, n - length):
            r = l + length
            best = 0
            for k in range(l + 1, r):
                best = max(best, dp[l][k] + dp[k][r] + a[l] * a[k] * a[r])
            dp[l][r] = best

    return dp[0][n - 1]
```

### Worked-through: Burst Balloons với nums = [3,1,5]

Ta chuẩn hoá:
- `nums = [3, 1, 5]`
- `a = [1, 3, 1, 5, 1]`
- Chỉ số: 0..4

Nhắc lại: `dp[l][r]` là max coins khi burst hết balloon trong **khoảng mở** (l, r) (tức burst các index `l+1..r-1`).

Ta duyệt `length = r - l` tăng dần.

**length = 2** (chỉ có đúng 1 balloon ở giữa)

- (l,r)=(0,2) ⇒ k=1
    - `dp[0][2] = a[0]*a[1]*a[2] = 1*3*1 = 3`
- (1,3) ⇒ k=2
    - `dp[1][3] = 3*1*5 = 15`
- (2,4) ⇒ k=3
    - `dp[2][4] = 1*5*1 = 5`

**length = 3** (mỗi đoạn có 2 lựa chọn k)

- (0,3), k∈{1,2}
    - k=1: `dp[0][1] + dp[1][3] + 1*3*5 = 0 + 15 + 15 = 30`
    - k=2: `dp[0][2] + dp[2][3] + 1*1*5 = 3 + 0 + 5 = 8`
    ⇒ `dp[0][3] = 30`

- (1,4), k∈{2,3}
    - k=2: `dp[1][2] + dp[2][4] + 3*1*1 = 0 + 5 + 3 = 8`
    - k=3: `dp[1][3] + dp[3][4] + 3*5*1 = 15 + 0 + 15 = 30`
    ⇒ `dp[1][4] = 30`

**length = 4** (đoạn full), k∈{1,2,3}

- (0,4)
    - k=1: `dp[0][1] + dp[1][4] + 1*3*1 = 0 + 30 + 3 = 33`
    - k=2: `dp[0][2] + dp[2][4] + 1*1*1 = 3 + 5 + 1 = 9`
    - k=3: `dp[0][3] + dp[3][4] + 1*5*1 = 30 + 0 + 5 = 35`
    ⇒ `dp[0][4] = 35`

Kết quả cuối: `dp[0][4] = 35`.

---

## 3.9 Tree DP

Template “chọn/bỏ node”:
- `dp[u][0]`: không chọn u
- `dp[u][1]`: chọn u

```python
def dfs(u, parent):
    dp0, dp1 = 0, value[u]
    for v in adj[u]:
        if v == parent:
            continue
        c0, c1 = dfs(v, u)
        dp0 += max(c0, c1)
        dp1 += c0
    return dp0, dp1
```

---

## 3.10 Bitmask DP

### Ví dụ: TSP (O(2^n * n^2))

```python
def tsp(dist):
    n = len(dist)
    INF = 10**30
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0

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

---

## 3.11 Profile / Broken profile DP (tiling)

Dấu hiệu: tiling / grid placement, chuyển theo từng row.

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

Worked-through: lát domino 2x3 → kết quả = 3.

---

## 3.12 Digit DP

Chiến lược chuẩn:
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

### Worked-through 1: tổng chữ số % 3 == 0 (tính cả số 0)

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
                return 1
            return 1 if mod == 0 else 0

        limit = digits[pos] if tight else 9
        res = 0

        for d in range(0, limit + 1):
            ntight = tight and (d == limit)
            if not started and d == 0:
                res += dfs(pos + 1, mod, ntight, False)
            else:
                res += dfs(pos + 1, (mod + d) % 3, ntight, True)
        return res

    return dfs(0, 0, True, False)

def count_sum_digits_mod3(L: int, R: int) -> int:
    return count_sum_digits_mod3_upto(R) - count_sum_digits_mod3_upto(L - 1)
```

Mini sanity check: x=20 ⇒ {0,3,6,9,12,15,18} → 7 số.

### Brute-force đối chiếu (R nhỏ) cho Worked-through 1

Khi tự học digit DP, cách chắc nhất là viết brute force và so sánh trên R nhỏ (vd 0..5000):

```python
def brute_count_sum_digits_mod3_upto(x: int) -> int:
    if x < 0:
        return 0
    ans = 0
    for v in range(0, x + 1):
        s = sum(int(ch) for ch in str(v))
        if s % 3 == 0:
            ans += 1
    return ans

for R in [0, 1, 20, 99, 1234, 5000]:
    assert count_sum_digits_mod3_upto(R) == brute_count_sum_digits_mod3_upto(R)
```

### Worked-through 2: unique digits + không có 2 chữ số kề nhau chênh lệch 1

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
                res += dfs(pos + 1, NO_PREV, mask, ntight, False)
                continue

            if prev != NO_PREV and abs(d - prev) == 1:
                continue

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

### Brute-force đối chiếu (R nhỏ) cho Worked-through 2

```python
def ok_adjacent_not1_and_unique(v: int) -> bool:
    s = str(v)
    if len(set(s)) != len(s):
        return False
    for i in range(1, len(s)):
        if abs(int(s[i]) - int(s[i - 1])) == 1:
            return False
    return True

def brute_count_adjacent_not1_and_unique_upto(x: int, include_zero: bool = False) -> int:
    if x < 0:
        return 0
    lo = 0 if include_zero else 1
    return sum(1 for v in range(lo, x + 1) if ok_adjacent_not1_and_unique(v))

for R in [0, 9, 20, 99, 500, 2000]:
    assert count_adjacent_not1_and_unique_upto(R, include_zero=True) == brute_count_adjacent_not1_and_unique_upto(R, include_zero=True)
```

---

## 3.13 Probability DP

Đặc điểm: tính xác suất/kỳ vọng (probability/expected value).

Ví dụ: Soup Servings (LeetCode 808)

```python
from functools import lru_cache

def soupServings(n):
    if n >= 4800:
        return 1.0

    @lru_cache(None)
    def dp(a, b):
        if a <= 0 and b <= 0:
            return 0.5
        if a <= 0:
            return 1.0
        if b <= 0:
            return 0.0

        return 0.25 * (
            dp(a - 100, b) +
            dp(a - 75, b - 25) +
            dp(a - 50, b - 50) +
            dp(a - 25, b - 75)
        )

    return dp(n, n)
```

---

# 4. Tối ưu hoá DP (khi TLE)

## Đổi state / giảm chiều

Khi DP đang O(n^2) hoặc O(n^3):
1) Đổi state (ví dụ LIS `dp ending` → `tails`).
2) Giảm chiều (2D → rolling/1D).
3) Precompute `cost()` để O(1).
4) Nhận diện “min/max over k” để dùng tối ưu nâng cao.

## Divide & Conquer DP Optimization

Áp dụng cho dạng:

`dp[i][j] = min_{k <= j} (dp[i-1][k] + C(k+1, j))`

và có tính đơn điệu: `opt[i][j] <= opt[i][j+1]`.

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

## Knuth Optimization

Áp dụng cho interval DP dạng:

`dp[l][r] = min_{k in [l..r]} (dp[l][k] + dp[k][r]) + C(l,r)`

và thỏa:

`opt[l][r-1] <= opt[l][r] <= opt[l+1][r]`

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

## Convex Hull Trick (CHT)

Áp dụng khi có dạng:

`dp[i] = min(dp[j] + b[j] * a[i])`

và b[j] đơn điệu (và thường a[i] đơn điệu theo thứ tự query).

Template (b giảm dần, a tăng dần):

```python
class CHT:
    def __init__(self):
        self.lines = []  # (slope, intercept)

    def bad(self, l1, l2, l3):
        return (l3[1]-l1[1]) * (l1[0]-l2[0]) <= (l2[1]-l1[1]) * (l1[0]-l3[0])

    def add(self, m, c):
        line = (m, c)
        while len(self.lines) >= 2 and self.bad(self.lines[-2], self.lines[-1], line):
            self.lines.pop()
        self.lines.append(line)

    def query(self, x):
        while len(self.lines) >= 2:
            m1, c1 = self.lines[0]
            m2, c2 = self.lines[1]
            if m1 * x + c1 >= m2 * x + c2:
                self.lines.pop(0)
            else:
                break
        m, c = self.lines[0]
        return m * x + c
```

Gợi ý: nếu b hoặc a không đơn điệu → cân nhắc Li Chao Tree hoặc query bằng binary search.

## SOS DP (Sum Over Subsets)

Bài toán: với mỗi mask, tính tổng `f[submask]` cho mọi `submask ⊆ mask`.

SOS DP O(n * 2^n):

```python
def sos_dp(f, n):
    sos = f.copy()
    for bit in range(n):
        for mask in range(1<<n):
            if mask & (1<<bit):
                sos[mask] += sos[mask ^ (1<<bit)]
    return sos
```

Superset SOS:

```python
def superset_sos(f, n):
    sos = f.copy()
    for bit in range(n):
        for mask in range((1<<n)-1, -1, -1):
            if not (mask & (1<<bit)):
                sos[mask] += sos[mask | (1<<bit)]
    return sos
```

---

# 5. Debug & verify

## Checklist trước khi code

- `dp[...]` có nghĩa rõ 1 câu chưa?
- Transition đã xét đủ choice chưa?
- Base case đủ chưa? (n=0, empty, start=false…)
- Invalid state xử lý thế nào? (INF / -INF / 0)
- Loop order đúng chưa? (đặc biệt knapsack 1D)
- Off-by-one (prefix, open interval) có bị dính không?
- Overflow: INF + cost?
- Nếu đếm số cách: có quên mod không?

## Sai lầm thường gặp

- Sai định nghĩa state (đặc biệt LIS, stock).
- Sai thứ tự duyệt (0-1 knapsack duyệt xuôi → chọn 1 vật nhiều lần).
- Sai base case (coin change, edit distance).
- Quên xử lý leading zeros trong digit DP.

## Cách tự test

- In bảng dp với n nhỏ.
- Với digit DP: brute force R nhỏ (vd 10000) để đối chiếu.
- Với interval DP: tự tính tay ví dụ 3–5 phần tử.
- Với tree DP: test cây nhỏ (1 node, chain, star).

---

# 6. Bài tập & lộ trình

## Bài tập theo pattern

Danh sách bài (gợi ý) được gom theo pattern:

- Linear DP: LC 70, 198, 213, 53, 152
- Knapsack: LC 416, 494, 322, 518, 474
- Subsequence: LC 300, 1143, 516, 72, 583
- Interval DP: LC 312, 1039, 87, 1000
- State machine: LC 121, 122, 123, 309, 714
- Bitmask DP: LC 1879, 847, 1125, 943
- Digit DP: LC 233, 357, 600, 902
- Advanced: CF 319C (CHT), CF 165E (SOS), CF 455E (D&C)

## Lộ trình 4 tuần

Tuần 1: Nền tảng
- Fibonacci/Climbing Stairs, House Robber, Maximum Subarray
- Unique Paths I/II, Min Path Sum

Tuần 2: Knapsack & Subsequence
- Coin Change I/II, Partition, Target Sum
- LIS (O(n^2) và O(n log n)), LCS, Edit Distance

Tuần 3: String & Advanced Patterns
- Word Break I/II, Palindrome Partitioning II
- Stock variants, Burst Balloons

Tuần 4: Competition level
- House Robber III (Tree DP), TSP (Bitmask DP)
- Digit DP, 1–2 bài CHT/SOS

---

# PHẦN MỞ RỘNG CHI TIẾT

---

# A. GIẢI THÍCH KỸ PATTERNS PHỨC TẠP

## A.1 Interval DP - Phân tích sâu

### Tại sao Interval DP khó?

```
Interval DP khó vì:
1. Phải nghĩ theo "khoảng" thay vì "vị trí"
2. Thứ tự duyệt không trực quan (theo length)
3. Có 2 archetype khác nhau dễ nhầm lẫn
```

### Archetype A: Split/Merge - Khi nào dùng?

**Dấu hiệu:**
- Bài yêu cầu **chia đoạn** thành các phần
- Cost phụ thuộc vào **toàn bộ đoạn** (VD: tổng, prefix sum)
- Ví dụ: Matrix Chain Multiplication, Merge Stones

```
┌─────────────────────────────────────────────────────────────┐
│   SPLIT/MERGE: Chọn điểm k để CHIA đoạn [l,r]              │
│                                                             │
│   [l ─────── k ─────── r]                                  │
│      ↓          ↓                                          │
│   [l...k]    [k+1...r]                                     │
│                                                             │
│   dp[l][r] = min(dp[l][k] + dp[k+1][r] + cost(l,r))        │
│              cho mọi k ∈ [l, r-1]                          │
└─────────────────────────────────────────────────────────────┘
```

### Archetype B: Choose-last - Khi nào dùng?

**Dấu hiệu:**
- Thứ tự xử lý **ảnh hưởng lẫn nhau**
- Nếu chọn phần tử "đầu tiên", 2 bên vẫn dính nhau
- Phải chọn phần tử **cuối cùng** để 2 bên độc lập
- Ví dụ: Burst Balloons

```
┌─────────────────────────────────────────────────────────────┐
│   CHOOSE-LAST: Chọn k là phần tử XỬ LÝ CUỐI trong (l,r)    │
│                                                             │
│   [l ─── ... ─── k ─── ... ─── r]                          │
│                  ↑                                          │
│            Làm cuối cùng                                    │
│                                                             │
│   Khi k làm cuối, hàng xóm của k là l và r (cố định)       │
│   → 2 phía (l,k) và (k,r) hoàn toàn độc lập                │
│                                                             │
│   dp[l][r] = max(dp[l][k] + dp[k][r] + profit(l,k,r))      │
│              cho mọi k ∈ (l, r)                            │
└─────────────────────────────────────────────────────────────┘
```

### So sánh 2 Archetype

| Aspect | Split/Merge | Choose-last |
|--------|-------------|-------------|
| Chia tại k | k là biên giữa 2 phần | k là phần tử cuối trong đoạn |
| Đoạn con | [l,k] và [k+1,r] | (l,k) và (k,r) (mở) |
| Cost | Thường phụ thuộc toàn đoạn | Phụ thuộc k và 2 biên |
| Ví dụ | Matrix Chain, Merge Stones | Burst Balloons |

### Worked-through: Matrix Chain Multiplication

**Bài toán:** Có n ma trận, kích thước cho bởi mảng p (ma trận i là p[i-1] × p[i]).
Tìm thứ tự nhân để minimize số phép nhân scalar.

**Ví dụ:** p = [10, 30, 5, 60] → 3 ma trận: A1(10×30), A2(30×5), A3(5×60)

**Phân tích từng bước:**

```
BƯỚC 1: Định nghĩa state
   dp[i][j] = min cost nhân Ai...Aj

BƯỚC 2: Transition
   Chọn k là điểm chia: (Ai...Ak) × (Ak+1...Aj)
   Cost = dp[i][k] + dp[k+1][j] + p[i-1] × p[k] × p[j]

BƯỚC 3: Base case
   dp[i][i] = 0 (1 ma trận, không cần nhân)

BƯỚC 4: Order
   Duyệt theo length tăng dần

BƯỚC 5: Tính tay
   length=2:
   - dp[1][2] = p[0]*p[1]*p[2] = 10*30*5 = 1500
   - dp[2][3] = p[1]*p[2]*p[3] = 30*5*60 = 9000

   length=3:
   - dp[1][3] = min(
       k=1: dp[1][1] + dp[2][3] + 10*30*60 = 0 + 9000 + 18000 = 27000
       k=2: dp[1][2] + dp[3][3] + 10*5*60  = 1500 + 0 + 3000 = 4500
     ) = 4500
```

**Kết quả:** 4500, thứ tự tối ưu: (A1 × (A2 × A3))

---

## A.2 State Machine DP - Phân tích sâu

### Tại sao gọi là "State Machine"?

```
┌─────────────────────────────────────────────────────────────┐
│  Tại mỗi thời điểm, ta ở một trong các TRẠNG THÁI:         │
│                                                             │
│     ┌──────┐      buy        ┌──────┐                      │
│     │ REST │ ───────────────→│ HOLD │                      │
│     │      │←────────────────│      │                      │
│     └──────┘    cooldown     └──────┘                      │
│         ↑                        │                          │
│         │        sell            │                          │
│         │                        ↓                          │
│         │                   ┌──────┐                        │
│         └───────────────────│ SOLD │                        │
│              (next day)     └──────┘                        │
│                                                             │
│  Transition = di chuyển giữa các state dựa trên action     │
└─────────────────────────────────────────────────────────────┘
```

### Các biến thể Stock và cách xử lý

| Biến thể | States | Đặc biệt |
|----------|--------|----------|
| **Stock I** (1 transaction) | Track min so far | Greedy đủ |
| **Stock II** (unlimited) | Mua mọi uptrend | Greedy đủ |
| **Stock III** (≤2 trans) | dp[trans][hold/cash] | DP |
| **Stock IV** (≤k trans) | dp[trans][hold/cash] | DP, check k lớn |
| **Cooldown** | hold/sold/rest | 3 states |
| **Transaction Fee** | hold/cash với fee khi sell | 2 states |

### Worked-through: Stock với Cooldown

**Bài toán:** Mua/bán không giới hạn, nhưng sau khi bán phải nghỉ 1 ngày.

**3 States:**
- `hold`: đang giữ stock
- `sold`: vừa bán hôm nay (ngày mai phải rest)
- `rest`: không giữ và không vừa bán

**Transitions:**

```python
# Ngày i, với giá p:

# hold[i]: đang giữ stock
#   - Giữ nguyên từ hôm qua: hold[i-1]
#   - Hoặc mua hôm nay (từ rest): rest[i-1] - p
hold[i] = max(hold[i-1], rest[i-1] - p)

# sold[i]: vừa bán hôm nay
#   - Bán stock đang giữ: hold[i-1] + p
sold[i] = hold[i-1] + p

# rest[i]: không giữ, không vừa bán
#   - Giữ nguyên rest: rest[i-1]
#   - Hoặc đã xong cooldown: sold[i-1]
rest[i] = max(rest[i-1], sold[i-1])
```

**Ví dụ:** prices = [1, 2, 3, 0, 2]

```
Khởi tạo: hold = -∞, sold = -∞, rest = 0

Ngày 0 (p=1): hold=-1, sold=-∞, rest=0
Ngày 1 (p=2): hold=-1, sold=1,  rest=0
Ngày 2 (p=3): hold=-1, sold=2,  rest=1
Ngày 3 (p=0): hold=1,  sold=-1, rest=2
Ngày 4 (p=2): hold=1,  sold=3,  rest=2

Kết quả: max(sold, rest) = 3
```

---

## A.3 Bitmask DP - Phân tích sâu

### Khi nào dùng Bitmask DP?

```
DÙNG KHI:
✅ n nhỏ (≤ 20-22)
✅ Cần track "đã thăm/chọn những gì"
✅ Không có cách encode state hiệu quả hơn

KHÔNG DÙNG KHI:
❌ n lớn (> 25)
❌ Có thể dùng DP đơn giản hơn
❌ Chỉ cần count, không cần track
```

### Các operations cơ bản với bitmask

```python
# Kiểm tra bit thứ i có bật không
if mask & (1 << i): ...

# Bật bit thứ i
new_mask = mask | (1 << i)

# Tắt bit thứ i
new_mask = mask & ~(1 << i)

# Toggle bit thứ i
new_mask = mask ^ (1 << i)

# Đếm số bit bật
count = bin(mask).count('1')
# Hoặc: count = mask.bit_count()  (Python 3.10+)

# Duyệt tất cả subset của mask
submask = mask
while submask > 0:
    # process submask
    submask = (submask - 1) & mask
```

### Worked-through: Assignment Problem

**Bài toán:** n người, n việc, cost[i][j] = chi phí người i làm việc j.
Mỗi người làm đúng 1 việc, mỗi việc đúng 1 người. Min tổng cost.

**State:** `dp[mask]` = min cost khi các việc trong mask đã được gán cho i người đầu tiên (i = popcount(mask))

```python
def assignment(cost):
    n = len(cost)
    INF = float('inf')
    dp = [INF] * (1 << n)
    dp[0] = 0
    
    for mask in range(1 << n):
        i = bin(mask).count('1')  # Số người đã gán
        if i >= n:
            continue
        
        for j in range(n):
            if mask & (1 << j):  # Việc j đã được gán
                continue
            new_mask = mask | (1 << j)
            dp[new_mask] = min(dp[new_mask], dp[mask] + cost[i][j])
    
    return dp[(1 << n) - 1]

# Ví dụ:
cost = [
    [9, 2, 7, 8],
    [6, 4, 3, 7],
    [5, 8, 1, 8],
    [7, 6, 9, 4]
]
print(assignment(cost))  # 13 (2+4+1+6? hoặc tính đúng)
```

---

# B. VÍ DỤ WORKED-THROUGH BỔ SUNG

## B.1 Longest Palindromic Subsequence

**Bài toán:** Tìm độ dài dãy con palindrome dài nhất.

**Ý tưởng:** LPS(s) = LCS(s, reverse(s))

```python
def longestPalindromeSubseq(s):
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

**Worked-through:** s = "bbbab"

```
t = "babbb"

      ""  b  a  b  b  b
  ""   0  0  0  0  0  0
  b    0  1  1  1  1  1
  b    0  1  1  2  2  2
  b    0  1  1  2  3  3
  a    0  1  2  2  3  3
  b    0  1  2  3  3  4

Kết quả: 4 (bbbb)
```

---

## B.2 Partition Equal Subset Sum

**Bài toán:** Chia mảng thành 2 subset có tổng bằng nhau.

**Chuyển đổi:** Tìm subset có tổng = total/2 (0-1 Knapsack boolean)

```python
def canPartition(nums):
    total = sum(nums)
    if total % 2:
        return False
    
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True
    
    for x in nums:
        for w in range(target, x-1, -1):  # Duyệt ngược!
            dp[w] = dp[w] or dp[w-x]
    
    return dp[target]
```

**Worked-through:** nums = [1, 5, 11, 5]

```
total = 22, target = 11

Khởi tạo: dp = [T, F, F, F, F, F, F, F, F, F, F, F]

Sau x=1:  dp = [T, T, F, F, F, F, F, F, F, F, F, F]
Sau x=5:  dp = [T, T, F, F, F, T, T, F, F, F, F, F]
Sau x=11: dp = [T, T, F, F, F, T, T, F, F, F, F, T]  ← dp[11]=True!
Sau x=5:  dp = [T, T, F, F, F, T, T, F, F, F, T, T]

Kết quả: True (subset [1,5,5] = 11)
```

---

## B.3 Unique Paths với Chướng ngại vật (Grid DP chi tiết)

**Worked-through:** 
```
grid = [
    [0, 0, 0],
    [0, 1, 0],
    [0, 0, 0]
]
```

**Bước 1: Khởi tạo dp**
```
dp = [
    [1, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]
```

**Bước 2: Điền hàng đầu**
```
dp = [
    [1, 1, 1],   ← Nếu không có chướng ngại
    [0, 0, 0],
    [0, 0, 0]
]
```

**Bước 3: Điền cột đầu**
```
dp = [
    [1, 1, 1],
    [1, 0, 0],   ← Dừng nếu gặp chướng ngại
    [1, 0, 0]
]
```

**Bước 4: Điền phần còn lại**
```
Ô (1,1) là chướng ngại → dp[1][1] = 0

dp = [
    [1, 1, 1],
    [1, 0, 1],   ← dp[1][2] = 0 + 1 = 1
    [1, 1, 2]    ← dp[2][2] = 1 + 1 = 2
]
```

**Kết quả:** 2 đường đi

---

# C. CHT VÀ SOS DP MỞ RỘNG

## C.1 Convex Hull Trick - Giải thích đầy đủ

### Bài toán gốc

Khi có recurrence dạng:
```
dp[i] = min(dp[j] + b[j] * a[i])   với j < i
```

Brute force: O(n²)

### Ý tưởng CHT

Mỗi j tạo ra đường thẳng: `y = b[j] * x + dp[j]`

Query tại x = a[i]: tìm đường thẳng cho y nhỏ nhất.

→ Duy trì **lower envelope** (convex hull) của các đường thẳng.

### Điều kiện áp dụng

| Điều kiện | Thuật toán | Complexity |
|-----------|------------|------------|
| b[j] giảm, a[i] tăng | Deque đơn giản | O(n) |
| b[j] giảm, a[i] bất kỳ | Binary search trên hull | O(n log n) |
| b[j] bất kỳ | Li Chao Tree | O(n log max_x) |

### Ví dụ chi tiết: Covered Walkway

**Bài toán:** n người tại vị trí x[0..n-1] (sorted).  
Xây mái che từ người i đến j tốn: C + (x[j] - x[i])²  
Tìm min cost để che hết.

**Phân tích:**
```
dp[i] = min cost che hết người 0..i

dp[i] = min(dp[j-1] + C + (x[i] - x[j])²)   với j ≤ i
      = min(dp[j-1] + C + x[i]² - 2*x[i]*x[j] + x[j]²)
      = x[i]² + C + min(dp[j-1] + x[j]² - 2*x[j]*x[i])

Đặt:
  - Query x = x[i]
  - Slope b[j] = -2*x[j]
  - Intercept c[j] = dp[j-1] + x[j]²

→ dp[i] = x[i]² + C + min(b[j]*x + c[j])
```

Vì x[j] tăng → b[j] = -2*x[j] giảm, và x[i] tăng → CHT deque O(n)!

```python
from collections import deque

def covered_walkway(x, C):
    n = len(x)
    dp = [0] * n
    
    # lines: deque of (slope, intercept)
    lines = deque()
    
    def add_line(m, c):
        while len(lines) >= 2:
            m1, c1 = lines[-2]
            m2, c2 = lines[-1]
            # Kiểm tra line cuối có cần không
            # (c - c1) / (m1 - m) <= (c2 - c1) / (m1 - m2)
            if (c - c1) * (m1 - m2) <= (c2 - c1) * (m1 - m):
                lines.pop()
            else:
                break
        lines.append((m, c))
    
    def query(x_val):
        while len(lines) >= 2:
            m1, c1 = lines[0]
            m2, c2 = lines[1]
            if m1 * x_val + c1 >= m2 * x_val + c2:
                lines.popleft()
            else:
                break
        m, c = lines[0]
        return m * x_val + c
    
    # Base: dp[-1] = 0, thêm line cho j=0
    add_line(-2 * x[0], x[0] ** 2)  # dp[-1] + x[0]² = 0 + x[0]²
    
    for i in range(n):
        dp[i] = x[i] ** 2 + C + query(x[i])
        # Thêm line mới cho j = i+1
        if i + 1 < n:
            add_line(-2 * x[i+1], dp[i] + x[i+1] ** 2)
    
    return dp[n-1]
```

---

## C.2 SOS DP - Giải thích đầy đủ

### Bài toán

Cho mảng f[mask], với mỗi mask tính:
```
sos[mask] = Σ f[submask]   với mọi submask ⊆ mask
```

### Brute force: O(3^n)

```python
for mask in range(1 << n):
    submask = mask
    while submask >= 0:
        sos[mask] += f[submask]
        if submask == 0:
            break
        submask = (submask - 1) & mask
```

### SOS DP: O(n * 2^n)

**Ý tưởng:** Xây dựng theo từng bit.

`sos[mask][i]` = tổng f của các subset mà chỉ khác mask ở các bit 0..i-1.

```python
def sos_dp(f, n):
    sos = f.copy()
    for bit in range(n):
        for mask in range(1 << n):
            if mask & (1 << bit):
                sos[mask] += sos[mask ^ (1 << bit)]
    return sos
```

### Worked-through: n=3

```
f = [f[000], f[001], f[010], f[011], f[100], f[101], f[110], f[111]]

Sau bit 0:
  sos[001] += sos[000]  → f[001] + f[000]
  sos[011] += sos[010]  → f[011] + f[010]
  sos[101] += sos[100]  → f[101] + f[100]
  sos[111] += sos[110]  → f[111] + f[110]

Sau bit 1:
  sos[010] += sos[000]  → f[010] + f[000]
  sos[011] += sos[001]  → (f[011]+f[010]) + (f[001]+f[000])
  sos[110] += sos[100]  → f[110] + f[100]
  sos[111] += sos[101]  → đã gồm tất cả 4 số bit0=1 + 4 số bit1=1

Sau bit 2:
  sos[100] += sos[000]
  sos[101] += sos[001]
  sos[110] += sos[010]
  sos[111] += sos[011]  → gồm tất cả 8 subsets
```

### Ví dụ: Đếm cặp (i,j) sao cho A[i] AND A[j] = 0

```python
def count_and_zero_pairs(arr, max_bits=20):
    cnt = [0] * (1 << max_bits)
    for x in arr:
        cnt[x] += 1
    
    # SOS: sos[mask] = số phần tử là subset của mask
    sos = cnt.copy()
    for bit in range(max_bits):
        for mask in range(1 << max_bits):
            if mask & (1 << bit):
                sos[mask] += sos[mask ^ (1 << bit)]
    
    result = 0
    for x in arr:
        complement = ((1 << max_bits) - 1) ^ x
        result += sos[complement]
    
    return result // 2  # Mỗi cặp đếm 2 lần
```

---

# D. CẤU TRÚC VÀ TIPS TỔ CHỨC

## D.1 Flowchart chọn Pattern

```
                    ┌─────────────────────────┐
                    │     ĐỌC ĐỀ BÀI          │
                    └───────────┬─────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
    ┌─────────┐           ┌─────────┐           ┌─────────┐
    │ 1 array │           │ 2 array │           │  Grid   │
    │ /string │           │ /string │           │   2D    │
    └────┬────┘           └────┬────┘           └────┬────┘
         │                      │                      │
    ┌────┴────┐                 │               ┌──────┴──────┐
    ▼         ▼                 ▼               ▼             ▼
┌───────┐ ┌───────┐       ┌─────────┐     ┌─────────┐   ┌─────────┐
│Linear │ │Subseq │       │2-Seq DP │     │Path DP  │   │Interval │
│  DP   │ │(LIS)  │       │(LCS,    │     │(Unique  │   │   DP    │
└───────┘ └───────┘       │ Edit)   │     │ Paths)  │   └─────────┘
                          └─────────┘     └─────────┘

         ┌─────────────────────────────────────────────┐
         │              CÁC DẤU HIỆU ĐẶC BIỆT          │
         ├─────────────────────────────────────────────┤
         │ n ≤ 20 + track subset → Bitmask DP          │
         │ Đếm số trong [L,R] theo digit → Digit DP    │
         │ Tree structure → Tree DP                    │
         │ Mua/bán/cooldown → State Machine DP         │
         │ Knapsack keywords → Knapsack family         │
         └─────────────────────────────────────────────┘
```

## D.2 Checklist Debug mở rộng

```
┌─────────────────────────────────────────────────────────────┐
│   CHECKLIST DEBUG DP (CHI TIẾT)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ □ 1. STATE: dp[...] có nghĩa rõ 1 câu?                     │
│      → Viết comment giải thích                              │
│                                                             │
│ □ 2. TRANSITION: đã xét ĐỦ choices?                        │
│      → Liệt kê tất cả trường hợp bằng tay                  │
│                                                             │
│ □ 3. BASE CASE: đủ và đúng?                                │
│      → Test với input nhỏ nhất (n=0, n=1)                  │
│                                                             │
│ □ 4. INVALID STATE: xử lý thế nào?                         │
│      → INF, -INF, hay 0? Có consistent không?              │
│                                                             │
│ □ 5. ORDER: đúng thứ tự?                                   │
│      → 0-1 knapsack phải duyệt ngược                       │
│      → Interval DP phải theo length                        │
│                                                             │
│ □ 6. INDEX: 0-indexed hay 1-indexed?                       │
│      → Prefix sum, dp[i] ứng với gì?                       │
│                                                             │
│ □ 7. OVERFLOW: INF + cost có tràn không?                   │
│      → Dùng 10**18 thay vì 10**30 nếu cần                  │
│                                                             │
│ □ 8. MOD: đếm số cách có quên mod?                         │
│      → Mod sau mỗi phép cộng                               │
│                                                             │
│ □ 9. EDGE CASE: empty, single element?                     │
│      → Test cả boundary conditions                         │
│                                                             │
│ □ 10. IN RA DP TABLE:                                      │
│       → Với n nhỏ, in ra để verify từng giá trị            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# E. DẠNG BÀI NÂNG CAO

## E.1 Tree DP với Rerooting

**Bài toán:** Tính đáp án khi mỗi node là root.

**Ý tưởng:** 
1. DFS 1: Tính dp[u] với root cố định
2. DFS 2: Tính dp[u] khi u là root (dùng thông tin từ parent)

```python
def tree_dp_rerooting(adj, n):
    # dp1[u] = đáp án cho subtree rooted at u (root = 0)
    # dp2[u] = đáp án khi u là root
    
    dp1 = [0] * n
    dp2 = [0] * n
    
    # DFS 1: Post-order
    def dfs1(u, parent):
        dp1[u] = base_value(u)
        for v in adj[u]:
            if v != parent:
                dfs1(v, u)
                dp1[u] = combine(dp1[u], dp1[v])
    
    # DFS 2: Pre-order
    def dfs2(u, parent, from_parent):
        dp2[u] = combine(dp1[u], from_parent)
        
        # Tính contribution của tất cả children
        children_sum = from_parent
        for v in adj[u]:
            if v != parent:
                children_sum = combine(children_sum, dp1[v])
        
        # Cho mỗi child, truyền "phần còn lại"
        for v in adj[u]:
            if v != parent:
                without_v = remove(children_sum, dp1[v])
                dfs2(v, u, without_v)
    
    dfs1(0, -1)
    dfs2(0, -1, identity_value)
    
    return dp2
```

### Ví dụ: Sum of Distances in Tree

**Bài toán:** Với mỗi node u, tính tổng khoảng cách đến tất cả node khác.

```python
def sumOfDistancesInTree(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    
    count = [1] * n  # Số node trong subtree
    ans = [0] * n
    
    # DFS 1: Tính count[u] và ans[0]
    def dfs1(u, parent):
        for v in adj[u]:
            if v != parent:
                dfs1(v, u)
                count[u] += count[v]
                ans[0] += ans[v] + count[v]
    
    # DFS 2: Tính ans[u] từ ans[parent]
    def dfs2(u, parent):
        for v in adj[u]:
            if v != parent:
                # Khi chuyển root từ u sang v:
                # - count[v] nodes gần hơn 1
                # - (n - count[v]) nodes xa hơn 1
                ans[v] = ans[u] + (n - count[v]) - count[v]
                dfs2(v, u)
    
    dfs1(0, -1)
    dfs2(0, -1)
    return ans
```

---

## E.2 Profile DP / Broken Profile - Chi tiết

**Bài toán:** Đếm cách lát domino 2×1 trên bảng R×C.

**Key insight:** 
- Scan từng hàng
- `mask` encode trạng thái "nhô ra" xuống hàng tiếp theo

### Worked-through chi tiết: 2×3 board

```
Bảng 2×3:
┌───┬───┬───┐
│   │   │   │ Row 0
├───┼───┼───┤
│   │   │   │ Row 1
└───┴───┴───┘
 c0  c1  c2

Mask 3-bit: bit i = 1 nghĩa là ô (row_hiện_tại, col_i) đã bị chiếm
           (do domino dọc từ row trước)
```

**Initial:** dp = {000: 1}

**Row 0, mask = 000:**
Các cách fill row 0:
1. 3 domino dọc → next_mask = 111
2. 1 ngang (col0,1) + 1 dọc (col2) → next_mask = 100
3. 1 dọc (col0) + 1 ngang (col1,2) → next_mask = 001

**Sau row 0:** dp = {111: 1, 100: 1, 001: 1}

**Row 1:**
- mask = 111: tất cả đã chiếm, chỉ skip → next = 000
- mask = 100: col0,1 trống, đặt ngang → next = 000
- mask = 001: col1,2 trống, đặt ngang → next = 000

**Sau row 1:** dp = {000: 3}

**Kết quả:** 3 cách lát domino.

---

## E.3 Probability/Expected Value DP

### Ý tưởng chung

```
Thay vì đếm/min/max, ta tính xác suất hoặc kỳ vọng.

E[X] = Σ P(event_i) × value_i

Transition thường có dạng:
dp[state] = Σ P(choice) × (cost(choice) + dp[next_state])
```

### Ví dụ: Expected rolls to get target

**Bài toán:** Xúc xắc 6 mặt, kỳ vọng số lần tung để tổng ≥ target.

```python
from functools import lru_cache

def expected_rolls(target):
    @lru_cache(None)
    def dp(sum_so_far):
        if sum_so_far >= target:
            return 0
        
        # E = 1 + (1/6) × Σ dp(sum + i) for i in 1..6
        exp = 1  # Tung 1 lần
        for die in range(1, 7):
            exp += (1/6) * dp(sum_so_far + die)
        return exp
    
    return dp(0)
```

---

# F. BÀI TẬP NÂNG CAO BỔ SUNG

## F.1 Theo độ khó

### Hard (Interview)
| Bài | Pattern | Gợi ý |
|-----|---------|-------|
| LC 312. Burst Balloons | Interval (Choose-last) | dp[l][r] open interval |
| LC 1000. Merge Stones | Interval + constraint | dp[l][r][k] |
| LC 10. Regex Matching | 2-seq + special char | Xét `.` và `*` |
| LC 188. Stock IV | State Machine | O(nk) với optimization |
| LC 943. Shortest Superstring | Bitmask + TSP-like | dp[mask][last] |

### Competition Level
| Bài | Pattern | Kỹ thuật đặc biệt |
|-----|---------|------------------|
| CF 319C. Kalila and Dimna | CHT | b giảm, a tăng |
| CF 455E. Function | D&C Optimization | opt[i][j] đơn điệu |
| CF 165E. Compatible Numbers | SOS DP | Subset sum |
| USACO Covered Walkway | CHT | Quadratic cost |
| AtCoder DP Contest - All | Various | Định hình tư duy |

## F.2 Roadmap nâng cao (sau 4 tuần cơ bản)

### Tuần 5-6: Interval DP + Optimization
- Matrix Chain, Merge Stones variants
- Knuth Optimization problems
- Burst Balloons và các biến thể

### Tuần 7-8: Tree DP + Rerooting
- House Robber III
- Sum of Distances in Tree
- Tree diameter và centroid

### Tuần 9-10: Bitmask + Profile DP
- Assignment, TSP
- Domino/Tetris tiling
- SOS DP applications

### Tuần 11-12: CHT + D&C + Contest Practice
- CHT basic + Li Chao Tree
- D&C DP problems
- Virtual contests (Codeforces Div2-3)

---

*Phần mở rộng chi tiết cho DP-Master-Guide*
*Cập nhật: 2025-12-30*

# PHẦN MỞ RỘNG: TƯ DUY CHI TIẾT TỪNG BƯỚC
## Bổ sung cho DP-Thinking-Methodology.md

---

# A. QUÁ TRÌNH TƯ DUY CHI TIẾT

## A.1 Phân tích sâu: "Nghĩ như máy tính vs Nghĩ như người"

### Sai lầm phổ biến: Nghĩ quá phức tạp

```
❌ CÁCH NGHĨ SAI (quá phức tạp):
   
   "Tôi cần xem xét tất cả 2^n tổ hợp..."
   "Tôi phải duyệt qua tất cả đường đi..."
   "Bài này chắc cần thuật toán phức tạp..."

✅ CÁCH NGHĨ ĐÚNG (đơn giản hóa):

   "Nếu tôi đứng ở VỊ TRÍ CUỐI CÙNG, 
    tôi cần biết gì để có câu trả lời?"
   
   "Nếu tôi ĐÃ BIẾT đáp án của bài toán nhỏ hơn,
    tôi có thể tìm đáp án bài toán hiện tại không?"
```

### Nguyên tắc "Backward Thinking" (Tư duy ngược)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   FORWARD (❌ Khó):                                         │
│   "Bắt đầu từ 0, làm sao để đến n?"                        │
│                                                             │
│   BACKWARD (✅ Dễ):                                         │
│   "Để ở vị trí n, tôi phải đến từ đâu?"                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

VÍ DỤ CỤ THỂ - Climbing Stairs:

Forward (khó nghĩ):
  - Từ bậc 0, tôi có thể leo 1 hoặc 2...
  - Rồi từ bậc 1, tôi lại có thể...
  - Cây quyết định phình to quá!

Backward (dễ nghĩ):
  - Để lên bậc 10, tôi phải đến từ bậc 9 hoặc bậc 8
  - Vậy: ways(10) = ways(9) + ways(8)
  - Done!
```

---

## A.2 Template Tư Duy 7 Bước (Chi tiết)

### BƯỚC 1: Đọc đề và xác định loại bài

```
┌─────────────────────────────────────────────────────────────┐
│  CÂU HỎI CẦN TRẢ LỜI:                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Bài toán yêu cầu gì?                                   │
│     □ Tìm giá trị tối ưu (max/min)                         │
│     □ Đếm số cách                                          │
│     □ Kiểm tra khả thi (Yes/No)                            │
│     □ Tìm phương án cụ thể                                 │
│                                                             │
│  2. Input là gì?                                           │
│     □ Một mảng/chuỗi                                       │
│     □ Hai mảng/chuỗi                                       │
│     □ Lưới 2D                                              │
│     □ Cây/đồ thị                                           │
│                                                             │
│  3. Có ràng buộc gì?                                       │
│     □ Không được chọn liên tiếp                            │
│     □ Giới hạn số lần chọn                                 │
│     □ Phải tuân theo thứ tự                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### BƯỚC 2: Vẽ ví dụ nhỏ bằng tay

```
QUAN TRỌNG: Luôn vẽ ví dụ trước khi code!

Ví dụ - House Robber với [2, 7, 9, 3, 1]:

Vẽ các phương án:
┌───────────────────────────────────────────────┐
│ Nhà:   [2]  [7]  [9]  [3]  [1]               │
│ Index:  0    1    2    3    4                │
├───────────────────────────────────────────────┤
│ PA1: Chọn 0,2,4 → 2+9+1 = 12                 │
│ PA2: Chọn 0,2   → 2+9   = 11                 │
│ PA3: Chọn 1,3   → 7+3   = 10                 │
│ PA4: Chọn 1,4   → 7+1   = 8                  │
│ PA5: Chọn 0,3   → 2+3   = 5                  │
├───────────────────────────────────────────────┤
│ → Max = 12 (PA1)                              │
└───────────────────────────────────────────────┘

Từ việc vẽ tay, nhận ra:
- Tại mỗi nhà, có 2 lựa chọn: cướp hoặc không
- Nếu cướp nhà i, không được cướp nhà i-1
```

### BƯỚC 3: Hỏi "Làm sao để đến trạng thái cuối?"

```
Câu hỏi ma thuật:
"Nếu tôi đang đứng ở TRẠNG THÁI CUỐI CÙNG,
 tôi có thể đến từ những trạng thái nào?"

House Robber - Phân tích:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Đứng ở nhà thứ i (trạng thái cuối trong bài toán con):    │
│                                                             │
│  CÂU HỎI: Số tiền max đến nhà i là bao nhiêu?              │
│                                                             │
│  TRẢ LỜI: Phụ thuộc vào 2 trường hợp:                      │
│                                                             │
│  ┌─ Nếu CƯỚP nhà i:                                        │
│  │   - Không được cướp nhà i-1                             │
│  │   - Tiền = (tiền đến nhà i-2) + money[i]                │
│  │                                                         │
│  └─ Nếu KHÔNG cướp nhà i:                                  │
│      - Tiền = (tiền đến nhà i-1)                           │
│                                                             │
│  → max(tiền đến i-1, tiền đến i-2 + money[i])              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### BƯỚC 4: Định nghĩa trạng thái rõ ràng

```
TEMPLATE ĐỊNH NGHĨA:

dp[...] = "Câu trả lời cho bài toán con khi ..."

Ví dụ cụ thể:

┌─────────────────────────────────────────────────────────────┐
│ BÀI TOÁN                │ ĐỊNH NGHĨA dp[...]               │
├─────────────────────────┼───────────────────────────────────┤
│ Climbing Stairs         │ dp[i] = số cách leo đến bậc i    │
├─────────────────────────┼───────────────────────────────────┤
│ House Robber            │ dp[i] = tiền max cướp được       │
│                         │         xét đến nhà thứ i        │
├─────────────────────────┼───────────────────────────────────┤
│ Coin Change             │ dp[i] = số xu ít nhất để         │
│                         │         đổi i đồng               │
├─────────────────────────┼───────────────────────────────────┤
│ LIS                     │ dp[i] = độ dài LIS kết thúc      │
│                         │         tại vị trí i             │
├─────────────────────────┼───────────────────────────────────┤
│ Knapsack                │ dp[i][w] = giá trị max với       │
│                         │            i vật đầu, túi w kg   │
├─────────────────────────┼───────────────────────────────────┤
│ LCS                     │ dp[i][j] = độ dài LCS của        │
│                         │            s[0..i-1] và t[0..j-1]│
├─────────────────────────┼───────────────────────────────────┤
│ Edit Distance           │ dp[i][j] = số phép biến đổi      │
│                         │            s[0..i-1] → t[0..j-1] │
└─────────────────────────┴───────────────────────────────────┘
```

### BƯỚC 5: Viết phương trình chuyển

```
PHƯƠNG PHÁP "LIỆT KÊ LỰA CHỌN":

1. Đứng tại trạng thái dp[i]
2. Liệt kê TẤT CẢ lựa chọn có thể
3. Mỗi lựa chọn → một giá trị
4. Kết hợp: max/min/sum tùy bài

VÍ DỤ THỰC HÀNH - Coin Change:

Đứng tại dp[amount] (số xu ít nhất cho amount đồng):

  Lựa chọn 1: Dùng xu 1 đồng → 1 + dp[amount-1]
  Lựa chọn 2: Dùng xu 2 đồng → 1 + dp[amount-2]
  Lựa chọn 3: Dùng xu 5 đồng → 1 + dp[amount-5]
  ...

  Kết hợp: dp[amount] = min(1 + dp[amount-coin]) 
                        với mọi coin <= amount
```

### BƯỚC 6: Xác định Base Cases

```
CÂU HỎI: Trạng thái NHỎ NHẤT mà ta biết chắc giá trị?

┌─────────────────────────────────────────────────────────────┐
│ BÀI TOÁN          │ BASE CASES                              │
├─────────────────────────────────────────────────────────────┤
│ Fibonacci         │ dp[0] = 0, dp[1] = 1                    │
├─────────────────────────────────────────────────────────────┤
│ Climbing Stairs   │ dp[0] = 1, dp[1] = 1                    │
├─────────────────────────────────────────────────────────────┤
│ Coin Change       │ dp[0] = 0 (0 xu cho 0 đồng)             │
│                   │ dp[<0] = ∞ (không thể)                  │
├─────────────────────────────────────────────────────────────┤
│ LIS               │ dp[i] = 1 (mỗi phần tử = LIS độ dài 1)  │
├─────────────────────────────────────────────────────────────┤
│ Knapsack          │ dp[0][w] = 0, dp[i][0] = 0              │
├─────────────────────────────────────────────────────────────┤
│ LCS               │ dp[0][j] = 0, dp[i][0] = 0              │
├─────────────────────────────────────────────────────────────┤
│ Edit Distance     │ dp[i][0] = i, dp[0][j] = j              │
└─────────────────────────────────────────────────────────────┘
```

### BƯỚC 7: Xác định thứ tự tính và kết quả

```
THỨ TỰ TÍNH:
- Bottom-Up: từ base cases lên
- Top-Down: từ bài toán lớn xuống (có memoization)

KẾT QUẢ:
- Thường là dp[n] hoặc dp[n][m]
- Đôi khi là max(dp) hoặc min(dp)

VÍ DỤ - LIS:
  Thứ tự: dp[0] → dp[1] → dp[2] → ... → dp[n-1]
  Kết quả: max(dp[0], dp[1], ..., dp[n-1])
           (vì LIS có thể kết thúc ở bất kỳ đâu)
```

---

# B. CASE STUDIES BỔ SUNG

## B.1 Word Break (Tách từ)

### Đề bài
```
Cho xâu s và từ điển wordDict.
Kiểm tra s có thể tách thành các từ trong từ điển không.

VD: s = "leetcode", wordDict = ["leet", "code"]
→ True (leet + code)
```

### Quá trình tư duy chi tiết

**Phút 1: Đọc đề**
```
- Input: 1 xâu + 1 danh sách từ
- Output: True/False (khả thi)
- Gợi ý: "Có thể hay không" → có thể DP
```

**Phút 2: Vẽ ví dụ**
```
s = "leetcode"
     01234567

wordDict = ["leet", "code"]

Thử tách:
- "l" có trong dict? No
- "le" có trong dict? No
- "lee" có trong dict? No
- "leet" có trong dict? Yes! → tách tại vị trí 4
- Phần còn lại "code" có trong dict? Yes!
- → True
```

**Phút 3: Backward thinking**
```
Câu hỏi: "Để s[0..n-1] có thể tách được,
         tôi cần điều kiện gì?"

Trả lời: Tồn tại vị trí j sao cho:
         1. s[j..n-1] là một từ trong dict
         2. s[0..j-1] có thể tách được

→ Đệ quy về bài toán con!
```

**Phút 4: Định nghĩa trạng thái**
```
dp[i] = True nếu s[0..i-1] có thể tách thành các từ trong dict

VD: s = "leetcode"
    dp[0] = True  (xâu rỗng)
    dp[4] = True  (s[0..3] = "leet" có trong dict)
    dp[8] = True  (s[0..7] = "leetcode" tách được)
```

**Phút 5: Phương trình chuyển**
```
dp[i] = True nếu TỒN TẠI j (0 ≤ j < i) sao cho:
        - dp[j] = True (phần đầu tách được)
        - s[j..i-1] có trong dict (phần sau là 1 từ)

Code:
for j in range(i):
    if dp[j] and s[j:i] in wordDict:
        dp[i] = True
        break
```

**Code hoàn chỉnh**
```python
def wordBreak(s, wordDict):
    n = len(s)
    word_set = set(wordDict)  # O(1) lookup
    dp = [False] * (n + 1)
    dp[0] = True  # Xâu rỗng tách được
    
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    
    return dp[n]

# Test
print(wordBreak("leetcode", ["leet", "code"]))  # True
```

---

## B.2 Target Sum (Tổng mục tiêu)

### Đề bài
```
Cho mảng nums và target.
Gán + hoặc - cho mỗi phần tử.
Đếm số cách để tổng = target.

VD: nums = [1, 1, 1, 1, 1], target = 3
→ 5 cách: -1+1+1+1+1, +1-1+1+1+1, ...
```

### Quá trình tư duy chi tiết

**Phân tích bài toán**
```
Với mỗi phần tử, có 2 lựa chọn: + hoặc -
→ Tổng 2^n cách
→ Brute force: O(2^n) - quá chậm với n lớn
→ Cần DP!
```

**Định nghĩa trạng thái**
```
dp[i][sum] = số cách để tổng của i phần tử đầu = sum

Vấn đề: sum có thể âm!
→ Dịch chuyển: sum_offset = sum + total_sum
→ dp[i][sum + offset] để tránh chỉ số âm
```

**Phương trình chuyển**
```
Tại phần tử thứ i, có 2 lựa chọn:

1. Gán + → tổng mới = sum + nums[i]
   → dp[i][sum] += dp[i-1][sum - nums[i]]

2. Gán - → tổng mới = sum - nums[i]
   → dp[i][sum] += dp[i-1][sum + nums[i]]

Kết hợp:
dp[i][sum] = dp[i-1][sum - nums[i]] + dp[i-1][sum + nums[i]]
```

**Code**
```python
def findTargetSumWays(nums, target):
    n = len(nums)
    total = sum(nums)
    
    # Target ngoài phạm vi
    if abs(target) > total:
        return 0
    
    # dp[sum + offset] = số cách để có tổng = sum
    offset = total
    dp = [0] * (2 * total + 1)
    dp[offset] = 1  # Tổng 0 có 1 cách (chưa chọn gì)
    
    for num in nums:
        new_dp = [0] * (2 * total + 1)
        for s in range(-total, total + 1):
            if dp[s + offset] > 0:
                # Gán +
                new_dp[s + num + offset] += dp[s + offset]
                # Gán -
                new_dp[s - num + offset] += dp[s + offset]
        dp = new_dp
    
    return dp[target + offset]
```

---

## B.3 Unique Paths II (Có chướng ngại vật)

### Đề bài
```
Robot đi từ góc trái-trên đến góc phải-dưới.
Chỉ đi xuống hoặc sang phải.
Có ô chướng ngại vật (1 = chướng ngại).
Đếm số đường đi.
```

### So sánh với Unique Paths I

```
Unique Paths I (không chướng ngại):
   dp[i][j] = dp[i-1][j] + dp[i][j-1]

Unique Paths II (có chướng ngại):
   Nếu grid[i][j] == 1:
       dp[i][j] = 0  (không thể đi qua)
   Ngược lại:
       dp[i][j] = dp[i-1][j] + dp[i][j-1]
```

### Xử lý edge cases

```
1. Ô xuất phát là chướng ngại → return 0
2. Ô đích là chướng ngại → return 0
3. Hàng đầu/cột đầu có chướng ngại 
   → Các ô sau đó trong hàng/cột = 0
```

**Code**
```python
def uniquePathsWithObstacles(grid):
    m, n = len(grid), len(grid[0])
    
    # Edge case: start/end blocked
    if grid[0][0] == 1 or grid[m-1][n-1] == 1:
        return 0
    
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = 1
    
    # Hàng đầu
    for j in range(1, n):
        if grid[0][j] == 0:
            dp[0][j] = dp[0][j-1]
    
    # Cột đầu
    for i in range(1, m):
        if grid[i][0] == 0:
            dp[i][0] = dp[i-1][0]
    
    # Fill bảng
    for i in range(1, m):
        for j in range(1, n):
            if grid[i][j] == 0:
                dp[i][j] = dp[i-1][j] + dp[i][j-1]
    
    return dp[m-1][n-1]
```

---

# C. SAI LẦM THƯỜNG GẶP VÀ CÁCH SỬA

## C.1 Sai định nghĩa trạng thái

### Ví dụ - LIS

```
❌ SAI: dp[i] = "độ dài LIS trong nums[0..i]"
   Vấn đề: Không biết phần tử cuối cùng là gì
           → Không thể quyết định nối tiếp

✅ ĐÚNG: dp[i] = "độ dài LIS KẾT THÚC tại i"
   Ưu điểm: Biết phần tử cuối = nums[i]
           → So sánh được với phần tử mới
```

### Ví dụ - Stock với Cooldown

```
❌ SAI: dp[i] = "max profit đến ngày i"
   Vấn đề: Không biết đang giữ stock hay không
           → Không thế quyết định buy/sell

✅ ĐÚNG: dp[i][0] = "max profit ngày i, KHÔNG giữ stock"
         dp[i][1] = "max profit ngày i, CÓ giữ stock"
   Ưu điểm: Biết trạng thái hiện tại
           → Quyết định được hành động tiếp
```

## C.2 Sai thứ tự duyệt

### Knapsack 0-1 với mảng 1D

```
❌ SAI: Duyệt xuôi
   for w in range(weight, W+1):
       dp[w] = max(dp[w], dp[w-weight] + value)
   
   Vấn đề: dp[w-weight] đã được cập nhật
           → Vật được chọn nhiều lần!

✅ ĐÚNG: Duyệt ngược
   for w in range(W, weight-1, -1):
       dp[w] = max(dp[w], dp[w-weight] + value)
   
   Giải thích: dp[w-weight] chưa cập nhật
              → Vật chỉ chọn 1 lần
```

## C.3 Sai base case

### Coin Change

```
❌ SAI: dp[0] = 1
   Sai vì: 0 đồng cần 0 xu, không phải 1 xu

✅ ĐÚNG: dp[0] = 0
   Đúng vì: Để có 0 đồng, cần 0 xu
```

### Edit Distance

```
❌ SAI: dp[i][0] = 0, dp[0][j] = 0
   Sai vì: Biến "abc" thành "" cần 3 phép delete

✅ ĐÚNG: dp[i][0] = i (delete i ký tự)
         dp[0][j] = j (insert j ký tự)
```

---

# D. BẢNG TỔNG HỢP PATTERNS

## D.1 Bảng tra cứu nhanh

```
┌──────────────────────────────────────────────────────────────┐
│                    DP PATTERN CHEATSHEET                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 LINEAR DP (1 mảng/chuỗi)                                │
│  ─────────────────────────────────────────────────────────  │
│  • Fibonacci-like: dp[i] = f(dp[i-1], dp[i-2])              │
│  • Kadane: dp[i] = max(nums[i], dp[i-1] + nums[i])          │
│  • House Robber: dp[i] = max(dp[i-1], dp[i-2] + nums[i])    │
│                                                              │
│  📊 2-SEQUENCE DP (2 mảng/chuỗi)                            │
│  ─────────────────────────────────────────────────────────  │
│  • LCS: dp[i][j] = dp[i-1][j-1]+1 hoặc max(dp[i-1][j],...)  │
│  • Edit Distance: 3 phép Insert/Delete/Replace              │
│  • Regex Matching: Xét ký tự đặc biệt . và *                │
│                                                              │
│  📊 KNAPSACK (túi/tối ưu với ràng buộc)                     │
│  ─────────────────────────────────────────────────────────  │
│  • 0-1: Mỗi vật 1 lần, duyệt NGƯỢC                         │
│  • Unbounded: Mỗi vật vô hạn, duyệt XUÔI                   │
│  • Partition: Tổng/2, boolean DP                            │
│                                                              │
│  📊 INTERVAL DP (khoảng)                                    │
│  ─────────────────────────────────────────────────────────  │
│  • Duyệt theo LENGTH tăng dần                               │
│  • Thử TẤT CẢ điểm chia trong khoảng                       │
│  • VD: Burst Balloons, Matrix Chain                         │
│                                                              │
│  📊 GRID DP (lưới 2D)                                       │
│  ─────────────────────────────────────────────────────────  │
│  • Unique Paths: Đếm đường đi                              │
│  • Min Path Sum: Tìm đường tốt nhất                        │
│  • Maximal Square: Tìm hình vuông lớn nhất                 │
│                                                              │
│  📊 STATE MACHINE DP (máy trạng thái)                      │
│  ─────────────────────────────────────────────────────────  │
│  • Stock: dp[i][hold/not_hold/cooldown]                    │
│  • Paint House: dp[i][color]                               │
│                                                              │
│  📊 BITMASK DP (tập hợp nhỏ)                               │
│  ─────────────────────────────────────────────────────────  │
│  • TSP: dp[mask][last_city]                                │
│  • Assignment: dp[mask] = min cost                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## D.2 Decision Tree (Cây quyết định chọn pattern)

```
                    ┌─────────────────┐
                    │  ĐỌC ĐỀ BÀI    │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
     ┌──────────┐     ┌──────────┐     ┌──────────┐
     │ 1 mảng/  │     │ 2 mảng/  │     │  Lưới    │
     │  chuỗi   │     │  chuỗi   │     │   2D     │
     └────┬─────┘     └────┬─────┘     └────┬─────┘
          │                │                │
    ┌─────┴─────┐         ▼           ┌─────┴─────┐
    ▼           ▼    2-Sequence DP    ▼           ▼
Linear DP   Knapsack              Path DP    Matrix DP


Linear DP:                    2-Sequence DP:
├─ Fibonacci-like            ├─ LCS (giống nhau)
├─ Kadane (max subarray)     ├─ Edit Distance (biến đổi)
├─ House Robber (ràng buộc)  └─ Regex/Wildcard (matching)
└─ LIS (tăng dần)

Knapsack:                     Grid DP:
├─ 0-1 (mỗi vật 1 lần)       ├─ Unique Paths (đếm)
├─ Unbounded (vô hạn)        ├─ Min/Max Path Sum
├─ Partition (chia 2)        └─ Maximal Square
└─ Coin Change
```

---

# E. LUYỆN TẬP CÓ HỆ THỐNG

## E.1 Lộ trình 4 tuần cho người mới

### Tuần 1: Nền tảng
```
Ngày 1-2: Fibonacci variants
  □ LC 509. Fibonacci Number
  □ LC 70. Climbing Stairs
  □ LC 746. Min Cost Climbing Stairs

Ngày 3-4: Linear DP cơ bản
  □ LC 198. House Robber
  □ LC 213. House Robber II
  □ LC 53. Maximum Subarray

Ngày 5-7: Grid DP
  □ LC 62. Unique Paths
  □ LC 63. Unique Paths II
  □ LC 64. Min Path Sum
```

### Tuần 2: Knapsack & Subsequence
```
Ngày 1-2: 0-1 Knapsack
  □ LC 416. Partition Equal Subset Sum
  □ LC 494. Target Sum

Ngày 3-4: Unbounded Knapsack
  □ LC 322. Coin Change
  □ LC 518. Coin Change 2

Ngày 5-7: LIS & LCS
  □ LC 300. Longest Increasing Subsequence
  □ LC 1143. Longest Common Subsequence
  □ LC 516. Longest Palindromic Subsequence
```

### Tuần 3: String DP
```
Ngày 1-2: Edit Distance
  □ LC 72. Edit Distance
  □ LC 583. Delete Operation for Two Strings

Ngày 3-4: Matching
  □ LC 10. Regular Expression Matching
  □ LC 44. Wildcard Matching

Ngày 5-7: Word Problems
  □ LC 139. Word Break
  □ LC 140. Word Break II
```

### Tuần 4: Advanced
```
Ngày 1-2: Interval DP
  □ LC 312. Burst Balloons
  □ LC 1039. Minimum Score Triangulation

Ngày 3-4: State Machine
  □ LC 121-123. Best Time to Buy/Sell Stock I-III
  □ LC 309. Stock with Cooldown

Ngày 5-7: Matrix & Tree DP
  □ LC 221. Maximal Square
  □ LC 337. House Robber III
```

---

*Tài liệu mở rộng chi tiết về tư duy DP*
*Cập nhật: 30/12/2024*

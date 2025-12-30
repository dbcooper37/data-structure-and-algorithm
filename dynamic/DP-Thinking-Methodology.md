# TƯ DUY GIẢI QUYẾT BÀI TOÁN QUY HOẠCH ĐỘNG
## Từ Cách Nghĩ Đến Cách Làm

> 📚 **Tài liệu bổ sung cho C.md** - Tập trung vào PHƯƠNG PHÁP TƯ DUY
> 
> 🎯 **Mục tiêu**: Hiểu CÁCH suy nghĩ khi gặp bài DP, không chỉ là template code

---

# MỤC LỤC

## PHẦN I: TƯ DUY CĂN BẢN
1. [Nhận diện bài toán DP](#1-nhận-diện-bài-toán-dp)
2. [Mô hình tư duy 4 câu hỏi](#2-mô-hình-tư-duy-4-câu-hỏi)
3. [Từ Đệ quy đến DP](#3-từ-đệ-quy-đến-dp)

## PHẦN II: PHƯƠNG PHÁP TIẾP CẬN
4. [Framework "Choice-State-Result"](#4-framework-choice-state-result)
5. [Kỹ thuật định nghĩa trạng thái](#5-kỹ-thuật-định-nghĩa-trạng-thái)
6. [Tìm phương trình chuyển](#6-tìm-phương-trình-chuyển)

## PHẦN III: CASE STUDIES - PHÂN TÍCH CHI TIẾT
7. [Case Study 1: Coin Change](#7-case-study-1-coin-change)
8. [Case Study 2: Longest Increasing Subsequence](#8-case-study-2-longest-increasing-subsequence)
9. [Case Study 3: 0-1 Knapsack](#9-case-study-3-0-1-knapsack)
10. [Case Study 4: Edit Distance](#10-case-study-4-edit-distance)

## PHẦN IV: TƯ DUY NÂNG CAO
11. [Nhận diện Pattern](#11-nhận-diện-pattern)
12. [Debug và Verify](#12-debug-và-verify)
13. [Tối ưu hóa tư duy](#13-tối-ưu-hóa-tư-duy)
14. [Cheat Sheet Nâng Cao](#14-cheat-sheet-nâng-cao)

---

# PHẦN I: TƯ DUY CĂN BẢN

## 1. Nhận diện bài toán DP

### 1.1 Dấu hiệu nhận biết

Khi đọc đề bài, hãy tìm các **từ khóa** sau:

```
┌─────────────────────────────────────────────────────────────┐
│  TỪ KHÓA GỢI Ý DP                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔹 TỐI ƯU HÓA:                                            │
│     "Tìm số lượng TỐI THIỂU..."                            │
│     "Tìm giá trị LỚN NHẤT..."                              │
│     "Tìm đường đi NGẮN NHẤT..."                            │
│                                                             │
│  🔹 ĐẾM SỐ CÁCH:                                           │
│     "Có BAO NHIÊU cách..."                                 │
│     "Đếm SỐ LƯỢNG phương án..."                            │
│     "Liệt kê TẤT CẢ các cách..."                           │
│                                                             │
│  🔹 KHẢ THI:                                               │
│     "Có THỂ hay không..."                                  │
│     "Kiểm tra KHẢ NĂNG..."                                 │
│                                                             │
│  🔹 CẤU TRÚC CON:                                          │
│     "Dãy con..."                                           │
│     "Tập con..."                                           │
│     "Đường đi qua các bước..."                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Kiểm tra 3 tính chất

Sau khi nghi ngờ bài toán có thể dùng DP, **kiểm tra 3 tính chất**:

```
┌───────────────────────────────────────────────────────────────┐
│  CHECKLIST 3 TÍNH CHẤT DP                                     │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ☐ 1. CẤU TRÚC CON TỐI ƯU (Optimal Substructure)             │
│     → Lời giải tối ưu của bài toán lớn có dùng               │
│       lời giải tối ưu của bài toán con không?                │
│                                                               │
│     Câu hỏi: "Nếu tôi biết lời giải tối ưu của bài toán      │
│              nhỏ hơn, tôi có thể xây dựng lời giải           │
│              cho bài toán lớn không?"                        │
│                                                               │
│  ☐ 2. BÀI TOÁN CON CHỒNG CHÉO (Overlapping Subproblems)      │
│     → Cùng một bài toán con có được tính nhiều lần không?    │
│                                                               │
│     Câu hỏi: "Nếu tôi vẽ cây đệ quy, có nhánh nào             │
│              được tính lại nhiều lần không?"                 │
│                                                               │
│  ☐ 3. KHÔNG HẬU HIỆU (No After-effect)                       │
│     → Khi đã xác định trạng thái, các quyết định sau         │
│       có ảnh hưởng giá trị của trạng thái đó không?          │
│                                                               │
│     Câu hỏi: "Giá trị dp[i] có thay đổi khi tôi              │
│              tính dp[i+1], dp[i+2],... không?"               │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 1.3 Phân biệt DP với các kỹ thuật khác

| Kỹ thuật | Khi nào dùng | Ví dụ |
|----------|--------------|-------|
| **Greedy** | Lựa chọn local optimal = global optimal | Activity Selection, Huffman |
| **DP** | Cần xét TẤT CẢ các trường hợp | Knapsack, LCS |
| **Chia để trị** | Bài toán con KHÔNG chồng chéo | Merge Sort, Quick Sort |
| **Backtracking** | Cần liệt kê TẤT CẢ lời giải | N-Queens, Sudoku |

**Rule of thumb**:
- Greedy không cần nhìn lại quá khứ
- DP cần nhớ quá khứ để quyết định hiện tại
- Chia để trị các bài toán con độc lập

---

## 2. Mô hình tư duy 4 câu hỏi

Khi gặp bài DP, trả lời **4 câu hỏi** theo thứ tự:

### Câu hỏi 1: "Trạng thái cuối cùng là gì?"

```
🎯 Mục tiêu: Xác định ĐIỂM ĐẾN của bài toán

Ví dụ - Climbing Stairs (n bậc):
   → Trạng thái cuối: "Đứng ở bậc n"

Ví dụ - 0-1 Knapsack (n vật, W kg):
   → Trạng thái cuối: "Đã xét n vật, túi chứa tối đa W kg"

Ví dụ - LCS (s, t):
   → Trạng thái cuối: "Đã xét toàn bộ s và t"
```

### Câu hỏi 2: "Trước trạng thái cuối, tôi có thể đứng ở đâu?"

```
🔙 Mục tiêu: Tìm các TRẠNG THÁI TRƯỚC đó

Ví dụ - Climbing Stairs:
   Để lên bậc n, trước đó tôi có thể đứng ở:
   ├─ Bậc (n-1) → leo 1 bậc
   └─ Bậc (n-2) → leo 2 bậc

Ví dụ - 0-1 Knapsack:
   Để có trạng thái (n vật, w kg), trước đó:
   ├─ (n-1 vật, w kg) → KHÔNG chọn vật n
   └─ (n-1 vật, w-weight[n] kg) → CÓ chọn vật n

Ví dụ - LCS:
   Để có dp[i][j], trước đó:
   ├─ dp[i-1][j] → bỏ qua s[i]
   ├─ dp[i][j-1] → bỏ qua t[j]
   └─ dp[i-1][j-1] → nếu s[i] == t[j], ghép đôi
```

### Câu hỏi 3: "Khi chuyển từ trạng thái trước đến trạng thái sau, chi phí/giá trị thay đổi thế nào?"

```
⚡ Mục tiêu: Xác định CÔNG THỨC CHUYỂN

Ví dụ - Climbing Stairs:
   dp[n] = dp[n-1] + dp[n-2]  (cộng số cách)

Ví dụ - 0-1 Knapsack:
   dp[i][w] = max(
       dp[i-1][w],                        # không chọn
       dp[i-1][w-weight[i]] + value[i]    # có chọn
   )

Ví dụ - Min Path Sum:
   dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]
```

### Câu hỏi 4: "Trạng thái ban đầu (base case) là gì?"

```
🏁 Mục tiêu: Xác định ĐIỂM XUẤT PHÁT

Ví dụ - Climbing Stairs:
   dp[0] = 1  (đứng yên = 1 cách)
   dp[1] = 1  (leo 1 bậc = 1 cách)

Ví dụ - 0-1 Knapsack:
   dp[0][w] = 0  (0 vật → giá trị 0)
   dp[i][0] = 0  (túi 0 kg → giá trị 0)

Ví dụ - LCS:
   dp[0][j] = 0  (xâu rỗng → LCS = 0)
   dp[i][0] = 0
```

---

## 3. Từ Đệ quy đến DP

### 3.1 Quy trình chuyển đổi

```
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 1: Viết giải pháp ĐỆ QUY THUẦN                       │
│          (Brute force, không quan tâm hiệu suất)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 2: Nhận diện THAM SỐ thay đổi trong đệ quy           │
│          (Đây chính là các chiều của trạng thái DP)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 3: Thêm MEMOIZATION (cache kết quả)                  │
│          → Top-Down DP                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 4: Chuyển sang TABULATION (vòng lặp)                 │
│          → Bottom-Up DP                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 5: TỐI ƯU KHÔNG GIAN (nếu cần)                       │
│          → Rolling array hoặc biến đơn                      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Ví dụ minh họa: Fibonacci

**BƯỚC 1: Đệ quy thuần**
```python
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

# Vấn đề: O(2^n) - tính lại nhiều lần
```

**BƯỚC 2: Nhận diện tham số**
```python
# Tham số thay đổi: n
# → Trạng thái DP chỉ cần 1 chiều: dp[n]
```

**BƯỚC 3: Top-Down (Memoization)**
```python
def fib_memo(n, memo={}):
    if n <= 1:
        return n
    if n in memo:
        return memo[n]
    
    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]

# O(n) thời gian, O(n) không gian
```

**BƯỚC 4: Bottom-Up (Tabulation)**
```python
def fib_dp(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

# O(n) thời gian, O(n) không gian
```

**BƯỚC 5: Tối ưu không gian**
```python
def fib_optimized(n):
    if n <= 1:
        return n
    
    prev2, prev1 = 0, 1
    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2, prev1 = prev1, current
    
    return prev1

# O(n) thời gian, O(1) không gian
```

---

# PHẦN II: PHƯƠNG PHÁP TIẾP CẬN

## 4. Framework "Choice-State-Result"

### 4.1 Mô hình CSR

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  DP = Tại mỗi TRẠNG THÁI, ta có các LỰA CHỌN,               │
│       mỗi lựa chọn dẫn đến một KẾT QUẢ.                     │
│                                                              │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                │
│  │ STATE   │ ──> │ CHOICE  │ ──> │ RESULT  │                │
│  │ (Trạng  │     │ (Lựa    │     │ (Kết    │                │
│  │  thái)  │     │  chọn)  │     │  quả)   │                │
│  └─────────┘     └─────────┘     └─────────┘                │
│                                                              │
│  dp[state] = optimize(                                       │
│      choice1: dp[prev_state1] + cost1,                       │
│      choice2: dp[prev_state2] + cost2,                       │
│      ...                                                     │
│  )                                                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Áp dụng CSR vào bài toán

**Ví dụ - House Robber**

```
Bài toán: Dãy nhà, không được cướp 2 nhà liền kề, max tiền?

┌─────────────────────────────────────────────────────────────┐
│  STATE: Đang đứng trước nhà thứ i                           │
│                                                             │
│  CHOICES:                                                   │
│    1. CƯỚP nhà i  → Không được cướp nhà i-1                │
│       → Kết quả: dp[i-2] + money[i]                        │
│                                                             │
│    2. BỎ QUA nhà i → Giữ nguyên số tiền đã có              │
│       → Kết quả: dp[i-1]                                   │
│                                                             │
│  RESULT: dp[i] = max(dp[i-1], dp[i-2] + money[i])          │
└─────────────────────────────────────────────────────────────┘
```

**Ví dụ - Coin Change**

```
Bài toán: Đổi số tiền amount với ít xu nhất

┌─────────────────────────────────────────────────────────────┐
│  STATE: Cần đổi số tiền = amount                            │
│                                                             │
│  CHOICES: Với mỗi loại xu coin[i]                          │
│    - Dùng xu coin[i] → Còn lại (amount - coin[i])          │
│    - Kết quả: 1 + dp[amount - coin[i]]                     │
│                                                             │
│  RESULT: dp[amount] = min(1 + dp[amount - coin[i]])        │
│          với mọi coin[i] <= amount                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Kỹ thuật định nghĩa trạng thái

### 5.1 Nguyên tắc "Đủ thông tin, Không thừa"

```
┌─────────────────────────────────────────────────────────────┐
│  TRẠNG THÁI TỐT                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ ĐỦ THÔNG TIN:                                          │
│     Từ trạng thái, có thể đưa ra quyết định                │
│     mà KHÔNG cần biết thêm gì                              │
│                                                             │
│  ✅ KHÔNG THỪA:                                             │
│     Không có thông tin dư thừa                             │
│     (giảm số chiều của dp)                                 │
│                                                             │
│  ✅ KHÔNG HẬU HIỆU:                                        │
│     Giá trị không thay đổi khi tính các trạng thái sau     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Các mẫu định nghĩa trạng thái phổ biến

**Mẫu 1: Trạng thái vị trí/chỉ số**
```python
dp[i]      # Kết quả khi xét đến vị trí i
dp[i][j]   # Kết quả khi xét đến (i, j) trong lưới

# Ví dụ: LIS, House Robber, Unique Paths
```

**Mẫu 2: Trạng thái "kết thúc tại"**
```python
dp[i] = "kết quả tốt nhất của dãy KẾT THÚC tại vị trí i"

# Ví dụ: Maximum Subarray (Kadane)
# dp[i] = max sum ending at i
# Kết quả = max(dp[0], dp[1], ..., dp[n-1])
```

**Mẫu 3: Trạng thái "đến vị trí"**
```python
dp[i] = "kết quả tốt nhất khi ĐẾN ĐƯỢC vị trí i"

# Ví dụ: Climbing Stairs
# dp[i] = số cách leo đến bậc i
```

**Mẫu 4: Trạng thái "dùng k phần tử đầu"**
```python
dp[i] = "kết quả khi xét i phần tử đầu tiên"

# Ví dụ: 0-1 Knapsack
# dp[i][w] = giá trị max với i vật đầu, túi w kg
```

**Mẫu 5: Trạng thái khoảng**
```python
dp[l][r] = "kết quả cho khoảng [l, r]"

# Ví dụ: Burst Balloons, Palindrome Partitioning
```

**Mẫu 6: Trạng thái + điều kiện phụ**
```python
dp[i][0/1] = "kết quả tại i với điều kiện 0 hoặc 1"

# Ví dụ: Best Time to Buy/Sell Stock
# dp[i][0] = max profit ngày i, KHÔNG giữ cổ phiếu
# dp[i][1] = max profit ngày i, CÓ giữ cổ phiếu
```

### 5.3 Khi trạng thái không đủ thông tin

```
❌ Vấn đề: Quyết định phụ thuộc vào thứ đã làm trước đó

✅ Giải pháp: MỞ RỘNG trạng thái

Ví dụ - Best Time to Buy/Sell Stock with Cooldown:
- Trước: dp[i] không đủ (không biết đang giữ hay không)
- Sau:  dp[i][state] với state = {hold, sold, rest}
```

---

## 6. Tìm phương trình chuyển

### 6.1 Phương pháp "Liệt kê lựa chọn"

```
┌─────────────────────────────────────────────────────────────┐
│  BƯỚC 1: Đứng tại trạng thái hiện tại                       │
│                                                             │
│  BƯỚC 2: Liệt kê TẤT CẢ lựa chọn có thể thực hiện          │
│                                                             │
│  BƯỚC 3: Với mỗi lựa chọn, xác định:                       │
│          - Trạng thái TRƯỚC đó                             │
│          - Chi phí/giá trị thay đổi                        │
│                                                             │
│  BƯỚC 4: Kết hợp các lựa chọn (max/min/sum/...)           │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Ví dụ chi tiết: Edit Distance

```
Bài toán: Biến xâu s thành t với ít phép biến đổi nhất
Các phép: Insert, Delete, Replace

Trạng thái: dp[i][j] = số phép biến đổi từ s[0..i-1] thành t[0..j-1]

┌─────────────────────────────────────────────────────────────┐
│  Đứng tại dp[i][j], tôi cần xét:                           │
│                                                             │
│  CÂU HỎI: s[i-1] có bằng t[j-1] không?                     │
│                                                             │
│  TRƯỜNG HỢP 1: s[i-1] == t[j-1]                            │
│    → Không cần làm gì, chỉ cần biến s[0..i-2] → t[0..j-2]  │
│    → dp[i][j] = dp[i-1][j-1]                               │
│                                                             │
│  TRƯỜNG HỢP 2: s[i-1] != t[j-1]                            │
│    → Phải thực hiện 1 trong 3 phép:                        │
│                                                             │
│    🔹 INSERT: Thêm t[j-1] vào cuối s                        │
│       s[0..i-1] → s[0..i-1] + t[j-1]                       │
│       Giờ cần biến s[0..i-1] thành t[0..j-2]               │
│       → 1 + dp[i][j-1]                                     │
│                                                             │
│    🔹 DELETE: Xóa s[i-1]                                    │
│       s[0..i-1] → s[0..i-2]                                │
│       Giờ cần biến s[0..i-2] thành t[0..j-1]               │
│       → 1 + dp[i-1][j]                                     │
│                                                             │
│    🔹 REPLACE: Thay s[i-1] bằng t[j-1]                      │
│       s[0..i-1] → s[0..i-2] + t[j-1]                       │
│       Giờ cần biến s[0..i-2] thành t[0..j-2]               │
│       → 1 + dp[i-1][j-1]                                   │
│                                                             │
│  KẾT QUẢ: dp[i][j] = 1 + min(dp[i][j-1],                   │
│                              dp[i-1][j],                    │
│                              dp[i-1][j-1])                  │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Các dạng phương trình chuyển phổ biến

**Dạng 1: MAX/MIN của các lựa chọn**
```python
dp[i] = max/min(choice1, choice2, ...)

# Ví dụ: dp[i] = max(dp[i-1], dp[i-2] + nums[i])
```

**Dạng 2: TỔNG của các lựa chọn**
```python
dp[i] = sum(choice1, choice2, ...)

# Ví dụ: dp[i] = dp[i-1] + dp[i-2]  (đếm số cách)
```

**Dạng 3: Điều kiện rẽ nhánh**
```python
if condition:
    dp[i][j] = case_1
else:
    dp[i][j] = case_2

# Ví dụ: LCS - nếu s[i] == t[j] thì..., ngược lại...
```

**Dạng 4: Duyệt qua tất cả khả năng trước đó**
```python
for k in range(i):
    dp[i] = optimize(dp[i], dp[k] + f(k, i))

# Ví dụ: LIS - dp[i] = max(dp[j] + 1) với mọi j < i và nums[j] < nums[i]
```

---

# PHẦN III: CASE STUDIES - PHÂN TÍCH CHI TIẾT

## 7. Case Study 1: Coin Change

### Đề bài
```
Cho mảng coins và số tiền amount.
Tìm số xu ÍT NHẤT để đổi ra amount.
Nếu không đổi được, trả về -1.

Ví dụ: coins = [1, 2, 5], amount = 11
Kết quả: 3 (5 + 5 + 1)
```

### Quá trình tư duy

**Bước 1: Nhận diện bài DP**
```
✅ "Số xu ÍT NHẤT" → Tối ưu hóa → Có thể DP
✅ Lựa chọn tại mỗi bước: Dùng xu nào?
✅ Bài toán con chồng chéo: amount = 11 cần tính amount = 6, 9, 10
   và các giá trị này lặp lại nhiều lần
```

**Bước 2: Trả lời 4 câu hỏi**
```
Q1: Trạng thái cuối cùng?
    → Đổi được số tiền = amount

Q2: Trước đó có thể đứng ở đâu?
    → Nếu dùng xu coins[i], trước đó tôi có (amount - coins[i])

Q3: Chi phí chuyển?
    → Mỗi lần dùng 1 xu, số xu tăng thêm 1

Q4: Base case?
    → amount = 0 → cần 0 xu
    → amount < 0 → không thể (vô cực)
```

**Bước 3: Viết đệ quy thuần**
```python
def coinChange_recursive(coins, amount):
    if amount == 0:
        return 0
    if amount < 0:
        return float('inf')
    
    min_coins = float('inf')
    for coin in coins:
        result = coinChange_recursive(coins, amount - coin)
        min_coins = min(min_coins, 1 + result)
    
    return min_coins
```

**Bước 4: Thêm Memoization**
```python
def coinChange_memo(coins, amount, memo={}):
    if amount == 0:
        return 0
    if amount < 0:
        return float('inf')
    if amount in memo:
        return memo[amount]
    
    min_coins = float('inf')
    for coin in coins:
        result = coinChange_memo(coins, amount - coin, memo)
        min_coins = min(min_coins, 1 + result)
    
    memo[amount] = min_coins
    return min_coins
```

**Bước 5: Chuyển Bottom-Up**
```python
def coinChange(coins, amount):
    # dp[i] = số xu ít nhất để đổi i đồng
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # Base case
    
    for i in range(1, amount + 1):
        for coin in coins:
            if i >= coin and dp[i - coin] != float('inf'):
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1
```

### Minh họa bảng DP
```
coins = [1, 2, 5], amount = 11

i:     0  1  2  3  4  5  6  7  8  9  10 11
dp[i]: 0  1  1  2  2  1  2  2  3  3  2  3

Giải thích:
- dp[1] = dp[0] + 1 = 1 (dùng xu 1)
- dp[2] = dp[0] + 1 = 1 (dùng xu 2)
- dp[5] = dp[0] + 1 = 1 (dùng xu 5)
- dp[11] = dp[6] + 1 = 3 (5 + 5 + 1)
```

---

## 8. Case Study 2: Longest Increasing Subsequence

### Đề bài
```
Cho mảng nums, tìm độ dài dãy con TĂNG DẦN dài nhất.
(Dãy con không cần liên tiếp)

Ví dụ: nums = [10, 9, 2, 5, 3, 7, 101, 18]
Kết quả: 4 ([2, 3, 7, 101] hoặc [2, 3, 7, 18])
```

### Quá trình tư duy

**Bước 1: Thử nghĩ Greedy?**
```
❌ Greedy không hoạt động:
   [3, 4, 2, 5]
   Greedy: [3, 4, 5] = 3
   Optimal: [3, 4, 5] = 3 (trùng nhưng may mắn)
   
   [1, 3, 2, 4]
   Nếu chọn 3 sớm, bỏ lỡ [1, 2, 4]
   → Cần xét TẤT CẢ trường hợp → DP
```

**Bước 2: Định nghĩa trạng thái**
```
🤔 Thử dp[i] = "độ dài LIS của nums[0..i]"?
   → Không work! Vì không biết phần tử cuối là gì
   → Không thể quyết định có nối tiếp được không

✅ dp[i] = "độ dài LIS KẾT THÚC tại nums[i]"
   → Biết phần tử cuối là nums[i]
   → Có thể so sánh để nối tiếp
```

**Bước 3: Tìm phương trình chuyển**
```
Để tính dp[i], xét TẤT CẢ j < i:
- Nếu nums[j] < nums[i], có thể nối nums[i] vào sau LIS kết thúc tại j
- dp[i] = max(dp[j] + 1) với mọi j thỏa mãn

Base case: dp[i] = 1 (mỗi phần tử tự là LIS độ dài 1)
```

**Bước 4: Code**
```python
def lengthOfLIS(nums):
    n = len(nums)
    dp = [1] * n  # Base: mỗi phần tử tự là LIS độ dài 1
    
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    
    return max(dp)  # LIS có thể kết thúc ở bất kỳ vị trí nào
```

### Minh họa
```
nums = [10, 9, 2, 5, 3, 7, 101, 18]
index:  0   1  2  3  4  5   6    7

dp[0] = 1                    (10)
dp[1] = 1                    (9)
dp[2] = 1                    (2)
dp[3] = dp[2] + 1 = 2        (2, 5)
dp[4] = dp[2] + 1 = 2        (2, 3)
dp[5] = dp[4] + 1 = 3        (2, 3, 7)
dp[6] = dp[5] + 1 = 4        (2, 3, 7, 101)
dp[7] = dp[5] + 1 = 4        (2, 3, 7, 18)

Kết quả: max(dp) = 4
```

---

## 9. Case Study 3: 0-1 Knapsack

### Đề bài
```
N vật, mỗi vật có weight[i] và value[i].
Túi chứa tối đa W kg.
Mỗi vật chỉ chọn 0 hoặc 1 lần.
Tìm giá trị LỚN NHẤT có thể mang.
```

### Quá trình tư duy

**Bước 1: Tại sao không Greedy?**
```
Greedy "lấy hàng giá trị/kg cao nhất":
   weights = [1, 3], values = [6, 7], W = 3
   
   Greedy: value/weight = [6, 2.33]
           → Chọn vật 1: w=1, v=6
           → Còn 2kg, không chọn được vật 2
           → Tổng: 6
   
   Optimal: Chọn vật 2: w=3, v=7
            → Tổng: 7

❌ Greedy thất bại → Cần DP
```

**Bước 2: Xác định trạng thái**
```
Cần biết:
1. Đã xét đến vật nào? → i
2. Túi còn bao nhiêu kg? → w

→ dp[i][w] = "giá trị max khi xét i vật đầu với túi w kg"
```

**Bước 3: CSR Framework**
```
STATE: (i vật đầu, túi w kg)

CHOICES tại vật thứ i:
  1. KHÔNG CHỌN vật i:
     → Giữ nguyên: dp[i-1][w]
  
  2. CHỌN vật i (nếu w >= weight[i]):
     → Thêm value[i]: dp[i-1][w - weight[i]] + value[i]

RESULT: dp[i][w] = max(choice1, choice2)
```

**Bước 4: Code 2D**
```python
def knapsack01(weights, values, W):
    n = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(W + 1):
            # Không chọn vật i
            dp[i][w] = dp[i-1][w]
            
            # Chọn vật i
            if w >= weights[i-1]:
                dp[i][w] = max(
                    dp[i][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]
                )
    
    return dp[n][W]
```

**Bước 5: Tối ưu 1D**
```python
def knapsack01_optimized(weights, values, W):
    dp = [0] * (W + 1)
    
    for i in range(len(weights)):
        # DUYỆT NGƯỢC để tránh chọn cùng vật 2 lần
        for w in range(W, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[W]
```

### Tại sao duyệt ngược?
```
weights = [2], values = [3], W = 4

Duyệt XUÔI (SAI):
  w=2: dp[2] = max(dp[2], dp[0] + 3) = 3
  w=4: dp[4] = max(dp[4], dp[2] + 3) = 6  ← SAI! Dùng vật 2 lần

Duyệt NGƯỢC (ĐÚNG):
  w=4: dp[4] = max(dp[4], dp[2] + 3) = 3  ← dp[2] chưa cập nhật
  w=2: dp[2] = max(dp[2], dp[0] + 3) = 3
```

---

## 10. Case Study 4: Edit Distance

### Đề bài
```
Biến xâu word1 thành word2 với số phép biến đổi ít nhất.
Cho phép: Insert, Delete, Replace

Ví dụ: "horse" → "ros" = 3 phép
```

### Quá trình tư duy chi tiết

**Bước 1: Vẽ ví dụ cụ thể**
```
word1 = "horse"
word2 = "ros"

Có thể làm:
1. horse → rorse (replace 'h' với 'r')
2. rorse → rose  (delete 'r')
3. rose  → ros   (delete 'e')

Tổng: 3 phép
```

**Bước 2: Nhận diện cấu trúc con**
```
🤔 Suy nghĩ:
   Để biến "horse" → "ros"
   
   Phần cuối: e != s
   → Phải làm gì đó với 'e' hoặc 's'
   
   Nếu Replace 'e' → 's':
   → Còn lại: biến "hors" → "ro"
   
   Nếu Delete 'e':
   → Còn lại: biến "hors" → "ros"
   
   Nếu Insert 's' vào cuối:
   → "horse" + "s" = "horses"
   → Còn lại: biến "horse" → "ro"

💡 Nhận xét: Các bài toán con nhỏ hơn → DP!
```

**Bước 3: Định nghĩa chính xác**
```
dp[i][j] = số phép biến đổi tối thiểu từ word1[0..i-1] → word2[0..j-1]

Tức là:
- dp[0][0] = 0 (không cần biến đổi gì)
- dp[i][0] = i (xóa hết i ký tự)
- dp[0][j] = j (thêm j ký tự)
```

**Bước 4: Phương trình chuyển (từng trường hợp)**
```
Xét word1[i-1] và word2[j-1]:

CASE 1: word1[i-1] == word2[j-1]
   → Không cần làm gì với ký tự cuối
   → dp[i][j] = dp[i-1][j-1]

CASE 2: word1[i-1] != word2[j-1]
   → Phải thực hiện 1 trong 3 phép:
   
   a) INSERT word2[j-1] vào cuối word1:
      word1 + word2[j-1] → khớp với word2[j-1]
      Còn lại: biến word1[0..i-1] → word2[0..j-2]
      → 1 + dp[i][j-1]
   
   b) DELETE word1[i-1]:
      word1[0..i-2] → word1 ngắn hơn 1
      Còn lại: biến word1[0..i-2] → word2[0..j-1]
      → 1 + dp[i-1][j]
   
   c) REPLACE word1[i-1] bằng word2[j-1]:
      word1[0..i-2] + word2[j-1] → khớp với word2[j-1]
      Còn lại: biến word1[0..i-2] → word2[0..j-2]
      → 1 + dp[i-1][j-1]

   → dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])
```

**Bước 5: Code**
```python
def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i][j-1],      # Insert
                    dp[i-1][j],      # Delete
                    dp[i-1][j-1]     # Replace
                )
    
    return dp[m][n]
```

### Minh họa bảng DP
```
      ""  r  o  s
  ""   0  1  2  3
  h    1  1  2  3
  o    2  2  1  2
  r    3  2  2  2
  s    4  3  3  2
  e    5  4  4  3

Kết quả: dp[5][3] = 3
```

---

# PHẦN IV: TƯ DUY NÂNG CAO

## 11. Nhận diện Pattern

### 11.1 Pattern nhận dạng nhanh

| Dấu hiệu đề bài | Pattern DP |
|-----------------|------------|
| "Đếm số cách..." | Addition DP: `dp[i] = dp[i-1] + dp[i-2] + ...` |
| "Min/Max..." | Optimization: `dp[i] = max/min(...)` |
| "Có thể hay không" | Boolean DP: `dp[i] = dp[j] or dp[k]` |
| "2 chuỗi/mảng" | 2D DP: `dp[i][j]` |
| "Tập hợp nhỏ (n≤20)" | Bitmask DP: `dp[mask]` |
| "Khoảng [l, r]" | Interval DP: `dp[l][r]` |
| "Cây" | Tree DP: `dp[node]` |

### 11.2 Quick mapping

```
┌─────────────────────────────────────────────────────────────┐
│  BÀI TOÁN                  →  PATTERN                      │
├─────────────────────────────────────────────────────────────┤
│  Climbing Stairs           →  Linear (Fibonacci-like)      │
│  House Robber              →  Linear + Constraint          │
│  Coin Change               →  Unbounded Knapsack           │
│  0-1 Knapsack              →  0-1 Knapsack                 │
│  Partition Equal Subset    →  0-1 Knapsack (boolean)       │
│  LIS                       →  LIS Pattern                   │
│  LCS                       →  Double Sequence              │
│  Edit Distance             →  Double Sequence              │
│  Burst Balloons            →  Interval DP                  │
│  Stock Buy/Sell            →  State Machine DP             │
│  TSP                       →  Bitmask DP                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 12. Debug và Verify

### 12.1 Khi code sai

```
┌─────────────────────────────────────────────────────────────┐
│  CHECKLIST DEBUG DP                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ☐ 1. In ra bảng DP với test case nhỏ                      │
│       → Kiểm tra từng giá trị có hợp lý không              │
│                                                             │
│  ☐ 2. Kiểm tra BASE CASES                                  │
│       → Đây là nguồn lỗi phổ biến nhất!                    │
│       → dp[0] = ? dp[1] = ? dp[-1] = ?                     │
│                                                             │
│  ☐ 3. Kiểm tra ĐIỀU KIỆN BIÊN                              │
│       → i = 0, i = n-1                                     │
│       → w = 0, w = W                                       │
│                                                             │
│  ☐ 4. Kiểm tra THỨ TỰ DUYỆT                                │
│       → Xuôi hay ngược?                                    │
│       → 0-1 Knapsack: phải duyệt ngược!                    │
│                                                             │
│  ☐ 5. Kiểm tra INDEX                                       │
│       → 0-indexed hay 1-indexed?                           │
│       → dp[i] ứng với item nào?                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 12.2 Verify lời giải

```python
# Luôn test với:
# 1. Edge cases: n=0, n=1, empty input
# 2. Small cases: tính tay được
# 3. Known examples: từ đề bài

def verify_dp(dp_solution, brute_force, test_cases):
    for tc in test_cases:
        expected = brute_force(tc)
        actual = dp_solution(tc)
        assert expected == actual, f"Failed: {tc}"
    print("All tests passed!")
```

---

## 13. Tối ưu hóa tư duy

### 13.1 Tư duy từ kết quả

```
❌ Tư duy từ đầu:
   "Bắt đầu từ 0, làm sao để đến n?"
   → Khó vì không biết đường đi

✅ Tư duy từ cuối:
   "Để có kết quả tại n, trước đó tôi phải ở đâu?"
   → Đây chính là tư duy DP!

Ví dụ - Climbing Stairs:
   ❌ "Từ bậc 0, leo lên như thế nào?"
   ✅ "Để lên bậc n, trước đó tôi đứng ở bậc nào?"
      → Bậc n-1 (leo 1) hoặc bậc n-2 (leo 2)
```

### 13.2 Chuyển đổi góc nhìn

```
Cùng một bài toán, có thể định nghĩa DP khác nhau:

LIS - Góc nhìn 1:
   dp[i] = "LIS kết thúc tại i"
   → O(n²)

LIS - Góc nhìn 2:
   tails[i] = "số nhỏ nhất kết thúc LIS độ dài i+1"
   → O(n log n) với binary search

💡 Tip: Nếu O(n²) không đủ nhanh, thử định nghĩa lại trạng thái!
```

### 13.3 Từ 2D xuống 1D

```
Quan sát: dp[i][...] chỉ phụ thuộc vào dp[i-1][...]

→ Có thể bỏ chiều i, chỉ giữ 2 hàng:
   dp_old[] và dp_new[]
   hoặc chỉ 1 hàng dp[] (cẩn thận thứ tự duyệt)

Ví dụ - Knapsack:
   2D: dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight] + value)
   1D: dp[w] = max(dp[w], dp[w-weight] + value)  [duyệt ngược]
```

---

## 14. Cheat Sheet Nâng Cao

Phần này là “bảng tra nhanh” khi gặp bài DP nâng cao: **nhận dạng → state → loop order → template → điều kiện tối ưu**.

### 14.1 Interval DP (DP Khoảng) – 2 archetype hay gặp

**A) Split / Merge (chia điểm k)**

Thường gặp khi “tối ưu/đếm trên đoạn [l,r]” và có bước **chia đoạn**:

```
dp[l][r] = min/max over k:
    dp[l][k] + dp[k+1][r] + cost(l,r)
```

**Loop order chuẩn**: theo độ dài đoạn.

```python
for length in range(2, n + 1):
    for l in range(0, n - length + 1):
        r = l + length - 1
        dp[l][r] = INF
        for k in range(l, r):
            dp[l][r] = min(dp[l][r], dp[l][k] + dp[k+1][r] + cost(l, r))
```

**B) Choose “last” (chọn phần tử cuối cùng được xử lý)**

Ví dụ kiểu Burst Balloons: chọn “phần tử cuối cùng” trong đoạn để đảm bảo 2 bên độc lập:

```
dp[l][r] = max over k in [l..r]:
    dp[l][k-1] + gain(l,k,r) + dp[k+1][r]
```

**Mẹo tư duy**: nếu “làm từ trái qua phải” bị phụ thuộc chéo, thử “chọn cái làm cuối” để tách phụ thuộc.

---

### 14.2 Digit DP (DP Chữ số) – template chuẩn

Digit DP thường dùng để tính **f(x)** (đếm/sum thỏa điều kiện với số trong [0..x]).
Sau đó bài [L..R] làm: `answer = f(R) - f(L-1)`.

**Trạng thái hay dùng**:
- `pos`: đang xét đến chữ số thứ pos (0..len-1)
- `state`: “thông tin ràng buộc” (vd: tổng chữ số mod k, mask chữ số đã dùng, số lần xuất hiện...)
- `tight` (isLimit): prefix hiện tại có đang bị giới hạn bởi x không
- `started` (isNum): đã bắt đầu đặt chữ số khác 0 chưa (để xử lý leading zeros)

**Template (Python, memo với (pos,state,started) khi tight=False)**:

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
            next_started = started or (d != 0)
            next_state = state

            if next_started:
                next_state = transition_state(state, d)

            res += dfs(
                pos + 1,
                next_state,
                tight and (d == limit),
                next_started,
            )

        return res

    return dfs(0, initial_state(), True, False)
```

**Bẫy phổ biến**:
- Quên xử lý `started` → leading zeros làm sai đếm.
- Terminal condition (pos==n): đề cho phép số 0 hay không phải rõ.

---

### 14.3 Profile DP / Broken Profile (DP mặt cắt)

Hay gặp trong bài **grid/tiling/đặt vật** khi chuyển theo từng hàng (hoặc cột). Ý tưởng:
- `mask` biểu diễn “trạng thái biên” giữa row hiện tại và row kế tiếp
- Duyệt từng ô trong row để sinh `next_mask`

**Khung ý tưởng**:
```
dp[row][mask] = số cách / min cost / max value
transition: từ mask -> next_mask bằng cách fill dần các cột
```

**Skeleton (Python pseudo, ví dụ domino tiling)**:

```python
def profile_dp(R, C):
    dp = {0: 1}  # mask -> ways

    for _row in range(R):
        ndp = {}

        def gen(col, mask, next_mask, ways):
            if col == C:
                ndp[next_mask] = ndp.get(next_mask, 0) + ways
                return

            if (mask >> col) & 1:
                gen(col + 1, mask, next_mask, ways)
                return

            # Domino ngang
            if col + 1 < C and ((mask >> (col + 1)) & 1) == 0:
                gen(col + 2, mask, next_mask, ways)

            # Domino dọc (đẩy occupancy xuống next_mask)
            gen(col + 1, mask, next_mask | (1 << col), ways)

        for mask, ways in dp.items():
            gen(0, mask, 0, ways)

        dp = ndp

    return dp.get(0, 0)
```

---

### 14.4 Divide & Conquer DP Optimization (Tối ưu chia để trị)

Áp dụng cho lớp bài kiểu “chia prefix thành k nhóm/đoạn”:

```
dp[i][j] = min_{k <= j} ( dp[i-1][k] + C(k+1, j) )
```

Nếu điểm tối ưu `opt[i][j]` **đơn điệu** theo j (thường: `opt[i][j] <= opt[i][j+1]`) thì có thể tính mỗi hàng dp nhanh hơn.

**Template compute(l,r,optl,optr)**:

```python
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

**Checklist trước khi dùng**:
- Recurrence đúng dạng “min over k” với cost có cấu trúc.
- Có cơ sở (hoặc known result) cho tính đơn điệu của `opt`.

---

### 14.5 Knuth Optimization (Tối ưu Knuth cho Interval DP)

Knuth thường áp dụng cho interval DP dạng:

```
dp[l][r] = min_{k in (l..r)} ( dp[l][k] + dp[k][r] ) + C(l,r)
```

Khi thỏa **opt monotonicity**:
```
opt[l][r-1] <= opt[l][r] <= opt[l+1][r]
```

ta thu hẹp range của k:
```
k chỉ cần duyệt từ opt[l][r-1] đến opt[l+1][r]
```

**Template (pseudo)**:

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

**Ghi chú**:
- Điều kiện áp dụng phụ thuộc bài (liên quan tính chất của cost). Nếu không chắc, đừng dùng Knuth.

---

### 14.6 Mini checklist: “khi nào cần tối ưu DP?”

```
Nếu O(n^3) hoặc O(n^2 * k) bị TLE:
  1) Có thể đổi state không? (vd LIS: dp ending -> tails)
  2) Có thể giảm chiều không? (2D -> rolling/1D)
  3) Có cấu trúc min over k không?
       - thử D&C optimization (opt đơn điệu)
       - thử Knuth (interval + opt monotonicity)
  4) Bitmask/profile: có thể chuyển theo “hàng” để giảm trạng thái?
```

---

# TỔNG KẾT

## Checklist khi giải bài DP

```
┌─────────────────────────────────────────────────────────────┐
│  CHECKLIST GIẢI BÀI DP                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ☐ 1. NHẬN DIỆN: Có phải bài DP không?                     │
│       → Tối ưu? Đếm? Khả thi?                              │
│       → 3 tính chất thỏa mãn?                              │
│                                                             │
│  ☐ 2. ĐỊNH NGHĨA TRẠNG THÁI: dp[...] là gì?                │
│       → Đủ thông tin? Không thừa?                          │
│       → Ý nghĩa rõ ràng?                                   │
│                                                             │
│  ☐ 3. TÌM PHƯƠNG TRÌNH CHUYỂN                              │
│       → Liệt kê tất cả lựa chọn                            │
│       → Xác định trạng thái trước đó                       │
│       → Kết hợp (max/min/sum)                              │
│                                                             │
│  ☐ 4. XÁC ĐỊNH BASE CASES                                  │
│       → Trạng thái nhỏ nhất?                               │
│       → Trạng thái không hợp lệ?                           │
│                                                             │
│  ☐ 5. XÁC ĐỊNH THỨ TỰ TÍNH                                 │
│       → Trạng thái nào tính trước?                         │
│       → Duyệt xuôi hay ngược?                              │
│                                                             │
│  ☐ 6. CODE VÀ TEST                                         │
│       → In bảng DP với test nhỏ                            │
│       → Verify với brute force                             │
│                                                             │
│  ☐ 7. TỐI ƯU (nếu cần)                                     │
│       → Giảm không gian?                                   │
│       → Dùng kỹ thuật tối ưu?                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Mental Model cuối cùng

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│             DP = TƯ DUY TỪ CUỐI VỀ ĐẦU                     │
│                      +                                      │
│               NHỚ NHỮNG GÌ ĐÃ LÀM                          │
│                                                             │
│  "Để đạt được trạng thái này,                              │
│   tôi phải đến từ trạng thái nào?"                         │
│                                                             │
│  "Và tôi sẽ nhớ kết quả để không tính lại."                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Tài liệu bổ sung cho C.md, tập trung vào phương pháp tư duy*

*Cập nhật: 30/12/2024*

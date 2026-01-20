# Phần 1.2: Giải thuật Chi tiết (Detailed Algorithms)

Tài liệu này là bản dịch và biên soạn chi tiết từ nguồn JavaGuide, bao gồm đầy đủ các giải thích, ví dụ code Java và hình ảnh minh họa.

---

## 1. Giới thiệu về Thuật toán Sắp xếp

### 1.1. Tổng quan các Thuật toán Sắp xếp

Sắp xếp là việc làm cho một chuỗi bản ghi xếp theo thứ tự tăng dần hoặc giảm dần dựa trên một hoặc nhiều khóa (key) của chúng. Thuật toán sắp xếp được ứng dụng rộng rãi trong nhiều lĩnh vực, đặc biệt là xử lý dữ liệu lớn. Một thuật toán tốt có thể tiết kiệm đáng kể tài nguyên.

| Thuật toán | Độ phức tạp (TB) | Độ phức tạp (Tệ nhất) | Độ phức tạp (Tốt nhất) | Không gian | Phương pháp | Ổn định |
| :--------- | :--------------- | :-------------------- | :--------------------- | :--------- | :---------- | :------ |
| Bubble Sort | O(n²) | O(n²) | O(n) | O(1) | In-place | ✅ Có |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) | In-place | ❌ Không |
| Insertion Sort | O(n²) | O(n²) | O(n) | O(1) | In-place | ✅ Có |
| Shell Sort | O(n log n) | O(n²) | O(n log n) | O(1) | In-place | ❌ Không |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Out-of-place | ✅ Có |
| Quick Sort | O(n log n) | O(n²) | O(n log n) | O(log n) | In-place | ❌ Không |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | In-place | ❌ Không |
| Counting Sort | O(n+k) | O(n+k) | O(n+k) | O(k) | Out-of-place | ✅ Có |
| Bucket Sort | O(n+k) | O(n²) | O(n+k) | O(n+k) | Out-of-place | ✅ Có |
| Radix Sort | O(n×k) | O(n×k) | O(n×k) | O(n+k) | Out-of-place | ✅ Có |

**Giải thích thuật ngữ:**

*   **n**: Kích thước dữ liệu (số lượng phần tử cần sắp xếp).
*   **k**: Số lượng "bucket" hoặc phạm vi dữ liệu (trong một số thuật toán như Radix Sort, Bucket Sort).
*   **In-place (Tại chỗ)**: Tất cả thao tác sắp xếp diễn ra trong bộ nhớ, không cần thêm bộ nhớ phụ ngoài disk.
*   **Out-of-place (Ngoài chỗ)**: Khi dữ liệu quá lớn, không thể load hết vào bộ nhớ, cần lưu trữ tạm vào thiết bị ngoài.
*   **Ổn định (Stable)**: Nếu A nằm trước B và A = B, sau khi sắp xếp A vẫn nằm trước B.
*   **Không ổn định (Unstable)**: Nếu A nằm trước B và A = B, sau khi sắp xếp A có thể nằm sau B.

### 1.2. Phân loại Thuật toán Sắp xếp

Thuật toán sắp xếp được chia thành hai loại chính: **So sánh** và **Không so sánh**.

![Phân loại thuật toán sắp xếp](https://oss.javaguide.cn/github/javaguide/cs-basics/sorting-algorithms/sort2.png)

**Thuật toán so sánh (Comparison-based):**
*   Quick Sort, Merge Sort, Heap Sort, Bubble Sort v.v.
*   Xác định thứ tự tương đối của các phần tử thông qua so sánh.
*   Độ phức tạp thời gian không thể vượt qua `O(n log n)`.

**Thuật toán không so sánh (Non-comparison):**
*   Counting Sort, Radix Sort, Bucket Sort.
*   Không so sánh để xác định thứ tự mà xác định vị trí của mỗi phần tử bằng cách đếm số phần tử trước nó.
*   Có thể đạt độ phức tạp thời gian tuyến tính `O(n)`.

---

## 2. Sắp xếp Nổi bọt (Bubble Sort)

Sắp xếp nổi bọt là thuật toán đơn giản. Nó lặp đi lặp lại việc duyệt qua chuỗi cần sắp xếp, so sánh hai phần tử kề nhau, nếu thứ tự sai thì hoán đổi chúng. Việc duyệt được lặp lại cho đến khi không cần hoán đổi nữa. Tên gọi này xuất phát từ việc phần tử nhỏ hơn sẽ dần "nổi" lên đầu dãy.

### 2.1. Các bước thuật toán

1.  So sánh hai phần tử kề nhau. Nếu phần tử đầu lớn hơn phần tử sau, hoán đổi chúng.
2.  Thực hiện tương tự cho mọi cặp phần tử kề nhau từ đầu đến cuối. Sau bước này, phần tử cuối cùng sẽ là lớn nhất.
3.  Lặp lại các bước trên cho tất cả phần tử, trừ phần tử cuối cùng.
4.  Tiếp tục lặp cho đến khi sắp xếp hoàn tất.

### 2.2. Hình ảnh minh họa

![Bubble Sort](images/bubble_sort.gif)

### 2.3. Code Java

```java
/**
 * Sắp xếp nổi bọt (Bubble Sort)
 * @param arr Mảng cần sắp xếp
 * @return arr Mảng đã sắp xếp
 */
public static int[] bubbleSort(int[] arr) {
    for (int i = 1; i < arr.length; i++) {
        // Đặt cờ, nếu true nghĩa là vòng lặp không có hoán đổi,
        // tức là dãy đã được sắp xếp, kết thúc sắp xếp.
        boolean flag = true;
        for (int j = 0; j < arr.length - i; j++) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
                // Đổi cờ
                flag = false;
            }
        }
        if (flag) {
            break;
        }
    }
    return arr;
}
```

**Tối ưu:** Code trên đã thêm cờ `flag` để tối ưu độ phức tạp thời gian tốt nhất thành `O(n)`, tức là khi dãy đầu vào đã được sắp xếp sẵn.

### 2.4. Phân tích thuật toán

*   **Tính ổn định**: Ổn định ✅
*   **Độ phức tạp thời gian**: Tốt nhất O(n), Tệ nhất O(n²), Trung bình O(n²)
*   **Độ phức tạp không gian**: O(1)
*   **Phương pháp**: In-place

---

## 3. Sắp xếp Chọn (Selection Sort)

Sắp xếp chọn là thuật toán đơn giản và trực quan, luôn có độ phức tạp O(n²) bất kể dữ liệu đầu vào. Ưu điểm duy nhất là không chiếm thêm bộ nhớ. **Nguyên lý:** Tìm phần tử nhỏ nhất (hoặc lớn nhất) trong dãy chưa sắp xếp, đặt vào đầu dãy đã sắp xếp. Tiếp tục tìm phần tử nhỏ nhất (lớn nhất) từ các phần tử chưa sắp xếp còn lại, đặt vào cuối dãy đã sắp xếp. Lặp lại cho đến khi hoàn tất.

### 3.1. Các bước thuật toán

1.  Tìm phần tử nhỏ nhất (lớn nhất) trong dãy chưa sắp xếp, đặt vào đầu dãy đã sắp xếp.
2.  Tiếp tục tìm phần tử nhỏ nhất (lớn nhất) từ các phần tử chưa sắp xếp còn lại, đặt vào cuối dãy đã sắp xếp.
3.  Lặp lại bước 2 cho đến khi tất cả phần tử đều được sắp xếp.

### 3.2. Hình ảnh minh họa

![Selection Sort](images/selection_sort.gif)

### 3.3. Code Java

```java
/**
 * Sắp xếp chọn (Selection Sort)
 * @param arr Mảng cần sắp xếp
 * @return arr Mảng đã sắp xếp
 */
public static int[] selectionSort(int[] arr) {
    for (int i = 0; i < arr.length - 1; i++) {
        int minIndex = i;
        for (int j = i + 1; j < arr.length; j++) {
            if (arr[j] < arr[minIndex]) {
                minIndex = j;
            }
        }
        if (minIndex != i) {
            int tmp = arr[i];
            arr[i] = arr[minIndex];
            arr[minIndex] = tmp;
        }
    }
    return arr;
}
```

### 3.4. Phân tích thuật toán

*   **Tính ổn định**: Không ổn định ❌
*   **Độ phức tạp thời gian**: Tốt nhất O(n²), Tệ nhất O(n²), Trung bình O(n²)
*   **Độ phức tạp không gian**: O(1)
*   **Phương pháp**: In-place

---

## 4. Sắp xếp Chèn (Insertion Sort)

Sắp xếp chèn là thuật toán đơn giản và trực quan. **Nguyên lý:** Xây dựng dãy đã sắp xếp, với mỗi phần tử chưa sắp xếp, quét từ sau ra trước trong dãy đã sắp xếp để tìm vị trí phù hợp và chèn vào. Giống như khi chơi bài, chúng ta xếp bài trên tay theo thứ tự bằng cách chèn từng lá bài mới vào đúng vị trí.

### 4.1. Các bước thuật toán

1.  Bắt đầu từ phần tử đầu tiên, coi phần tử đó đã được sắp xếp.
2.  Lấy phần tử tiếp theo, quét từ sau ra trước trong dãy đã sắp xếp.
3.  Nếu phần tử đã sắp xếp lớn hơn phần tử mới, di chuyển phần tử đó sang vị trí tiếp theo.
4.  Lặp lại bước 3 cho đến khi tìm được vị trí phần tử đã sắp xếp nhỏ hơn hoặc bằng phần tử mới.
5.  Chèn phần tử mới vào vị trí đó.
6.  Lặp lại bước 2~5.

### 4.2. Hình ảnh minh họa

![Insertion Sort](images/insertion_sort.gif)

### 4.3. Code Java

```java
/**
 * Sắp xếp chèn (Insertion Sort)
 * @param arr Mảng cần sắp xếp
 * @return arr Mảng đã sắp xếp
 */
public static int[] insertionSort(int[] arr) {
    for (int i = 1; i < arr.length; i++) {
        int preIndex = i - 1;
        int current = arr[i];
        while (preIndex >= 0 && current < arr[preIndex]) {
            arr[preIndex + 1] = arr[preIndex];
            preIndex -= 1;
        }
        arr[preIndex + 1] = current;
    }
    return arr;
}
```

### 4.4. Phân tích thuật toán

*   **Tính ổn định**: Ổn định ✅
*   **Độ phức tạp thời gian**: Tốt nhất O(n), Tệ nhất O(n²), Trung bình O(n²)
*   **Độ phức tạp không gian**: O(1)
*   **Phương pháp**: In-place

---

## 5. Sắp xếp Shell (Shell Sort)

Shell Sort được Donald Shell đề xuất năm 1959. Đây là phiên bản cải tiến của Insertion Sort, còn gọi là thuật toán sắp xếp tăng dần giảm (Diminishing Increment Sort), là một trong những thuật toán đầu tiên phá vỡ ngưỡng O(n²).

**Ý tưởng cơ bản:** Chia dãy cần sắp xếp thành nhiều dãy con để thực hiện Insertion Sort riêng lẻ. Khi toàn bộ dãy "gần như đã sắp xếp", thực hiện Insertion Sort lần cuối trên toàn bộ dãy.

### 5.1. Các bước thuật toán

Chọn chuỗi tăng (increment sequence) `{n/2, (n/2)/2, ..., 1}` (gọi là "Shell increment"):

*   Chọn một chuỗi tăng `{t₁, t₂, ..., tₖ}`, trong đó `tᵢ > tⱼ` nếu `i < j`, `tₖ = 1`.
*   Theo số lượng phần tử k trong chuỗi tăng, thực hiện k lượt sắp xếp.
*   Mỗi lượt sắp xếp, dựa vào giá trị tăng t tương ứng, chia dãy thành các dãy con có độ dài m, thực hiện Insertion Sort trên từng dãy con. Chỉ khi giá trị tăng bằng 1, toàn bộ dãy được coi như một bảng duy nhất.

### 5.2. Hình ảnh minh họa

![Shell Sort](images/shell_sort.png)

### 5.3. Code Java

```java
/**
 * Sắp xếp Shell (Shell Sort)
 * @param arr Mảng cần sắp xếp
 * @return arr Mảng đã sắp xếp
 */
public static int[] shellSort(int[] arr) {
    int n = arr.length;
    int gap = n / 2;
    while (gap > 0) {
        for (int i = gap; i < n; i++) {
            int current = arr[i];
            int preIndex = i - gap;
            // Insertion sort với gap
            while (preIndex >= 0 && arr[preIndex] > current) {
                arr[preIndex + gap] = arr[preIndex];
                preIndex -= gap;
            }
            arr[preIndex + gap] = current;
        }
        gap /= 2;
    }
    return arr;
}
```

### 5.4. Phân tích thuật toán

*   **Tính ổn định**: Không ổn định ❌
*   **Độ phức tạp thời gian**: Tốt nhất O(n log n), Tệ nhất O(n²), Trung bình O(n log n)
*   **Độ phức tạp không gian**: O(1)

---

## 6. Sắp xếp Trộn (Merge Sort)

Merge Sort được xây dựng trên thao tác trộn (merge), là ứng dụng điển hình của **Chia để Trị (Divide and Conquer)**. Đây là thuật toán sắp xếp ổn định. Trộn các dãy con đã sắp xếp để có dãy hoàn toàn có thứ tự: trước tiên làm cho từng dãy con có thứ tự, sau đó làm cho các đoạn dãy con có thứ tự với nhau. Trộn hai bảng có thứ tự thành một bảng có thứ tự gọi là "2-way merge".

### 6.1. Các bước thuật toán

Merge Sort là quá trình đệ quy, điều kiện biên là khi dãy đầu vào chỉ có một phần tử, trả về ngay:

1.  Nếu đầu vào chỉ có một phần tử, trả về ngay. Ngược lại, chia dãy độ dài n thành hai dãy con độ dài n/2.
2.  Đệ quy Merge Sort trên hai dãy con để làm chúng có thứ tự.
3.  Đặt hai con trỏ, trỏ đến vị trí đầu của hai dãy con đã sắp xếp.
4.  So sánh hai phần tử tại hai con trỏ, chọn phần tử nhỏ hơn đưa vào không gian kết quả, di chuyển con trỏ tương ứng.
5.  Lặp lại bước 3~4 cho đến khi một con trỏ đến cuối dãy.
6.  Sao chép tất cả phần tử còn lại của dãy kia vào cuối kết quả.

### 6.2. Hình ảnh minh họa

![Merge Sort](images/merge_sort.gif)

### 6.3. Code Java

```java
/**
 * Sắp xếp trộn (Merge Sort)
 * @param arr Mảng cần sắp xếp
 * @return arr Mảng đã sắp xếp
 */
public static int[] mergeSort(int[] arr) {
    if (arr.length <= 1) {
        return arr;
    }
    int middle = arr.length / 2;
    int[] arr_1 = Arrays.copyOfRange(arr, 0, middle);
    int[] arr_2 = Arrays.copyOfRange(arr, middle, arr.length);
    return merge(mergeSort(arr_1), mergeSort(arr_2));
}

/**
 * Trộn hai mảng đã sắp xếp
 */
public static int[] merge(int[] arr_1, int[] arr_2) {
    int[] sorted_arr = new int[arr_1.length + arr_2.length];
    int idx = 0, idx_1 = 0, idx_2 = 0;
    while (idx_1 < arr_1.length && idx_2 < arr_2.length) {
        if (arr_1[idx_1] < arr_2[idx_2]) {
            sorted_arr[idx] = arr_1[idx_1];
            idx_1 += 1;
        } else {
            sorted_arr[idx] = arr_2[idx_2];
            idx_2 += 1;
        }
        idx += 1;
    }
    // Sao chép phần còn lại
    while (idx_1 < arr_1.length) {
        sorted_arr[idx++] = arr_1[idx_1++];
    }
    while (idx_2 < arr_2.length) {
        sorted_arr[idx++] = arr_2[idx_2++];
    }
    return sorted_arr;
}
```

### 6.4. Phân tích thuật toán

*   **Tính ổn định**: Ổn định ✅
*   **Độ phức tạp thời gian**: Tốt nhất O(n log n), Tệ nhất O(n log n), Trung bình O(n log n)
*   **Độ phức tạp không gian**: O(n)

---

## 7. Sắp xếp Nhanh (Quick Sort)

Quick Sort sử dụng tư tưởng **Chia để Trị**, tương tự Merge Sort. Điểm khác biệt là Quick Sort khi chia bài toán con sẽ xử lý thêm một bước: chia thành hai nhóm lớn và nhỏ, do đó khi ghép lại không cần so sánh như Merge Sort. Tuy nhiên, do tính không xác định trong việc chia, độ phức tạp thời gian của Quick Sort không ổn định.

**Ý tưởng cơ bản:** Qua một lượt sắp xếp, chia dãy thành hai phần độc lập, một phần chứa các phần tử nhỏ hơn phần còn lại. Sau đó đệ quy sắp xếp hai phần đó, đạt được dãy hoàn toàn có thứ tự.

### 7.1. Các bước thuật toán

1.  **Chọn Pivot**: Chọn một phần tử làm điểm chốt. Để tránh trường hợp tệ nhất, thường chọn ngẫu nhiên.
2.  **Phân hoạch (Partition)**: Sắp xếp lại dãy: các phần tử nhỏ hơn pivot đặt trước, các phần tử lớn hơn pivot đặt sau (các phần tử bằng có thể đặt bất kỳ bên nào). Sau thao tác này, pivot nằm ở vị trí giữa dãy.
3.  **Đệ quy (Recurse)**: Đệ quy Quick Sort trên dãy con nhỏ hơn pivot và dãy con lớn hơn pivot.

**Về hiệu suất:**
*   **Trường hợp trung bình và tốt nhất**: O(n log n). Xảy ra khi mỗi lần phân hoạch đều chia dãy thành hai nửa gần bằng nhau.
*   **Trường hợp tệ nhất**: O(n²). Xảy ra khi mỗi lần chọn pivot đều là phần tử nhỏ nhất hoặc lớn nhất (ví dụ dãy đã sắp xếp sẵn và luôn chọn phần tử đầu làm pivot). Đây là lý do **chọn pivot ngẫu nhiên** rất quan trọng.

### 7.2. Hình ảnh minh họa

![Quick Sort](images/random_quick_sort.gif)

### 7.3. Code Java

```java
import java.util.concurrent.ThreadLocalRandom;

class Solution {
    public int[] sortArray(int[] a) {
        quick(a, 0, a.length - 1);
        return a;
    }

    // Hàm đệ quy chính của Quick Sort
    void quick(int[] a, int left, int right) {
        if (left >= right) { // Điều kiện kết thúc đệ quy
            return;
        }
        int p = partition(a, left, right); // Phân hoạch, trả về vị trí pivot
        quick(a, left, p - 1);  // Đệ quy sắp xếp dãy con trái
        quick(a, p + 1, right); // Đệ quy sắp xếp dãy con phải
    }

    // Hàm phân hoạch: chia mảng thành 2 phần, nhỏ hơn pivot bên trái, lớn hơn bên phải
    int partition(int[] a, int left, int right) {
        // Chọn ngẫu nhiên một điểm pivot để tránh trường hợp tệ nhất
        int idx = ThreadLocalRandom.current().nextInt(right - left + 1) + left;
        swap(a, left, idx); // Đưa pivot về đầu mảng
        int pv = a[left];   // Giá trị pivot
        int i = left + 1;   // Con trỏ trái
        int j = right;      // Con trỏ phải

        while (i <= j) {
            // Con trỏ trái di chuyển sang phải cho đến khi gặp phần tử >= pivot
            while (i <= j && a[i] < pv) {
                i++;
            }
            // Con trỏ phải di chuyển sang trái cho đến khi gặp phần tử <= pivot
            while (i <= j && a[j] > pv) {
                j--;
            }
            // Nếu con trỏ trái chưa vượt con trỏ phải, hoán đổi hai phần tử
            if (i <= j) {
                swap(a, i, j);
                i++;
                j--;
            }
        }
        // Đưa pivot về vị trí phân hoạch
        swap(a, j, left);
        return j;
    }

    // Hoán đổi hai phần tử trong mảng
    void swap(int[] a, int i, int j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
    }
}
```

### 7.4. Phân tích thuật toán

*   **Tính ổn định**: Không ổn định ❌
*   **Độ phức tạp thời gian**: Tốt nhất O(n log n), Tệ nhất O(n²), Trung bình O(n log n)
*   **Độ phức tạp không gian**: O(log n)

---

## 8. Sắp xếp Heap (Heap Sort)

Heap Sort sử dụng cấu trúc dữ liệu Heap để sắp xếp. Heap là cấu trúc cây nhị phân gần hoàn chỉnh, đồng thời thỏa mãn **tính chất Heap**: giá trị nút con luôn nhỏ hơn (hoặc lớn hơn) giá trị nút cha.

### 8.1. Các bước thuật toán

1.  Xây dựng dãy ban đầu thành Max Heap, đây là vùng chưa sắp xếp.
2.  Hoán đổi phần tử đỉnh heap (R₁) với phần tử cuối (Rₙ). Thu được vùng chưa sắp xếp mới (R₁...Rₙ₋₁) và vùng đã sắp xếp (Rₙ), thỏa mãn Rᵢ ≤ Rₙ.
3.  Do sau hoán đổi, đỉnh heap mới có thể vi phạm tính chất heap, cần điều chỉnh (heapify) vùng chưa sắp xếp thành heap mới. Lặp lại hoán đổi R₁ với phần tử cuối vùng chưa sắp xếp cho đến khi vùng đã sắp xếp có n-1 phần tử.

### 8.2. Hình ảnh minh họa

![Heap Sort](images/heap_sort.gif)

### 8.3. Code Java

```java
static int heapLen;

private static void swap(int[] arr, int i, int j) {
    int tmp = arr[i];
    arr[i] = arr[j];
    arr[j] = tmp;
}

// Xây dựng Max Heap
private static void buildMaxHeap(int[] arr) {
    for (int i = arr.length / 2 - 1; i >= 0; i--) {
        heapify(arr, i);
    }
}

// Điều chỉnh thành Max Heap
private static void heapify(int[] arr, int i) {
    int left = 2 * i + 1;
    int right = 2 * i + 2;
    int largest = i;
    if (right < heapLen && arr[right] > arr[largest]) {
        largest = right;
    }
    if (left < heapLen && arr[left] > arr[largest]) {
        largest = left;
    }
    if (largest != i) {
        swap(arr, largest, i);
        heapify(arr, largest);
    }
}

// Heap Sort
public static int[] heapSort(int[] arr) {
    heapLen = arr.length;
    buildMaxHeap(arr);
    for (int i = arr.length - 1; i > 0; i--) {
        // Di chuyển đỉnh heap xuống cuối
        swap(arr, 0, i);
        heapLen -= 1;
        heapify(arr, 0);
    }
    return arr;
}
```

### 8.4. Phân tích thuật toán

*   **Tính ổn định**: Không ổn định ❌
*   **Độ phức tạp thời gian**: Tốt nhất O(n log n), Tệ nhất O(n log n), Trung bình O(n log n)
*   **Độ phức tạp không gian**: O(1)

---

## 9. Sắp xếp Đếm (Counting Sort)

Counting Sort là thuật toán sắp xếp tuyến tính. **Yêu cầu dữ liệu đầu vào phải là số nguyên trong phạm vi xác định.**

Counting Sort sử dụng một mảng phụ C, trong đó phần tử thứ i là số lượng phần tử có giá trị bằng i trong mảng A. Sau đó dựa vào mảng C để đặt các phần tử của A vào đúng vị trí.

### 9.1. Các bước thuật toán

1.  Tìm giá trị lớn nhất `max`, nhỏ nhất `min` trong mảng.
2.  Tạo mảng mới C có độ dài `max - min + 1`, tất cả phần tử mặc định là 0.
3.  Duyệt mảng gốc A, với mỗi phần tử `A[i]`, dùng `A[i] - min` làm chỉ số trong C, tăng giá trị `C[A[i] - min]` lên 1.
4.  Biến đổi C: phần tử mới = phần tử hiện tại + phần tử trước đó, tức `C[i] = C[i] + C[i-1]` (khi i > 0).
5.  Tạo mảng kết quả R cùng độ dài mảng gốc.
6.  Duyệt ngược mảng gốc A, với mỗi `A[i]`, dùng `A[i] - min` làm chỉ số trong C, `C[A[i] - min] - 1` là vị trí của `A[i]` trong R. Sau đó giảm `C[A[i] - min]` đi 1.

### 9.2. Hình ảnh minh họa

![Counting Sort](images/counting_sort.gif)

### 9.3. Phân tích thuật toán

*   **Tính ổn định**: Ổn định ✅
*   **Độ phức tạp thời gian**: O(n+k)
*   **Độ phức tạp không gian**: O(k)

---

## 10. Sắp xếp Bucket (Bucket Sort)

Bucket Sort là phiên bản nâng cấp của Counting Sort. Nó sử dụng hàm ánh xạ để phân phối dữ liệu vào các bucket, sau đó sắp xếp từng bucket riêng lẻ.

### 10.1. Các bước thuật toán

1.  Thiết lập BucketSize (số lượng giá trị khác nhau mỗi bucket có thể chứa).
2.  Duyệt dữ liệu đầu vào, phân phối vào các bucket tương ứng.
3.  Sắp xếp từng bucket không rỗng (có thể dùng thuật toán khác hoặc đệ quy Bucket Sort).
4.  Ghép các bucket đã sắp xếp lại với nhau.

### 10.2. Hình ảnh minh họa

![Bucket Sort](images/bucket_sort.gif)

### 10.3. Phân tích thuật toán

*   **Tính ổn định**: Ổn định ✅
*   **Độ phức tạp thời gian**: Tốt nhất O(n+k), Tệ nhất O(n²), Trung bình O(n+k)
*   **Độ phức tạp không gian**: O(n+k)

---

## 11. Sắp xếp Cơ số (Radix Sort)

Radix Sort cũng là thuật toán không so sánh, sắp xếp theo từng chữ số của phần tử, bắt đầu từ chữ số thấp nhất. Độ phức tạp O(n×k), với n là độ dài mảng, k là số chữ số lớn nhất của phần tử.

**Ý tưởng:** Sắp xếp theo chữ số thấp trước, thu thập lại; sắp xếp theo chữ số cao hơn, thu thập lại; tiếp tục cho đến chữ số cao nhất.

### 11.1. Các bước thuật toán

1.  Lấy phần tử lớn nhất trong mảng, xác định số chữ số (số lần lặp N).
2.  A là mảng gốc, lấy từng chữ số từ thấp đến cao tạo thành mảng radix.
3.  Thực hiện Counting Sort trên mảng radix (tận dụng đặc tính Counting Sort phù hợp với phạm vi nhỏ).
4.  Gán lại giá trị từ radix vào mảng gốc.
5.  Lặp lại bước 2~4 N lần.

### 11.2. Hình ảnh minh họa

![Radix Sort](images/radix_sort.gif)

### 11.3. Phân tích thuật toán

*   **Tính ổn định**: Ổn định ✅
*   **Độ phức tạp thời gian**: O(n×k)
*   **Độ phức tạp không gian**: O(n+k)

**So sánh Radix Sort, Counting Sort, Bucket Sort:**

*   **Radix Sort**: Phân phối bucket theo từng chữ số của key.
*   **Counting Sort**: Mỗi bucket chỉ lưu một giá trị key duy nhất.
*   **Bucket Sort**: Mỗi bucket lưu một phạm vi giá trị.

---

## 12. Thuật toán KMP (Knuth-Morris-Pratt)

KMP là thuật toán tìm kiếm chuỗi con trong chuỗi cha. Nó có thể tìm vị trí xuất hiện của chuỗi con W trong chuỗi S. KMP có độ phức tạp thời gian **O(m+n)** và không gian **O(m)** (m là độ dài chuỗi con).

**Vấn đề của "Brute Force Search":** Khi so khớp thất bại, phương pháp vét cạn sẽ quay lui con trỏ chuỗi chính về, gây ra hiệu suất thấp.

**Ý tưởng KMP:** Tận dụng thông tin về phần đã khớp thành công, giữ nguyên con trỏ chuỗi chính (không quay lui), chỉ điều chỉnh con trỏ chuỗi mẫu để chuỗi mẫu di chuyển đến vị trí hiệu quả nhất có thể.

**Tài liệu tham khảo:**
*   [Từ đầu đến cuối hiểu rõ KMP](https://blog.csdn.net/v_july_v/article/details/7041827)
*   [Làm sao để hiểu và nắm vững thuật toán KMP?](https://www.zhihu.com/question/21923021)
*   [KMP Algorithm - Bilibili](https://www.bilibili.com/video/av3246487/)

**Thuật toán BM (Boyer-Moore):** Cũng là thuật toán khớp chuỗi chính xác, so sánh từ phải sang trái, áp dụng hai quy tắc: "Bad Character Rule" và "Good Suffix Rule".

---

## 13. Các Bài toán Chuỗi Phổ biến

### 13.1. Thay thế Khoảng trắng

> **Bài toán (Kiếm chỉ Offer):** Triển khai hàm thay thế mỗi khoảng trắng trong chuỗi thành "%20". Ví dụ: "We Are Happy" → "We%20Are%20Happy".

**Giải pháp 1: Cách thông thường**
```java
public static String replaceSpace(StringBuffer str) {
    int length = str.length();
    StringBuffer result = new StringBuffer();
    for (int i = 0; i < length; i++) {
        char b = str.charAt(i);
        if (String.valueOf(b).equals(" ")) {
            result.append("%20");
        } else {
            result.append(b);
        }
    }
    return result.toString();
}
```

**Giải pháp 2: Sử dụng API**
```java
public static String replaceSpace2(StringBuffer str) {
    return str.toString().replace(" ", "%20");
}
```

### 13.2. Tiền tố Chung Dài nhất

> **Bài toán (Leetcode):** Tìm tiền tố chung dài nhất của mảng chuỗi. Nếu không tồn tại, trả về chuỗi rỗng "".

**Ví dụ:**
*   Input: `["flower","flow","flight"]` → Output: `"fl"`
*   Input: `["dog","racecar","car"]` → Output: `""`

**Ý tưởng:** Sắp xếp mảng, sau đó so sánh phần tử đầu và cuối của mảng đã sắp xếp!

```java
public static String longestCommonPrefix(String[] strs) {
    if (strs == null || strs.length == 0) return "";
    Arrays.sort(strs);
    int len = strs.length;
    StringBuilder res = new StringBuilder();
    int m = strs[0].length();
    int n = strs[len - 1].length();
    int num = Math.min(m, n);
    for (int i = 0; i < num; i++) {
        if (strs[0].charAt(i) == strs[len - 1].charAt(i)) {
            res.append(strs[0].charAt(i));
        } else {
            break;
        }
    }
    return res.toString();
}
```

### 13.3. Chuỗi Đối xứng (Palindrome)

#### Chuỗi Đối xứng Dài nhất có thể Xây dựng

> **Bài toán (Leetcode):** Cho chuỗi chứa chữ hoa và chữ thường, tìm độ dài chuỗi đối xứng dài nhất có thể xây dựng từ các ký tự này.

*   Input: `"abccccdd"` → Output: `7` (giải thích: "dccaccd" có độ dài 7)

**Ý tưởng:** Đếm số lần xuất hiện của mỗi ký tự. Ký tự xuất hiện số chẵn lần có thể dùng hết. Nếu có ký tự xuất hiện số lẻ lần, có thể thêm 1 vào độ dài.

```java
public int longestPalindrome(String s) {
    if (s.length() == 0) return 0;
    HashSet<Character> hashset = new HashSet<>();
    char[] chars = s.toCharArray();
    int count = 0;
    for (int i = 0; i < chars.length; i++) {
        if (!hashset.contains(chars[i])) {
            hashset.add(chars[i]);
        } else {
            hashset.remove(chars[i]);
            count++;
        }
    }
    return hashset.isEmpty() ? count * 2 : count * 2 + 1;
}
```

#### Chuỗi Con Đối xứng Dài nhất

> **Bài toán (Leetcode):** Cho chuỗi s, tìm chuỗi con đối xứng dài nhất trong s.

*   Input: `"babad"` → Output: `"bab"` (hoặc "aba")

**Ý tưởng:** Với mỗi phần tử làm tâm, mở rộng ra hai bên để tìm chuỗi đối xứng dài nhất (cần kiểm tra cả trường hợp độ dài chẵn và lẻ).

```java
class Solution {
    private int index, len;

    public String longestPalindrome(String s) {
        if (s.length() < 2) return s;
        for (int i = 0; i < s.length() - 1; i++) {
            PalindromeHelper(s, i, i);       // Độ dài lẻ
            PalindromeHelper(s, i, i + 1);   // Độ dài chẵn
        }
        return s.substring(index, index + len);
    }

    public void PalindromeHelper(String s, int l, int r) {
        while (l >= 0 && r < s.length() && s.charAt(l) == s.charAt(r)) {
            l--;
            r++;
        }
        if (len < r - l - 1) {
            index = l + 1;
            len = r - l - 1;
        }
    }
}
```

---

## 14. Các Bài toán Danh sách Liên kết Phổ biến

### 14.1. Cộng hai Số (Add Two Numbers)

> **Bài toán (Leetcode):** Cho hai danh sách liên kết không rỗng biểu diễn hai số không âm. Các chữ số được lưu theo thứ tự ngược (chữ số thấp ở đầu). Cộng hai số và trả về kết quả dưới dạng danh sách liên kết.

Input: `(2 -> 4 -> 3) + (5 -> 6 -> 4)` → Output: `7 -> 0 -> 8` (vì 342 + 465 = 807)

![Add Two Numbers](images/34910956.jpg)

**Ý tưởng:** Duyệt từ đầu hai danh sách liên kết (từ chữ số thấp nhất), cộng từng vị trí và theo dõi số nhớ (carry).

```java
public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
    ListNode dummyHead = new ListNode(0);
    ListNode p = l1, q = l2, curr = dummyHead;
    int carry = 0;  // Số nhớ
    while (p != null || q != null) {
        int x = (p != null) ? p.val : 0;
        int y = (q != null) ? q.val : 0;
        int sum = carry + x + y;
        carry = sum / 10;
        curr.next = new ListNode(sum % 10);
        curr = curr.next;
        if (p != null) p = p.next;
        if (q != null) q = q.next;
    }
    if (carry > 0) {
        curr.next = new ListNode(carry);
    }
    return dummyHead.next;
}
```

### 14.2. Đảo ngược Danh sách Liên kết (Reverse Linked List)

> **Bài toán (Kiếm chỉ Offer):** Cho một danh sách liên kết, đảo ngược danh sách và xuất ra các phần tử.

![Reverse Linked List](images/81431871.jpg)

**Ý tưởng:** Làm cho nút sau trỏ đến nút trước. Sử dụng biến `next` để lưu nút tiếp theo, tránh "đứt" danh sách.

```java
public ListNode ReverseList(ListNode head) {
    ListNode next = null;
    ListNode pre = null;

    while (head != null) {
        next = head.next;    // Lưu nút tiếp theo
        head.next = pre;     // Nút hiện tại trỏ về nút đã đảo ngược trước đó
        pre = head;          // Cập nhật nút đã đảo ngược
        head = next;         // Tiến đến nút tiếp theo
    }
    return pre;
}
```

### 14.3. Nút thứ K từ Cuối

> **Bài toán (Kiếm chỉ Offer):** Cho một danh sách liên kết, xuất nút thứ k từ cuối.

**Ý tưởng:** Nút thứ k từ cuối cũng là nút thứ (L - K + 1) từ đầu. Dùng hai con trỏ: con trỏ 1 đi trước k-1 bước, sau đó cả hai cùng đi. Khi con trỏ 1 đến cuối, con trỏ 2 chính là nút cần tìm.

```java
public ListNode FindKthToTail(ListNode head, int k) {
    if (head == null || k <= 0) return null;
    ListNode node1 = head, node2 = head;
    int count = 0;
    int index = k;
    while (node1 != null) {
        node1 = node1.next;
        count++;
        if (k < 1) {
            node2 = node2.next;
        }
        k--;
    }
    if (count < index) return null;
    return node2;
}
```

### 14.4. Trộn hai Danh sách Liên kết Đã sắp xếp

> **Bài toán (Kiếm chỉ Offer):** Cho hai danh sách liên kết đã sắp xếp tăng dần, trộn chúng thành một danh sách liên kết mới sao cho vẫn giữ thứ tự tăng dần.

**Ý tưởng (Đệ quy):** So sánh nút đầu của hai danh sách, nút nào nhỏ hơn sẽ là nút tiếp theo, và đệ quy cho phần còn lại.

```java
public ListNode Merge(ListNode list1, ListNode list2) {
    if (list1 == null) return list2;
    if (list2 == null) return list1;
    if (list1.val <= list2.val) {
        list1.next = Merge(list1.next, list2);
        return list1;
    } else {
        list2.next = Merge(list1, list2.next);
        return list2;
    }
}
```

---

*Kết thúc Phần 1.2: Giải thuật*

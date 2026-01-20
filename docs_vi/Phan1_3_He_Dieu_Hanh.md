# Phần 1.3: Hệ Điều hành Chi tiết (Detailed Operating Systems)

Tài liệu này là bản dịch và biên soạn chi tiết từ nguồn JavaGuide, bao gồm đầy đủ các giải thích về các khái niệm cơ bản của hệ điều hành, quản lý tiến trình, quản lý bộ nhớ, hệ thống tập tin và Linux.

---

## 1. Tổng quan về Hệ điều hành

### 1.1. Hệ điều hành là gì?

Hệ điều hành (Operating System - OS) có thể hiểu qua 4 điểm sau:

1.  **OS là chương trình quản lý tài nguyên phần cứng và phần mềm của máy tính**, là nền tảng của hệ thống máy tính.
2.  **Bản chất OS là một phần mềm chạy trên máy tính**, có nhiệm vụ chính là quản lý phần cứng và phần mềm. Ví dụ: tất cả ứng dụng chạy trên máy tính của bạn đều thông qua OS để gọi bộ nhớ, đĩa cứng v.v.
3.  **OS che giấu sự phức tạp của tầng phần cứng**. OS như một người quản lý tổng hợp mọi vấn đề liên quan đến việc sử dụng phần cứng.
4.  **Nhân (Kernel) của OS là phần cốt lõi**, chịu trách nhiệm quản lý bộ nhớ, thiết bị phần cứng, hệ thống tập tin và ứng dụng. Nhân là cầu nối giữa ứng dụng và phần cứng, quyết định hiệu suất và độ ổn định của hệ thống.

![Kernel Layout](https://oss.javaguide.cn/2020-8/Kernel_Layout.png)

**Phân biệt Kernel và CPU:**
*   Kernel thuộc về tầng hệ điều hành, còn CPU là phần cứng.
*   CPU cung cấp khả năng tính toán và xử lý các lệnh. Kernel chịu trách nhiệm quản lý hệ thống như quản lý bộ nhớ, che giấu các thao tác với phần cứng.

### 1.2. Các chức năng chính của Hệ điều hành

Từ góc độ quản lý tài nguyên, OS có 6 chức năng chính:

1.  **Quản lý tiến trình và luồng**: Tạo, hủy, chặn, đánh thức tiến trình, giao tiếp giữa các tiến trình, v.v.
2.  **Quản lý bộ nhớ**: Phân bổ và quản lý bộ nhớ trong (RAM) và bộ nhớ ngoài (đĩa cứng).
3.  **Quản lý tập tin**: Đọc, ghi, tạo và xóa tập tin.
4.  **Quản lý thiết bị**: Xử lý yêu cầu và giải phóng thiết bị (I/O và thiết bị lưu trữ ngoài), khởi động thiết bị.
5.  **Quản lý mạng**: Quản lý cấu hình, kết nối, truyền thông và bảo mật mạng máy tính.
6.  **Quản lý bảo mật**: Xác thực người dùng, kiểm soát truy cập, mã hóa tập tin để ngăn chặn truy cập trái phép.

---

## 2. Chế độ User Mode và Kernel Mode

### 2.1. User Mode và Kernel Mode là gì?

Dựa trên đặc điểm truy cập tài nguyên của tiến trình, chúng ta có thể chia quá trình chạy thành hai cấp độ:

![User Mode và Kernel Mode](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/usermode-and-kernelmode.png)

*   **User Mode (Chế độ người dùng)**: Tiến trình chạy ở chế độ này chỉ có thể đọc dữ liệu của chương trình người dùng, có quyền hạn thấp. Khi ứng dụng cần thực hiện các thao tác đòi hỏi quyền đặc biệt (như đọc/ghi đĩa, truyền thông mạng), nó cần gửi yêu cầu system call lên OS và chuyển sang Kernel Mode.

*   **Kernel Mode (Chế độ nhân)**: Tiến trình chạy ở chế độ này gần như có thể truy cập mọi tài nguyên của máy tính bao gồm bộ nhớ hệ thống, thiết bị, driver, không bị hạn chế, có quyền hạn rất cao.

**Tại sao cần cả User Mode và Kernel Mode?**

*   **Bảo mật**: Một số lệnh CPU nguy hiểm (phân bổ bộ nhớ, thiết lập đồng hồ, xử lý I/O) nếu để tất cả chương trình sử dụng sẽ gây thảm họa cho hệ thống. Những lệnh này chỉ được thực thi ở Kernel Mode, gọi là **lệnh đặc quyền**.
*   **Ổn định và hiệu suất**: Nếu chỉ có Kernel Mode, tất cả chương trình phải chia sẻ tài nguyên hệ thống, dẫn đến cạnh tranh và xung đột, ảnh hưởng hiệu suất và bảo mật.

### 2.2. Chuyển đổi giữa User Mode và Kernel Mode

![3 cách chuyển đổi User Mode sang Kernel Mode](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/the-way-switch-between-user-mode-and-kernel-mode.drawio.png)

Có 3 cách chuyển từ User Mode sang Kernel Mode:

1.  **System Call (Trap)**: Phổ biến nhất, do ứng dụng **chủ động** phát động. Khi chương trình cần đọc file hoặc gửi dữ liệu mạng, nó phải gọi API của OS (như `read()`, `send()`), kích hoạt chuyển đổi sang Kernel Mode.

2.  **Interrupt (Ngắt)**: **Bị động**, do thiết bị phần cứng bên ngoài kích hoạt. Ví dụ, khi đĩa cứng hoàn thành đọc dữ liệu, nó gửi tín hiệu ngắt đến CPU. CPU tạm dừng chương trình User Mode hiện tại, chuyển sang Kernel Mode để xử lý ngắt.

3.  **Exception (Ngoại lệ)**: **Bị động**, do lỗi của chính chương trình gây ra. Ví dụ, code thực hiện phép chia cho 0, hoặc truy cập địa chỉ bộ nhớ không hợp lệ (page fault). CPU bắt ngoại lệ và chuyển sang Kernel Mode để xử lý.

**Lưu ý**: Việc chuyển đổi này có chi phí hiệu suất vì cần lưu ngữ cảnh User Mode (thanh ghi v.v.), chuyển sang Kernel Mode thực thi, rồi khôi phục ngữ cảnh User Mode.

---

## 3. System Call (Gọi hệ thống)

### 3.1. System Call là gì?

Chương trình của chúng ta chạy ở User Mode. Nếu cần gọi các chức năng ở cấp Kernel Mode thì sao? Đó là lúc cần System Call!

Tức là, trong chương trình user đang chạy, mọi thao tác liên quan đến tài nguyên cấp hệ thống (quản lý file, điều khiển tiến trình, quản lý bộ nhớ v.v.) đều phải thông qua System Call để yêu cầu dịch vụ từ OS, và để OS thực hiện thay.

![System Call](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/system-call.png)

**Phân loại System Call theo chức năng:**

*   **Quản lý thiết bị**: Yêu cầu/giải phóng thiết bị, khởi động thiết bị.
*   **Quản lý file**: Đọc, ghi, tạo, xóa file.
*   **Quản lý tiến trình**: Tạo, hủy, chặn, đánh thức tiến trình, giao tiếp giữa tiến trình.
*   **Quản lý bộ nhớ**: Phân bổ, thu hồi bộ nhớ, lấy thông tin về vùng nhớ của tiến trình.

### 3.2. Quy trình System Call

1.  Chương trình User Mode phát động System Call. Vì System Call liên quan đến lệnh đặc quyền, chương trình User Mode không có quyền, nên sẽ bị ngắt (Trap).
2.  Sau khi ngắt, chương trình CPU đang chạy bị dừng, nhảy đến trình xử lý ngắt. Chương trình Kernel bắt đầu thực thi, xử lý System Call.
3.  Sau khi xử lý xong, OS dùng lệnh đặc quyền (như `iret`, `sysret`, `eret`) chuyển về User Mode, khôi phục ngữ cảnh User Mode, tiếp tục thực thi chương trình user.

---

## 4. Tiến trình và Luồng

### 4.1. Sự khác biệt giữa Tiến trình và Luồng

**Tiến trình (Process)** giống như một **nhà máy**. OS phân bổ tài nguyên theo đơn vị tiến trình. Khi bạn khởi động WeChat, OS xây dựng một nhà máy độc lập cho nó, phân bổ không gian bộ nhớ riêng, file handle v.v. Nhà máy này cách ly với các nhà máy khác (như trình duyệt bạn mở).

**Luồng (Thread)** giống như **công nhân trong nhà máy**. Một nhà máy có thể có nhiều công nhân, họ chia sẻ tài nguyên của nhà máy, nhưng mỗi công nhân có hộp công cụ và danh sách công việc riêng, cho phép họ thực hiện các task khác nhau một cách độc lập. Ví dụ, nhà máy WeChat có thể có một công nhân (luồng) nhận tin nhắn, một công nhân render giao diện.

![Process vs Thread](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/process-and-thread-difference-wechat-factory-as-an-example.png)

**3 điểm khác biệt cốt lõi:**

1.  **Quyền sở hữu tài nguyên**: Tiến trình là đơn vị cơ bản để phân bổ tài nguyên, sở hữu không gian địa chỉ độc lập. Luồng là đơn vị cơ bản để lập lịch CPU, gần như không sở hữu tài nguyên hệ thống, chỉ giữ lại một ít dữ liệu riêng tư (PC, stack, thanh ghi), chủ yếu chia sẻ tài nguyên của tiến trình chứa nó.

2.  **Chi phí**: Tạo/hủy một tiến trình có chi phí lớn, cần phân bổ tài nguyên độc lập. Tạo/hủy một luồng có chi phí nhỏ hơn nhiều. Tương tự, context switch giữa tiến trình tốn kém hơn context switch giữa luồng.

3.  **Tính ổn định**: Các tiến trình cách ly với nhau, một tiến trình crash không ảnh hưởng tiến trình khác. Nhưng các luồng trong một tiến trình chia sẻ tài nguyên, một luồng thao tác sai (truy cập bộ nhớ không hợp lệ) có thể làm sập toàn bộ tiến trình.

### 4.2. Tại sao cần Luồng (có Tiến trình rồi)?

Lý do cốt lõi là **để thực hiện xử lý song song với chi phí thấp, hiệu suất cao trong một ứng dụng**. Nếu muốn WeChat vừa nhận tin nhắn vừa gửi file, dùng 2 tiến trình sẽ tốn tài nguyên lớn và giao tiếp giữa chúng rất phức tạp (cần IPC). Dùng 2 luồng, chi phí chuyển đổi thấp, có thể giao tiếp hiệu quả qua shared memory, tận dụng tốt hơn CPU đa nhân.

### 4.3. Các phương pháp Đồng bộ hóa Luồng

1.  **Mutex (Mutex Lock)**: Dùng cơ chế đối tượng mutex, chỉ luồng sở hữu mutex mới có quyền truy cập tài nguyên công cộng. Vì mutex chỉ có một, đảm bảo tài nguyên không bị nhiều luồng truy cập đồng thời. Ví dụ: `synchronized` và các `Lock` trong Java.

2.  **Read-Write Lock (Khóa đọc-ghi)**: Cho phép nhiều luồng đồng thời đọc tài nguyên chia sẻ, nhưng chỉ một luồng có thể ghi.

3.  **Semaphore (Cờ hiệu)**: Cho phép nhiều luồng truy cập cùng tài nguyên đồng thời, nhưng cần kiểm soát số lượng tối đa luồng truy cập.

4.  **Barrier (Rào cản)**: Dùng để đợi nhiều luồng đạt đến một điểm nào đó rồi mới tiếp tục thực thi cùng nhau. Ví dụ: `CyclicBarrier` trong Java.

5.  **Event (Wait/Notify)**: Giữ đồng bộ các luồng thông qua thao tác thông báo, có thể triển khai so sánh ưu tiên giữa các luồng.

### 4.4. PCB (Process Control Block) là gì?

PCB là cấu trúc dữ liệu được OS sử dụng để quản lý và theo dõi tiến trình. Mỗi tiến trình có một PCB tương ứng duy nhất. PCB giống như bộ não của tiến trình.

**PCB bao gồm:**

*   Thông tin mô tả tiến trình: tên, ID v.v.
*   Thông tin lập lịch: lý do bị chặn, trạng thái (ready, running, blocked), độ ưu tiên v.v.
*   Nhu cầu tài nguyên: thời gian CPU, không gian bộ nhớ, thiết bị I/O v.v.
*   Thông tin file đã mở: file descriptor, loại file, chế độ mở v.v.
*   Thông tin trạng thái CPU: thanh ghi, bộ đếm chương trình, stack pointer v.v.

### 4.5. Các Trạng thái của Tiến trình

Tiến trình có 5 trạng thái chính:

1.  **Created (New)**: Tiến trình đang được tạo, chưa đến trạng thái Ready.
2.  **Ready**: Tiến trình đã có mọi tài nguyên cần thiết trừ CPU, sẵn sàng chạy ngay khi được cấp time slice.
3.  **Running**: Tiến trình đang chạy trên CPU (CPU đơn nhân chỉ có một tiến trình Running tại bất kỳ thời điểm nào).
4.  **Blocked (Waiting)**: Tiến trình đang đợi một sự kiện nào đó (tài nguyên, I/O hoàn thành). Dù CPU rảnh, tiến trình này cũng không thể chạy.
5.  **Terminated**: Tiến trình đang thoát khỏi hệ thống (kết thúc bình thường hoặc bị ngắt).

![Sơ đồ chuyển trạng thái tiến trình](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/state-transition-of-process.png)

### 4.6. Các phương thức Giao tiếp Liên tiến trình (IPC)

1.  **Pipe (Ống dẫn)**: Dùng cho tiến trình có quan hệ cha-con hoặc anh-em.
2.  **Named Pipe (Ống dẫn có tên)**: Khắc phục hạn chế của anonymous pipe, có thể giao tiếp giữa hai tiến trình bất kỳ trên cùng máy. Tuân thủ nguyên tắc FIFO.
3.  **Signal (Tín hiệu)**: Dùng để thông báo cho tiến trình nhận rằng một sự kiện đã xảy ra.
4.  **Message Queue (Hàng đợi tin nhắn)**: Danh sách liên kết tin nhắn có định dạng cụ thể, lưu trong kernel. Cho phép truy vấn tin nhắn ngẫu nhiên.
5.  **Semaphore (Cờ hiệu)**: Bộ đếm dùng để đồng bộ truy cập dữ liệu chia sẻ giữa nhiều tiến trình, tránh race condition.
6.  **Shared Memory (Bộ nhớ chia sẻ)**: Cho phép nhiều tiến trình truy cập cùng một vùng bộ nhớ, cần cơ chế đồng bộ như mutex, semaphore. Phương pháp hiệu quả nhất.
7.  **Socket**: Giao tiếp qua mạng giữa client và server, hoặc giao tiếp không qua mạng trên cùng máy. Dựa trên TCP/IP.

### 4.7. Các Thuật toán Lập lịch Tiến trình

![Các thuật toán lập lịch tiến trình](https://oss.javaguide.cn/github/javaguide/cs-basics/network/scheduling-algorithms-of-process.png)

Mục tiêu cốt lõi của thuật toán lập lịch là quyết định tiến trình nào trong hàng đợi ready sẽ được cấp CPU, cân bằng giữa throughput, turnaround time, response time và fairness.

#### Lập lịch Không chiếm quyền (Non-Preemptive)

1.  **FCFS (First-Come First-Served)**: Đơn giản nhất, ai đến trước thì được phục vụ trước. Ưu điểm: công bằng, dễ triển khai. Nhược điểm: nếu một công việc dài đến trước, các công việc ngắn phía sau phải chờ rất lâu ("hiệu ứng đoàn xe").

2.  **SJF (Shortest Job First)**: Chọn tiến trình có thời gian thực thi ước tính ngắn nhất. Lý thuyết, thời gian chờ trung bình là ngắn nhất. Nhược điểm: khó dự đoán thời gian chạy, công việc dài có thể "chết đói" mãi không được chạy.

#### Lập lịch Chiếm quyền (Preemptive)

1.  **RR (Round-Robin)**: Thuật toán công bằng nhất. Mỗi tiến trình được cấp một time slice cố định, dùng hết thì đưa về cuối hàng đợi. Phù hợp cho hệ thống time-sharing. Time slice quá dài thì giống FCFS, quá ngắn thì context switch quá nhiều.

2.  **Priority Scheduling**: Mỗi tiến trình có một độ ưu tiên, luôn chọn tiến trình có độ ưu tiên cao nhất. Linh hoạt nhưng có thể gây "chết đói" cho tiến trình độ ưu tiên thấp.

3.  **MFQ (Multi-level Feedback Queue)**: Phổ biến nhất trong thực tế. Kết hợp RR và Priority. Có nhiều hàng đợi với độ ưu tiên khác nhau, time slice khác nhau. Tiến trình mới vào hàng đợi ưu tiên cao nhất; nếu không hoàn thành trong time slice, bị hạ cấp xuống hàng đợi thấp hơn. Cân bằng giữa công việc ngắn và công việc dài.

---

## 5. Deadlock (Bế tắc)

### 5.1. Deadlock là gì?

Deadlock mô tả tình huống nhiều tiến trình/luồng đồng thời bị chặn, mỗi tiến trình đang đợi tài nguyên do tiến trình khác nắm giữ, không ai chịu nhả.

**Ví dụ "khóa chéo":**
*   Luồng 1 lấy được Lock A, rồi cố lấy Lock B.
*   Gần như đồng thời, Luồng 2 lấy được Lock B, rồi cố lấy Lock A.
*   Luồng 1 đợi Luồng 2 nhả Lock B, Luồng 2 đợi Luồng 1 nhả Lock A → Bế tắc!

### 5.2. Bốn Điều kiện Cần để xảy ra Deadlock

Deadlock cần **đồng thời thỏa mãn cả 4 điều kiện** sau:

1.  **Mutual Exclusion (Loại trừ lẫn nhau)**: Tài nguyên phải ở chế độ không chia sẻ, tức mỗi lần chỉ một tiến trình có thể sử dụng.
2.  **Hold and Wait (Giữ và Chờ)**: Một tiến trình chiếm ít nhất một tài nguyên và đang đợi tài nguyên khác do tiến trình khác nắm giữ.
3.  **No Preemption (Không chiếm quyền)**: Tài nguyên không thể bị cưỡng đoạt. Chỉ khi tiến trình đang giữ hoàn thành xong mới nhả tài nguyên.
4.  **Circular Wait (Chờ vòng tròn)**: Tồn tại tập hợp {P0, P1,..., Pn}, trong đó P0 đợi tài nguyên của P1, P1 đợi tài nguyên của P2,..., Pn đợi tài nguyên của P0.

### 5.3. Ví dụ Code Java mô phỏng Deadlock

```java
public class DeadLockDemo {
    private static Object resource1 = new Object(); // Tài nguyên 1
    private static Object resource2 = new Object(); // Tài nguyên 2

    public static void main(String[] args) {
        new Thread(() -> {
            synchronized (resource1) {
                System.out.println(Thread.currentThread() + " lấy resource1");
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println(Thread.currentThread() + " đợi lấy resource2");
                synchronized (resource2) {
                    System.out.println(Thread.currentThread() + " lấy resource2");
                }
            }
        }, "Luồng 1").start();

        new Thread(() -> {
            synchronized (resource2) {
                System.out.println(Thread.currentThread() + " lấy resource2");
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println(Thread.currentThread() + " đợi lấy resource1");
                synchronized (resource1) {
                    System.out.println(Thread.currentThread() + " lấy resource1");
                }
            }
        }, "Luồng 2").start();
    }
}
```

**Output:**
```
Thread[Luồng 1,5,main] lấy resource1
Thread[Luồng 2,5,main] lấy resource2
Thread[Luồng 1,5,main] đợi lấy resource2
Thread[Luồng 2,5,main] đợi lấy resource1
```

### 5.4. Các phương pháp Giải quyết Deadlock

1.  **Phòng ngừa Deadlock (Prevention)**: Phá vỡ một trong 4 điều kiện cần. Phổ biến nhất là **phá vỡ Circular Wait** bằng cách quy định tất cả luồng phải lấy khóa **theo cùng một thứ tự** (ví dụ luôn lấy A trước B).

2.  **Tránh Deadlock (Avoidance)**: Dự đoán trước khi phân bổ tài nguyên. **Thuật toán Banker** của Dijkstra: trước khi phân bổ, thử nghiệm xem việc phân bổ này có dẫn đến trạng thái không an toàn (có thể deadlock) không. Nếu có, từ chối phân bổ.

3.  **Phát hiện và Giải quyết Deadlock (Detection & Recovery)**: Cho phép deadlock xảy ra, nhưng có một luồng/cơ chế nền định kỳ kiểm tra xem có tồn tại vòng tròn đợi không (phân tích đồ thị chờ luồng). Nếu phát hiện, cưỡng chế thu hồi tài nguyên của một luồng hoặc kết thúc luồng đó. Database thường dùng cách này.

---

## 6. Quản lý Bộ nhớ

### 6.1. Các nhiệm vụ chính của Quản lý Bộ nhớ

*   **Phân bổ và thu hồi bộ nhớ**: `malloc()` cấp phát, `free()` giải phóng.
*   **Dịch địa chỉ**: Chuyển đổi địa chỉ ảo (virtual address) trong chương trình thành địa chỉ vật lý (physical address) trong bộ nhớ.
*   **Mở rộng bộ nhớ**: Khi bộ nhớ không đủ, dùng Virtual Memory để mở rộng logic.
*   **Ánh xạ bộ nhớ**: Ánh xạ file trực tiếp vào không gian tiến trình để đọc/ghi nhanh hơn.
*   **Bảo mật bộ nhớ**: Đảm bảo các tiến trình không xâm phạm bộ nhớ của nhau.

### 6.2. Memory Fragmentation (Phân mảnh Bộ nhớ)

*   **Internal Fragmentation (Phân mảnh Nội)**: Bộ nhớ đã phân bổ cho tiến trình nhưng không được sử dụng. Ví dụ: tiến trình cần 65 byte nhưng được cấp 128 byte → 63 byte lãng phí.

*   **External Fragmentation (Phân mảnh Ngoại)**: Các vùng nhớ chưa phân bổ nhưng quá nhỏ, rải rác, không thể thỏa mãn yêu cầu của bất kỳ tiến trình nào.

![Memory Fragmentation](https://oss.javaguide.cn/github/javaguide/cs-basics/operating-system/internal-and-external-fragmentation.png)

### 6.3. Các phương pháp Quản lý Bộ nhớ

**Quản lý Bộ nhớ Liên tục:**
*   **Buddy System**: Chia bộ nhớ theo lũy thừa 2, kết hợp các khối kề nhau thành cặp "buddy". Khi phân bổ, tìm khối vừa đủ; nếu quá lớn, chia đôi. Khi giải phóng, nếu buddy cũng rảnh, hợp nhất lại. Giải quyết được phân mảnh ngoại, nhưng vẫn có phân mảnh nội.

**Quản lý Bộ nhớ Không liên tục:**
*   **Segmentation (Phân đoạn)**: Chia thành các segment có kích thước khác nhau, mỗi segment có ý nghĩa logic (code, data, stack). Dễ gây phân mảnh ngoại.
*   **Paging (Phân trang)**: Chia bộ nhớ thành các page có kích thước cố định bằng nhau (thường 4KB). Tránh được phân mảnh ngoại, là phương pháp phổ biến nhất của OS hiện đại.
*   **Segmented Paging**: Kết hợp cả hai.

---

## 7. Bộ nhớ Ảo (Virtual Memory)

### 7.1. Virtual Memory là gì?

Virtual Memory là kỹ thuật quan trọng, về bản chất chỉ tồn tại logic, là một không gian bộ nhớ tưởng tượng, làm cầu nối cho tiến trình truy cập bộ nhớ vật lý và đơn giản hóa quản lý bộ nhớ.

**Các khả năng của Virtual Memory:**

*   **Cách ly tiến trình**: Mỗi tiến trình có không gian địa chỉ ảo riêng, nghĩ rằng mình sở hữu toàn bộ bộ nhớ vật lý. Code của tiến trình này không thể thay đổi bộ nhớ của tiến trình khác.
*   **Nâng cao hiệu suất sử dụng bộ nhớ vật lý**: Chỉ cần load phần dữ liệu/lệnh đang sử dụng vào bộ nhớ vật lý (theo nguyên lý locality).
*   **Đơn giản hóa quản lý bộ nhớ**: Lập trình viên không cần làm việc trực tiếp với bộ nhớ vật lý.
*   **Chia sẻ bộ nhớ giữa nhiều tiến trình**: Các thư viện động dùng chung thực tế chỉ load một lần vào bộ nhớ.
*   **Tăng bảo mật**: Kiểm soát quyền truy cập của tiến trình vào bộ nhớ vật lý.
*   **Mở rộng không gian bộ nhớ**: Khi bộ nhớ vật lý không đủ, dùng đĩa cứng làm swap space.

### 7.2. Địa chỉ Ảo và Địa chỉ Vật lý

*   **Physical Address**: Địa chỉ thực trong bộ nhớ vật lý (trong thanh ghi địa chỉ bộ nhớ).
*   **Virtual Address**: Địa chỉ mà chương trình truy cập (ví dụ: con trỏ trong C).

**MMU (Memory Management Unit)** trong CPU chuyển đổi Virtual Address thành Physical Address, quá trình này gọi là **Address Translation**.

### 7.3. Cơ chế Phân trang (Paging)

Phân trang chia bộ nhớ vật lý thành các **physical page** có kích thước bằng nhau (thường 4KB), và không gian địa chỉ ảo thành các **virtual page** tương ứng.

**Page Table (Bảng Trang):** Ánh xạ virtual page number → physical page number.

**Địa chỉ ảo gồm:**
*   **Page Number (Số trang ảo)**: Dùng để truy vấn Page Table, lấy Physical Page Number.
*   **Page Offset (Độ lệch trong trang)**: Cộng với địa chỉ bắt đầu của Physical Page để có địa chỉ vật lý cuối cùng.

**Quy trình dịch địa chỉ:**
1.  MMU lấy Virtual Page Number từ địa chỉ ảo.
2.  Tìm trong Page Table của tiến trình để lấy Physical Page Number.
3.  Physical Page Address + Page Offset = Physical Address.

### 7.4. TLB (Translation Lookaside Buffer)

TLB là **bộ nhớ đệm tốc độ cao** trong MMU, lưu ánh xạ virtual page → physical page (như hash table).

**Quy trình với TLB:**
1.  Dùng virtual page number làm key tra TLB.
2.  **TLB hit**: Tìm thấy → không cần tra Page Table trong RAM.
3.  **TLB miss**: Không tìm thấy → tra Page Table trong RAM, đồng thời thêm mapping vào TLB.
4.  Khi TLB đầy, áp dụng thuật toán loại bỏ (eviction policy).

### 7.5. Page Fault (Lỗi Trang)

Page Fault xảy ra khi truy cập địa chỉ ảo đã được map nhưng **chưa được load vào bộ nhớ vật lý** hoặc **chưa có mapping trong Page Table**.

*   **Hard Page Fault**: Không có physical page tương ứng trong RAM → Page Fault Handler đọc dữ liệu từ đĩa vào RAM, rồi tạo mapping.
*   **Soft Page Fault**: Có physical page trong RAM, nhưng chưa có mapping → Page Fault Handler tạo mapping.

### 7.6. Các Thuật toán Thay thế Trang (Page Replacement Algorithms)

Khi Hard Page Fault xảy ra mà không còn physical page trống, OS phải **swap out** một trang để lấy chỗ cho trang mới.

1.  **OPT (Optimal)**: Loại bỏ trang sẽ không bao giờ được sử dụng hoặc lâu nhất mới được sử dụng trong tương lai. Lý thuyết tối ưu nhất nhưng không thể triển khai vì không thể dự đoán tương lai.

2.  **FIFO (First-In First-Out)**: Loại bỏ trang vào sớm nhất. Đơn giản nhưng hiệu suất không tốt, có thể xảy ra "Belady's anomaly".

3.  **LRU (Least Recently Used)**: Loại bỏ trang lâu nhất chưa được truy cập. Phổ biến nhất trong thực tế, gần với OPT nhất.

4.  **LFU (Least Frequently Used)**: Loại bỏ trang được truy cập ít lần nhất trong một khoảng thời gian.

5.  **Clock**: Dùng một bit tham chiếu (reference bit), quét vòng tròn như kim đồng hồ.

---

## 8. Hệ thống Tập tin (File System)

### 8.1. Các chức năng chính của File System

1.  **Quản lý lưu trữ**: Lưu dữ liệu file vào thiết bị lưu trữ, quản lý phân bổ không gian.
2.  **Quản lý file**: Tạo, xóa, di chuyển, đổi tên, nén, mã hóa, chia sẻ file.
3.  **Quản lý thư mục**: Tạo, xóa, di chuyển, đổi tên thư mục.
4.  **Kiểm soát truy cập file**: Quản lý quyền truy cập của user/process vào file.

### 8.2. Hard Link vs Soft Link

**Hard Link (Liên kết cứng):**
*   Liên kết thông qua **inode number**. Hard link và file gốc có **cùng inode**.
*   Xóa file gốc **không ảnh hưởng** hard link (và ngược lại). File chỉ bị xóa thực sự khi cả file gốc và tất cả hard link đều bị xóa.
*   **Không thể** tạo hard link cho thư mục hoặc file không tồn tại.
*   **Không thể** xuyên file system (vì mỗi file system có bảng inode riêng).
*   Lệnh: `ln source_file hard_link_file`

**Soft Link (Liên kết mềm / Symbolic Link):**
*   Liên kết thông qua **đường dẫn file**. Soft link và file gốc có **inode khác nhau**.
*   Xóa file gốc, soft link **vẫn tồn tại** nhưng trỏ đến đường dẫn không hợp lệ.
*   Giống **shortcut** trên Windows.
*   **Có thể** tạo cho thư mục hoặc file không tồn tại.
*   **Có thể** xuyên file system.
*   Lệnh: `ln -s source_file soft_link_file`

### 8.3. Các Thuật toán Lập lịch Đĩa

1.  **FCFS**: Xử lý yêu cầu theo thứ tự đến. Đơn giản nhưng seek time trung bình cao, có thể gây "đói".
2.  **SSTF (Shortest Seek Time First)**: Chọn yêu cầu gần đầu đọc nhất. Tối thiểu seek time nhưng có thể gây "đói" cho yêu cầu xa.
3.  **SCAN (Elevator)**: Đầu đọc di chuyển một hướng, xử lý mọi yêu cầu trên đường đi, đến biên thì đổi hướng.
4.  **C-SCAN**: Biến thể của SCAN, chỉ quét một chiều, đến biên thì quay về đầu.
5.  **LOOK**: Cải tiến SCAN, nếu không còn yêu cầu phía trước thì đổi hướng ngay (không cần đi đến biên).
6.  **C-LOOK**: Cải tiến C-SCAN, nếu không còn yêu cầu phía trước thì quay về vị trí có yêu cầu (không cần về đầu).

---

## 9. Linux Cơ bản

### 9.1. Giới thiệu Linux

*   **Hệ điều hành họ Unix**: Linux là hệ điều hành mã nguồn mở, miễn phí, tương tự Unix.
*   **Linux = Linux Kernel**: Nghiêm ngặt mà nói, Linux chỉ là nhân. Các bản phân phối (distribution) kết hợp kernel với phần mềm, tài liệu để tạo thành OS hoàn chỉnh.
*   **Tác giả**: Linus Torvalds (1991), người cũng tạo ra Git.

**Các bản phân phối phổ biến:**
*   **RHEL (Red Hat Enterprise Linux)**: Thương mại, dành cho doanh nghiệp.
*   **CentOS**: Dựa trên RHEL, miễn phí, ổn định, phổ biến cho server.
*   **Ubuntu**: Dựa trên Debian, thân thiện người dùng, phổ biến cho desktop.

### 9.2. Triết lý "Everything is a File"

Trong Linux, mọi thứ (thiết bị mạng, ổ đĩa, máy in, file thông thường, thư mục) đều được coi là **file**. Thiết kế này đến từ triết lý Unix, giúp quản lý và thao tác các tài nguyên khác nhau bằng một giao diện file thống nhất.

### 9.3. inode và Block

*   **inode**: Lưu metadata của file (quyền truy cập, kích thước, thời gian sửa đổi, con trỏ đến data block). Mỗi file có một inode duy nhất.
*   **block**: Lưu nội dung thực của file. Nếu file lớn hơn một block, sẽ chiếm nhiều block. Một block chỉ chứa dữ liệu của một file.

### 9.4. Cây Thư mục Linux

```
/           → Thư mục gốc
├── bin     → Binary (lệnh cơ bản: ls, cat, mkdir)
├── etc     → Cấu hình hệ thống
├── home    → Thư mục chính của user
├── usr     → Ứng dụng hệ thống
├── opt     → Ứng dụng bổ sung (Tomcat, v.v.)
├── var     → Dữ liệu biến đổi (log, cache)
├── tmp     → File tạm
├── root    → Thư mục chính của root user
├── dev     → File thiết bị
├── proc    → Thông tin tiến trình (virtual file system)
└── boot    → File khởi động hệ thống
```

### 9.5. Các Lệnh Linux Thường dùng

#### Điều hướng Thư mục
```bash
cd /path         # Chuyển đến thư mục
cd ..            # Lên thư mục cha
cd ~             # Về thư mục home
cd -             # Về thư mục trước đó
pwd              # Hiển thị đường dẫn hiện tại
```

#### Thao tác File/Thư mục
```bash
ls -la           # Liệt kê chi tiết
mkdir -p dir     # Tạo thư mục (cả cha)
rm -r dir        # Xóa đệ quy
cp -r src dst    # Copy đệ quy
mv src dst       # Di chuyển/đổi tên
touch file       # Tạo file rỗng
cat file         # Xem nội dung file
less file        # Xem file (cuộn được)
tail -f file     # Theo dõi file real-time
vim file         # Chỉnh sửa file
```

#### Nén/Giải nén
```bash
tar -zcvf archive.tar.gz files/   # Nén
tar -xvf archive.tar.gz -C /dest  # Giải nén
```

#### Quyền File
```bash
chmod 755 file     # rwxr-xr-x
chmod u+x file     # Thêm quyền thực thi cho owner
chown user:group file  # Đổi chủ sở hữu
```

#### Quản lý User
```bash
useradd username   # Tạo user
userdel username   # Xóa user
passwd username    # Đặt mật khẩu
su - username      # Chuyển user
```

#### Trạng thái Hệ thống
```bash
top / htop         # Xem CPU, RAM, tiến trình real-time
df -h              # Dung lượng đĩa
free -h            # Dung lượng RAM
ps aux | grep java # Tìm tiến trình Java
kill -9 PID        # Kết thúc tiến trình
```

#### Mạng
```bash
ping host          # Test kết nối
ifconfig / ip a    # Xem IP
netstat -tulpn     # Xem port đang lắng nghe
ss -tulpn          # (thay thế netstat)
```

---

*Kết thúc Phần 1.3: Hệ Điều hành*

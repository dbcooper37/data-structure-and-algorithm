# Phần 2: Java Core Chi tiết (Comprehensive Java Core)

Tài liệu này là bản dịch và biên soạn chi tiết từ nguồn JavaGuide, bao gồm đầy đủ các khái niệm cơ bản Java, Collections, Concurrency, IO/NIO, JVM và New Features.

---

## 2.1. Java Cơ bản (Java Basics)

### 2.1.1. Khái niệm Cơ bản và Kiến thức Thường thức

#### Ngôn ngữ Java có những đặc điểm gì?

1. **Đơn giản, dễ học**: Cú pháp đơn giản, dễ tiếp cận
2. **Hướng đối tượng** (OOP): Đóng gói (Encapsulation), Kế thừa (Inheritance), Đa hình (Polymorphism)
3. **Độc lập nền tảng**: Nhờ Java Virtual Machine (JVM)
4. **Hỗ trợ đa luồng**: Java có cơ chế đa luồng tích hợp sẵn
5. **Tin cậy**: Xử lý ngoại lệ và quản lý bộ nhớ tự động
6. **Bảo mật**: Modifier truy cập, giới hạn truy cập trực tiếp OS
7. **Hiệu suất cao**: JIT compiler tối ưu hóa runtime
8. **Hỗ trợ lập trình mạng**: API mạng phong phú và dễ sử dụng
9. **Biên dịch và Thông dịch song hành**

> **"Write Once, Run Anywhere"** - Khẩu hiệu kinh điển của Java! Tuy nhiên, ngày nay, lợi thế lớn nhất của Java không còn là tính đa nền tảng, mà là **hệ sinh thái mạnh mẽ**.

#### Java SE vs Java EE

*   **Java SE** (Standard Edition): Phiên bản chuẩn, bao gồm core class libraries và JVM. Phù hợp cho ứng dụng desktop hoặc server đơn giản.
*   **Java EE** (Enterprise Edition): Phiên bản doanh nghiệp, xây dựng trên Java SE, bổ sung

 các tiêu chuẩn cho ứng dụng phân tán (Servlet, JSP, EJB, JDBC, JPA, JTA, JavaMail, JMS). Phù hợp cho Web app và hệ thống enterprise phức tạp.
*   **Java ME** (Micro Edition): Phiên bản nhỏ gọn cho thiết bị nhúng (điện thoại, PDA, tủ lạnh). Hiện đã ít được sử dụng.

#### ⭐ JVM vs JDK vs JRE

**JVM (Java Virtual Machine)**

JVM là máy ảo chạy bytecode Java. JVM có triển khai riêng cho từng hệ điều hành (Windows, Linux, macOS), nhưng tất cả đều chạy cùng một bytecode `.class`, đảm bảo "**một lần biên dịch, chạy mọi nơi**".

![Running on JVM](https://oss.javaguide.cn/github/javaguide/java/basis/java-virtual-machine-program-language-os.png)

**JVM không chỉ có một loại!** Miễn tuân thủ JVM specification, ai cũng có thể phát triển JVM riêng. Phổ biến nhất là **HotSpot VM**. Ngoài ra còn có J9 VM, Zing VM, JRockit VM, v.v.

**JDK (Java Development Kit)**

JDK là bộ công cụ phát triển Java đầy đủ, bao gồm:
*   JRE (để chạy chương trình Java)
*   Compiler `javac`
*   Các công cụ: `javadoc` (tạo tài liệu), `jdb` (debugger), `jconsole` (monitoring), `javap` (disassembler)

**JRE (Java Runtime Environment)**

JRE là môi trường để **chạy** chương trình Java đã biên dịch, bao gồm:
1.  **JVM**: Máy ảo Java
2.  **Class Library**: Thư viện class chuẩn (I/O, networking, data structures, v.v.)

**Quan hệ giữa JDK, JRE, JVM:**

![JDK include JRE](https://oss.javaguide.cn/github/javaguide/java/basis/jdk-include-jre.png)

**Lưu ý**: Từ JDK 9, không cần phân biệt JDK và JRE nữa. JDK được tổ chức lại thành 94 modules và dùng công cụ **jlink** để tạo custom runtime chỉ chứa các module cần thiết. Từ JDK 11, Oracle không còn cung cấp JRE riêng.

#### ⭐ Bytecode là gì? Lợi ích của việc dùng Bytecode?

**Bytecode** là code mà JVM có thể hiểu được (file `.class`). Bytecode không phụ thuộc vào bất kỳ processor cụ thể nào, chỉ hướng đến JVM.

**Lợi ích:**
*   **Hiệu suất tốt hơn ngôn ngữ thông dịch thuần túy**: Java tránh được vấn đề hiệu suất thấp của ngôn ngữ thông dịch truyền thống.
*   **Tính di động**: Bytecode không cần biên dịch lại khi chạy trên hệ điều hành khác, miễn có JVM.

**Quy trình từ Source Code đến Machine Code:**

![Java code to machine code](https://oss.javaguide.cn/github/javaguide/java/basis/java-code-to-machine-code.png)

1.  `.java` → **javac** → `.class` (bytecode)
2.  `.class` → **Class Loader** → load vào JVM
3.  JVM **Interpreter** thông dịch từng dòng bytecode
4.  **JIT Compiler** biên dịch **hot code** (code chạy nhiều lần) thành machine code, lưu lại để tái sử dụng

![Java code to machine code with JIT](https://oss.javaguide.cn/github/javaguide/java/basis/java-code-to-machine-code-with-jit.png)

**Quan hệ JDK, JRE, JVM, JIT:**

![JDK JRE JVM JIT](https://oss.javaguide.cn/github/javaguide/java/basis/jdk-jre-jvm-jit.png)

#### ⭐ Tại sao Java là "Biên dịch và Thông dịch Song hành"?

Có thể phân loại ngôn ngữ lập trình theo cách thực thi:

*   **Compiled (Biên dịch)**: Compiler biên dịch toàn bộ source code thành machine code một lần. Ví dụ: C, C++, Go, Rust. Ưu điểm: nhanh. Nhược điểm: phát triển chậm hơn.
*   **Interpreted (Thông dịch)**: Interpreter thông dịch từng câu lệnh thành machine code rồi chạy. Ví dụ: Python, JavaScript, PHP. Ưu điểm: phát triển nhanh. Nhược điểm: chậm hơn.

![Compiled vs Interpreted](https://oss.javaguide.cn/github/javaguide/java/basis/compiled-and-interpreted-languages.png)

**Java kết hợp cả hai:**
1.  **Biên dịch**: `javac` biên dịch `.java` → `.class` (bytecode)
2.  **Thông dịch**: JVM interpreter thông dịch bytecode
3.  **JIT**: Biên dịch hot code thành machine code runtime

Vì vậy, Java vừa có tính di động của ngôn ngữ thông dịch, vừa có hiệu suất tốt nhờ JIT.

#### AOT có lợi ích gì? Tại sao không dùng toàn bộ AOT?

**AOT (Ahead-of-Time Compilation)** được giới thiệu trong JDK 9. Khác với JIT (biên dịch runtime), AOT biên dịch chương trình thành machine code **trước khi chạy** (static compilation như C, C++, Go, Rust).

**Ưu điểm của AOT:**
*   Tăng tốc khởi động (không cần warm-up)
*   Giảm memory footprint
*   Tăng bảo mật (code khó bị decompile)
*   Phù hợp cloud-native, microservices

**So sánh JIT vs AOT:**

| Chỉ tiêu | JIT | AOT |
|----------|-----|-----|
| Thời gian khởi động | Chậm (cần warm-up) | Nhanh |
| Memory | Nhiều hơn | Ít hơn |
| Kích thước package | Nhỏ hơn | Lớn hơn |
| Peak performance | Cao hơn | Thấp hơn |
| Latency tối đa | Cao hơn | Thấp hơn |

**Tại sao không dùng toàn AOT?**
*   AOT không hỗ trợ tốt các tính năng động của Java: **reflection, dynamic proxy, dynamic loading, JNI**.
*   Nhiều framework (Spring, CGLIB) phụ thuộc vào các tính năng động này.
*   Ví dụ: CGLIB dùng ASM để tạo bytecode `.class` trong memory runtime → AOT không thể làm điều này.

**GraalVM**: JDK hiệu suất cao, hỗ trợ cả AOT và JIT, chạy được Java và nhiều ngôn ngữ khác.

#### Oracle JDK vs OpenJDK

**Lịch sử:**
*   2006: SUN mở mã nguồn Java → OpenJDK
*   2009: Oracle mua SUN, phát triển Oracle JDK dựa trên OpenJDK

**Sự khác biệt:**

1.  **Mã nguồn mở**: OpenJDK hoàn toàn mở. Oracle JDK không hoàn toàn mở.
2.  **Miễn phí**: OpenJDK miễn phí hoàn toàn. Oracle JDK có phiên bản miễn phí nhưng giới hạn thời gian (JDK 17+ chỉ miễn phí 3 năm).
3.  **Tính năng**: Oracle JDK trước đây có thêm công cụ riêng (Java Flight Recorder, Java Mission Control). Từ JDK 11, Oracle đã donate hầu hết cho OpenJDK, nên giờ tính năng gần như tương đương.
4.  **Stability**: Oracle JDK cung cấp LTS (Long-Term Support). OpenJDK không có LTS chính thức, nhưng nhiều vendor (Amazon Corretto, Alibaba Dragonwell) cung cấp LTS cho OpenJDK.
5.  **License**: Oracle JDK dùng BCL/OTN. OpenJDK dùng GPL v2.

**Nên chọn loại nào?**

Khuyến nghị dùng **OpenJDK** hoặc bản phân phối dựa trên OpenJDK như **Amazon Corretto**, **Alibaba Dragonwell**, **Azul Zulu**.

#### Java vs C++

Java và C++ đều là ngôn ngữ hướng đối tượng, đều hỗ trợ đóng gói, kế thừa, đa hình. Nhưng có nhiều điểm khác biệt:

*   **Con trỏ**: Java không cung cấp con trỏ truy cập trực tiếp bộ nhớ → an toàn hơn.
*   **Đa kế thừa**: C++ hỗ trợ đa kế thừa class. Java không (class chỉ kế thừa 1 class, nhưng interface có thể đa kế thừa).
*   **Quản lý bộ nhớ**: Java có **Garbage Collection (GC)** tự động. C++ phải tự quản lý (`new`/`delete`).
*   **Operator overloading**: C++ hỗ trợ. Java không hỗ trợ (vì tăng độ phức tạp).

---

### 2.1.2. Cú pháp Cơ bản (Basic Syntax)

#### Comment (Chú thích) có mấy dạng?

Java có 3 loại comment:

1.  **Single-line comment (`//`)**: Giải thích một dòng code
2.  **Multi-line comment (`/* */`)**: Giải thích một đoạn code
3.  **Documentation comment (`/** */`)**: Tạo tài liệu Java (Javadoc)

Ví dụ:
```java
// Đây là single-line comment

/*
Đây là
multi-line comment
*/

/**
 * Đây là documentation comment
 * @param args tham số dòng lệnh
 */
public static void main(String[] args) { }
```

**Lưu ý**: Theo cuốn **Clean Code**:
> Code tốt chính là chú thích. Nên viết code rõ ràng, tự giải thích, giảm thiểu comment không cần thiết.
>
> Ví dụ thay vì:
> ```java
> // check if employee is eligible for full benefits
> if ((employee.flags & HOURLY_FLAG) && (employee.age > 65))
> ```
> Nên viết:
> ```java
> if (employee.isEligibleForFullBenefits())
> ```

#### Identifier và Keyword khác nhau thế nào?

*   **Identifier (Định danh)**: Tên bạn đặt cho biến, lớp, phương thức, v.v.
*   **Keyword (Từ khóa)**: Identifier được Java gán ý nghĩa đặc biệt, chỉ dùng cho mục đích cụ thể.

Ví dụ: bạn mở cửa hàng, tên cửa hàng là identifier. Nhưng không thể đặt tên "Công An" vì đó là keyword.

#### Java có những Keyword nào?

| Phân loại | Keyword |  |  |  |  |  |  |
|-----------|---------|--|--|--|--|--|--|
| Kiểm soát truy cập | `private` | `protected` | `public` |  |  |  |  |
| Class, method, biến | `abstract` | `class` | `extends` | `final` | `implements` | `interface` | `native` |
|  | `new` | `static` | `strictfp` | `synchronized` | `transient` | `volatile` | `enum` |
| Điều khiển luồng | `break` | `continue` | `return` | `do` | `while` | `if` | `else` |
|  | `for` | `instanceof` | `switch` | `case` | `default` | `assert` |  |
| Xử lý lỗi | `try` | `catch` | `throw` | `throws` | `finally` |  |  |
| Package | `import` | `package` |  |  |  |  |  |
| Kiểu cơ bản | `boolean` | `byte` | `char` | `double` | `float` | `int` | `long` |
|  | `short` |  |  |  |  |  |  |
| Tham chiếu | `super` | `this` | `void` |  |  |  |  |
| Từ dự trữ | `goto` | `const` |  |  |  |  |  |

**Lưu ý**:
*   `default` vừa dùng trong `switch`, vừa là modifier (JDK 8+) để định nghĩa phương thức mặc định trong interface, vừa là access modifier mặc định (package-private).
*   `true`, `false`, `null` không phải keyword mà là **literal values**, nhưng cũng không thể dùng làm identifier.

#### ⭐ Toán tử Tự tăng/Tự giảm (`++` / `--`)

*   **Prefix** (`++a`, `--a`): Tăng/giảm trước, rồi dùng giá trị mới.
*   **Postfix** (`a++`, `a--`): Dùng giá trị hiện tại trước, rồi mới tăng/giảm.

**Công thức ghi nhớ**: "Ký hiệu trước thì tăng/giảm trước, ký hiệu sau thì tăng/giảm sau."

**Bài tập**: Sau khi chạy đoạn code sau, `a`, `b`, `c`, `d`, `e` bằng bao nhiêu?
```java
int a = 9;
int b = a++;      // b = 9, a = 10
int c = ++a;      // a = 11, c = 11
int d = c--;      // d = 11, c = 10
int e = --d;      // d = 10, e = 10
```
Đáp án: `a=11`, `b=9`, `c=10`, `d=10`, `e=10`.

#### ⭐ Toán tử Dịch bit (Shift Operators)

Dịch bit là thao tác dịch chuyển các bit sang trái hoặc phải. Được sử dụng rộng rãi trong JDK và framework (ví dụ: `HashMap` JDK 1.8).

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

**Tại sao dùng Shift Operators?**
1.  **Hiệu quả**: Processor có lệnh phần cứng chuyên dụng cho dịch bit, thực thi trong 1 clock cycle. Nhanh hơn nhiều so với phép nhân/chia.
2.  **Tiết kiệm bộ nhớ**: Có thể lưu nhiều boolean trong 1 `int`/`long` bằng cách dùng bit flags.

**Ứng dụng:**
*   Nhân/chia nhanh với lũy thừa 2
*   Quản lý bit fields (flags)
*   Hash algorithms, encryption
*   Data compression (Huffman encoding)
*   Data checksums (CRC)
*   Memory alignment

**Java có 3 toán tử dịch bit:**

*   **`<<`** (Left shift): Dịch trái `n` bit. `x << n` ≈ `x * 2^n` (không tràn).
*   **`>>`** (Signed right shift): Dịch phải `n` bit, bit cao điền bằng **bit dấu** (0 nếu số dương, 1 nếu số âm). `x >> n` ≈ `x / 2^n`.
*   **`>>>`** (Unsigned right shift): Dịch phải `n` bit, bit cao luôn điền **0** (bỏ qua dấu).

**Lưu ý**:
*   `double`, `float` không thể dịch bit (biểu diễn đặc biệt).
*   `short`, `byte`, `char` sẽ được convert sang `int` trước khi dịch.
*   Nếu dịch ≥ 32 bit (int) hoặc ≥ 64 bit (long), sẽ lấy phần dư (`%`). Ví dụ: `x << 42` ≡ `x << 10` (42 % 32 = 10).

**Ví dụ Left Shift:**
```java
int i = -1;
System.out.println("Initial: " + i);
System.out.println("Binary: " + Integer.toBinaryString(i));
// 11111111111111111111111111111111
i <<= 10;
System.out.println("After left shift 10: " + i);
System.out.println("Binary: " + Integer.toBinaryString(i));
// 11111111111111111111110000000000
// Output: -1024
```

#### `continue`, `break`, `return` khác nhau thế nào?

*   **`continue`**: Bỏ qua vòng lặp hiện tại, tiếp tục vòng lặp tiếp theo.
*   **`break`**: Thoát khỏi toàn bộ vòng lặp, chạy tiếp code sau vòng lặp.
*   **`return`**: Thoát khỏi phương thức.
    *   `return;` - kết thúc phương thức `void`
    *   `return value;` - kết thúc phương thức có giá trị trả về

**Ví dụ:**
```java
public static void main(String[] args) {
    boolean flag = false;
    for (int i = 0; i <= 3; i++) {
        if (i == 0) {
            System.out.println("0");
        } else if (i == 1) {
            System.out.println("1");
            continue;  // Bỏ qua "xixi" ở dưới
        } else if (i == 2) {
            System.out.println("2");
            flag = true;
        } else if (i == 3) {
            System.out.println("3");
            break;  // Thoát vòng lặp, không chạy i=4
        }
        System.out.println("xixi");
    }
    if (flag) {
        System.out.println("haha");
        return;  // Thoát main, không in "heihei"
    }
    System.out.println("heihei");
}
```
Output:
```
0
xixi
1
2
xixi
3
haha
```

---

### 2.1.3. ⭐ Kiểu Dữ liệu Cơ bản (Primitive Data Types)

#### Java có mấy kiểu dữ liệu cơ bản?

Java có **8 kiểu cơ bản**:

*   **6 kiểu số**:
    *   4 kiểu nguyên: `byte`, `short`, `int`, `long`
    *   2 kiểu thực: `float`, `double`
*   **1 kiểu ký tự**: `char`
*   **1 kiểu logic**: `boolean`

| Kiểu | Bits | Bytes | Default | Phạm vi |
|------|------|-------|---------|---------|
| `byte` | 8 | 1 | 0 | -128 ~ 127 |
| `short` | 16 | 2 | 0 | -32,768 ~ 32,767 |
| `int` | 32 | 4 | 0 | -2,147,483,648 ~ 2,147,483,647 |
| `long` | 64 | 8 | 0L | -2^63 ~ 2^63-1 |
| `char` | 16 | 2 | '\u0000' | 0 ~ 65,535 |
| `float` | 32 | 4 | 0.0f | 1.4E-45 ~ 3.4028235E38 |
| `double` | 64 | 8 | 0.0d | 4.9E-324 ~ 1.7976931348623157E308 |
| `boolean` | 1 | - | false | `true`, `false` |

**Lưu ý:**
1.  Dùng `long` phải thêm hậu tố **L**: `long a = 123L;`
2.  Dùng `float` phải thêm hậu tố **f/F**: `float b = 1.5f;`
3.  `char` dùng **single quote**: `char c = 'A';`. `String` dùng **double quote**: `String s = "Hello";`
4.  Kích thước các kiểu cơ bản trong Java **không thay đổi** theo kiến trúc máy (khác C/C++) → tăng tính di động.

#### Wrapper Type (Kiểu Bọc) vs Primitive Type

Mỗi kiểu cơ bản có một wrapper class tương ứng: `Byte`, `Short`, `Integer`, `Long`, `Float`, `Double`, `Character`, `Boolean`.

**Sự khác biệt:**

| Tiêu chí | Primitive | Wrapper |
|----------|-----------|---------|
| **Mục đích sử dụng** | Biến cục bộ, hằng số | Tham số method, thuộc tính object, generic |
| **Lưu trữ** | Stack (biến cục bộ), Heap (biến thành viên) | Heap (như object) |
| **Kích thước** | Nhỏ | Lớn hơn (là object) |
| **Giá trị mặc định** | 0, false, '\u0000' | `null` |
| **So sánh** | `==` so sánh giá trị | `==` so sánh địa chỉ, dùng `.equals()` để so sánh giá trị |

**Tại sao "hầu hết" object trong heap?**

HotSpot VM có **JIT optimization** với **escape analysis**. Nếu object không escape ra ngoài phương thức, JVM có thể dùng **scalar replacement** để lưu object trên stack thay vì heap, tăng hiệu suất.

⚠️ **Lưu ý**: "Kiểu cơ bản lưu trên stack" là **quan niệm sai**! Vị trí lưu trữ phụ thuộc vào **scope**:
*   **Biến cục bộ**: stack
*   **Biến thành viên**: heap (hoặc method area/metaspace nếu static)

```java
public class Test {
    int a = 10;         // Heap
    static int b = 20;  // Method area / Metaspace (không phải heap)
    
    public void method() {
        int c = 30;     // Stack
        // static int d = 40; // COMPILE ERROR: không thể dùng static cho biến cục bộ
    }
}
```

#### Cơ chế Cache của Wrapper Class

Hầu hết wrapper class đều dùng cache để tăng hiệu suất:

*   `Byte`, `Short`, `Integer`, `Long`: cache **[-128, 127]**
*   `Character`: cache **[0, 127]**
*   `Boolean`: cache `TRUE` và `FALSE`
*   `Float`, `Double`: **không có cache**

Với `Integer`, có thể dùng JVM param `-XX:AutoBoxCacheMax=<size>` để thay đổi **upper bound** (không thể đổi lower bound -128).

**Integer cache source code:**
```java
public static Integer valueOf(int i) {
    if (i >= IntegerCache.low && i <= IntegerCache.high)
        return IntegerCache.cache[i + (-IntegerCache.low)];
    return new Integer(i);
}
```

**Ví dụ:**
```java
Integer i1 = 33;
Integer i2 = 33;
System.out.println(i1 == i2);  // true (trong cache)

Float f1 = 333f;
Float f2 = 333f;
System.out.println(f1 == f2);  // false (không có cache)

Integer i3 = 40;
Integer i4 = new Integer(40);
System.out.println(i3 == i4);  // false (i3 dùng cache, i4 tạo object mới)
```

**Kết luận**: **Luôn dùng `.equals()` để so sánh wrapper type!**

#### Autoboxing và Unboxing

*   **Autoboxing**: Chuyển kiểu cơ bản → wrapper type
*   **Unboxing**: Chuyển wrapper type → kiểu cơ bản

```java
Integer i = 10;  // Autoboxing: Integer.valueOf(10)
int n = i;       // Unboxing: i.intValue()
```

**Bytecode tương ứng:**
```
INVOKESTATIC java/lang/Integer.valueOf (I)Ljava/lang/Integer;
INVOKEVIRTUAL java/lang/Integer.intValue ()I
```

⚠️ **Lưu ý**: Tránh boxing/unboxing không cần thiết vì ảnh hưởng hiệu suất!

```java
// SAI: dùng Long cho biến sum
Long sum = 0L;
for (long i = 0; i <= Integer.MAX_VALUE; i++)
    sum += i;  // Mỗi vòng lặp đều unbox và box lại!

// ĐÚNG: dùng long
long sum = 0L;
for (long i = 0; i <= Integer.MAX_VALUE; i++)
    sum += i;
```

#### Tại sao phép tính số thực mất độ chính xác?

```java
float a = 2.0f - 1.9f;
float b = 1.8f - 1.7f;
System.out.println(a);  // 0.100000024
System.out.println(b);  // 0.099999905
System.out.println(a == b);  // false
```

**Nguyên nhân**: Máy tính dùng hệ nhị phân, không thể biểu diễn chính xác nhiều số thập phân. Ví dụ 0.2 trong thập phân:

```
0.2 * 2 = 0.4 → 0
0.4 * 2 = 0.8 → 0
0.8 * 2 = 1.6 → 1
0.6 * 2 = 1.2 → 1
0.2 * 2 = 0.4 → 0  (lặp lại)
...
```

→ 0.2 trong nhị phân là **0.001100110011...**  (vô hạn tuần hoàn) → bị cắt xén → mất độ chính xác.

#### Giải quyết vấn đề mất độ chính xác?

Dùng **`BigDecimal`** cho các phép tính yêu cầu độ chính xác cao (tiền bạc, tài chính).

```java
BigDecimal a = new BigDecimal("1.0");
BigDecimal b = new BigDecimal("0.8");
BigDecimal x = a.subtract(b);
System.out.println(x);  // 0.2

// So sánh giá trị dùng compareTo (trả về 0 nếu bằng nhau)
System.out.println(0 == x.compareTo(new BigDecimal("0.20")));  // true
```

#### Số nguyên lớn hơn `long` thì dùng gì?

Dùng **`BigInteger`**:

```java
long l = Long.MAX_VALUE;
System.out.println(l + 1);  // -9223372036854775808 (tràn số)
System.out.println(l + 1 == Long.MIN_VALUE);  // true

BigInteger big = new BigInteger(String.valueOf(Long.MAX_VALUE));
System.out.println(big.add(BigInteger.ONE));  // 9223372036854775808
```

`BigInteger` dùng mảng `int[]` để lưu số lớn tùy ý, nhưng hiệu suất kém hơn kiểu nguyên chuẩn.

---

### 2.1.4. Biến (Variables)

#### ⭐ Biến Thành viên vs Biến Cục bộ

| Tiêu chí | Biến thành viên | Biến cục bộ |
|----------|----------------|-------------|
| **Vị trí** | Thuộc class | Trong method/code block |
| **Modifier** | Có thể dùng `public`, `private`, `static`, `final` | Chỉ dùng `final` |
| **Lưu trữ** | Heap (non-static) hoặc method area (static) | Stack |
| **Thời gian sống** | Theo object | Theo method call |
| **Giá trị mặc định** | Có (0, false, null) | Không có (phải khởi tạo) |

**Tại sao biến thành viên có giá trị mặc định?**

*   Biến cục bộ: compile-time có thể kiểm tra xem có được gán giá trị trước khi dùng không → compiler bắt buộc phải gán.
*   Biến thành viên: có thể được gán trong constructor, setter, hoặc bất kỳ đâu. Compiler không thể biết chắc thời điểm gán → cung cấp giá trị mặc định **an toàn** (0, null) để tránh "garbage value" nguy hiểm.

**Ví dụ:**
```java
public class VariableExample {
    private String name;  // Biến thành viên, default = null
    private int age;      // Biến thành viên, default = 0

    public void method() {
        int num1 = 10;    // Biến cục bộ (stack)
        String str = "Hello";
        System.out.println(num1);
        System.out.println(str);
    }

    public VariableExample(String name, int age) {
        this.name = name;
        this.age = age;
        int num3 = 20;    // Biến cục bộ trong constructor
    }
}
```

#### Static Variable có tác dụng gì?

**Static variable** (biến tĩnh) được chia sẻ bởi **tất cả instance** của class. Chỉ phân bổ bộ nhớ **một lần duy nhất**, tiết kiệm bộ nhớ.

```java
public class Counter {
    static int count = 0;

    public Counter() {
        count++;
        System.out.println(count);
    }

    public static void main(String[] args) {
        Counter c1 = new Counter();  // count = 1
        Counter c2 = new Counter();  // count = 2
        Counter c3 = new Counter();  // count = 3
    }
}
```


### 2.1.5. Phương thức (Methods)

#### Giá trị Trả về của Method là gì? Method có mấy loại?

**Giá trị trả về (Return value)** là kết quả thu được sau khi thực thi code trong method. Giá trị trả về cho phép sử dụng kết quả cho các thao tác khác.

Phân loại method theo tham số và giá trị trả về:

**1. No params, no return value**:
```java
public void f1() {
    System.out.println("Hello");
}
```

**2. Has params, no return value**:
```java
public void f2(String name, int age) {
    System.out.println(name + " is " + age);
}
```

**3. No params, has return value**:
```java
public int f3() {
    return 42;
}
```

**4. Has params, has return value**:
```java
public int f4(int a, int b) {
    return a * b;
}
```

#### Tại sao Static Method không gọi được Non-Static Member?

Nguyên nhân chính (liên quan đến JVM):

1.  **Static method thuộc class**, được load vào memory khi class load, có thể gọi qua class name trực tiếp.
2.  **Non-static member thuộc object instance**, chỉ tồn tại sau khi khởi tạo object bằng `new`.
3.  Khi static method đã tồn tại, non-static member có thể chưa tồn tại → gọi member chưa tồn tại trong memory = **illegal operation**.

#### ⭐ Static Method vs Instance Method

**1. Cách gọi**:

*   **Static method**: Có thể gọi qua `ClassName.methodName()` hoặc `object.methodName()`. Khuyến nghị dùng cách 1 để tránh nhầm lẫn. **Không cần tạo object**.
*   **Instance method**: Chỉ có thể gọi qua `object.methodName()`.

```java
public class Person {
    public void method() {
        // Instance method
    }

    public static void staticMethod() {
        // Static method
    }

    public static void main(String[] args) {
        Person person = new Person();
        person.method();         // Gọi instance method
        Person.staticMethod();   // Gọi static method (khuyến nghị)
    }
}
```

**2. Hạn chế truy cập**:

*   **Static method**: Chỉ được truy cập static member (static variable, static method). Không được truy cập instance member.
*   **Instance method**: Không có hạn chế, truy cập được cả static và instance member.

#### ⭐ Overloading vs Overriding

> **Overloading (Nạp chồng)**: Cùng một method có thể xử lý khác nhau tùy input data.  
> **Overriding (Ghi đè)**: Con kế thừa method của cha, input giống nhau, nhưng muốn xử lý khác với cha.

**Overloading (Nạp chồng)**

Xảy ra trong **cùng một class** (hoặc giữa cha-con). Method name **phải giống nhau**, nhưng **parameter list phải khác** (khác type, số lượng, hoặc thứ tự). Return type và access modifier có thể khác nhau.

```java
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public double add(double a, double b) {
        return a + b;
    }

    public int add(int a, int b, int c) {
        return a + b + c;
    }
}
```

**Overriding (Ghi đè)**

Xảy ra khi con kế thừa cha. Method name và parameter list **phải hoàn toàn giống nhau**. Return type con phải **≤** return type cha (covariant return). Access modifier con phải **≥** cha. Exception con throws phải **≤** cha throws.

Nếu method cha là `private`/`final`/`static` thì con không override được (nhưng static method có thể declare lại).

```java
public class Animal {
    public void makeSound() {
        System.out.println("Some sound");
    }
}

public class Dog extends Animal {
    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}
```

**Tổng kết:**

| Tiêu chí | Overloading | Overriding |
|----------|-------------|------------|
| **Phạm vi** | Cùng class | Cha-con |
| **Method signature** | Tên giống, param **khác** | Tên + param **hoàn toàn giống** |
| **Return type** | Bất kỳ | ≤ return type cha (hoặc giống) |
| **Access modifier** | Bất kỳ | ≥ cha |
| **Binding** | Compile-time | Runtime |

**Quy tắc "Hai đồng, Hai nhỏ, Một lớn"** cho Overriding:
*   **Hai đồng**: Tên method giống, param list giống
*   **Hai nhỏ**: Return type con ≤ cha, Exception con ≤ cha
*   **Một lớn**: Access modifier con ≥ cha

⭐ **Lưu ý về return type**: Nếu return type là `void` hoặc primitive, **không được thay đổi** khi override. Nhưng nếu return type là reference type, có thể return **subtype** của type cha.

```java
public class Hero {
    public String name() {
        return "Super Hero";
    }
}

public class SuperMan extends Hero {
    @Override
    public String name() {  // OK, cùng String
        return "Superman";
    }

    public Hero getHero() {
        return new Hero();
    }
}

public class SuperSuperMan extends SuperMan {
    @Override
    public SuperMan getHero() {  // OK, SuperMan là subtype của Hero
        return new SuperMan();
    }
}
```

#### Varargs (Tham số Biến đổi) là gì?

Từ Java 5, Java hỗ trợ varargs - cho phép truyền **số lượng tham số không xác định** vào method.

```java
public static void method1(String... args) {
    // Có thể nhận 0 hoặc nhiều String
}
```

**Lưu ý:**
*   Varargs **chỉ được là tham số cuối cùng**
*   Một method chỉ có tối đa **1 varargs**

```java
public static void method2(String arg1, String... args) {
    // OK
}
```

**Khi gặp Overloading, ưu tiên nào?**

Ưu tiên **fixed params** trước varargs (vì matching degree cao hơn).

```java
public class VariableLengthArgument {
    public static void printVariable(String... args) {
        for (String s : args) {
            System.out.println(s);
        }
    }

    public static void printVariable(String arg1, String arg2) {
        System.out.println(arg1 + arg2);
    }

    public static void main(String[] args) {
        printVariable("a", "b");         // Output: ab (gọi fixed params)
        printVariable("a", "b", "c", "d"); // Output: a b c d (gọi varargs)
    }
}
```

**Bản chất**: Java compiler chuyển varargs thành **array**.

---

### 2.1.6. Hướng Đối tượng (OOP)

#### ⭐ OOP vs Procedural Programming

**Procedural-Oriented Programming (POP)**: Chia vấn đề thành các **method** (hàm), giải quyết bằng cách thực thi từng hàm.

**Object-Oriented Programming (OOP)**: Trước tiên **trừu tượng hóa thành object**, sau đó dùng object thực thi method để giải quyết vấn đề.

**Ưu điểm của OOP so với POP:**
*   **Dễ bảo trì**: Cấu trúc tốt, đóng gói rõ ràng
*   **Dễ tái sử dụng**: Kế thừa và đa hình giúp tái sử dụng code
*   **Dễ mở rộng**: Thiết kế module hóa

POP đơn giản, trực tiếp hơn, phù hợp với task đơn giản.

**Ví dụ**: Tính diện tích và chu vi hình tròn

**OOP:**
```java
public class Circle {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    public double getArea() {
        return Math.PI * radius * radius;
    }

    public double getPerimeter() {
        return 2 * Math.PI * radius;
    }
}
```

**POP:**
```java
public class Main {
    public static void main(String[] args) {
        double radius = 3.0;
        double area = Math.PI * radius * radius;
        double perimeter = 2 * Math.PI * radius;
        System.out.println("Area: " + area);
        System.out.println("Perimeter: " + perimeter);
    }
}
```

#### Object Instance vs Object Reference

*   **Object instance**: Tạo bằng `new`, lưu trong **heap**.
*   **Object reference**: Con trỏ trỏ đến object instance, lưu trong **stack**.

Một reference có thể trỏ 0 hoặc 1 object. Một object có thể có n reference trỏ đến nó.

#### ⭐ Object Equality vs Reference Equality

*   **Object equality**: So sánh **nội dung** trong memory (dùng `.equals()`).
*   **Reference equality**: So sánh **địa chỉ memory** (dùng `==`).

```java
String str1 = "hello";
String str2 = new String("hello");
String str3 = "hello";

System.out.println(str1 == str2);      // false (khác địa chỉ)
System.out.println(str1 == str3);      // true (cùng địa chỉ trong pool)
System.out.println(str1.equals(str2)); // true (cùng nội dung)
```

#### Constructor (Hàm Khởi tạo)

*   Nếu class không khai báo constructor, Java tự động thêm **default no-arg constructor**.
*   Nếu bạn thêm constructor có tham số, Java **không tạo default constructor** nữa. Nên luôn khai báo cả no-arg constructor để tránh lỗi.

**Đặc điểm của Constructor:**
*   Tên giống tên class
*   Không có return type (kể cả `void`)
*   Tự động được gọi khi tạo object
*   **Không thể override**, nhưng **có thể overload**

#### ⭐ Ba Đặc tính OOP

**1. Encapsulation (Đóng gói)**

Che giấu trạng thái nội bộ (thuộc tính private), chỉ cho phép truy cập qua method public (getter/setter).

```java
public class Student {
    private int id;
    private String name;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
```

**2. Inheritance (Kế thừa)**

Class con kế thừa class cha, tái sử dụng code, tăng tính bảo trì.

**3 điểm quan trọng:**
1.  Con **sở hữu** mọi thuộc tính và method của cha (kể cả private), nhưng **không truy cập được** private member.
2.  Con có thể có thuộc tính và method riêng (mở rộng cha).
3.  Con có thể override method của cha (ghi đè).

**3. Polymorphism (Đa hình)**

Một object có nhiều hình thái. Cụ thể: **reference của cha trỏ đến instance của con**.

**Đặc điểm:**
*   Object type và reference type có quan hệ kế thừa/triển khai
*   Method được gọi phụ thuộc vào **runtime type** (dynamic binding)
*   Không thể gọi method "chỉ tồn tại ở con"
*   Nếu con override method cha, chạy code của con; nếu không, chạy code của cha

#### ⭐ Interface vs Abstract Class

**Giống nhau:**
*   Đều **không thể khởi tạo trực tiếp**
*   Đều có thể chứa **abstract method** (method không có body)

**Khác nhau:**

| Tiêu chí | Interface | Abstract Class |
|----------|-----------|----------------|
| **Mục đích** | Ràng buộc hành vi | Tái sử dụng code, quan hệ "is-a" |
| **Kế thừa/Triển khai** | Một class có thể implement nhiều interface | Một class chỉ kế thừa 1 abstract class |
| **Member variable** | Chỉ `public static final` | Bất kỳ modifier nào |
| **Method** | Default là `public abstract` (Java 8+ có `default`, `static`, Java 9+ có `private`) | Có thể có abstract method và concrete method |

**Java 8+ Interface Methods:**

*   **`default` method**: Có triển khai mặc định, có thể override ở implementation class.
*   **`static` method**: Gọi qua interface name, **không thể override**.
*   **`private` method** (Java 9+): Dùng nội bộ trong interface, chia sẻ code giữa `default` và `static`.

```java
public interface MyInterface {
    default void defaultMethod() {
        System.out.println("Default method");
    }

    static void staticMethod() {
        System.out.println("Static method");
    }

    private static void commonMethod() {
        System.out.println("Private method for code reuse");
    }
}
```

#### Shallow Copy vs Deep Copy

*   **Shallow Copy (Sao chép nông)**: Tạo object mới, nhưng nếu thuộc tính là reference type, chỉ copy **địa chỉ reference** → object gốc và copy **dùng chung** internal object.

*   **Deep Copy (Sao chép sâu)**: Copy hoàn toàn, bao gồm cả internal object.

**Shallow Copy Example:**
```java
public class Person implements Cloneable {
    private Address address;

    @Override
    public Person clone() {
        try {
            return (Person) super.clone();  // Shallow copy
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}

Person person1 = new Person(new Address("Hanoi"));
Person person1Copy = person1.clone();
System.out.println(person1.getAddress() == person1Copy.getAddress());  // true
```

**Deep Copy Example:**
```java
@Override
public Person clone() {
    try {
        Person person = (Person) super.clone();
        person.setAddress(person.getAddress().clone());  // Deep copy Address
        return person;
    } catch (CloneNotSupportedException e) {
        throw new AssertionError();
    }
}

Person person1 = new Person(new Address("Hanoi"));
Person person1Copy = person1.clone();
System.out.println(person1.getAddress() == person1Copy.getAddress());  // false
```

**Reference Copy**: Hai reference khác nhau trỏ đến **cùng một object**.

---

### 2.1.7. ⭐ Object Class

#### Object Class có những Method nào?

`Object` là class cha của tất cả class trong Java, cung cấp 11 method:

```java
public final native Class<?> getClass()          // Lấy Class object
public native int hashCode()                     // Hash code
public boolean equals(Object obj)                // So sánh object
protected native Object clone()                  // Clone object
public String toString()                         // Convert to String
public final native void notify()                // Đánh thức 1 thread
public final native void notifyAll()             // Đánh thức all threads
public final native void wait(long timeout)      // Thread đợi
public final void wait(long timeout, int nanos)
public final void wait()
protected void finalize()                        // GC callback (deprecated)
```

#### `==` vs `.equals()`

**`==`**:
*   Primitive type: so sánh **giá trị**
*   Reference type: so sánh **địa chỉ memory**

**`.equals()`**:
*   Chỉ dùng cho object (không dùng cho primitive)
*   Mặc định (Object class): so sánh địa chỉ (`return this == obj`)
*   Nếu class override: thường so sánh **nội dung** (ví dụ: `String`)

```java
String a = new String("hello");
String b = new String("hello");
String aa = "hello";
String bb = "hello";

System.out.println(aa == bb);      // true (cùng object trong pool)
System.out.println(a == b);        // false (khác object trong heap)
System.out.println(a.equals(b));   // true (cùng nội dung)
```

#### `hashCode()` dùng để làm gì?

`hashCode()` trả về **hash code** (int), dùng để xác định vị trí của object trong **hash table** (HashMap, HashSet).

**Tại sao cần hashCode?**

Khi thêm object vào `HashSet`:
1.  Gọi `hashCode()` → tính bucket (vị trí trong array)
2.  Nếu bucket rỗng: thêm trực tiếp
3.  Nếu bucket đã có element: so sánh hash code
    *   Hash khác: thêm vào cùng bucket (linked list/tree)
    *   Hash giống: gọi `.equals()` để kiểm tra xem có trùng không

→ `hashCode()` giúp thu hẹp phạm vi tìm kiếm, tăng hiệu suất.

#### Tại sao override `equals()` phải override `hashCode()`?

**Quy tắc**: Nếu `a.equals(b) == true` → `a.hashCode() == b.hashCode()`.

Nếu chỉ override `equals()` mà không override `hashCode()`:
*   Hai object bằng nhau theo `equals()` nhưng có hash code khác nhau
*   Khi dùng `HashMap`/`HashSet`, sẽ lưu 2 object giống nhau vào 2 bucket khác nhau → **lỗi logic**

**Tóm tắt:**
*   `equals()` true → `hashCode()` phải bằng nhau
*   `hashCode()` bằng nhau → `equals()` **có thể** false (hash collision)

---

### 2.1.8. ⭐ String

#### String vs StringBuffer vs StringBuilder

| Đặc điểm | String | StringBuffer | StringBuilder |
|----------|--------|--------------|---------------|
| **Khả biến** | Immutable | Mutable | Mutable |
| **Thread-safe** | Yes | Yes (synchronized) | No |
| **Hiệu suất** | Chậm (tạo object mới mỗi lần) | Trung bình | Nhanh nhất |
| **Khi nào dùng** | Ít thao tác | Multi-thread, nhiều thao tác | Single-thread, nhiều thao tác |

**String immutable:**
```java
public final class String {
    private final char[] value;  // (Java 9+: byte[] value)
}
```

String immutable vì:
1.  Array `value` là `private final` và không có method public để sửa
2.  Class `String` là `final` → không thể kế thừa để phá vỡ immutability

**Java 9 thay đổi**: `char[]` → `byte[]` để tiết kiệm memory. Nếu string chỉ chứa Latin-1 characters, dùng 1 byte/char thay vì 2 byte.

#### String Concatenation: `+` vs `StringBuilder`?

Compiler tự động chuyển `+` thành `StringBuilder.append()`:

```java
String str = "he" + "llo" + "world";
// → StringBuilder sb = new StringBuilder(); sb.append("he").append("llo").append("world");
```

**Vấn đề**: Trong vòng lặp, mỗi lần lặp tạo **một StringBuilder mới** → kém hiệu suất.

```java
String s = "";
for (int i = 0; i < arr.length; i++) {
    s += arr[i];  // Mỗi lần tạo StringBuilder mới!
}
```

**Giải pháp**: Tự tạo StringBuilder ngoài vòng lặp:
```java
StringBuilder s = new StringBuilder();
for (String value : arr) {
    s.append(value);
}
```

#### ⭐ String Pool (Bể Hằng Chuỗi)

**String Pool** là vùng đặc biệt trong JVM để lưu string literal, tránh tạo trùng lặp.

```java
String aa = "ab";  // Pool: tạo "ab" nếu chưa có
String bb = "ab";  // Pool: tái sử dụng "ab"
System.out.println(aa == bb);  // true
```

#### ⭐ `String s = new String("abc")` tạo mấy object?

**Đáp án**: 1 hoặc 2 object.

**Trường hợp 1**: String pool **chưa có** "abc"
*   Tạo 1 object trong **string pool** (do `ldc` instruction)
*   Tạo 1 object trong **heap** (do `new String()`)
*   **Tổng: 2 objects**

**Trường hợp 2**: String pool **đã có** "abc"
*   Chỉ tạo 1 object trong **heap** (do `new String()`)
*   **Tổng: 1 object**

**Bytecode analysis:**
```java
0 new #2 <java/lang/String>    // Tạo object trong heap
3 dup
4 ldc #3 <abc>                  // Load "abc" từ pool (hoặc tạo nếu chưa có)
6 invokespecial #4              // Gọi constructor
9 astore_1
10 return
```

#### `String.intern()` làm gì?

`intern()` đảm bảo string reference tồn tại trong **string pool**:

*   Nếu pool đã có string giống hệt → trả về reference của object trong pool
*   Nếu chưa có → thêm vào pool và trả về reference

```java
String s1 = "Java";               // Pool
String s2 = new String("Java");   // Heap
String s3 = s2.intern();          // Lấy từ pool

System.out.println(s1 == s2);  // false
System.out.println(s1 == s3);  // true
```

---


## 2.2. Collections Framework (Tập hợp)

### 2.2.1. Tổng quan Collection Framework

#### Java Collection Framework là gì?

Java Collection (tập hợp), còn gọi là **container** (thùng chứa), chủ yếu bắt nguồn từ 2 interface lớn:

*   **`Collection`**: Lưu trữ **single element** (phần tử đơn)
*   **`Map`**: Lưu trữ **key-value pairs** (cặp khóa-giá trị)

`Collection` interface có 3 sub-interface chính:
*   **`List`**: Có thứ tự, có thể trùng
*   **`Set`**: Không trùng lặp
*   **`Queue`**: Hàng đợi, có thể trùng, theo quy tắc sắp xếp

![Java Collection Hierarchy](https://oss.javaguide.cn/github/javaguide/java/collection/java-collection-hierarchy.png)

#### ⭐ List, Set, Queue, Map khác nhau thế nào?

| Interface | Đặc điểm |
|-----------|----------|
| **List** | Có thứ tự, có thể trùng lặp |
| **Set** | Không trùng lặp |
| **Queue** | Hàng đợi, có thứ tự (theo quy tắc), có thể trùng |
| **Map** | Key-value, key không trùng, value có thể trùng |

#### Cấu trúc Dữ liệu Nền tảng

**List:**
*   `ArrayList`: **`Object[]` array**
*   `Vector`: **`Object[]` array**
*   `LinkedList`: **Doubly linked list** (JDK 1.6 trước là circular, JDK 1.7 bỏ circular)

**Set:**
*   `HashSet`: Dựa trên **`HashMap`**
*   `LinkedHashSet`: Dựa trên **`LinkedHashMap`**
*   `TreeSet`: **Red-Black Tree** (cây đỏ-đen tự cân bằng)

**Queue:**
*   `PriorityQueue`: **`Object[]` array** (min heap)
*   `DelayQueue`: Dựa trên **`PriorityQueue`**
*   `ArrayDeque`: **Resizable array** (mảng động 2 đầu)

**Map:**
*   `HashMap`: JDK 1.7: **Array + Linked List**. JDK 1.8+: **Array + Linked List/Red-Black Tree** (khi chain dài > 8 và array size ≥ 64)
*   `LinkedHashMap`: Kế thừa `HashMap` + **doubly linked list** (giữ thứ tự insertion)
*   `Hashtable`: **Array + Linked List**
*   `TreeMap`: **Red-Black Tree**

#### Chọn Collection nào?

*   Cần **key-value**: dùng `Map`
    *   Cần sắp xếp: `TreeMap`
    *   Không cần: `HashMap`
    *   Thread-safe: `ConcurrentHashMap`
*   Chỉ cần lưu **value**:
    *   Cần **unique**: `Set` (`HashSet`, `TreeSet`)
    *   Không cần unique: `List` (`ArrayList`, `LinkedList`)

#### Tại sao dùng Collection thay vì Array?

Array có hạn chế:
*   **Kích thước cố định** (không thể thay đổi sau khi khởi tạo)
*   **Không hỗ trợ generic tốt**
*   **Thiếu API phong phú** (thêm, xóa, tìm kiếm)

Collection ưu việt hơn:
*   **Kích thước linh hoạt** (auto resize)
*   **Generic type-safe**
*   **API phong phú** (`add`, `remove`, `contains`, v.v.)
*   **Built-in algorithms** (sort, search)

---

### 2.2.2. ⭐ List Interface

#### ArrayList vs Array

| Tiêu chí | ArrayList | Array |
|----------|-----------|-------|
| **Kích thước** | Dynamic (auto expand/shrink) | Fixed |
| **Generic** | Có | Không |
| **Kiểu lưu** | Chỉ object (wrapper primitive) | Cả primitive và object |
| **API** | Phong phú (`add`, `remove`, `iterator`) | Hạn chế (chỉ index access) |
| **Khởi tạo** | Không cần size | Phải chỉ định size |

**Ví dụ Array:**
```java
String[] stringArr = new String[]{"hello", "world", "!"};
stringArr[0] = "goodbye";
// Xóa element phải tự shift
for (int i = 0; i < stringArr.length - 1; i++) {
    stringArr[i] = stringArr[i + 1];
}
stringArr[stringArr.length - 1] = null;
```

**Ví dụ ArrayList:**
```java
ArrayList<String> list = new ArrayList<>(Arrays.asList("hello", "world", "!"));
list.add("goodbye");          // [hello, world, !, goodbye]
list.set(0, "hi");            // [hi, world, !, goodbye]
list.remove(0);               // [world, !, goodbye]
```

#### ArrayList vs Vector

*   **`ArrayList`**: Không thread-safe, hiệu suất cao hơn
*   **`Vector`**: Thread-safe (synchronized), hiệu suất thấp hơn, **đã lỗi thời**

**Khuyến nghị**: Dùng `CopyOnWriteArrayList` hoặc `Collections.synchronizedList(new ArrayList<>())` thay vì `Vector`.

#### ArrayList có thể chứa `null` không?

**Có**, nhưng **không khuyến nghị** vì dễ gây `NullPointerException` và code khó maintain.

```java
ArrayList<String> list = new ArrayList<>();
list.add(null);
list.add("java");
System.out.println(list);  // [null, java]
```

#### ⭐ ArrayList Insert/Delete Time Complexity

**Insert:**
*   **Head insert**: O(n) - phải shift tất cả element sang phải
*   **Tail insert**: O(1) amortized - nếu không cần expand; O(n) nếu cần expand + copy
*   **Middle insert**: O(n) - shift trung bình n/2 elements

**Delete:**
*   **Head delete**: O(n) - shift tất cả sang trái
*   **Tail delete**: O(1)
*   **Middle delete**: O(n) - shift trung bình n/2 elements

**Minh họa:**
```
Initial array (size 10, 7 elements):
+---+---+---+---+---+---+---+---+---+---+
| 1 | 2 | 3 | 4 | 5 | 6 | 7 |   |   |   |
+---+---+---+---+---+---+---+---+---+---+

Insert 8 at index 1:
+---+---+---+---+---+---+---+---+---+---+
| 1 | 8 | 2 | 3 | 4 | 5 | 6 | 7 |   |   |
+---+---+---+---+---+---+---+---+---+---+

Delete at index 1:
+---+---+---+---+---+---+---+---+---+---+
| 1 | 2 | 3 | 4 | 5 | 6 | 7 |   |   |   |
+---+---+---+---+---+---+---+---+---+---+
```

#### ⭐ LinkedList Insert/Delete Time Complexity

*   **Head insert/delete**: O(1) - chỉ sửa pointer của head
*   **Tail insert/delete**: O(1) - chỉ sửa pointer của tail
*   **Middle insert/delete**: O(n) - phải traverse trung bình n/4 nodes (vì có head + tail pointer, chọn con đường gần hơn)

![LinkedList unlink](https://oss.javaguide.cn/github/javaguide/java/collection/linkedlist-unlink.jpg)

#### LinkedList không implement `RandomAccess` vì sao?

`RandomAccess` là **marker interface** để đánh dấu class hỗ trợ **random access** (truy cập nhanh qua index).

*   **ArrayList**: Có `RandomAccess` - array hỗ trợ O(1) index access
*   **LinkedList**: Không có - linked list phải traverse O(n)

**Ứng dụng**: `Collections.binarySearch()` kiểm tra `instanceof RandomAccess` để chọn thuật toán phù hợp.

```java
public static <T> int binarySearch(List<? extends Comparable<? super T>> list, T key) {
    if (list instanceof RandomAccess || list.size() < BINARYSEARCH_THRESHOLD)
        return Collections.indexedBinarySearch(list, key);
    else
        return Collections.iteratorBinarySearch(list, key);
}
```

#### ⭐ ArrayList vs LinkedList

| Tiêu chí | ArrayList | LinkedList |
|----------|-----------|------------|
| **Thread-safe** | No | No |
| **Cấu trúc** | Dynamic array | Doubly linked list |
| **Insert/Delete** | Chậm ở middle (O(n)), nhanh ở tail (O(1)) | Nhanh ở head/tail (O(1)), chậm ở middle (O(n)) |
| **Random Access** | Có (O(1)) | Không (O(n)) |
| **Memory** | Lãng phí ở cuối (reserve capacity) | Lãng phí ở mỗi node (prev/next pointers) |

**Kết luận**: Trong thực tế, **ArrayList thường tốt hơn LinkedList** ngay cả khi cần insert/delete nhiều! Ngay cả tác giả `LinkedList` (Joshua Bloch) cũng không dùng nó.

![Josh Bloch quote](https://oss.javaguide.cn/github/javaguide/redisimage-20220412110853807.png)

#### ⭐ ArrayList Expansion Mechanism

ArrayList mở rộng khi **hết chỗ**:

1.  Mặc định capacity = **10**
2.  Khi `add()` vượt capacity, expand **1.5x** (new capacity = old * 1.5)
3.  Copy elements sang array mới
4.  Nếu 1.5x vẫn không đủ, dùng **minCapacity** (số lượng cần thiết)

**Source code:**
```java
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);  // 1.5x
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

#### ⭐ Fail-Fast vs Fail-Safe

**Fail-Fast (Nhanh thất bại)**

Dừng ngay lập tức khi phát hiện concurrent modification. Dùng **`modCount`** để tracking.

**ArrayList (fail-fast) ví dụ:**
```java
List<Integer> list = new ArrayList<>(Arrays.asList(0, 1, 2, 3, 4));

Thread t1 = new Thread(() -> {
    try {
        for (Integer i : list) {
            System.out.println("Thread 1: " + i);
            Thread.sleep(100);
        }
    } catch (ConcurrentModificationException e) {
        System.err.println("Caught ConcurrentModificationException!");
    }
});

Thread t2 = new Thread(() -> {
    try {
        Thread.sleep(50);
        list.remove(Integer.valueOf(1));  // Modify during iteration
    } catch (InterruptedException e) {}
});

t1.start();
t2.start();
```

**Output:**
```
Thread 1: 0
Caught ConcurrentModificationException!
```

**Cơ chế:**
```java
public E next() {
    checkForComodification();  // Check if modCount changed
    return elementData[lastRet = i];
}

final void checkForComodification() {
    if (modCount != expectedModCount)
        throw new ConcurrentModificationException();
}
```

**Fail-Safe (An toàn thất bại)**

Tiếp tục hoạt động ngay cả khi có modification. Dùng **Copy-On-Write** (CopyOnWriteArrayList).

Khi modify, tạo **snapshot copy** của array, thực hiện thay đổi trên copy, sau đó update reference.

**CopyOnWriteArrayList:**
```java
public boolean add(E e) {
    final ReentrantLock lock = this.lock;
    lock.lock();
    try {
        Object[] elements = getArray();
        int len = elements.length;
        Object[] newElements = Arrays.copyOf(elements, len + 1);  // Copy
        newElements[len] = e;
        setArray(newElements);  // Update reference
        return true;
    } finally {
        lock.unlock();
    }
}
```

**Trade-off**: Fail-safe đảm bảo thread-safe nhưng iterator có thể đọc **stale data** (dữ liệu cũ).

---

### 2.2.3. Set Interface

#### `Comparable` vs `Comparator`

Cả hai đều dùng để **sắp xếp**, nhưng khác nhau:

| Tiêu chí | Comparable | Comparator |
|----------|------------|------------|
| **Package** | `java.lang` | `java.util` |
| **Method** | `int compareTo(Object obj)` | `int compare(Object o1, Object o2)` |
| **Mục đích** | Định nghĩa **natural ordering** (thứ tự tự nhiên) | Định nghĩa **custom ordering** (thứ tự tùy chỉnh) |
| **Implement** | Class tự implement | Tạo Comparator riêng |

**Comparable example:**
```java
public class Person implements Comparable<Person> {
    private String name;
    private int age;

    @Override
    public int compareTo(Person o) {
        return Integer.compare(this.age, o.age);  // Sort by age
    }
}

TreeMap<Person, String> map = new TreeMap<>();
map.put(new Person("Alice", 30), "alice");
map.put(new Person("Bob", 20), "bob");
```

**Comparator example:**
```java
ArrayList<Integer> list = new ArrayList<>(Arrays.asList(-1, 3, -5, 7, 4));

// Natural order (ascending)
Collections.sort(list);
System.out.println(list);  // [-5, -1, 3, 4, 7]

// Custom order (descending)
Collections.sort(list, new Comparator<Integer>() {
    @Override
    public int compare(Integer o1, Integer o2) {
        return o2.compareTo(o1);
    }
});
System.out.println(list);  // [7, 4, 3, -1, -5]

// Lambda (Java 8+)
Collections.sort(list, (o1, o2) -> o2.compareTo(o1));
```

#### Unordered vs Non-repeatable

*   **Unordered (Vô thứ tự)**: Không theo index, mà theo **hash value** (không random!)
*   **Non-repeatable (Không trùng)**: Dùng `.equals()` để kiểm tra. Phải override cả `equals()` và `hashCode()`.

#### HashSet vs LinkedHashSet vs TreeSet

| Class | Cấu trúc | Đặc điểm | Khi nào dùng |
|-------|----------|----------|--------------|
| **HashSet** | HashMap | Không thứ tự, không trùng | Không cần ordering |
| **LinkedHashSet** | LinkedHashMap | FIFO order, không trùng | Cần giữ insertion order |
| **TreeSet** | Red-Black Tree | Sorted, không trùng | Cần sorting (natural hoặc custom) |

---

### 2.2.4. Queue Interface

#### Queue vs Deque

**Queue** (Single-ended queue): FIFO

| Operation | Throw Exception | Return Special Value |
|-----------|----------------|----------------------|
| Insert | `add(e)` | `offer(e)` |
| Remove | `remove()` | `poll()` |
| Examine | `element()` | `peek()` |

**Deque** (Double-ended queue): Insert/remove ở cả 2 đầu

| Operation | Throw Exception | Return Special Value |
|-----------|----------------|----------------------|
| Insert First | `addFirst(e)` | `offerFirst(e)` |
| Insert Last | `addLast(e)` | `offerLast(e)` |
| Remove First | `removeFirst()` | `pollFirst()` |
| Remove Last | `removeLast()` | `pollLast()` |
| Examine First | `getFirst()` | `peekFirst()` |
| Examine Last | `getLast()` | `peekLast()` |

Deque cũng có `push()`/`pop()` → có thể dùng như **Stack**.

#### ArrayDeque vs LinkedList

| Tiêu chí | ArrayDeque | LinkedList |
|----------|------------|------------|
| **Cấu trúc** | Resizable circular array | Doubly linked list |
| **Null support** | No | Yes |
| **JDK version** | 1.6+ | 1.2+ |
| **Performance** | Nhanh hơn (ít allocation) | Chậm hơn (mỗi node cần allocate) |

**Kết luận**: Nên dùng **ArrayDeque** thay vì LinkedList cho queue và stack.

#### PriorityQueue

*   Dựa trên **binary heap** (min heap mặc định)
*   Insert/delete: **O(log n)**
*   Không thread-safe
*   Không hỗ trợ `null` hoặc non-comparable object
*   Có thể custom comparator

**Ví dụ:**
```java
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.add(3);
minHeap.add(1);
minHeap.add(2);
System.out.println(minHeap.poll());  // 1 (min)

// Max heap
PriorityQueue<Integer> maxHeap = new PriorityQueue<>((a, b) -> b - a);
maxHeap.add(3);
maxHeap.add(1);
maxHeap.add(2);
System.out.println(maxHeap.poll());  // 3 (max)
```

#### BlockingQueue

**BlockingQueue** là interface kế thừa `Queue`, hỗ trợ **blocking operations**:
*   Nếu queue **empty**, `take()` sẽ block cho đến khi có element
*   Nếu queue **full**, `put()` sẽ block cho đến khi có chỗ

**Dùng cho**: Producer-Consumer pattern

**Các implementation:**
1.  **`ArrayBlockingQueue`**: Bounded, array-based, single lock
2.  **`LinkedBlockingQueue`**: Optionally bounded, linked list, dual locks (put/take)
3.  **`PriorityBlockingQueue`**: Unbounded, heap-based, sorted
4.  **`SynchronousQueue`**: No storage, direct handoff
5.  **`DelayQueue`**: Unbounded, elements available after delay

#### ⭐ ArrayBlockingQueue vs LinkedBlockingQueue

| Tiêu chí | ArrayBlockingQueue | LinkedBlockingQueue |
|----------|-------------------|---------------------|
| **Cấu trúc** | Array | Linked list |
| **Bounded** | Yes (phải chỉ định) | Optional (default `Integer.MAX_VALUE`) |
| **Lock** | Single lock (put + take) | Dual locks (`putLock`, `takeLock`) |
| **Memory** | Pre-allocated | Dynamic allocation |

**Kết luận**: `LinkedBlockingQueue` thường tốt hơn vì **dual locks** giảm contention giữa producer/consumer.

---


## 2.3. Concurrency (Đồng thời)

### 2.3.1. Thread Basics

#### ⭐ Thread vs Process

**Process (Tiến trình)**

Process là một lần thực thi chương trình, là đơn vị cơ bản để OS chạy program. Process là **dynamic** (động).

Khi chạy `main()` trong Java, thực chất là khởi động 1 **JVM process**, và `main()` là một **thread** (main thread) trong process đó.

**Thread (Luồng)**

Thread nhỏ hơn process. Một process có thể có nhiều thread. **Các thread trong cùng process chia sẻ**:
*   **Heap** (bộ nhớ động)
*   **Method Area** (metadata, static)

**Mỗi thread có riêng**:
*   **Program Counter** (PC - vị trí thực thi)
*   **VM Stack** (stack frame cho method calls)
*   **Native Method Stack**

![Java Runtime Data Areas JDK 1.8+](https://oss.javaguide.cn/github/javaguide/java/jvm/java-runtime-data-areas-jdk1.8.png)

**Tại sao PC, Stack riêng?**
*   **PC private**: Để thread biết chạy tiếp từ đâu sau khi bị context switch
*   **Stack private**: Để biến cục bộ của thread không bị thread khác truy cập

#### Java Thread vs OS Thread

*   **JDK 1.2 trước**: Java dùng **Green Threads** (user-level threads) - JVM tự quản lý, không phụ thuộc OS
*   **JDK 1.2+**: Java chuyển sang **Native Threads** (kernel-level threads) - map 1:1 với OS threads

**Thread models:**
1.  **1:1** (one-to-one): 1 user thread = 1 kernel thread (Java hiện tại)
2.  **N:1** (many-to-one): nhiều user threads = 1 kernel thread
3.  **N:M** (many-to-many): nhiều user threads = nhiều kernel threads

![Thread Models](https://oss.javaguide.cn/github/javaguide/java/concurrent/three-types-of-thread-models.png)

**Kết luận**: Java thread hiện tại **chính là OS thread** (1:1 model).

#### Tạo Thread như thế nào?

Các cách "tạo" thread:
1.  Extend `Thread` class
2.  Implement `Runnable` interface
3.  Implement `Callable` interface
4.  Thread pool
5.  `CompletableFuture`

**Nhưng thực chất**, tất cả đều qua **`new Thread().start()`**.

#### ⭐ Thread Lifecycle & States

Java thread có **6 states**:

| State | Ý nghĩa |
|-------|---------|
| **NEW** | Thread mới tạo, chưa gọi `start()` |
| **RUNNABLE** | Đã gọi `start()`, sẵn sàng chạy hoặc đang chạy |
| **BLOCKED** | Bị block chờ lock (monitor) |
| **WAITING** | Chờ vô thời hạn (cần thread khác notify) |
| **TIMED_WAITING** | Chờ có timeout |
| **TERMINATED** | Thread đã chạy xong `run()` |

![Java Thread State Diagram](https://oss.javaguide.cn/github/javaguide/java/concurrent/640.png)

**Lưu ý**: JVM **không phân biệt** READY vs RUNNING (cả hai đều là RUNNABLE), vì:
*   OS dùng time-slicing, mỗi thread chỉ chạy vài ms rồi switch
*   Switch quá nhanh (0.01s) → phân biệt không có ý nghĩa

![RUNNABLE vs RUNNING](https://oss.javaguide.cn/github/javaguide/java/RUNNABLE-VS-RUNNING.png)

**State transitions:**
*   `start()`: NEW → RUNNABLE
*   `wait()`: RUNNABLE → WAITING
*   `sleep(ms)`, `wait(ms)`: RUNNABLE → TIMED_WAITING
*   `synchronized` lock occupied: RUNNABLE → BLOCKED
*   `run()` kết thúc: → TERMINATED

#### Context Switching

**Context switch** xảy ra khi:
1.  Thread chủ động nhường CPU (`sleep()`, `wait()`)
2.  Time slice hết
3.  IO blocking
4.  Thread kết thúc

**Chi phí**: Lưu/restore PC, stack, registers  → càng nhiều switch, càng chậm.

#### `Thread.sleep()` vs `Object.wait()`

| Tiêu chí | `sleep()` | `wait()` |
|----------|-----------|----------|
| **Lock** | **KHÔNG** release lock | **CÓ** release lock |
| **Mục đích** | Tạm dừng thực thi | Giao tiếp giữa threads |
| **Wake up** | Tự động sau timeout | Cần `notify()`/`notifyAll()` |
| **Location** | `Thread` class (static) | `Object` class (instance method) |

**Tại sao `wait()` trong `Object`?**

`wait()` release **object lock**, nên phải gọi trên object chứa lock. `sleep()` chỉ tạm dừng thread, không liên quan object.

#### `start()` vs `run()`

*   **`start()`**: Tạo thread mới, JVM gọi `run()` trong thread mới → **multithreading**
*   **`run()`**: Gọi method bình thường trong thread hiện tại → **KHÔNG phải multithreading**

**Kết luận**: Phải gọi `start()` để tạo thread mới!

---

### 2.3.2. Concurrency Concepts

#### Concurrency vs Parallelism

*   **Concurrency (Đồng thời)**: Nhiều task trong **cùng time period** (time-slicing)
*   **Parallelism (Song song)**: Nhiều task tại **cùng instant** (multi-core)

#### Synchronous vs Asynchronous

*   **Synchronous (Đồng bộ)**: Đợi kết quả trước khi return
*   **Asynchronous (Bất đồng bộ)**: Return ngay, không đợi kết quả

#### ⭐ Tại sao dùng Multithreading?

**Từ góc độ phần cứng:**
*   Thread nhẹ hơn process → context switch nhanh hơn
*   Multi-core CPU → nhiều thread chạy **parallel** → tăng throughput

**Từ góc độ ứng dụng:**
*   Hệ thống hiện đại cần **high concurrency** (hàng triệu requests)
*   Multithreading là nền tảng của high-concurrency systems

**Single-core era:**
*   Tăng CPU + IO utilization
*   Thread bị IO block → thread khác dùng CPU → efficiency ~100% thay vì 50%

**Multi-core era:**
*   Tận dụng nhiều cores
*   Ví dụ: 1 thread trên 4-core CPU → chỉ dùng 1 core. 4 threads → dùng cả 4 cores → nhanh gấp ~4 lần

#### Single-core CPU có hỗ trợ multithreading không?

**Có**. OS dùng **time-slicing** (chia CPU time thành các time slice nhỏ, gán cho các thread khác nhau).

**Java dùng Preemptive Scheduling (Lập lịch ưu tiên)**:
*   OS quyết định khi nào switch thread (dựa trên time slice, priority, IO)
*   Không phải Cooperative Scheduling (thread tự nhường CPU)

#### Single-core multithreading có nhanh hơn không?

**Phụ thuộc vào loại task:**
*   **CPU-intensive**: Nhiều thread → nhiều context switch → **CHẬM hơn**
*   **IO-intensive**: Nhiều thread → tận dụng thời gian đợi IO → **NHANH hơn**

#### Vấn đề của Multithreading

*   **Memory leak**
*   **Deadlock** (bế tắc)
*   **Thread unsafe** (không thread-safe)
*   **Race condition** (điều kiện tranh chấp)

---

### 2.3.3. ⭐ Deadlock (Bế tắc)

#### Deadlock là gì?

**Deadlock**: Nhiều thread bị block vô thời hạn, chờ nhau release resource.

![Deadlock Diagram](https://oss.javaguide.cn/github/javaguide/java/2019-4%E6%AD%BB%E9%94%811.png)

*   Thread A giữ Resource 2, chờ Resource 1
*   Thread B giữ Resource 1, chờ Resource 2
*   → Cả hai chờ mãi → **Deadlock**

**Code example:**
```java
public class DeadLockDemo {
    private static Object resource1 = new Object();
    private static Object resource2 = new Object();

    public static void main(String[] args) {
        new Thread(() -> {
            synchronized (resource1) {
                System.out.println(Thread.currentThread() + " get resource1");
                try { Thread.sleep(1000); } catch (InterruptedException e) {}
                System.out.println(Thread.currentThread() + " waiting resource2");
                synchronized (resource2) {
                    System.out.println(Thread.currentThread() + " get resource2");
                }
            }
        }, "Thread 1").start();

        new Thread(() -> {
            synchronized (resource2) {
                System.out.println(Thread.currentThread() + " get resource2");
                try { Thread.sleep(1000); } catch (InterruptedException e) {}
                System.out.println(Thread.currentThread() + " waiting resource1");
                synchronized (resource1) {
                    System.out.println(Thread.currentThread() + " get resource1");
                }
            }
        }, "Thread 2").start();
    }
}
```

**Output:**
```
Thread[Thread 1,5,main] get resource1
Thread[Thread 2,5,main] get resource2
Thread[Thread 1,5,main] waiting resource2
Thread[Thread 2,5,main] waiting resource1
```

→ Cả hai thread đều chờ mãi → **Deadlock!**

#### 4 Điều kiện cần của Deadlock

1.  **Mutual Exclusion (Loại trừ lẫn nhau)**: Resource chỉ có thể bị 1 thread chiếm tại một thời điểm
2.  **Hold and Wait (Giữ và chờ)**: Thread giữ resource A, chờ resource B
3.  **No Preemption (Không preempt)**: Resource không thể bị cướp, chỉ tự nguyện release
4.  **Circular Wait (Chờ vòng)**: Thread 1 chờ Thread 2 chờ Thread 3 chờ Thread 1 (vòng tròn)

#### Phát hiện Deadlock

**Tools:**
*   **`jstack`**: `jstack <pid>` → tìm "Found one Java-level deadlock"
*   **JConsole**: GUI tool, tab "Threads" → click "Detect Deadlock"
*   **VisualVM**: Tương tự JConsole

![JConsole Detect Deadlock](https://oss.javaguide.cn/github/javaguide/java/concurrent/jconsole-check-deadlock-done.png)

#### Phòng tránh và Tránh Deadlock

**Phòng (Prevention)**: Phá vỡ 1 trong 4 điều kiện

1.  **Phá Hold and Wait**: Xin tất cả resource cùng lúc
2.  **Phá No Preemption**: Cho phép thread release resource nếu không xin được thêm
3.  **Phá Circular Wait**: **Xin resource theo thứ tự cố định** ← phổ biến nhất!

**Ví dụ fix deadlock:**
```java
// Thread 2 cũng xin resource1 trước, resource2 sau (giống Thread 1)
new Thread(() -> {
    synchronized (resource1) {  // Thay đổi: xin resource1 trước
        System.out.println(Thread.currentThread() + " get resource1");
        try { Thread.sleep(1000); } catch (InterruptedException e) {}
        System.out.println(Thread.currentThread() + " waiting resource2");
        synchronized (resource2) {
            System.out.println(Thread.currentThread() + " get resource2");
        }
    }
}, "Thread 2").start();
```

→ Cả hai thread đều xin `resource1` trước → không có circular wait → **Không deadlock!**

**Tránh (Avoidance)**: Dùng thuật toán (Banker's Algorithm) để đánh giá xem có vào **safe state** không.

---

### 2.3.4. ⭐ Thread Pool (Chi tiết)

#### Tại sao cần Thread Pool?

**Vấn đề tạo thread trực tiếp:**
```java
// Mỗi request tạo 1 thread mới
for (int i = 0; i < 10000; i++) {
    new Thread(() -> {
        // Process request
    }).start();
}
```

**Nhược điểm:**
1. **Overhead cao**: Tạo/destroy thread tốn CPU và memory
2. **Unbounded**: Có thể tạo vô số threads → OOM
3. **Khó quản lý**: Không kiểm soát được số lượng threads

**Solution: Thread Pool** - Tái sử dụng threads, giới hạn số lượng.

#### ⭐ ThreadPoolExecutor Parameters (7 tham số)

```java
ThreadPoolExecutor(
    int corePoolSize,              // 1. Số threads cố định (core threads)
    int maximumPoolSize,           // 2. Số threads tối đa
    long keepAliveTime,            // 3. Thời gian idle threads sống (ngoài core)
    TimeUnit unit,                 // 4. Đơn vị thời gian
    BlockingQueue<Runnable> workQueue,  // 5. Queue chứa tasks
    ThreadFactory threadFactory,   // 6. Factory tạo threads
    RejectedExecutionHandler handler    // 7. Handler khi queue đầy
)
```

**3 tham số quan trọng nhất:**

1. **`corePoolSize`**: Số threads cố định, luôn giữ trong pool
2. **`maximumPoolSize`**: Số threads tối đa (bao gồm core + non-core)
3. **`workQueue`**: Queue chứa tasks chờ xử lý

**Execution Flow:**

```
1. Task đến → Threads < corePoolSize?
   → YES: Tạo thread mới → Execute task
   → NO: Bước 2

2. workQueue chưa đầy?
   → YES: Đưa task vào queue
   → NO: Bước 3

3. Threads < maximumPoolSize?
   → YES: Tạo non-core thread → Execute task
   → NO: Bước 4

4. Reject task (gọi RejectedExecutionHandler)
```

**Ví dụ:**
```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    2,      // corePoolSize = 2
    5,      // maximumPoolSize = 5
    60L,    // keepAliveTime = 60s
    TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(10),  // Queue size = 10
    Executors.defaultThreadFactory(),
    new ThreadPoolExecutor.CallerRunsPolicy()
);

// Scenario: 20 tasks đến cùng lúc
// - 2 tasks → 2 core threads execute
// - 10 tasks → Queue (đầy)
// - 3 tasks → 3 non-core threads execute (total = 5 threads)
// - 5 tasks → Rejected (CallerRunsPolicy)
```

#### ⭐ Work Queue Types

**1. LinkedBlockingQueue (Unbounded)**
- **Size**: `Integer.MAX_VALUE` (vô hạn)
- **Use case**: FixedThreadPool, SingleThreadExecutor
- **Risk**: OOM nếu tasks tích tụ quá nhiều

**2. ArrayBlockingQueue (Bounded)**
- **Size**: Cố định (ví dụ: 100)
- **Use case**: Production (khuyến nghị)
- **Safe**: Giới hạn memory usage

**3. SynchronousQueue (No capacity)**
- **Size**: 0 (không lưu tasks)
- **Use case**: CachedThreadPool
- **Behavior**: Task đến → Phải có thread sẵn sàng, không thì reject

**4. DelayedWorkQueue**
- **Use case**: ScheduledThreadPool
- **Behavior**: Tasks được schedule theo thời gian

#### ⭐ RejectedExecutionHandler (4 Strategies)

**1. AbortPolicy (Mặc định)**
```java
// Throw RejectedExecutionException
new ThreadPoolExecutor.AbortPolicy()
```
- **Behavior**: Reject task → Throw exception
- **Use case**: Cần biết khi nào reject

**2. CallerRunsPolicy**
```java
// Execute task trong caller thread
new ThreadPoolExecutor.CallerRunsPolicy()
```
- **Behavior**: Reject task → Chạy trong thread gọi `execute()`
- **Use case**: Slow down producer (backpressure)

**3. DiscardPolicy**
```java
// Silently discard task
new ThreadPoolExecutor.DiscardPolicy()
```
- **Behavior**: Reject task → Bỏ qua (không exception)
- **Use case**: Tasks không quan trọng

**4. DiscardOldestPolicy**
```java
// Discard oldest task in queue
new ThreadPoolExecutor.DiscardOldestPolicy()
```
- **Behavior**: Reject task → Xóa task cũ nhất trong queue → Thêm task mới
- **Use case**: Ưu tiên tasks mới

#### ⭐ Executors Factory Methods (Cẩn thận!)

**❌ KHÔNG nên dùng trong production:**

**1. `Executors.newFixedThreadPool(n)`**
```java
// LinkedBlockingQueue (unbounded) → OOM risk
Executors.newFixedThreadPool(10);
```

**2. `Executors.newCachedThreadPool()`**
```java
// maximumPoolSize = Integer.MAX_VALUE → OOM risk
Executors.newCachedThreadPool();
```

**3. `Executors.newSingleThreadExecutor()`**
```java
// LinkedBlockingQueue (unbounded) → OOM risk
Executors.newSingleThreadExecutor();
```

**✅ Nên dùng:**
```java
// Manual configuration với bounded queue
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    10, 20, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(100),  // Bounded!
    new ThreadFactoryBuilder()
        .setNameFormat("my-pool-%d")
        .build(),
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

#### ⭐ Best Practices

**1. Named Thread Pool**
```java
ThreadFactory namedFactory = new ThreadFactoryBuilder()
    .setNameFormat("order-processor-%d")
    .setDaemon(false)
    .build();
```
- **Lợi ích**: Dễ debug (thread dump có tên rõ ràng)

**2. Monitor Thread Pool**
```java
// Metrics
int activeThreads = executor.getActiveCount();
int queueSize = executor.getQueue().size();
long completedTasks = executor.getCompletedTaskCount();
```

**3. Graceful Shutdown**
```java
executor.shutdown();  // Không nhận tasks mới
try {
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow();  // Force shutdown
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
}
```

---

### 2.3.5. ⭐ Locks & Synchronization (Chi tiết)

#### `synchronized` Keyword

**Cách dùng:**

**1. Synchronized Method**
```java
public synchronized void increment() {
    count++;
}
// Lock = this (instance) hoặc Class (static method)
```

**2. Synchronized Block**
```java
public void increment() {
    synchronized (this) {  // Lock = this
        count++;
    }
}
```

**Đặc điểm:**
- **Reentrant**: Thread đã giữ lock có thể lock lại
- **Automatic**: Tự động release khi method/block kết thúc
- **JVM-level**: Implement bằng monitor (monitorenter/monitorexit)

**Lock Object:**
- **Instance method**: Lock = `this`
- **Static method**: Lock = `Class` object
- **Synchronized block**: Lock = object trong `synchronized(obj)`

#### ⭐ ReentrantLock (Chi tiết)

**Ưu điểm so với `synchronized`:**

**1. Fairness (Công bằng)**
```java
ReentrantLock fairLock = new ReentrantLock(true);  // Fair = true
// Threads được phục vụ theo thứ tự (FIFO)
```

**2. Try-Lock (Non-blocking)**
```java
if (lock.tryLock(5, TimeUnit.SECONDS)) {
    try {
        // Critical section
    } finally {
        lock.unlock();
    }
} else {
    // Timeout - không lấy được lock
}
```

**3. Interruptible**
```java
try {
    lock.lockInterruptibly();  // Có thể bị interrupt
    // Critical section
} catch (InterruptedException e) {
    // Handle interrupt
} finally {
    if (lock.isHeldByCurrentThread()) {
        lock.unlock();
    }
}
```

**4. Multiple Conditions**
```java
Condition notEmpty = lock.newCondition();
Condition notFull = lock.newCondition();

// Producer
lock.lock();
try {
    while (queue.isFull()) {
        notFull.await();  // Wait until not full
    }
    queue.add(item);
    notEmpty.signal();  // Signal consumer
} finally {
    lock.unlock();
}
```

**Code Pattern:**
```java
ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    // Critical section
} finally {
    lock.unlock();  // QUAN TRỌNG: Phải unlock trong finally!
}
```

#### ⭐ ReadWriteLock

**Vấn đề**: Nhiều readers không cần lock lẫn nhau, nhưng writer cần exclusive lock.

**Solution: ReadWriteLock**
```java
ReadWriteLock rwLock = new ReentrantReadWriteLock();
Lock readLock = rwLock.readLock();   // Shared lock
Lock writeLock = rwLock.writeLock(); // Exclusive lock

// Reader
readLock.lock();
try {
    // Multiple readers can read simultaneously
    return data;
} finally {
    readLock.unlock();
}

// Writer
writeLock.lock();
try {
    // Only one writer at a time
    data = newData;
} finally {
    writeLock.unlock();
}
```

**Rules:**
- **Multiple readers**: Có thể đọc đồng thời
- **Single writer**: Chỉ 1 writer tại một thời điểm
- **Reader + Writer**: Không thể đồng thời (writer exclusive)

**Use case**: Cache, Database connection pool (nhiều read, ít write)

#### ⭐ `volatile` Keyword

**Đảm bảo Visibility (Không đảm bảo Atomicity):**

```java
private volatile boolean flag = false;

// Thread 1
flag = true;  // Write → Flush to main memory immediately

// Thread 2
if (flag) {   // Read → Load from main memory (not cache)
    // ...
}
```

**Tại sao cần `volatile`?**

**Vấn đề CPU Cache:**
- Mỗi CPU core có cache riêng
- Thread 1 (Core 1) write `flag = true` → Chỉ update cache của Core 1
- Thread 2 (Core 2) đọc `flag` → Đọc từ cache của Core 2 (cũ) → **Không thấy update!**

**Solution: `volatile`**
- Write → Flush to main memory ngay
- Read → Load from main memory (bypass cache)

**❌ `volatile` KHÔNG đảm bảo Atomicity:**
```java
private volatile int count = 0;

// Thread 1
count++;  // ❌ NOT atomic! (read → increment → write)

// Thread 2
count++;  // ❌ Race condition!
```

**Fix: Dùng `synchronized` hoặc `AtomicInteger`**

---

### 2.3.6. ⭐ Atomic Operations & CAS

#### CAS (Compare-And-Swap)

**Cơ chế:**
```java
// Pseudocode
boolean compareAndSwap(V expected, V newValue) {
    if (currentValue == expected) {
        currentValue = newValue;
        return true;
    }
    return false;
}
```

**Hardware Support:**
- CPU instruction: `CMPXCHG` (x86), `LL/SC` (ARM)
- **Atomic**: Không thể bị interrupt giữa chừng

#### Atomic Classes

**1. AtomicInteger**
```java
AtomicInteger count = new AtomicInteger(0);

// Atomic operations
count.incrementAndGet();        // ++count
count.getAndIncrement();        // count++
count.addAndGet(5);            // count += 5
count.compareAndSet(0, 10);    // if (count == 0) count = 10
```

**2. AtomicLong**
```java
AtomicLong total = new AtomicLong(0);
total.addAndGet(100);
```

**3. AtomicReference**
```java
AtomicReference<String> ref = new AtomicReference<>("initial");

ref.compareAndSet("initial", "updated");
```

**4. AtomicIntegerArray, AtomicLongArray**
```java
AtomicIntegerArray array = new AtomicIntegerArray(10);
array.incrementAndGet(0);  // Atomic increment at index 0
```

**Performance:**
- **CAS** (lock-free) nhanh hơn **synchronized** (lock-based) cho simple operations
- **Nhưng**: CAS có **ABA problem** (giải quyết bằng version number)

**ABA Problem:**
```
Thread 1: Read A
Thread 2: A → B → A (change và change lại)
Thread 1: CAS(A, C) → Success (nhưng A đã bị thay đổi!)
```

**Solution: AtomicStampedReference** (thêm version number)

---

*( Tiếp tục với JVM Tuning ở phần 2.5... )*


## 2.4. IO/NIO (Input/Output)

### 2.4.1. IO Basics

#### IO Stream Classification

Java IO streams phân loại theo nhiều cách:

**Theo hướng:**
*   **Input Stream**: Đọc data từ nguồn (file, network) vào program
*   **Output Stream**: Ghi data từ program ra đích (file, network)

**Theo đơn vị xử lý:**
*   **Byte Stream**: Xử lý binary data (8-bit bytes) - `InputStream`, `OutputStream`
*   **Character Stream**: Xử lý text data (16-bit chars) - `Reader`, `Writer`

#### BIO vs NIO vs AIO

| Model | Tên đầy đủ | Đặc điểm | Khi nào dùng |
|-------|-----------|----------|--------------|
| **BIO** | Blocking IO | Blocking, synchronous | Ít connections, simple |
| **NIO** | Non-blocking IO | Non-blocking, synchronous (với Selector) | Nhiều connections, high concurrency |
| **AIO** | Asynchronous IO | Non-blocking, asynchronous | Very high concurrency (ít dùng trong Java) |

**BIO (Blocking IO):**
*   1 thread per connection
*   Thread bị block khi đợi data
*   Không scale với nhiều connections

**NIO (Non-blocking IO):**
*   **Channels**: Bidirectional data flow
*   **Buffers**: Container for data
*   **Selectors**: Monitor multiple channels with 1 thread
*   1 thread có thể handle nhiều connections

**NIO Core Components:**
1.  **Channel**: `FileChannel`, `SocketChannel`, `ServerSocketChannel`
2.  **Buffer**: `ByteBuffer`, `CharBuffer`, `IntBuffer`
3.  **Selector**: Multiplex I/O operations

---

## 2.5. JVM (Java Virtual Machine)

### 2.5.1. JVM Memory Areas

![Java Runtime Data Areas](https://oss.javaguide.cn/github/javaguide/java/jvm/java-runtime-data-areas-jdk1.8.png)

#### Runtime Data Areas

**Thread-shared (Chia sẻ giữa threads):**

1.  **Heap (Bộ nhớ động)**
    *   Lưu **objects** (hầu hết)
    *   Chia thành: Young Generation (Eden + Survivor) và Old Generation
    *   Garbage Collection chạy ở đây
    *   JVM's largest memory area

2.  **Method Area / Metaspace (JDK 8+)**
    *   Lưu **class metadata**, **static variables**, **constants**
    *   JDK 7-: Method Area (trong heap, có size limit)
    *   JDK 8+: Metaspace (dùng native memory, auto expand)

**Thread-private (Riêng từng thread):**

3.  **Program Counter (PC) Register**
    *   Lưu địa chỉ bytecode instruction hiện tại
    *   Để thread biết chạy tiếp từ đâu sau context switch

4.  **JVM Stack**
    *   Mỗi method call tạo 1 **stack frame**
    *   Stack frame chứa: local variables, operand stack, method return address
    *   `StackOverflowError`: Stack quá sâu (recursive vô hạn)

5.  **Native Method Stack**
    *   Stack cho native methods (C/C++)
    *   HotSpot VM: merge với JVM Stack

### 2.5.2. Garbage Collection (GC)

#### GC Basics

**Tại sao cần GC?**
*   Tự động free memory (không cần manual `delete` như C/C++)
*   Tránh memory leak và dangling pointers

**GC chỉ chạy ở Heap**, không chạy ở stack (stack tự động pop khi method return).

#### Object Reachability

Object được coi là **"rác"** (garbage) khi **không reachable** từ GC Roots.

**GC Roots include:**
*   Local variables trong active stack frames
*   Static variables
*   JNI references
*   Active threads

#### GC Algorithms

**Mark-Sweep (Đánh dấu-Quét):**
1.  **Mark**: Duyệt từ GC roots, đánh dấu objects reachable
2.  **Sweep**: Quét heap, free objects không được mark

**Pros**: Simple  
**Cons**: **Memory fragmentation** (rác rải rác khắp nơi)

**Mark-Compact (Đánh dấu-Nén):**
1.  Mark reachable objects
2.  **Compact**: Di chuyển live objects về một phía, free toàn bộ phía còn lại

**Pros**: No fragmentation  
**Cons**: Chậm hơn (phải move objects)

**Copying (Sao chép):**
*   Chia heap thành 2 vùng: From-space và To-space
*   Copy live objects từ From sang To
*   Sau đó swap roles

**Pros**: Fast, no fragmentation  
**Cons**: Lãng phí 50% memory

#### Generational GC

**Giả thuyết**: Hầu hết objects **"die young"** (sống ngắn).

**Chia heap:**
*   **Young Generation** (objects mới tạo):
    *   Eden: Nơi objects được allocate
    *   Survivor 0, Survivor 1: Chứa objects sống sót sau Minor GC
*   **Old Generation** (objects sống lâu):
    *   Objects survive nhiều Minor GC → promote lên Old

**GC types:**
*   **Minor GC**: GC ở Young Gen (nhanh, thường xuyên)
*   **Major GC / Full GC**: GC ở Old Gen (chậm, ít xuyên)

#### GC Collectors

**Serial GC**: Single-threaded, dùng cho small apps

**Parallel GC**: Multi-threaded, throughput-oriented

**CMS (Concurrent Mark-Sweep)**: Low-latency, deprecated trong JDK 14

**G1 GC (Garbage-First)**: Default từ JDK 9, balance giữa throughput và latency

**ZGC, Shenandoah**: Ultra-low latency GCs (JDK 15+)

### 2.5.3. ⭐ JVM Tuning (Tối ưu JVM)

#### Memory Tuning

**1. Heap Size Configuration**

```bash
# Set heap size
-Xms2g          # Initial heap size (min)
-Xmx4g          # Maximum heap size (max)

# Best practice: Xms = Xmx (tránh dynamic resize)
-Xms4g -Xmx4g
```

**Tại sao Xms = Xmx?**
- Tránh JVM resize heap (tốn CPU)
- Predictable memory usage

**2. Young Generation Size**

```bash
# Set Young Gen size
-Xmn1g          # Young Gen = 1GB

# Hoặc dùng ratio
-XX:NewRatio=2  # Old:Young = 2:1 (Young = 1/3 heap)
```

**Best Practice:**
- Young Gen = 25-50% của heap
- Quá nhỏ → Objects promote lên Old Gen nhanh → Full GC nhiều
- Quá lớn → Minor GC chậm

**3. Metaspace Size (JDK 8+)**

```bash
-XX:MetaspaceSize=256m    # Initial metaspace
-XX:MaxMetaspaceSize=512m # Max metaspace
```

**Lưu ý**: Metaspace dùng native memory, không nằm trong heap.

**4. Stack Size**

```bash
-Xss1m          # Stack size per thread (default: 1MB)
```

**Trade-off:**
- Stack lớn → Ít `StackOverflowError` nhưng tốn memory
- Stack nhỏ → Tiết kiệm memory nhưng dễ overflow

#### GC Tuning

**1. Choose GC Collector**

**G1 GC (Khuyến nghị cho production):**
```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200  # Target pause time (ms)
-XX:G1HeapRegionSize=16m  # Region size
```

**Parallel GC (Throughput-oriented):**
```bash
-XX:+UseParallelGC
-XX:ParallelGCThreads=4  # Number of GC threads
```

**ZGC (Ultra-low latency, JDK 15+):**
```bash
-XX:+UseZGC
-XX:+UnlockExperimentalVMOptions  # JDK 15
```

**2. GC Logging**

```bash
# JDK 8 style
-Xloggc:/path/to/gc.log
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps

# JDK 9+ style (unified logging)
-Xlog:gc*:file=/path/to/gc.log:time,level,tags
```

**3. GC Analysis Tools**

- **GCViewer**: Visualize GC logs
- **jstat**: Real-time GC statistics
  ```bash
  jstat -gc <pid> 1000  # Print GC stats every 1s
  ```

#### Performance Tuning

**1. JIT Compiler**

```bash
# Disable JIT (chỉ dùng để debug)
-Xint

# Tiered compilation (default)
-XX:+TieredCompilation

# Compile threshold
-XX:CompileThreshold=10000  # Compile after 10k invocations
```

**2. String Deduplication (JDK 8u20+)**

```bash
-XX:+UseStringDeduplication  # G1 GC only
```

**Lợi ích**: Giảm memory usage cho duplicate strings.

**3. Compressed OOPs (64-bit JVM)**

```bash
-XX:+UseCompressedOops  # Default: enabled if heap < 32GB
-XX:+UseCompressedClassPointers
```

**Lợi ích**: Giảm memory overhead (object header từ 16 bytes → 12 bytes).

#### Common JVM Options Summary

**Memory:**
```bash
-Xms4g -Xmx4g              # Heap size
-Xmn2g                      # Young Gen
-XX:MetaspaceSize=256m      # Metaspace
```

**GC:**
```bash
-XX:+UseG1GC                # G1 GC
-XX:MaxGCPauseMillis=200    # Target pause
```

**Logging:**
```bash
-Xlog:gc*:file=gc.log:time,level,tags
```

**Performance:**
```bash
-XX:+UseStringDeduplication
-XX:+UseCompressedOops
```

**Debug:**
```bash
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/path/to/dump.hprof
-XX:+PrintGCDetails
```

#### Production JVM Configuration Example

```bash
java -Xms4g \
     -Xmx4g \
     -Xmn2g \
     -XX:MetaspaceSize=256m \
     -XX:MaxMetaspaceSize=512m \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/var/log/heapdump.hprof \
     -Xlog:gc*:file=/var/log/gc.log:time,level,tags \
     -jar myapp.jar
```

---

### 2.5.4. Class Loading

#### Class Lifecycle

```
Loading → Verification → Preparation → Resolution → Initialization → Using → Unloading
```

**Loading**: Đọc `.class` file, tạo `Class` object trong memory

**Verification**: Kiểm tra bytecode hợp lệ (không vi phạm JVM spec)

**Preparation**: Cấp phát memory cho static variables, set default values

**Resolution**: Convert symbolic references → direct references

**Initialization**: Chạy static initializers và static blocks

#### ClassLoader Hierarchy

```
Bootstrap ClassLoader (C++)
    ↓
Extension/Platform ClassLoader
    ↓
Application/System ClassLoader
    ↓
Custom ClassLoaders
```

**Bootstrap**: Load core Java classes (`java.lang.*`, `java.util.*`)

**Extension/Platform**: Load extension classes (JDK 8: Extension, JDK 9+: Platform)

**Application**: Load application classes (từ classpath)

#### Delegation Model

**Parent Delegation**: Trước khi load class, hỏi parent trước. Chỉ load nếu parent không tìm thấy.

**Lợi ích**: Tránh duplicate loading, security (không thể thay thế core classes)

---

## 2.6. New Features (Tính năng mới)

### Java 8 Key Features

#### Lambda Expressions

```java
// Old way
Runnable r1 = new Runnable() {
    @Override
    public void run() {
        System.out.println("Hello");
    }
};

// Lambda
Runnable r2 = () -> System.out.println("Hello");
```

#### Stream API

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// Filter, map, reduce
int sum = numbers.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * 2)
    .reduce(0, Integer::sum);

System.out.println(sum);  // 12 (2*2 + 4*2)
```

#### Optional

```java
Optional<String> opt = Optional.ofNullable(getName());

// Avoid NullPointerException
String name = opt.orElse("Default Name");

// Functional style
opt.ifPresent(n -> System.out.println("Name: " + n));
```

#### Default Methods in Interfaces

```java
public interface MyInterface {
    default void defaultMethod() {
        System.out.println("Default implementation");
    }
}
```

#### Method References

```java
// Lambda
list.forEach(s -> System.out.println(s));

// Method reference
list.forEach(System.out::println);
```

### Java 9+ Highlights

**Java 9:**
*   **Module System** (Project Jigsaw): `module-info.java`
*   **JShell**: Interactive REPL

**Java 10:**
*   **`var` keyword**: Local variable type inference
    ```java
    var list = new ArrayList<String>();  // Type inferred
    ```

**Java 11 (LTS):**
*   **HTTP Client API** (java.net.http)
*   **String methods**: `isBlank()`, `lines()`, `strip()`

**Java 14:**
*   **Switch Expressions**:
    ```java
    int numLetters = switch (day) {
        case MONDAY, FRIDAY, SUNDAY -> 6;
        case TUESDAY -> 7;
        default -> throw new IllegalStateException();
    };
    ```

**Java 15:**
*   **Text Blocks**:
    ```java
    String json = """
        {
            "name": "John",
            "age": 30
        }
        """;
    ```

**Java 16:**
*   **Records**: Compact data carriers
    ```java
    record Person(String name, int age) {}
    ```
*   **Pattern Matching for `instanceof`**:
    ```java
    if (obj instanceof String s) {
        System.out.println(s.length());  // No cast needed
    }
    ```

**Java 17 (LTS):**
*   **Sealed Classes**: Restrict which classes can extend/implement
    ```java
    public sealed class Shape permits Circle, Rectangle {}
    ```

**Java 21 (LTS):**
*   **Virtual Threads** (Project Loom): Lightweight threads
    ```java
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        executor.submit(() -> System.out.println("Virtual thread"));
    }
    ```
*   **Pattern Matching for switch** (finalized)
*   **Sequenced Collections**: `SequencedCollection`, `SequencedSet`, `SequencedMap`

---

## Tổng kết Part 2: Java Core

Đã hoàn thành **Part 2: Java Core** với các nội dung chi tiết:

✅ **2.1. Java Basics**: JVM/JDK/JRE, bytecode, kiểu dữ liệu, biến, methods, OOP, Object class, String  
✅ **2.2. Collections**: List, Set, Queue, Map - cấu trúc, time complexity, fail-fast/safe  
✅ **2.3. Concurrency**: Threads, deadlock, synchronization, locks, **Thread Pool (chi tiết)**, **Atomic Operations**, **CAS**  
✅ **2.4. IO/NIO**: BIO, NIO components (Channels, Buffers, Selectors)  
✅ **2.5. JVM**: Memory areas, GC algorithms, ClassLoaders, **JVM Tuning (Memory, GC, Performance)**  
✅ **2.6. New Features**: Java 8-21 highlights (Lambda, Stream, Records, Virtual Threads)

**Tổng cộng: ~2,800+ dòng** tài liệu Java Core chi tiết bằng tiếng Việt, bao gồm Thread Pool, Locks, Atomic Operations, CAS, JVM Tuning và mọi kiến thức cần thiết cho phỏng vấn và thực hành!

---

*Kết thúc Part 2 - Java Core*





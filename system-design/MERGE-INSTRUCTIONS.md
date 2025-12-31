# HƯỚNG DẪN MERGE ENHANCEMENTS VÀO FILE CHÍNH

## 📋 Tổng Quan

File này hướng dẫn cách merge tất cả nội dung từ `ENHANCEMENTS-Q14-Q20.md` vào `naver-sample-extended.md` một cách chính xác.

---

## ✅ Q14 - RATE LIMITER

### 1. Capacity Estimation Class

**Vị trí trong file chính**: Sau dòng `> 💡 Hệ quả thiết kế: luôn có **TTL**...` (khoảng line 2088)

**Hành động**: Thêm section mới `### 📐 Detailed Capacity Formulas` với toàn bộ Python class từ ENHANCEMENTS

**Nội dung thêm**:
- Class `RateLimiterCapacityEstimator` 
- 4 methods: calculate_redis_ops, calculate_memory, calculate_bandwidth, calculate_latency_budget
- Summary Table

### 2. Sequence Diagram  

**Vị trí**: Sau section "Key Design" (khoảng line 2140)

**Hành động**: Thêm section mới `### 🔄 Sequence Diagram - Rate Limit Check Flow`

**Nội dung thêm**:
- SCENARIO 1: Request Allowed (full ASCII diagram)
- SCENARIO 2: Rate Limit Exceeded
- Key Points in Flow (5 điểm)

### 3. Enhanced Monitoring

**Vị trí**: Sau Phase 5 hoặc trước "Common Questions" (khoảng line 2500+)

**Hành động**: Thêm section `## 📊 Observability & Monitoring (Production-Grade)`

**Nội dung thêm**:
- `RateLimiterMetrics` class
- Prometheus Alert Rules (YAML)
- Grafana Dashboard Queries (SQL)
- Key Metrics to Track table

---

## ✅ Q15 - VIDEO TRANSCODING

### 1. Capacity Estimation Class

**Vị trí**: Thay thế phần Capacity Estimation hiện tại (sau line 2593)

**Hành động**: Thay thế toàn bộ Phase 2 bằng version mới

**Nội dung thay**:
- Class `VideoTranscodingCapacityEstimator`
- 6 methods: QPS, Storage, Compute, Bandwidth, Queue depth
- Summary Table với cost analysis

### 2. Sequence Diagram

**Vị trí**: Trong Phase 3 sau Architecture Overview

**Hành động**: Thêm section `### 🔄 Video Transcoding Flow - Detailed Sequence`

**Nội dung thêm**:
- SCENARIO 1: Successful Transcoding (10+ steps)
- Key Points in Flow

---

## ✅ Q16 - COLLABORATIVE EDITING

### 1. Capacity Estimation Class

**Vị trí**: Phase 2 (sau line ~3100)

**Hành động**: Thêm hoặc thay thế Capacity Estimation

**Nội dung thêm**:
- Class `CollaborativeEditingCapacityEstimator`
- 5 methods: ops throughput, websocket, storage, fanout, conflict resolution
- Summary Table

### 2. Database Schema

**Vị trí**: Phase 4 Deep Dive

**Hành động**: Bổ sung database schema chi tiết nếu chưa có

---

## ✅ Q18 - LOCATION-BASED SERVICE

### 1. Capacity Estimation Class

**Vị trí**: Phase 2

**Hành động**: Thay thế hoàn toàn

**Nội dung thay**:
- Class `LocationBasedServiceCapacityEstimator`
- 6 methods: query throughput, spatial index, tile storage, routing, bandwidth
- Summary Table

### 2. Enhanced PostGIS Schema

**Vị trí**: Phase 4 hoặc section Database Schema

**Hành động**: Thay thế/bổ sung schema hiện có

**Nội dung thay**:
- 6 tables: places, user_saved_places, user_location_history, location_clusters, route_cache
- Tất cả indexes
- 4 Prepared Queries (nearby, bbox, geohash, text search)

---

## ✅ Q19 - AD SERVING

### 1. Capacity Estimation Class

**Vị trí**: Phase 2

**Hành động**: Bổ sung chi tiết

**Nội dung thêm**:
- Class `AdServingCapacityEstimator`  
- 6 methods: serving QPS, latency budget, event stream, user profiles, budget tracking, fraud detection
- Summary Table

---

## ✅ Q20 - ML MODEL SERVING

### 1. Capacity Estimation Class

**Vị trí**: Phase 2

**Hành động**: Bổ sung chi tiết

**Nội dung thêm**:
- Class `MLModelServingCapacityEstimator`
- 6 methods: inference, feature store, model storage, prediction logging, A/B testing, feature pipeline
- Summary Table với GPU vs CPU comparison

---

## 🛠️ CÁCH THỰC HIỆN NHANH

### Option A: Manual Copy-Paste (Recommended)

1. Mở 2 files song song (naver-sample-extended.md và ENHANCEMENTS-Q14-Q20.md)
2. Tìm đúng vị trí trong file chính theo hướng dẫn trên
3. Copy từ ENHANCEMENTS và paste vào đúng vị trí
4. Kiểm tra formatting (đặc biệt code blocks và tables)

### Option B: Search & Replace

Với mỗi section:

1. Search keyword trong file chính (vd: "## 📊 Phase 2: Capacity Estimation (3 phút)" trong Q14)
2. Copy toàn bộ section tương ứng từ ENHANCEMENTS
3. Replace section cũ bằng section mới

### Option C: Script-based (Advanced)

Nếu biết Python/PowerShell, có thể viết script tự động merge dựa trên markers.

---

## ✅ CHECKLIST SAU KHI MERGE

### Kiểm tra Format:

- [ ] Code blocks có đúng syntax highlighting không? (```python, ```sql)
- [ ] Tables render đúng không?
- [ ] ASCII diagrams có giữ nguyên alignment không?
- [ ] Heading levels đúng hierarchy không?

### Kiểm tra Nội dung:

- [ ] Q14: Có Capacity Class, Sequence Diagram, Monitoring không?
- [ ] Q15: Có Capacity Class với cost analysis không?
- [ ] Q16: Có Capacity Class với WebSocket sizing không?
- [ ] Q18: Có PostGIS schema đầy đủ không?
- [ ] Q19: Có Latency budget breakdown không?
- [ ] Q20: Có GPU vs CPU comparison không?

### Kiểm tra Consistency:

- [ ] Tất cả Capacity Estimation đều có Python class?
- [ ] Tất cả Summary Tables đều có 3 columns?
- [ ] Formatting đồng nhất (spacing, headers)?

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi merge xong:

1. **File chính phình to thêm ~5,000-7,000 dòng**
2. **Mỗi Q14-Q20 đều có độ sâu tương đương Q11-Q13**:
   - Capacity Estimation với Python class
   - Database schema production-grade
   - Sequence diagrams chi tiết
   - Monitoring/observability section
3. **Cấu trúc nhất quán** từ đầu đến cuối

---

## 💡 TIPS

1. **Làm từng section nhỏ**, commit/save thường xuyên
2. **Test render** markdown sau mỗi section merge
3. **Giữ backup** file gốc trước khi merge
4. **Double-check** code blocks và tables vì dễ bị lỗi format
5. Nếu quá phức tạp, có thể **giữ riêng file ENHANCEMENTS** làm companion document

---

## 🚀 BẮT ĐẦU MERGE

**Thứ tự đề xuất**:
1. Q14 (Rate Limiter) - đơn giản nhất, test flow
2. Q18 (Location) - có schema lớn, test formatting
3. Q15 (Video) - có sequence diagram dài
4. Q19, Q20, Q16 - hoàn thiện

Chúc bạn merge thành công! 🎉

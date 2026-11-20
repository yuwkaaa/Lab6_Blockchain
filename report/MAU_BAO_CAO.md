# NT547 - LAB 06 - BÁO CÁO (TỰ ĐIỀN)

**MSSV:** ...  | **Họ tên:** ... | **Lớp:** ...
**Session code tự sinh:** SC-...... | **Tên contract:** ...
**Solidity / Slither:** ... / ... | **Ngày hoàn thành:** ...
**URL GitHub repository:** ...

## 1. Static scan (2,0 điểm)

- Lệnh raw: `python tools/scan.py --mode raw --tag before`
- Số lượng finding raw từ `evidence/before_raw/summary.json`:
  - High: ...; Medium: ...; Low: ...; Informational: ...; Optimization: ...
- Chạy configured: `python tools/scan.py --mode configured --tag before`
- So sánh raw/configured: ... (không biến mất High/Medium khi chỉ đổi config)
- 3 detector **khác tên**: ...

| ID finding | Detector | Impact | Confidence | Source (file:dòng) | Luồng dữ liệu: đầu vào -> thao tác -> tác hại |
|---|---|---|---|---|---|
| F01 | | | | | |
| F02 | | | | | |
| F03 | | | | | |

## 2. Triage và sửa lỗi (2,5 điểm)

Đọc toàn bộ AuditTarget.sol: nhận diện **4 mẫu lỗi thật + 2 đoạn cần đánh giá ngữ cảnh**,
kể cả khi Slither không hiển thị đủ 6 cảnh báo. Với mẫu không có detector,
ghi “Manual review / Not reported”, KHÔNG sửa slither.json hoặc tạo finding giả.

| Detector + vị trí | TP / FP / Chưa kết luận | Bằng chứng kiểm soát/khả năng khai thác | Biện pháp (Fix / Accept có lý do) | Sau sửa |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

- Mô tả ít nhất 01 kịch bản khai thác TP: người gọi -> điều kiện -> call/state -> hậu quả: ...
- Phân tích 01 finding có severity cao nhưng risk thực tế không tương ứng: ...
- Dẫn bằng chứng `git diff`, scan before/after và giải thích cảnh báo còn lại: ...
- Lý do của mọi `slither-disable-next-line`: ... (tên detector, đúng vị trí, kiểm soát bù trừ).

## 3. Kiến trúc / Inheritance (1,5 điểm)

- Lệnh printer đã chạy: ...
- Ảnh `evidence/architecture/inheritance.png` (hoặc .dot, nếu Graphviz chưa có): ...
- Access control nằm ở ...; logic số dư nằm ở ...; contract triển khai nằm ở ...
- Giải thích 3–5 câu điểm audit cần bắt đầu: ...

## 4. Red -> Green CI (2,5 điểm)

| Phase | Commit (full/short SHA) | Run URL | Kết quả | Detector khiến RED / lý do GREEN |
|---|---|---|---|---|
| Baseline vulnerable | | | RED | |
| Patched | | | GREEN | |

- So sánh local `--fail-none` (thu thập findings) với CI `fail-on: medium`: ...
- `exclude_low/informational` thay đổi kết quả hiển thị ra sao: ...

## 5. Mutation RED -> GREEN (1,5 điểm)

- Mutation một dòng: `require(msg.sender == owner, "not owner")` -> `require(tx.origin == owner, "not owner")` trong `modifier onlyOwner`.
- Detector kỳ vọng: `tx-origin` (mức Medium); xác nhận của em từ CI: ...

| Phase | Commit SHA | Run URL | Kết quả |
|---|---|---|---|
| Mutation | | | RED |
| Revert mutation | | | GREEN |

- Giải thích sự thay đổi về nguồn định danh/authorization: ...

## 6. Bằng chứng, tự kiểm

- [ ] `AuditTarget.sol`, `lab_identity.json`
- [ ] `evidence/before_raw/` và `evidence/before_configured/`
- [ ] `evidence/after_raw/` và `evidence/after_configured/`
- [ ] `evidence/architecture/`
- [ ] 04 URL Actions run RED/GREEN/RED/GREEN + 04 commit SHA
- [ ] Link repo và ảnh màn hình có terminal / URL / commit SHA; không cắt mất ngữ cảnh
- [ ] Các finding được triage, không chép lại mô tả detector thay cho suy luận
- [ ] Tuyệt đối không có seed phrase, private key, credentials

**Nhận xét cuối cùng (5–7 câu):** ...

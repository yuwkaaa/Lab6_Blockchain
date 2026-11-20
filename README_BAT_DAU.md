# NT547 – Lab 06 | Security Automation & CI/CD

**BẮT ĐẦU TẠI ĐÂY.** Mở `01_HUONG_DAN_LAB06.docx` để xem toàn bộ hướng dẫn, rubric,
troubleshooting và bảng kiểm nộp bài. File này là tóm tắt lệnh thực thi; chạy từ
thư mục `01_SINH_VIEN` (chứa `tools/`, `.github/`, `slither.config.json`).

**Thứ tự bắt buộc:** cài đặt → tạo hợp đồng → scan BEFORE → commit/push CI RED
→ sửa/triage → scan AFTER → commit/push CI GREEN → printers → mutation RED →
revert GREEN → đóng gói bài nộp. Không sửa code trước lần CI RED đầu tiên.

Yêu cầu: Python 3.11 hoặc 3.12, git, Graphviz, Slither 0.11.6, solc 0.8.24,
Internet để cài công cụ / sử dụng GitHub. Windows: khuyến nghị WSL2 Ubuntu.

## 0. Cài đặt (WSL2 Ubuntu / Linux / macOS)

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
solc-select install 0.8.24
solc-select use 0.8.24
python tools/preflight.py
```

Kiểm tra: `solc --version` phải ghi 0.8.24; `slither --version` và `dot -V`.
Trên Ubuntu có thể cài `sudo apt update && sudo apt install git graphviz python3-venv -y`.
Trên macOS: `brew install git graphviz python@3.11` nếu thiếu.

## 1. Cá nhân hoá (thay 23520104 bằng MSSV của BẠN)

```sh
python tools/create_lab.py 23520104
```

Lệnh tự tạo `AuditTarget.sol`, `lab_identity.json` và mã phiên `SC-xxxxxx`.
**Không chạy lại lệnh với `--force` sau khi đã sửa hợp đồng.**

## 2. Quét baseline / lưu bằng chứng

```sh
python tools/scan.py --mode raw --tag before
python tools/scan.py --mode configured --tag before
python tools/print_arch.py
```

Kết quả ở `evidence/`; bảng báo cáo ở `report/MAU_BAO_CAO.md`.

## 3. GitHub CI RED

```sh
git init -b main
git add .
git commit -m "lab06: vulnerable baseline"
```

Tạo repo GitHub rỗng, **không** tạo README trên web; copy URL `<YOUR_REPO_URL>`:

```sh
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

Vào GitHub → Actions → run gần nhất → xác nhận RED do Slither finding.

## 4. Sửa / quét lại / CI GREEN

Đọc mã và nhận diện 4 mẫu lỗi thật + 2 đoạn ngữ cảnh, kể cả khi một số mẫu
Slither không báo (ghi Manual review / Not reported). Sửa tất cả lỗi thật thuộc phạm vi bài; đối với cảnh báo chấp nhận phải có lý do
kỹ thuật, dấu vết trong report, không bỏ trống. Nếu CI chưa GREEN, đọc log và
sửa finding MEDIUM/HIGH còn tồn tại (không dùng `exclude_medium` / `exclude_high`).

```sh
python tools/scan.py --mode raw --tag after
python tools/scan.py --mode configured --tag after
git add .
git commit -m "lab06: fix and triage findings"
git push
```

## 5. Mutation (không cần GV công bố mã)

Trong `AuditTarget.sol`, bên trong `modifier onlyOwner`, **chỉ đổi một dòng**:

- Từ: `require(msg.sender == owner, "not owner");`
- Thành: `require(tx.origin == owner, "not owner");`

```sh
git add AuditTarget.sol
git commit -m "lab06: one-line mutation tx-origin"
git push
# Chụp/ghi nhận RED (tx-origin); sau đó:
git revert --no-edit HEAD
git push
# Chụp/ghi nhận GREEN cuối cùng
```

## 6. Đóng gói bài nộp

Điền report/MAU_BAO_CAO.md rồi chạy:

```sh
python tools/package_submission.py
```

Tệp `submissions/NT547_Lab06_<MSSV>.zip` chứa source/evidence/report/git history.
Script kiểm tra evidence còn thiếu. Trên LMS nộp thêm link GitHub, 4 run URL
RED/GREEN/RED/GREEN và commit SHA. Không gửi private key hoặc secrets. Bảng chấm đủ 10 điểm trong DOCX.

Tài liệu chính thức: https://github.com/crytic/slither ;
https://github.com/crytic/slither-action ;
https://docs.github.com/en/actions .

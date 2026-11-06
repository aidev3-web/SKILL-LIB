---
recipe: kit
version: 1
---
# Soạn Meeting Kit cho một lead

Đầu vào: profile (lấy từ `record.json`, xem dưới), `kit.kyc` và `vars` đã có; `playbook.json` → `qa.bank`.
Đầu ra: `kit.qa`, `kit.objections`, `kit.close_checks`, `kit.videos`, `lead.framework`.
`kit` phải đủ 6 khối: `kyc`, `ask`, `qa`, `objections`, `close_checks`, `videos`. Khối trống ghi `[]`.

0. Lấy profile từ `record.json` (nguồn duy nhất của hồ sơ):
   `node <skill>/tools/add-facts.mjs <slug> --profile` (`<skill>` và `<leads>`: xem SKILL.md).
   Kết quả là `{key: {v, s, src, at, id}}`. Đọc xong mới soạn kit.
1. `kit.qa`: 1–4 nhóm `{"role", "label", "q": [chuỗi]}`, mỗi vai một nhóm, vai `it`, `finance`, `owner`, `ops`, mỗi vai 1–8 câu.
   Bắt đầu từ `qa.bank` rồi chỉnh theo profile (tên phần mềm, quy định, quy trình của ngành).
   `label` là nhãn hiện sau chữ "Ask", ví dụ "IT", "finance", "the owner", "sales and production".
2. `kit.objections`: 3–6 mục `{"if", "then"}`,  khách có thể nói (`if`, không có dấu ngoặc kép) và cách đáp (`then`).
   Dựa trên `risks`, ngân sách, hạn chót, đối thủ tìm được.
   `then` không có số tiền, không hứa phạm vi.
3. `kit.close_checks`: danh sách chuỗi, 1–3 việc cần xin khách trước khi kết thúc buổi họp, riêng cho lead này.
4. `kit.videos`: chọn trong các video Rico có: `{"id": "vCas", "label": "CAS / EIS"}`, `{"id": "vBir", "label": "BIR"}`.
   Một hoặc hai video. Đây là danh sách video duy nhất hiện có (của Rico); playbook chưa có danh sách video. `id` duy nhất, dạng `^v[A-Z][A-Za-z0-9]*$`.
5. `lead.framework`:
   - `a` khi người liên hệ phải tự thuyết phục nội bộ;
   - `b` khi đã quan tâm rõ;
   - `c` khi khách hay im lặng.
6. Không chào theo buổi. Không dùng dấu ngoặc vuông hay ngoặc nhọn trong bất kỳ chữ nào AI viết (bộ kiểm coi mọi `[...]` và `{...}` là chỗ trống). Không có giá trong phần AI viết.
7. Không thêm khối `demo`.
8. Nếu `lead.json` chưa đủ khối thì dựng trước: mọi khóa cấp trên (`slug`, `version`, `playbook_version`, `lead`, `profile`, `vars`, `kit`, `versions`, `runs`) và đủ 6 khối kit.
9. Chạy `python <skill>/tools/build.py <slug> --check` (in `OK`, hoặc danh sách lỗi và mã 1; không ghi file; kiểm cả `record.json` và profile) (lần validate đầu tiên của cả quy trình; sai thì sửa một lần, vẫn sai thì dừng và báo lỗi).
   Công thức dừng ở đây. Không chạy `build.py`: build là bước 4 của skill, chỉ session chính chạy.

# Lab Solution Day09

File này tổng hợp phần đã hoàn thành theo `Lab-assignment-checklist.md` và
`CODELAB.md`.

## 1. Lab trên lớp

### Bài 1.1 - Thay đổi câu hỏi Stage 1

Có thể sửa biến `QUESTION` trong `stages/stage_1_direct_llm/main.py` thành một
câu hỏi pháp lý khác rồi chạy:

```bash
uv run python stages/stage_1_direct_llm/main.py
```

### Bài 1.2 - Temperature control

Đã cập nhật `common/llm.py`:

```python
def get_llm(temperature: float = 0.3) -> ChatOpenAI:
```

Nhờ vậy toàn bộ agent dùng output ổn định hơn, đồng thời vẫn có thể truyền
temperature khác khi cần thử nghiệm.

### Bài 2.1 - Thêm knowledge base entry

Đã thêm entry `labor_law` vào:

- `exercises/exercise_2_tools.py`
- `stages/stage_2_rag_tools/main.py`

Entry bao gồm keyword về lao động, sa thải, hợp đồng lao động, labor,
termination và nội dung tóm tắt Bộ luật Lao động Việt Nam 2019.

### Bài 2.2 - Tạo tool kiểm tra thời hiệu

Đã thêm tool:

```python
@tool
def check_statute_of_limitations(case_type: str) -> str:
```

Tool hỗ trợ:

- `contract`: 4 năm
- `tort`: 2-3 năm tùy bang
- `property`: 5 năm

Tool đã được thêm vào danh sách tools và dispatch handler trong
`exercises/exercise_2_tools.py`.

### Bài 3.1 - Thêm tool tra cứu án lệ

Đã thêm `search_case_law` vào `stages/stage_3_single_agent/main.py` và đưa vào
`TOOLS`.

Tool hỗ trợ các keyword:

- `breach`: Hadley v. Baxendale
- `negligence`: Donoghue v. Stevenson
- `contract`: Carlill v. Carbolic Smoke Ball Co

### Bài 3.2 - Debug agent reasoning

Stage 3 hiện đang dùng `graph.astream(..., stream_mode="updates")` để in rõ các
bước:

- `THINK + ACT`
- `OBSERVE`
- `FINAL ANSWER`

Cách này tương đương mục tiêu quan sát reasoning/tool loop mà không phụ thuộc
tham số `verbose` của từng phiên bản LangGraph.

### Bài 4.1 - Thêm Privacy Agent

Đã implement `privacy_agent` trong `exercises/exercise_4_multiagent.py`.
Agent tập trung vào:

- GDPR
- data protection
- privacy rights
- data breach
- consent
- reporting obligations

Stage 4 demo chính cũng đã được mở rộng thêm `call_privacy_specialist` và
`search_privacy_law`.

### Bài 4.2 - Conditional routing

Đã thêm routing privacy theo keyword:

- `data`
- `privacy`
- `gdpr`
- `dữ liệu`
- `rò rỉ`

Khi câu hỏi liên quan đến privacy, graph sẽ dispatch thêm nhánh privacy song
song với tax và compliance.

### Bài 5.1 - Trace request flow Stage 5

Luồng request theo tài liệu:

```text
User
  -> Customer Agent (:10100)
  -> Registry discover legal_question (:10000)
  -> Law Agent (:10101)
  -> Registry discover tax_question/compliance_question (:10000)
  -> Tax Agent (:10102) + Compliance Agent (:10103)
  -> Law Agent aggregate
  -> Customer Agent
  -> User
```

`trace_id` và `context_id` được truyền qua các hop để theo dõi request.

### Bài 5.2 - Test dynamic discovery

Cách test:

1. Chạy `./start_all.sh`.
2. Dừng Tax Agent.
3. Chạy `uv run python test_client.py`.

Kỳ vọng: hệ thống không crash toàn bộ. Law Agent bắt exception trong `call_tax`
và trả về phần tax analysis unavailable, sau đó vẫn aggregate các phần còn lại.

### Bài 5.3 - Modify agent behavior

Có thể sửa prompt trong `tax_agent/graph.py`, ví dụ thêm yêu cầu trả lời ngắn
gọn, sau đó restart Tax Agent:

```bash
uv run python -m tax_agent
```

## 2. Assignment Supervisor-Workers

Đã tạo thư mục `Lab_Assignment/` theo checklist.

Nội dung:

- `Lab_Assignment/README.md`
- `Lab_Assignment/main.py`
- `Lab_Assignment/agent_interaction_demo.html`

Pattern:

```text
supervisor
  -> contract_worker
  -> tax_worker
  -> compliance_worker
aggregator
```

Chạy:

```bash
uv run python Lab_Assignment/main.py
```

Demo này không cần API key nên phù hợp để chấm nhanh, nhưng vẫn dùng LangGraph
`StateGraph` và `Send` để thể hiện Supervisor - Workers pattern.

## 3. Bài cộng điểm

Đã tạo HTML demo tương tác agent:

```text
Lab_Assignment/agent_interaction_demo.html
```

File này mô phỏng flow Stage 4 và Stage 5, có nút run/reset, event log, các node
agent và elapsed timer trong trình duyệt.

Yêu cầu đo latency thực của Stage 5 cần môi trường runtime Stage 5 và OpenAI
API key thật:

- đo latency khi chạy `test_client.py`, đề xuất và demo cách giảm latency.

`test_client.py` đã in `LATENCY_SECONDS` ở cuối response. Vì máy hiện tại không
có `uv`, lệnh đo thực tế là:

```bash
.venv/bin/python test_client.py
```

Kết quả đo thật ngày 2026-06-10 với `OPENAI_MODEL=gpt-4o-mini`:

```text
LATENCY_SECONDS: 41.73
```

Phương án giảm latency đề xuất:

- dùng model nhanh hơn qua `OPENAI_MODEL`, ví dụ `gpt-4o-mini`;
- nếu quay lại OpenRouter fallback, chọn model nhanh hơn qua `OPENROUTER_MODEL`;
- giữ parallel delegation ở Law Agent;
- cache kết quả discovery từ Registry;
- giảm số vòng LLM/tool calls ở specialist agents;
- đặt timeout và fallback ngắn gọn khi một specialist chậm.

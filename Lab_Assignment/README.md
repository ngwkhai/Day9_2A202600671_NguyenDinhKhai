# Lab Assignment: Supervisor-Workers Agent

Assignment Day09 yêu cầu cải tiến agent Day08 theo pattern Supervisor - Workers
với ít nhất 2-3 workers. Thư mục này chứa một demo độc lập sử dụng LangGraph:

- `supervisor`: đọc câu hỏi và chọn workers cần gọi.
- `contract_worker`: phân tích hợp đồng, trách nhiệm dân sự và remedies.
- `tax_worker`: phân tích rủi ro thuế.
- `compliance_worker`: phân tích tuân thủ, privacy và regulatory exposure.
- `aggregator`: tổng hợp kết quả từ các workers.
- `agent_interaction_demo.html`: demo HTML mô phỏng tương tác Stage 4/Stage 5.

Các worker được dispatch bằng `Send`, nên có thể chạy song song trong graph. Demo
không cần API key để dễ chấm bài; nếu muốn tích hợp LLM thật, có thể thay phần
logic trong từng worker bằng `get_llm().invoke(...)`.

## Chạy demo

```bash
uv run python Lab_Assignment/main.py
```

Có thể truyền câu hỏi riêng:

```bash
uv run python Lab_Assignment/main.py "Cong ty vi pham hop dong, tron thue va lam ro ri du lieu khach hang"
```

Mở demo HTML trực tiếp bằng trình duyệt:

```text
Lab_Assignment/agent_interaction_demo.html
```

## Pattern

```text
START
  -> supervisor
       -> contract_worker
       -> tax_worker
       -> compliance_worker
  -> aggregator
END
```

Nếu câu hỏi không chứa keyword chuyên biệt, supervisor vẫn gọi
`contract_worker` làm worker mặc định để luôn có phân tích nền tảng.

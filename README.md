#  AgriCarbonDEX Multi-Agent LLM System

##  Giới thiệu

Hệ thống này được thiết kế dựa trên kiến trúc **Multi-Agent** – gồm nhiều tác nhân LLM thông minh có khả năng tương tác, phối hợp hoặc hoạt động độc lập nhằm giải quyết các tác vụ phức tạp trong lĩnh vực ESG và tín chỉ carbon.

Mục tiêu chính là cung cấp **trợ lý thông minh** cho người dùng doanh nghiệp trong việc truy vấn, tìm kiếm, phân tích và giải thích thông tin liên quan đến hệ thống AgriCarbonDEX cũng như các kiến thức ESG tổng quát.

---

##  Kiến trúc hệ thống hiện tại

Hệ thống bao gồm một **Manager Agent** điều phối, cùng với hai **tác nhân chức năng chính**:

###  RAG Agent (Retrieval-Augmented Generation)
- Xử lý các câu hỏi liên quan đến **AgriCarbonDEX** như:
  > “AgriCarbonDEX hoạt động như thế nào?”  
  > “Tại sao AgriCarbonDEX được đề xuất?”
- Kết hợp giữa **truy xuất thông tin** và **mô hình sinh câu trả lời** nhằm cung cấp kết quả chính xác, có trích dẫn.

###  Search Agent
- Xử lý các câu hỏi **ngoài phạm vi hệ thống**, ví dụ:
  > “ESG là gì?”  
  > “Cơ chế hoạt động của token ERC-20?”
- Thực hiện tìm kiếm, tổng hợp và trích xuất thông tin từ **nguồn bên ngoài (Web)** để trả lời người dùng.

---

##  Định hướng phát triển (Future Work)

### a) Mở rộng tác nhân chuyên biệt (Specialized Agents)

- **Regulation Agent**  
  Giải thích quy định ESG & Carbon hiện hành từ IPCC, UNFCCC, luật quốc gia. Giúp người dùng hiểu rõ nghĩa vụ pháp lý.

- **ESG Risk Agent**  
  Phát hiện rủi ro liên quan đến **greenwashing** hoặc báo cáo ESG sai lệch.

- **Twin Interpretation Agent**  
  Diễn giải dữ liệu từ **Digital Twin**, giúp người dùng không chuyên hiểu rõ chỉ số phát thải và xu hướng carbon.

---

### b) Tăng cường phối hợp giữa các Agent

Hiện tại, các agent hoạt động theo điều phối của `Manager Agent`. Trong tương lai, hệ thống sẽ:
- Triển khai **giao thức điều phối chung** giữa các agent.
- Cho phép các tác nhân **tự động giao tiếp và chia nhiệm vụ** linh hoạt.

**Ví dụ truy vấn phức tạp**:
> “Tác động của carbon footprint trong chuỗi cung ứng nông nghiệp là gì?”

Sẽ được xử lý tự động như sau:
- **RAG Agent**: Cung cấp thông tin nền.
- **Search Agent**: Tìm dữ liệu thực tế.
- **Twin Interpretation Agent**: Hiển thị trực quan số liệu.
- **ESG Risk Agent**: Phân tích rủi ro ESG.
- **Manager Agent**: Tổng hợp và trình bày câu trả lời rõ ràng, toàn diện.

---

##  Mục tiêu dài hạn

- Hỗ trợ tư vấn ESG chuyên sâu.
- Phân tích dữ liệu carbon thực tế.
- Cung cấp giải pháp trợ lý thông minh đáng tin cậy cho doanh nghiệp.




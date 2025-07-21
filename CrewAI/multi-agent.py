import os
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool
from crewai import LLM, Agent, Crew, Process, Task
# from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import HuggingFaceHub
from huggingface_hub import login
login("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")
os.environ["OPENAI_API_KEY"] = ""



embedder={
"provider": "ollama",
"config": {
    "model": "nomic-embed-text",
    "api_key": "ABCD",
    }
}

# manager_llm = ChatOllama(
#   model="ollama/gemma3:27b",
#   base_url="http://localhost:11434"
# )

llm_local = ChatOllama(
  model="ollama/llama3.1:8b",
  base_url="http://localhost:11434"
)



from crewai import LLM
# OPENAI_API_KEY="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"

manager_llm = LLM(
    model="openai/gpt-4", # call model by provider/model_name
    temperature=0.8,
    max_tokens=250,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    stop=["END"],
    seed=42
)


# 2. Knowledge from PDF
# =======================
content_source = PDFKnowledgeSource(
    file_paths=["AgriCarbonDEX.pdf"]  # hoặc đường dẫn chính xác trên máy bạn
)


RAG_agent = Agent(
    name="RAG Agent",  # <- THÊM TÊN RÕ RÀNG
    role="RAG Analyst",
    goal="Hiểu rõ hệ thống AgriCarbonDEX và trả lời các câu hỏi liên quan.",
    backstory="Bạn là chuyên gia nắm rõ toàn bộ tài liệu AgriCarbonDEX.",
    llm=llm_local,
    embedder = embedder,
    knowledge_sources=[content_source],
    allow_delegation=True,
    verbose=True,
    max_iter=2,
)

rag_task = Task(
    description="Trả lời câu hỏi sau về hệ thống AgriCarbonDEX: {question}",
    expected_output="Một đoạn văn giải thích rõ ràng về hệ thống.",
    agent=RAG_agent
)



# =======================
# =======================
# 3. Web Scrape Agent
# =======================

# ✅ Các công cụ quét dữ liệu từ web
tool1 = ScrapeWebsiteTool(website_url="https://www.vinacontrol.com.vn/news/Thi-truong-carbon")
tool2 = ScrapeWebsiteTool(website_url="https://baochinhphu.vn/hinh-thanh-thi-truong-tin-chi-carbon-rung-cua-viet-nam-102240331060535888.htm")

# ✅ Định nghĩa Agent thực hiện scraping
scrape_agent = Agent(
    role="Chuyên gia thu thập dữ liệu ESG",
    goal="Tự động tìm kiếm và tổng hợp thông tin ESG, tín chỉ carbon từ các nguồn web đáng tin cậy.",
    backstory=(
        "Bạn là một chuyên gia giàu kinh nghiệm trong việc khai thác dữ liệu từ các trang web "
        "liên quan đến môi trường, tín chỉ carbon và ESG. Mục tiêu của bạn là trích xuất thông tin chính xác "
        "và tạo ra bản tóm tắt súc tích, dễ hiểu cho nhóm nghiên cứu."
    ),
    tools=[tool1, tool2],
    llm=llm_local,
    allow_delegation=True,
    verbose=True,
    max_iter=2,
)

# ✅ Task tương ứng cho scrape agent
scrape_task = Task(
    description=(
        "Tìm kiếm và tóm tắt thông tin chi tiết về chủ đề: '{question}'. "
        "Dựa trên nội dung lấy được từ các trang web, hãy tạo ra bản tóm tắt thể hiện định nghĩa, "
        "ý nghĩa và vai trò của chủ đề một cách ngắn gọn, rõ ràng."
    ),
    expected_output=(
        "Một đoạn tóm tắt khoảng 5–10 dòng, trình bày khái niệm, vai trò và mức độ liên quan của chủ đề đến ESG hoặc tín chỉ carbon."
    ),
    agent=scrape_agent
)

# =======================
# 4. Manager Agent
# =======================
manager = Agent(
    role="Project Manager",
    goal="Điều phối các chuyên gia để hoàn thành báo cáo phân tích hệ thống và thị trường.",
    backstory="Một quản lý dày dạn, có khả năng phân phối nhiệm vụ và tổng hợp kết quả hiệu quả.",
    allow_delegation=True,
    llm=manager_llm, 
    verbose=True,
    max_iter=2,
)

manager_task = Task(
    description=(
        "Chỉ đạo nhóm gồm một RAG agent và một Web Scraper để trả lời câu hỏi sau: '{question}'. "
        "Phối hợp các chuyên gia để tổng hợp thành một báo cáo đầy đủ dựa trên dữ liệu từ tài liệu PDF và các website ESG."
    ),
    expected_output="Một báo cáo phân tích tầm 4-6 dòng liên quan đến '{question}'.",
    agent=manager
)

# =======================
# 5. Crew cấu trúc phân cấp
# =======================



crew = Crew(
    agents=[manager, RAG_agent, scrape_agent],
    tasks=[manager_task],
    process=Process.hierarchical,
    manager_llm=manager_llm,
    verbose=True,
    max_iter=2  # 🛑 stop after 5 interactions

)

try:
    result = crew.kickoff(
        inputs={"question": "Thị trường tín chỉ carbon đang như nào?"}
    )
    print("======== KẾT QUẢ =========")
    print(result)
except Exception as e:
    print("❌ Đã xảy ra lỗi:")
    print(e)



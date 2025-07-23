import re
import html
from clss import CrewAIRAGSystem  # Import RAG system của chúng ta
import traceback
import time
from datetime import datetime

def clean_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def format_thinking_process(log_text: str) -> str:
    """Format thinking process for RAG system"""
    if not log_text:
        return "🤖 RAG Agent đang xử lý câu hỏi..."
    
    # Clean and format RAG logs
    text = clean_ansi_codes(log_text)
    text = re.sub(r'🚀.*?Crew.*?Started.*?\n', '<div class="thinking-block">🚀 <strong>Khởi động RAG Crew</strong></div>\n', text)
    text = re.sub(r'🔍.*?Knowledge Retrieval Started.*?\n', '<div class="thinking-block">🔍 <strong>Đang tìm kiếm trong tài liệu...</strong></div>\n', text)
    text = re.sub(r'✅.*?Knowledge Retrieval Completed.*?\n', '<div class="thinking-block">✅ <strong>Hoàn thành tìm kiếm tài liệu</strong></div>\n', text)
    text = re.sub(r'🤖.*?Agent Started.*?\n', '<div class="thinking-block">🤖 <strong>Agent đang phân tích...</strong></div>\n', text)
    text = re.sub(r'🧠.*?Thinking.*?\n', '<div class="thinking-block">🧠 <strong>Đang suy nghĩ...</strong></div>\n', text)
    text = re.sub(r'✅.*?Agent Final Answer.*?\n', '<div class="thinking-block">✅ <strong>Đã có câu trả lời</strong></div>\n', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

def polish_final_answer(text: str) -> str:
    """Polish the final answer"""
    if not text:
        return "Xin lỗi, không thể tạo câu trả lời."
    
    # Convert to string if it's not already
    text = str(text)
    
    # Clean up common formatting issues
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text

class MultiAgent:
    """RAG-powered Multi-Agent Chatbot"""
    
    def __init__(self):
        print("🚀 Initializing RAG Multi-Agent Chatbot...")
        self.agent = None
        self.rag_system = None
        
        try:
            # Initialize RAG system
            self.rag_system = CrewAIRAGSystem(
                model_name="ollama/llama3.1:8b",
                base_url="http://localhost:11434",
                pdf_path="AgriCarbonDEX.pdf",
                temperature=0.7
            )
            
            # Set agent to non-None to indicate success
            self.agent = "RAG_READY"
            print("✅ RAG Multi-Agent initialized successfully.")
            
        except Exception as e:
            print(f"❌ Error initializing RAG system: {e}")
            print(traceback.format_exc())
            self.rag_system = None
            self.agent = None
            print("⚠️ Chatbot will not be functional.")
    
    def get_answer(self, question: str) -> tuple[str, str]:
        """
        Get answer from RAG system
        Returns: (answer, thinking_steps)
        """
        if not self.agent or not self.rag_system:
            return (
                "❌ RAG system không khả dụng. Vui lòng kiểm tra server logs.", 
                "Hệ thống RAG chưa được khởi tạo thành công."
            )
        
        print(f"📝 Processing RAG question: {question}")
        start_time = datetime.now()
        
        # Generate thinking steps for UI
        thinking_steps = f"""
        <div class="thinking-block">🚀 <strong>Bắt đầu xử lý câu hỏi</strong></div>
        <div class="thinking-block">📝 <strong>Câu hỏi:</strong> {html.escape(question)}</div>
        <div class="thinking-block">⏰ <strong>Thời gian bắt đầu:</strong> {start_time.strftime('%H:%M:%S')}</div>
        <div class="thinking-block">🔍 <strong>Đang tìm kiếm trong tài liệu AgriCarbonDEX...</strong></div>
        <div class="thinking-block">🤖 <strong>RAG Agent đang phân tích...</strong></div>
        <div class="thinking-block">⏳ <strong>Quá trình này có thể mất 2-4 phút...</strong></div>
        """
        
        try:
            # Execute RAG query (single agent for faster response)
            print("🤖 Executing RAG query...")
            result = self.rag_system.execute_single_agent(question, agent_index=0)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Check if result is error
            if isinstance(result, str) and ("error" in result.lower() or "failed" in result.lower()):
                error_thinking = thinking_steps + f"""
                <div class="thinking-block">❌ <strong>Lỗi:</strong> {html.escape(str(result))}</div>
                <div class="thinking-block">⏱️ <strong>Thời gian xử lý:</strong> {execution_time:.1f} giây</div>
                """
                return (
                    "❌ Xin lỗi, đã xảy ra lỗi trong quá trình xử lý. Vui lòng thử lại sau.",
                    error_thinking
                )
            
            # Success case
            polished_answer = polish_final_answer(str(result))
            
            success_thinking = thinking_steps + f"""
            <div class="thinking-block">✅ <strong>Tìm thấy thông tin trong tài liệu</strong></div>
            <div class="thinking-block">🧠 <strong>RAG Agent đã phân tích và tổng hợp câu trả lời</strong></div>
            <div class="thinking-block">⏱️ <strong>Thời gian xử lý:</strong> {execution_time/60:.1f} phút</div>
            <div class="thinking-block">📊 <strong>Nguồn:</strong> Tài liệu AgriCarbonDEX</div>
            <div class="thinking-block">✅ <strong>Hoàn thành câu trả lời</strong></div>
            """
            
            print(f"✅ RAG query completed in {execution_time/60:.1f} minutes")
            
            return polished_answer, success_thinking
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            error_message = f"Lỗi RAG system: {str(e)}"
            print(f"❌ {error_message}")
            print(traceback.format_exc())
            
            error_thinking = thinking_steps + f"""
            <div class="thinking-block">❌ <strong>Lỗi xử lý:</strong> {html.escape(error_message)}</div>
            <div class="thinking-block">⏱️ <strong>Thời gian trước khi lỗi:</strong> {execution_time:.1f} giây</div>
            <div class="thinking-block">💡 <strong>Gợi ý:</strong> Vui lòng thử lại sau hoặc đặt câu hỏi khác</div>
            """
            
            return (
                "❌ Xin lỗi, đã xảy ra lỗi trong quá trình xử lý. Vui lòng thử lại với câu hỏi khác.", 
                error_thinking
            )

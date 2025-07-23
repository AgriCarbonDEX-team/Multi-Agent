import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
import traceback

class CrewAIRAGSystem:
    def __init__(self, 
                 model_name="ollama/llama3.1:8b",
                 base_url="http://localhost:11434", 
                 pdf_path="AgriCarbonDEX.pdf",
                 temperature=0.7):
        """
        Initialize CrewAI RAG System
        
        Args:
            model_name (str): Ollama model name
            base_url (str): Ollama server URL
            pdf_path (str): Path to PDF file
            temperature (float): LLM temperature
        """
        self.model_name = model_name
        self.base_url = base_url
        self.pdf_path = pdf_path
        self.temperature = temperature
        
        # Initialize components
        self.llm = None
        self.embedder = None
        self.content_source = None
        self.agents = []
        self.tasks = []
        self.crew = None
        
        # Setup the system
        self._setup_llm()
        self._setup_embedder()
        self._setup_knowledge_source()
        self._setup_agents()
        self._setup_tasks()
        self._setup_crew()
        
    def _setup_llm(self):
        """Setup LLM configuration"""
        try:
            self.llm = LLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature
            )
            print("✅ LLM setup successful")
        except Exception as e:
            print(f"❌ LLM setup failed: {e}")
            raise
    
    def _setup_embedder(self):
        """Setup embedder configuration"""
        self.embedder = {
            "provider": "ollama",
            "config": {
                "model": "nomic-embed-text",
            }
        }
        print("✅ Embedder setup successful")
    
    def _setup_knowledge_source(self):
        """Setup PDF knowledge source"""
        try:
            self.content_source = PDFKnowledgeSource(
                file_paths=[self.pdf_path]
            )
            print("✅ PDF knowledge source loaded successfully")
        except FileNotFoundError:
            print(f"❌ File {self.pdf_path} not found!")
            raise
        except Exception as e:
            print(f"❌ PDF loading error: {e}")
            raise
    
    def _setup_agents(self):
        """Setup all agents"""
        try:
            # RAG Analyst Agent
            rag_agent = Agent(
                role="RAG Analyst",
                goal="Trả lời câu hỏi về hệ thống AgriCarbonDEX dựa trên tài liệu.",
                backstory="Bạn là chuyên gia nắm rõ tài liệu AgriCarbonDEX và có khả năng phân tích thông tin chi tiết.",
                llm=self.llm,
                embedder=self.embedder,
                knowledge_sources=[self.content_source],
                allow_delegation=False,
                verbose=True,
                max_iter=1,
            )
            
            # Content Summarizer Agent (additional agent)
            summarizer_agent = Agent(
                role="Content Summarizer", 
                goal="Tóm tắt thông tin từ tài liệu AgriCarbonDEX.",
                backstory="Bạn là chuyên gia tóm tắt nội dung, có khả năng trích xuất những điểm chính từ tài liệu phức tạp.",
                llm=self.llm,
                embedder=self.embedder,
                knowledge_sources=[self.content_source],
                allow_delegation=False,
                verbose=True,
                max_iter=1,
            )
            
            self.agents = [rag_agent, summarizer_agent]
            print(f"✅ {len(self.agents)} agents setup successful")
            
        except Exception as e:
            print(f"❌ Agents setup failed: {e}")
            raise
    
    def _setup_tasks(self):
        """Setup all tasks"""
        try:
            # RAG Task
            rag_task = Task(
                description=
                """
                Phân tích câu hỏi: {question}
                
                Nếu câu hỏi quá ngắn (1-2 từ) hoặc không rõ ràng, hãy yêu cầu người dùng đặt câu hỏi cụ thể hơn.
                Nếu câu hỏi không liên quan đến nội dung tài liệu, hãy trả lời rằng thông tin không có trong tài liệu.
                Chỉ trả lời dựa trên tài liệu khi câu hỏi có liên quan.
                """,
                expected_output="Câu trả lời chi tiết về AgriCarbonDEX dựa trên nội dung tài liệu.",
                agent=self.agents[0]  # RAG Analyst
            )
            
            # Summary Task
            summary_task = Task(
                description="Tóm tắt thông tin chính liên quan đến câu hỏi: {question}",
                expected_output="Bản tóm tắt ngắn gọn các điểm chính từ tài liệu.",
                agent=self.agents[1]  # Content Summarizer
            )
            
            self.tasks = [rag_task, summary_task]
            print(f"✅ {len(self.tasks)} tasks setup successful")
            
        except Exception as e:
            print(f"❌ Tasks setup failed: {e}")
            raise
    
    def _setup_crew(self):
        """Setup crew with all agents and tasks"""
        try:
            self.crew = Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.sequential,
                verbose=True
            )
            print("✅ Crew setup successful")
            
        except Exception as e:
            print(f"❌ Crew setup failed: {e}")
            raise
    
    def execute_query(self, question):
        """
        Execute query using all agents
        
        Args:
            question (str): Question to ask
            
        Returns:
            str: Combined result from all agents
        """
        try:
            print(f"🚀 Starting query execution...")
            print(f"📝 Question: {question}")
            
            result = self.crew.kickoff(
                inputs={"question": question}
            )
            
            print("======== KẾT QUẢ TỪ TẤT CẢ AGENTS =========")
            return result
            
        except Exception as e:
            error_msg = f"❌ Query execution failed: {type(e).__name__}: {e}"
            print(error_msg)
            print("\n🔍 Stack trace:")
            traceback.print_exc()
            return error_msg
    
    def execute_single_agent(self, question, agent_index=0):
        """
        Execute query using single agent
        
        Args:
            question (str): Question to ask
            agent_index (int): Index of agent to use (0 for RAG, 1 for Summarizer)
            
        Returns:
            str: Result from specified agent
        """
        try:
            if agent_index >= len(self.agents):
                return f"❌ Agent index {agent_index} out of range. Available agents: {len(self.agents)}"
            
            # Create single agent crew
            single_crew = Crew(
                agents=[self.agents[agent_index]],
                tasks=[self.tasks[agent_index]],
                process=Process.sequential,
                verbose=True
            )
            
            print(f"🚀 Starting single agent execution (Agent {agent_index})...")
            
            result = single_crew.kickoff(
                inputs={"question": question}
            )
            
            return result
            
        except Exception as e:
            error_msg = f"❌ Single agent execution failed: {type(e).__name__}: {e}"
            print(error_msg)
            return error_msg
    
    def get_agent_info(self):
        """Get information about all agents"""
        agent_info = []
        for i, agent in enumerate(self.agents):
            info = {
                "index": i,
                "role": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory
            }
            agent_info.append(info)
        return agent_info
    
    def update_pdf(self, new_pdf_path):
        """Update PDF knowledge source"""
        try:
            self.pdf_path = new_pdf_path
            self._setup_knowledge_source()
            self._setup_agents()  # Recreate agents with new knowledge source
            self._setup_tasks()   # Recreate tasks
            self._setup_crew()    # Recreate crew
            print(f"✅ PDF updated to: {new_pdf_path}")
            
        except Exception as e:
            print(f"❌ PDF update failed: {e}")


# Usage Example
if __name__ == "__main__":
    try:
        # Initialize RAG System
        rag_system = CrewAIRAGSystem(
            model_name="ollama/llama3.1:8b",
            base_url="http://localhost:11434",
            pdf_path="AgriCarbonDEX.pdf",
            temperature=0.7
        )
        
        # Show agent information
        print("\n📋 THÔNG TIN AGENTS:")
        for info in rag_system.get_agent_info():
            print(f"Agent {info['index']}: {info['role']} - {info['goal']}")
        
        # Execute query with all agents
        print("\n" + "="*50)
        result = rag_system.execute_query("AgriCarbonDEX là gì?")
        print(result)
        
        # Execute with single agent (optional)
        print("\n" + "="*50)
        print("🔄 Testing single agent execution...")
        single_result = rag_system.execute_single_agent("Tóm tắt về carbon trading", agent_index=1)
        print(single_result)
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")

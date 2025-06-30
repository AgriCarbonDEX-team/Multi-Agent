# import re
# import requests
# from markdownify import markdownify as md
# from requests.exceptions import RequestException
# from smolagents import tool, DuckDuckGoSearchTool, InferenceClientModel, ToolCallingAgent

# # --- Định nghĩa Tool visit_webpage ---
# @tool
# def visit_webpage(url: str) -> str:
#     """Visits a webpage at the given URL and returns its content as a markdown string.

#     Args:
#         url: The URL of the webpage to visit.

#     Returns:
#         The content of the webpage converted to Markdown, or an error message if the request fails.
#     """
#     try:
#         # Send a GET request to the URL with a timeout for robustness
#         response = requests.get(url, timeout=15) # Added timeout
#         response.raise_for_status()  # Raise an exception for bad status codes

#         # Convert the HTML content to Markdown
#         markdown_content = md(response.text).strip()

#         # Remove multiple line breaks (3 or more become 2)
#         markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

#         # Limit content length to avoid exceeding LLM context window
#         max_content_length = 4000 # Adjust as needed, a common safe upper limit
#         if len(markdown_content) > max_content_length:
#             markdown_content = markdown_content[:max_content_length] + "\n\n... [Content truncated]"

#         return markdown_content

#     except RequestException as e:
#         return f"Error fetching the webpage: {str(e)}"
#     except Exception as e:
#         return f"An unexpected error occurred: {str(e)}"

# # --- Định nghĩa lớp BasicChatBot ---
# class MultiAgent:
#     def __init__(self):
#         print("Initializing Chatbot...")
#         try:
#             # Khởi tạo model
#             self.model = InferenceClientModel("Qwen/Qwen2.5-7B-Instruct")
#             print("Model initialized successfully.")

#             # Khởi tạo agent
#             self.agent = ToolCallingAgent(
#                 tools=[DuckDuckGoSearchTool(), visit_webpage],
#                 model=self.model,
#                 name="search_agent",
#                 description="Runs web searches for you and visits webpages to gather information."
#             )
#             print("Agent initialized successfully.")
#         except Exception as e:
#             self.model = None
#             self.agent = None
#             print(f"Error during chatbot initialization: {e}")
#             print("Chatbot will not be functional.")


#     def get_answer(self, question: str) -> str:
#         if not self.agent:
#             return "Chatbot is not fully initialized. Please check server logs for errors."
        
#         print(f"Processing question: {question}")
#         try:
#             # Gọi agent để lấy câu trả lời
#             # search_agent là một đối tượng có thể gọi được (callable)
#             answer = self.agent(question)
#             print(f"Agent provided answer.")
#             return answer
#         except Exception as e:
#             # Bắt các lỗi xảy ra trong quá trình agent hoạt động (ví dụ: lỗi JSON parsing)
#             print(f"Error from agent during processing: {e}")


# query.py

import re
import requests
import time
import random
from markdownify import markdownify as md
from requests.exceptions import RequestException
from smolagents import tool, DuckDuckGoSearchTool, InferenceClientModel, ToolCallingAgent
import io
import contextlib
import html

# --- (Các hàm clean_ansi_codes, format_thinking_process, visit_webpage, smart_web_search giữ nguyên) ---
def clean_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def format_thinking_process(log_text: str) -> str:
    text = clean_ansi_codes(log_text)
    text = re.sub(r'╭─+ New run.*?─╯\n', '', text, flags=re.DOTALL)
    text = re.sub(r'━━━━━━━━━━━━ Step (\d+) ━━━━━━━━━━━━', r'<hr><strong>Step \1</strong>', text)
    def format_tool_call(match):
        tool_name = match.group(1)
        tool_args = match.group(2)
        if tool_name == 'final_answer':
            return '<div class="thinking-block">✅ Agent đang tổng hợp câu trả lời cuối cùng...</div>'
        return f'<div class="thinking-block"><strong>Calling tool:</strong> <code>{tool_name}</code><br><strong>Arguments:</strong> <code>{html.escape(tool_args)}</code></div>'
    text = re.sub(r"╭─+\n│ Calling tool: '(\w+)' with arguments: (\{.*?\})\s*│\n╰─*?─╯", format_tool_call, text, flags=re.DOTALL)
    text = re.sub(r"Observations:", r"<strong>Observations:</strong>", text)
    text = re.sub(r"(Error executing tool.*)", r"<strong>\1</strong>", text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as a markdown string.

    Args:
        url (str): The URL of the webpage to visit.
    """
    #... (nội dung hàm giữ nguyên)
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        markdown_content = md(response.text).strip()
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
        max_content_length = 4000
        if len(markdown_content) > max_content_length:
            markdown_content = markdown_content[:max_content_length] + "\n\n... [Content truncated]"
        return markdown_content
    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

@tool
def smart_web_search(query: str, max_retries: int = 2) -> str:
    """
    Performs a web search using DuckDuckGo with a smart retry mechanism to handle rate limiting.
    Args:
        query (str): The search query.
        max_retries (int): The maximum number of times to retry if a rate limit error occurs.
    Returns:
        The search results or an error message.
    """
    #... (nội dung hàm giữ nguyên)
    ddg_search = DuckDuckGoSearchTool()
    for attempt in range(max_retries + 1):
        try:
            print(f"Attempt {attempt + 1} to search for: '{query}'")
            return ddg_search(query)
        except Exception as e:
            if "Ratelimit" in str(e) and attempt < max_retries:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit. Waiting for {wait_time:.2f} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print(f"Failed to search after {attempt + 1} attempts. Error: {e}")
                return f"Error: The search tool failed after multiple retries. Please try again later. Details: {e}"


# +++ NEW: HÀM LÀM ĐẸP VĂN BẢN TRẢ VỀ +++
def polish_final_answer(text: str) -> str:
    """
    "Làm đẹp" văn bản cuối cùng bằng cách sửa các lỗi ngắt dòng không mong muốn.
    """
    # Danh sách các cụm từ cần "dán" lại với nhau
    replacements = {
        "độ pH": "độ pH",
        "Độ pH": "Độ pH",
        "TP. HCM": "TP. HCM"
        # Bạn có thể thêm các trường hợp khác vào đây trong tương lai
    }
    for find, replace in replacements.items():
        text = text.replace(find, replace)
    return text

# --- Lớp MultiAgent ---
class MultiAgent:
    def __init__(self):
        # ... (nội dung hàm giữ nguyên)
        print("Initializing Chatbot...")
        try:
            self.model = InferenceClientModel("Qwen/Qwen2.5-7B-Instruct")
            print("Model initialized successfully.")
            self.agent = ToolCallingAgent(
                tools=[smart_web_search, visit_webpage], 
                model=self.model,
                name="search_agent",
                description="Runs web searches for you and visits webpages to gather information."
            )
            print("Agent initialized successfully with smart search.")
        except Exception as e:
            self.model = None
            self.agent = None
            print(f"Error during chatbot initialization: {e}")
            print("Chatbot will not be functional.")

    def get_answer(self, question: str) -> tuple[str, str]:
        if not self.agent:
            return "Chatbot is not fully initialized. Please check server logs for errors.", "Chatbot không khả dụng."
        
        print(f"Processing question: {question}")
        thinking_log_stream = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(thinking_log_stream):
                # Giả sử agent trả về một chuỗi duy nhất
                final_answer_text = self.agent(question)
            
            raw_thinking_steps = thinking_log_stream.getvalue()
            formatted_steps = format_thinking_process(raw_thinking_steps)
            
            # === FIX HERE: GỌI HÀM LÀM ĐẸP MỚI ===
            polished_answer = polish_final_answer(final_answer_text)
            
            return polished_answer, formatted_steps
            
        except Exception as e:
            error_message = f"Lỗi từ agent trong quá trình xử lý: {e}"
            print(error_message)
            raw_thinking_steps = thinking_log_stream.getvalue()
            cleaned_thinking_steps = clean_ansi_codes(raw_thinking_steps) + f"\n\nERROR: {error_message}"
            return "Xin lỗi, đã xảy ra lỗi trong quá trình xử lý. Vui lòng thử lại.", cleaned_thinking_steps
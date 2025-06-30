# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from query import MultiAgent # Import BasicChatBot từ file query.py
# from dotenv import load_dotenv
# import os

# app = Flask(__name__)
# CORS(app) # Cho phép Cross-Origin Resource Sharing (quan trọng cho frontend)
# load_dotenv(".env") # Tải biến môi trường (nếu có API key, token...)

# # Khởi tạo chatbot một lần khi server khởi động
# # Nếu quá trình khởi tạo thất bại (ví dụ: không kết nối được LLM),
# # self.chatbot sẽ là None hoặc có lỗi.
# chatbot = None
# try:
#     chatbot = MultiAgent()
#     if chatbot.agent is None: # Kiểm tra xem agent có được khởi tạo thành công không
#         print("Chatbot agent failed to initialize in BasicChatBot.__init__.")
# except Exception as e:
#     print(f"Failed to instantiate BasicChatBot: {e}")
#     chatbot = None # Đảm bảo chatbot là None nếu có lỗi khởi tạo


# @app.route('/ask', methods=['POST'])
# def ask():
#     # Kiểm tra xem chatbot đã được khởi tạo thành công chưa
#     if chatbot is None or chatbot.agent is None:
#         return jsonify({"error": "Chatbot service is not available. Please check server logs for initialization errors."}), 503

#     data = request.get_json()
#     if not data or 'question' not in data or not data['question']:
#         return jsonify({"error": "Question is missing or empty."}), 400

#     try:
#         question = data['question']
#         print(f"Received question: {question}")
#         answer = chatbot.get_answer(question) # Gọi phương thức get_answer từ đối tượng chatbot
#         print(f"Sending answer: {answer[:100]}...") # In ra một phần câu trả lời để debug
#         return jsonify({"answer": answer})
#     except Exception as e:
#         print(f"Error processing /ask request: {e}")
#         return jsonify({"error": f"An error occurred while processing your question: {e}"}), 500

# @app.route('/')
# def mainPage():
#     return "Backend server is running."

# if __name__ == "__main__":
#     # Chạy Flask app
#     # debug=True sẽ tự động reload server khi có thay đổi code và hiển thị lỗi chi tiết
#     # port=3000 là cổng mà server sẽ lắng nghe
#     app.run(debug=True, port=3000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from query import MultiAgent # Import BasicChatBot từ file query.py
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app) # Cho phép Cross-Origin Resource Sharing (quan trọng cho frontend)
load_dotenv(".env") # Tải biến môi trường (nếu có API key, token...)

# Khởi tạo chatbot một lần khi server khởi động
# Nếu quá trình khởi tạo thất bại (ví dụ: không kết nối được LLM),
# self.chatbot sẽ là None hoặc có lỗi.
chatbot = None
try:
    chatbot = MultiAgent()
    if chatbot.agent is None: # Kiểm tra xem agent có được khởi tạo thành công không
        print("Chatbot agent failed to initialize in BasicChatBot.__init__.")
except Exception as e:
    print(f"Failed to instantiate BasicChatBot: {e}")
    chatbot = None # Đảm bảo chatbot là None nếu có lỗi khởi tạo


@app.route('/ask', methods=['POST'])
def ask():
    # Kiểm tra xem chatbot đã được khởi tạo thành công chưa
    if chatbot is None or chatbot.agent is None:
        return jsonify({"error": "Chatbot service is not available. Please check server logs for initialization errors."}), 503

    data = request.get_json()
    if not data or 'question' not in data or not data['question']:
        return jsonify({"error": "Question is missing or empty."}), 400

    try:
        question = data['question']
        print(f"Received question: {question}")
        
        # Gọi phương thức get_answer từ đối tượng chatbot
        # Bây giờ nó trả về cả câu trả lời và các bước suy nghĩ
        answer, thinking_steps = chatbot.get_answer(question) 
        
        print(f"Sending answer: {answer[:100]}...") # In ra một phần câu trả lời để debug
        print(f"Thinking steps: {thinking_steps}") # In ra các bước suy nghĩ để debug

        # Gửi cả câu trả lời và các bước suy nghĩ về frontend
        return jsonify({"answer": answer, "thinking_steps": thinking_steps})
    except Exception as e:
        print(f"Error processing /ask request: {e}")
        # Đảm bảo gửi cả bước suy nghĩ lỗi nếu có
        return jsonify({"error": f"An error occurred while processing your question: {e}", "thinking_steps": ["Lỗi: " + str(e)]}), 500

@app.route('/')
def mainPage():
    return "Backend server is running."

if __name__ == "__main__":
    # Chạy Flask app
    # debug=True sẽ tự động reload server khi có thay đổi code và hiển thị lỗi chi tiết
    # port=3000 là cổng mà server sẽ lắng nghe
    app.run(debug=True, port=3000)
    
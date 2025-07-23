from flask import Flask, request, jsonify
from flask_cors import CORS
from ChatbotResponse import MultiAgent  # Import RAG MultiAgent
from dotenv import load_dotenv
import os
import time

app = Flask(__name__)
CORS(app)
load_dotenv(".env")

# Initialize RAG chatbot
chatbot = None
try:
    print("🚀 Initializing RAG Chatbot Backend...")
    chatbot = MultiAgent()
    if chatbot.agent is None:
        print("❌ RAG Chatbot agent failed to initialize.")
    else:
        print("✅ RAG Chatbot initialized successfully.")
except Exception as e:
    print(f"❌ Failed to instantiate RAG Chatbot: {e}")
    chatbot = None

@app.route('/ask', methods=['POST'])
def ask():
    """Handle question requests with RAG processing"""
    
    # Check if chatbot is available
    if chatbot is None or chatbot.agent is None:
        return jsonify({
            "error": "RAG Chatbot service is not available. Please check server logs for initialization errors.",
            "thinking_steps": "❌ Hệ thống RAG chưa sẵn sàng."
        }), 503

    data = request.get_json()
    if not data or 'question' not in data or not data['question']:
        return jsonify({
            "error": "Question is missing or empty.",
            "thinking_steps": "❌ Câu hỏi trống hoặc không hợp lệ."
        }), 400

    try:
        question = data['question'].strip()
        print(f"📝 Received RAG question: {question}")
        
        # Log request info
        request_info = f"⏰ Request time: {time.strftime('%H:%M:%S')}"
        print(request_info)
        
        # Call RAG system (this will take 2-4 minutes)
        print("🤖 Processing with RAG Multi-Agent system...")
        answer, thinking_steps = chatbot.get_answer(question)
        
        print(f"✅ RAG response completed: {answer[:100]}...")
        
        # Return response in same format as original
        return jsonify({
            "answer": answer, 
            "thinking_steps": thinking_steps
        })
        
    except Exception as e:
        error_message = f"An error occurred while processing your question: {e}"
        print(f"❌ Error processing /ask request: {e}")
        
        error_thinking = f"""
        <div class="thinking-block">❌ <strong>Server Error:</strong> {str(e)}</div>
        <div class="thinking-block">💡 <strong>Gợi ý:</strong> Vui lòng thử lại sau</div>
        """
        
        return jsonify({
            "error": error_message, 
            "thinking_steps": error_thinking
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check for RAG system"""
    if chatbot and chatbot.agent:
        return jsonify({
            "status": "healthy",
            "service": "RAG Multi-Agent Chatbot",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({
            "status": "unhealthy", 
            "service": "RAG Multi-Agent Chatbot",
            "error": "RAG system not initialized"
        }), 503

@app.route('/')
def mainPage():
    return """
    <h1>🤖 RAG Multi-Agent Chatbot Backend</h1>
    <p>✅ Server is running</p>
    <p>📋 Endpoints:</p>
    <ul>
        <li>POST /ask - Send questions</li>
        <li>GET /health - Health check</li>
    </ul>
    <p>📚 Powered by AgriCarbonDEX knowledge base</p>
    """

if __name__ == "__main__":
    print("🚀 Starting RAG Multi-Agent Backend Server...")
    print("⏱️ Note: RAG responses typically take 2-4 minutes")
    print("🔗 Make sure Ollama is running on localhost:11434")
    
    # Run Flask app (change port if needed)
    app.run(debug=True, port=3000)

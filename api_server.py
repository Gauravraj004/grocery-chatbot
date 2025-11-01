"""
Flask API Backend for Grocery Chatbot
Provides REST endpoints for the React frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import GroceryChatbot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize chatbot
chatbot = GroceryChatbot()

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from the frontend
    
    Request body:
    {
        "message": "user's message"
    }
    
    Response:
    {
        "message": "bot's response text",
        "products": [list of matching products],
        "filters_used": {extracted filters}
    }
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'error': 'No message provided'
            }), 400
        
        # Get response from chatbot
        response = chatbot.chat(user_message)
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Sorry, I encountered an error processing your request.'
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """
    Reset the conversation memory
    
    Response:
    {
        "message": "Conversation reset successfully"
    }
    """
    try:
        chatbot.reset_conversation()
        return jsonify({
            'message': 'Conversation reset successfully'
        })
    
    except Exception as e:
        print(f"Error in reset endpoint: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint
    
    Response:
    {
        "status": "healthy",
        "gemini_configured": true/false
    }
    """
    gemini_key = os.getenv('GEMINI_API_KEY')
    return jsonify({
        'status': 'healthy',
        'gemini_configured': bool(gemini_key)
    })

if __name__ == '__main__':
    print("🚀 Server starting on http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')

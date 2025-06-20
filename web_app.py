"""
ConvoAI Web Interface - Browser-based chatbot
"""

from flask import Flask, render_template, request, jsonify
from chatbot.ollama_brain import ConvoAIBrain
from chatbot.web_memory_fixed import ConversationMemory

app = Flask(__name__)

# Initialize ConvoAI
print("🤖 Starting ConvoAI Web Interface...")
memory = ConversationMemory()
brain = ConvoAIBrain(memory)

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>ConvoAI - Intelligent Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .chat-box { border: 2px solid #ddd; border-radius: 10px; height: 400px; overflow-y: auto; padding: 15px; margin-bottom: 20px; background: #fafafa; }
        .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
        .user { background: #007bff; color: white; margin-left: 20%; text-align: right; }
        .ai { background: #e9ecef; color: #333; margin-right: 20%; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; }
        .input-area button { padding: 12px 20px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
        .input-area button:hover { background: #0056b3; }
        .status { text-align: center; color: #666; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ConvoAI</h1>
            <p>Intelligent chatbot with memory and personalities</p>
        </div>
        
        <div class="status">
            <strong>✅ AI Model: tinyllama (Ollama) | Memory: Active | Status: Ready</strong>
        </div>
        
        <div id="chat-box" class="chat-box">
            <div class="message ai">
                <strong>ConvoAI:</strong> Hello! I'm ConvoAI, your intelligent assistant with memory and personality. How can I help you today?
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Type your message here..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const chatBox = document.getElementById('chat-box');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            chatBox.innerHTML += `<div class="message user"><strong>You:</strong> ${message}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // Add thinking indicator
            chatBox.innerHTML += `<div class="message ai" id="thinking"><strong>ConvoAI:</strong> <em>�� Thinking...</em></div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                // Send to backend
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                // Remove thinking indicator
                document.getElementById('thinking').remove();
                
                // Add AI response
                chatBox.innerHTML += `<div class="message ai"><strong>ConvoAI:</strong> ${data.response}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
                
            } catch (error) {
                document.getElementById('thinking').remove();
                chatBox.innerHTML += `<div class="message ai"><strong>ConvoAI:</strong> <em>Sorry, I encountered an error. Please try again.</em></div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }
    </script>
</body>
</html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Generate AI response
        response = brain.generate_response(user_message, 'web_user')
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'})

if __name__ == '__main__':
    print("🌐 Starting web interface...")
    print("🔗 Access your chatbot at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

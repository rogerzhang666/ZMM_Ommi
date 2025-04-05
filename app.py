from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 通义千问API配置
QIANWEN_API_KEY = os.getenv('QIANWEN_API_KEY')
QIANWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

def chat_with_qianwen(message):
    """
    与通义千问API交互
    """
    headers = {
        "Authorization": f"Bearer {QIANWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen-omni-turbo",
        "input": {
            "messages": [
                {
                    "role": "system",
                    "content": "你的名字是赵敏敏，一个活泼可爱的女孩。请用活泼可爱的语气回答问题。保持回答简洁。"
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
    }
    
    try:
        response = requests.post(QIANWEN_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['output']['text']
    except Exception as e:
        return f"抱歉，我现在有点累了，休息一下~（错误：{str(e)}）"

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    处理聊天请求的API端点
    """
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "消息不能为空哦~"}), 400
    
    response = chat_with_qianwen(user_message)
    return jsonify({"response": response})

@app.route('/')
def index():
    """
    返回简单的测试页面
    """
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>与赵敏敏聊天</title>
        <meta charset="utf-8">
        <style>
            body { max-width: 800px; margin: 0 auto; padding: 20px; }
            #chat-box { height: 400px; border: 1px solid #ccc; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
            #message-input { width: 80%; padding: 5px; }
            button { padding: 5px 15px; }
        </style>
    </head>
    <body>
        <h1>与赵敏敏聊天</h1>
        <div id="chat-box"></div>
        <input type="text" id="message-input" placeholder="输入消息...">
        <button onclick="sendMessage()">发送</button>

        <script>
            function appendMessage(role, content) {
                const chatBox = document.getElementById('chat-box');
                const messageDiv = document.createElement('div');
                messageDiv.style.margin = '5px';
                messageDiv.style.padding = '5px';
                messageDiv.style.borderRadius = '5px';
                messageDiv.style.backgroundColor = role === 'user' ? '#e3f2fd' : '#f5f5f5';
                messageDiv.textContent = `${role === 'user' ? '你' : '赵敏敏'}: ${content}`;
                chatBox.appendChild(messageDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            async function sendMessage() {
                const input = document.getElementById('message-input');
                const message = input.value.trim();
                
                if (!message) return;
                
                appendMessage('user', message);
                input.value = '';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({message: message}),
                    });
                    
                    const data = await response.json();
                    appendMessage('bot', data.response);
                } catch (error) {
                    appendMessage('bot', '抱歉，我遇到了一些问题，请稍后再试~');
                }
            }

            // 支持回车发送消息
            document.getElementById('message-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)

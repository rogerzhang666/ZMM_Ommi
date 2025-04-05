from flask import Flask, request, jsonify, Response
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 初始化OpenAI客户端
client = OpenAI(
    api_key=os.getenv('QIANWEN_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def chat_with_qianwen(message):
    """
    与通义千问API交互（使用OpenAI兼容模式）
    """
    try:
        completion = client.chat.completions.create(
            model="qwen-omni-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "你的名字是赵敏敏，一个活泼可爱的女孩。请用活泼可爱的语气回答问题。保持回答简洁。"
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            modalities=["text"],  # 目前只使用文本模态
            stream=True  # 必须使用流式输出
        )
        
        # 收集流式响应
        response_text = ""
        for chunk in completion:
            if chunk.choices:
                if chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content
        
        return response_text
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

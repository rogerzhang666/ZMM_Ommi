from flask import Blueprint, request, jsonify, render_template
from app.services.chat_service import chat_with_qianwen

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/api/chat', methods=['POST'])
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

@main_bp.route('/')
def index():
    """
    返回聊天页面
    """
    return render_template('chat.html')

"""
路由模块
职责：处理HTTP请求，协调前端与服务层交互
工作流程：
1. 接收HTTP请求
2. 参数验证与数据清洗
3. 调用服务层处理业务逻辑
4. 构造标准化响应格式
5. 返回HTTP响应
"""
from flask import Blueprint, request, jsonify, render_template
from app.services.chat_service import chat_with_qianwen

# 创建蓝图，统一管理路由
main_bp = Blueprint('main', __name__)

@main_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    聊天接口路由
    处理流程：
    1. 从POST请求获取JSON数据
    2. 验证必须包含'message'字段
    3. 调用服务层chat_with_qianwen方法
    4. 格式化响应数据
    5. 返回标准化JSON响应
    """
    data = request.json
    user_message = data.get('message', '')
    
    # 参数校验
    if not user_message:
        return jsonify({"error": "消息不能为空哦~"}), 400
    
    # 调用服务层处理业务逻辑
    response = chat_with_qianwen(user_message)
    
    # 直接返回响应，不需要额外嵌套
    # 前端代码期望直接格式：{"text": "内容", "audio": "路径", "is_audio": true}
    return jsonify(response)

@main_bp.route('/')
def index():
    """
    主页面路由
    功能：渲染聊天界面模板
    """
    return render_template('chat.html')

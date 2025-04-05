import os
import json
from openai import OpenAI
import httpx

def load_config():
    """
    加载配置文件
    """
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return {"system_prompt": "你的名字是赵敏敏，一个活泼可爱的女孩。"}

config = load_config()

# 创建自定义的HTTP客户端
http_client = httpx.Client()

# 初始化OpenAI客户端
client = OpenAI(
    api_key=os.getenv('QIANWEN_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    http_client=http_client
)

def chat_with_qianwen(message):
    """
    与通义千问API交互（使用OpenAI兼容模式）
    """
    try:
        # 从配置中获取系统提示
        system_prompt = config.get("system_prompt", "你的名字是赵敏敏，一个活泼可爱的女孩。")
        
        completion = client.chat.completions.create(
            model="qwen-omni-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
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

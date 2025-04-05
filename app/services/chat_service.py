import os
import json
import base64
import numpy as np
import soundfile as sf
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
        return {
            "system_prompt": "你的名字是赵敏敏，一个活泼可爱的女孩。",
            "text_length_threshold": 100,  # 文本长度阈值，超过此值使用语音
            "voice": "Cherry",  # 默认语音角色
            "timeout": 60  # 默认超时时间（秒）
        }

config = load_config()

# 从配置中获取超时设置，默认为60秒
timeout = config.get("timeout", 60)

# 创建自定义的HTTP客户端，设置更长的超时时间
http_client = httpx.Client(timeout=timeout)

# 初始化OpenAI客户端
client = OpenAI(
    api_key=os.getenv('QIANWEN_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    http_client=http_client
)

def should_use_audio(text):
    """
    根据文本长度判断是否使用语音回复
    """
    # 从配置中获取文本长度阈值，默认为100个字符
    threshold = config.get("text_length_threshold", 100)
    return len(text) > threshold

def save_audio_data(audio_data, filename="static/audio/response.wav"):
    """
    保存音频数据为WAV文件
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # 解码Base64音频数据
        wav_bytes = base64.b64decode(audio_data)
        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
        
        # 保存为WAV文件
        sf.write(filename, audio_np, samplerate=24000)
        return filename
    except Exception as e:
        print(f"保存音频数据失败: {str(e)}")
        return None

def chat_with_qianwen(message):
    """
    与通义千问API交互（使用OpenAI兼容模式）
    """
    try:
        # 从配置中获取系统提示
        system_prompt = config.get("system_prompt", "你的名字是赵敏敏，一个活泼可爱的女孩。")
        voice = config.get("voice", "Cherry")
        
        # 先用纯文本模式获取完整回复，用于判断是否需要语音
        text_completion = client.chat.completions.create(
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
            stream=True
        )
        
        # 收集文本响应
        response_text = ""
        for chunk in text_completion:
            if chunk.choices and chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
        
        # 判断是否需要语音输出
        if should_use_audio(response_text):
            # 使用文本+语音模式重新获取响应
            # 注意: 这里作为特殊处理，直接传递参数而不使用modalities参数
            audio_params = {
                "model": "qwen-omni-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "stream": True,
                "audio": {"voice": voice, "format": "wav"}
            }
            # 添加modalities参数
            audio_params["modalities"] = ["text", "audio"]
            
            # 创建请求
            audio_completion = client.chat.completions.create(**audio_params)
            
            # 收集音频数据
            audio_string = ""
            audio_text = ""
            for chunk in audio_completion:
                if chunk.choices:
                    if hasattr(chunk.choices[0].delta, "audio"):
                        try:
                            audio_string += chunk.choices[0].delta.audio["data"]
                        except Exception as e:
                            # 处理错误或获取音频转录文本
                            if "transcript" in chunk.choices[0].delta.audio:
                                audio_text += chunk.choices[0].delta.audio["transcript"]
                    elif chunk.choices[0].delta.content:
                        audio_text += chunk.choices[0].delta.content
            
            # 保存音频文件
            if audio_string:
                import time
                current_timestamp = int(time.time() * 1000)
                audio_filename = f"static/audio/response_{current_timestamp}.wav"
                audio_path = save_audio_data(audio_string, audio_filename)
                # 返回包含音频路径的响应
                return {
                    "text": audio_text or response_text,
                    "audio": audio_path,
                    "is_audio": True
                }
        
        # 如果不需要语音或者音频生成失败，返回纯文本响应
        return {
            "text": response_text,
            "audio": None,
            "is_audio": False
        }
    except Exception as e:
        error_message = f"抱歉，我现在有点累了，休息一下~（错误：{str(e)}）"
        return {
            "text": error_message,
            "audio": None,
            "is_audio": False
        }

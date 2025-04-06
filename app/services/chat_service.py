import os
import base64
import numpy as np
import soundfile as sf
import httpx
import logging
import traceback
from openai import OpenAI
from config import config  # 导入全局配置单例

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 从配置中获取超时设置
timeout = config.get("timeout", 60)
http_client = httpx.Client(timeout=timeout)  # 设置全局请求超时

def should_use_audio(text):
    """
    智能判断是否使用语音回复
    决策流程：
    1. 从配置获取文本长度阈值
    2. 计算输入文本的字符数
    3. 返回判断结果（True/False）
    """
    threshold = config.get("text_length_threshold", 300)
    return len(text) > threshold

def save_audio_data(audio_data, filename="static/audio/response.wav"):
    """
    保存音频文件到指定路径
    处理步骤：
    1. 创建目录结构（如果不存在）
    2. 解码Base64音频数据
    3. 写入WAV格式文件
    4. 异常处理文件操作错误
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        wav_bytes = base64.b64decode(audio_data)
        with open(filename, 'wb') as f:
            f.write(wav_bytes)
        return filename
    except Exception as e:
        logger.error(f"保存音频文件失败: {str(e)}")
        return None

def chat_with_qianwen(message):
    """
    与通义千问API交互（使用OpenAI兼容模式）
    工作流程：
    1. 获取系统提示和语音角色
    2. 使用纯文本模式获取完整回复
    3. 判断是否需要语音输出
    4. 如果需要语音输出，使用文本+语音模式重新获取响应
    5. 保存音频文件并返回响应结果
    """
    try:
        logger.info(f"开始处理聊天请求: {message[:20]}...")
        
        # 检查API密钥是否配置
        api_key = os.getenv('QIANWEN_API_KEY')
        logger.debug(f"API密钥是否配置: {bool(api_key)}")
        if not api_key:
            logger.error("未配置QIANWEN_API_KEY环境变量")
            return {
                "text": "抱歉，我的API密钥未正确配置，请联系管理员~",
                "audio": None,
                "is_audio": False
            }
        
        # 从配置中获取系统提示
        system_prompt = config.get("system_prompt", "你的名字是赵敏敏，一个活泼可爱的女孩。")
        voice = config.get("voice", "Cherry")
        logger.info(f"使用系统提示: {system_prompt[:30]}...")
        
        # 先用纯文本模式获取完整回复，用于判断是否需要语音
        logger.info("开始纯文本模式API调用")
        try:
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
            
            logger.info(f"获取到文本响应: {response_text[:30]}...")
            
            # 判断是否需要语音输出
            if should_use_audio(response_text):
                logger.info("文本长度超过阈值，准备生成语音")
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
                    "tts_voice": voice,
                    "stream": True
                }
                
                audio_params["modalities"] = ["text", "audio"]
                
                # 创建请求
                logger.info("开始多模态API调用（文本+语音）")
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
                                logger.error(f"处理音频数据时出错: {str(e)}")
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
                    logger.info(f"保存音频文件: {audio_filename}")
                    audio_path = save_audio_data(audio_string, audio_filename)
                    # 返回包含音频路径的响应
                    return {
                        "text": audio_text or response_text,
                        "audio": audio_path,
                        "is_audio": True
                    }
                else:
                    logger.warning("未能获取音频数据，返回纯文本响应")
            
            # 如果不需要语音或者音频生成失败，返回纯文本响应
            return {
                "text": response_text,
                "audio": None,
                "is_audio": False
            }
        except httpx.RequestError as e:
            logger.error(f"HTTP请求错误: {str(e)}")
            return {
                "text": "抱歉，网络连接出现问题，请稍后再试~",
                "audio": None,
                "is_audio": False
            }
        except Exception as api_error:
            logger.error(f"API调用错误: {str(api_error)}")
            logger.error(traceback.format_exc())
            return {
                "text": "抱歉，我遇到了一些技术问题，请稍后再试~",
                "audio": None,
                "is_audio": False
            }
    except Exception as e:
        logger.error(f"聊天处理过程中出错: {str(e)}", exc_info=True)
        error_message = f"抱歉，我现在有点累了，休息一下~"
        return {
            "text": error_message,
            "audio": None,
            "is_audio": False
        }

# 初始化OpenAI客户端
try:
    client = OpenAI(
        api_key=os.getenv('QIANWEN_API_KEY'),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        http_client=http_client
    )
    logger.info("成功初始化OpenAI客户端")
except Exception as e:
    logger.error(f"初始化OpenAI客户端失败: {str(e)}")
    client = None

from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import json
import base64
import numpy as np
import soundfile as sf
from io import BytesIO
import traceback
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# API密钥
api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

@app.route('/')
def index():
    """主页路由，返回测试界面"""
    return render_template('voice_test.html')

@app.route('/voice-test', methods=['POST'])
def voice_test():
    """
    语音测试接口完整工作流程：
    
    1. 请求验证阶段：
       - 检查音频文件是否存在
       - 验证文件名有效性
       - 检查API密钥配置
       
    2. 音频预处理阶段：
       - 读取音频文件数据
       - 转换为base64编码
       - 记录原始音频信息
       
    3. API交互阶段：
       - 构建带系统角色的请求体
       - 发送语音识别请求
       - 处理流式响应(SSE)
       
    4. 音频处理阶段：
       - 收集音频base64数据块
       - 验证并补齐base64数据
       - 解码WAV音频数据
       
    5. 响应返回阶段：
       - 生成内存音频文件
       - 处理异常情况
       - 返回标准化响应
    
    关键技术点：
    - 音频base64编码/解码
    - 流式响应处理机制
    - WAV头部验证(44字节)
    
    安全注意事项：
    - API密钥脱敏处理
    - 输入文件验证
    - 错误信息过滤
    """
    try:
        # 检查请求中是否包含音频文件
        if 'audio' not in request.files:
            print("请求中没有音频文件")
            return jsonify({'error': '没有收到音频文件'}), 400
            
        audio_file = request.files['audio']
        if audio_file.filename == '':
            print("音频文件名为空")
            return jsonify({'error': '音频文件名为空'}), 400
            
        print(f"收到音频文件: {audio_file.filename}")
        
        # 检查API密钥是否存在
        if not api_key:
            print("API密钥未配置")
            return jsonify({'error': 'API密钥未配置，请检查.env文件'}), 500
            
        # 读取音频文件数据
        audio_data = audio_file.read()
        
        # 将音频数据转换为base64编码
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        print(f"音频文件大小: {len(audio_data)} 字节")
        print(f"Base64编码后大小: {len(audio_base64)} 字符")
        
        # 准备API请求数据
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 日志中只显示部分API密钥
        safe_headers = headers.copy()
        safe_headers["Authorization"] = f"Bearer {api_key[:5]}****" 
        print(f"API请求头: {json.dumps(safe_headers, ensure_ascii=False)}")
        
        # 构建请求数据
        data = {
            "model": "qwen-omni-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "你是赵敏敏，一个活泼可爱的女孩。请用活泼可爱的语气回答问题。保持回答简洁。"}]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": f"data:audio/wav;base64,{audio_base64}",
                                "format": "wav"
                            }
                        }
                    ]
                }
            ],
            "modalities": ["text", "audio"],
            "audio": {"voice": "Cherry", "format": "wav"},
            "stream": True
        }
        
        # 记录当前时间用于调试
        start_time = time.time()
        print(f"[{start_time}] 开始API请求")
        
        # 发送请求
        print("正在发送API请求...")
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60,  # 增加超时时间，因为语音处理可能需要更长时间
                stream=True  # 启用流式响应处理
            )
            print(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("API请求成功，开始处理流式响应...")
                
                # 处理流式响应
                audio_string = ""
                text_response = ""
                chunk_count = 0
                
                # 解析SSE流
                print("开始解析SSE流...")
                for line in response.iter_lines():
                    if line:
                        chunk_count += 1
                        line_text = line.decode('utf-8')
                        if chunk_count % 10 == 0:  # 每10个块输出一次日志，减少日志量
                            print(f"已接收 {chunk_count} 个响应块...")
                        
                        if line_text.startswith('data: '):
                            json_str = line_text[6:]  # 去掉 'data: ' 前缀
                            if json_str.strip() == '[DONE]':
                                print("收到结束标记 [DONE]")
                                break
                                
                            try:
                                chunk = json.loads(json_str)
                                
                                if 'choices' in chunk and chunk['choices']:
                                    delta = chunk['choices'][0].get('delta', {})
                                    
                                    # 收集音频数据
                                    if 'audio' in delta:
                                        if 'data' in delta['audio']:
                                            current_chunk = delta['audio']['data']
                                            audio_string += current_chunk
                                        
                                    # 收集文本响应
                                    if 'content' in delta:
                                        content = delta.get('content', '')
                                        # 确保content不是None
                                        if content is not None:
                                            text_response += content
                            except json.JSONDecodeError as e:
                                print(f"JSON解析错误: {e}, 数据: {json_str[:100]}")
                
                print(f"共收到 {chunk_count} 个响应块")
                print(f"收集到的音频数据长度: {len(audio_string)}")
                print(f"收集到的文本响应: {text_response}")
                
                # 解码音频数据
                if audio_string:
                    try:
                        print(f"开始解码音频数据，base64字符串长度: {len(audio_string)}")
                        # 检查base64字符串是否有效
                        if len(audio_string) % 4 != 0:
                            # 补齐base64字符串
                            padding = 4 - (len(audio_string) % 4)
                            audio_string += "=" * padding
                            print(f"base64字符串不是4的倍数，已补齐到 {len(audio_string)} 字符")
                            
                        wav_bytes = base64.b64decode(audio_string)
                        print(f"解码后wav字节数: {len(wav_bytes)}")
                        
                        # 检查字节数据的有效性
                        if len(wav_bytes) < 44:  # WAV头部至少44字节
                            raise ValueError(f"解码后数据过短 ({len(wav_bytes)} 字节)，不足以构成有效的WAV文件")
                            
                        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
                        print(f"解码后音频样本数: {len(audio_np)}")
                        
                        # 如果音频样本数为0，则生成一个简短的提示音
                        if len(audio_np) == 0:
                            print("音频样本数为0，生成提示音")
                            audio_np = np.sin(np.linspace(0, 3 * np.pi, 24000)) * 32767
                            audio_np = audio_np.astype(np.int16)
                        
                        # 创建内存文件对象
                        audio_buffer = BytesIO()
                        sf.write(audio_buffer, audio_np, samplerate=24000, format='WAV')
                        audio_buffer.seek(0)
                        
                        processing_time = time.time() - start_time
                        print(f"音频处理完成，总耗时: {processing_time:.2f}秒，准备发送音频响应")
                        
                        return send_file(
                            audio_buffer,
                            mimetype='audio/wav',
                            as_attachment=True,
                            download_name='response.wav'
                        )
                    except Exception as e:
                        error_msg = f"音频数据处理错误: {str(e)}"
                        print(error_msg)
                        traceback.print_exc()
                        
                        # 尝试返回文本响应作为后备方案
                        if text_response:
                            print(f"音频处理失败，返回文本响应: {text_response}")
                            return jsonify({
                                'error': '音频处理失败', 
                                'text_response': text_response
                            }), 500
                        
                        # 尝试返回一个默认的音频响应
                        try:
                            print("尝试生成默认音频响应")
                            # 生成1秒的正弦波
                            sample_rate = 24000
                            t = np.linspace(0, 1, sample_rate)
                            audio_np = np.sin(2 * np.pi * 440 * t) * 32767
                            audio_np = audio_np.astype(np.int16)
                            
                            audio_buffer = BytesIO()
                            sf.write(audio_buffer, audio_np, samplerate=sample_rate, format='WAV')
                            audio_buffer.seek(0)
                            
                            return send_file(
                                audio_buffer,
                                mimetype='audio/wav',
                                as_attachment=True,
                                download_name='fallback.wav'
                            )
                        except Exception as fb_error:
                            print(f"默认音频生成失败: {str(fb_error)}")
                            return jsonify({'error': error_msg}), 500
                else:
                    # 尝试直接返回文本响应
                    if text_response:
                        print(f"未收到音频数据，但收到了文本响应: {text_response}")
                        return jsonify({
                            'error': '未收到音频数据', 
                            'text_response': text_response
                        }), 500
                    return jsonify({'error': '未收到音频数据也没有文本响应'}), 500
            else:
                error_message = f"API错误: {response.status_code}"
                try:
                    error_detail = response.json()
                    print(f"API错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                    error_message += f", 详情: {error_detail.get('error', {}).get('message', '未知错误')}"
                except:
                    print(f"无法解析错误响应: {response.text[:500]}")
                
                return jsonify({'error': error_message}), 500
        except requests.exceptions.RequestException as e:
            error_msg = f"请求异常: {str(e)}"
            print(error_msg)
            return jsonify({'error': error_msg}), 500
    
    except Exception as e:
        error_msg = f"处理错误: {str(e)}"
        print(error_msg)
        traceback.print_exc()  # 打印完整的错误栈
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    # 运行在5002端口，避免与主应用和文本测试工具冲突
    app.run(debug=True, port=5002)

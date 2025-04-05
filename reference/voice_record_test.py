from flask import Flask, render_template, request, jsonify
import os
import subprocess
import tempfile
from datetime import datetime
import shutil
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 设置ffmpeg路径
FFMPEG_PATH = r'D:\ffmpeg\bin\ffmpeg.exe'

@app.route('/')
def index():
    """主页路由，返回测试界面"""
    return render_template('voice_record_test.html')

@app.route('/voice-record-test', methods=['POST'])
def voice_record_test():
    """
    录音文件处理完整工作流程：
    
    1. 文件接收阶段：
       - 验证请求包含有效文件
       - 检查文件名和扩展名
       - 生成带时间戳的唯一文件名
       
    2. 临时文件处理：
       - 保存到临时目录
       - 验证文件大小
       - 记录原始文件信息
       
    3. 音频转换阶段：
       - 检查ffmpeg可用性
       - 执行WAV格式转换
       - 验证输出文件有效性
       
    4. 资源清理阶段：
       - 删除临时文件
       - 记录处理结果
       
    关键技术点：
    - ffmpeg参数配置(PCM编码/44100采样率)
    - 临时文件安全处理
    - 文件大小验证机制
    
    安全注意事项：
    - 文件上传路径限制
    - 临时文件自动清理
    - 子进程调用安全
    """
    try:
        # 检查请求中是否包含音频文件
        if 'audio' not in request.files:
            logger.error("请求中没有音频文件")
            return jsonify({
                'success': False,
                'message': '没有收到音频文件'
            }), 400
            
        audio_file = request.files['audio']
        if audio_file.filename == '':
            logger.error("音频文件名为空")
            return jsonify({
                'success': False,
                'message': '音频文件名为空'
            }), 400
        
        # 获取文件后缀
        file_ext = os.path.splitext(audio_file.filename)[1].lower()
        logger.info(f"接收到音频文件，格式: {file_ext}")
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        wav_filename = f'recording_{timestamp}.wav'
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        
        # 确保static目录存在
        os.makedirs(static_path, exist_ok=True)
        
        wav_output_path = os.path.join(static_path, wav_filename)
        
        # 保存原始文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name
            logger.info(f"原始音频已保存到临时文件: {temp_path}")
        
        # 检查临时文件是否存在且有内容
        temp_file_size = os.path.getsize(temp_path)
        logger.info(f"临时文件大小: {temp_file_size} 字节")
        
        if temp_file_size == 0:
            logger.error("临时文件为空")
            os.unlink(temp_path)
            return jsonify({
                'success': False,
                'message': '上传的音频文件为空'
            }), 400
        
        try:
            # 先检查ffmpeg是否可用
            try:
                version_result = subprocess.run([FFMPEG_PATH, '-version'], 
                                              capture_output=True, text=True, check=True)
                logger.info(f"FFmpeg版本: {version_result.stdout.split(chr(10))[0]}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.error(f"FFmpeg执行失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'ffmpeg执行失败，请检查路径是否正确'
                }), 500
            
            # 直接将输入文件转换为WAV，使用最简单的命令，确保稳定性
            command = [
                FFMPEG_PATH,
                '-i', temp_path,  # 输入文件
                '-c:a', 'pcm_s16le',  # 16位PCM编码
                '-ar', '44100',  # 标准CD音质采样率
                '-ac', '1',  # 单声道
                '-af', 'volume=2.0',  # 适度增加音量
                '-y',  # 覆盖已存在的文件
                wav_output_path  # 输出文件
            ]
            
            logger.info(f"执行FFmpeg命令: {' '.join(command)}")
            
            # 执行转换
            result = subprocess.run(command, capture_output=True, text=True)
            
            # 检查结果
            if result.returncode != 0:
                logger.error(f"FFmpeg转换失败: {result.stderr}")
                return jsonify({
                    'success': False,
                    'message': f'音频转换失败: {result.stderr}'
                }), 500
            
            # 检查输出文件是否存在
            if not os.path.exists(wav_output_path):
                logger.error(f"输出文件不存在: {wav_output_path}")
                return jsonify({
                    'success': False,
                    'message': '输出文件创建失败'
                }), 500
            
            # 获取输出文件大小
            wav_file_size = os.path.getsize(wav_output_path)
            logger.info(f"生成的WAV文件大小: {wav_file_size} 字节")
            
            if wav_file_size == 0:
                logger.error("生成的WAV文件为空")
                return jsonify({
                    'success': False,
                    'message': '生成的WAV文件为空'
                }), 500
            
            # 删除临时文件
            try:
                os.unlink(temp_path)
                logger.info("临时文件已删除")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': f'录音已保存为 {wav_filename}',
                'filename': wav_filename,
                'fileSize': wav_file_size
            })
            
        except Exception as e:
            logger.exception(f"音频处理过程中发生错误: {str(e)}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise Exception(f'音频转换失败: {str(e)}')
    
    except Exception as e:
        logger.exception(f"处理请求时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)

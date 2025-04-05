Qwen-Omni 系列模型支持输入多种模态的数据，包括视频、音频、图片、文本，并输出音频与文本。

模型介绍与计费
相比于 Qwen-VL 与 Qwen-Audio 模型，Qwen-Omni 模型可以：

理解视频文件中的视觉与音频信息；

理解多种模态的数据；

输出音频。

在视觉理解、音频理解等能力上，Qwen-Omni 模型也表现出色。

商业版模型开源版模型
相较于开源版，商业版模型具有最新的能力和改进。



PythonNode.js

 
import math
# 使用以下命令安装Pillow库：pip install Pillow
from PIL import Image

def token_calculate(image_path):
    # 打开指定的PNG图片文件
    image = Image.open(image_path)
    # 获取图片的原始尺寸
    height = image.height
    width = image.width
    # 将高度调整为28的整数倍
    h_bar = round(height / 28) * 28
    # 将宽度调整为28的整数倍
    w_bar = round(width / 28) * 28
    # 图像的Token下限：4个Token
    min_pixels = 28 * 28 * 4
    # 图像的Token上限：1280个Token
    max_pixels = 1280 * 28 * 28
    # 对图像进行缩放处理，调整像素的总数在范围[min_pixels,max_pixels]内
    if h_bar * w_bar > max_pixels:
        # 计算缩放因子beta，使得缩放后的图像总像素数不超过max_pixels
        beta = math.sqrt((height * width) / max_pixels)
        # 重新计算调整后的高度，确保为28的整数倍
        h_bar = math.floor(height / beta / 28) * 28
        # 重新计算调整后的宽度，确保为28的整数倍
        w_bar = math.floor(width / beta / 28) * 28
    elif h_bar * w_bar < min_pixels:
        # 计算缩放因子beta，使得缩放后的图像总像素数不低于min_pixels
        beta = math.sqrt(min_pixels / (height * width))
        # 重新计算调整后的高度，确保为28的整数倍
        h_bar = math.ceil(height * beta / 28) * 28
        # 重新计算调整后的宽度，确保为28的整数倍
        w_bar = math.ceil(width * beta / 28) * 28
    print(f"缩放后的图像尺寸为：高度为{h_bar}，宽度为{w_bar}")
    # 计算图像的Token数：总像素除以28 * 28
    token = int((h_bar * w_bar) / (28 * 28))
    # 系统会自动添加<|vision_bos|>和<|vision_eos|>视觉标记（各1个Token）
    total_token = token + 2
    print(f"图像的Token数为{total_token}")    
    return total_token
if __name__ == "__main__":
    total_token = token_calculate(image_path="test.png")

使用方法
输入
支持的输入模态
支持以下输入组合：

文本输入

图片+文本输入

音频+文本输入

视频（包括图像列表与视频文件形式）+文本输入

无法在一个 User Message中输入多种非文本模态的数据。
输入多模态数据的方式
输入的图片、音频、视频文件支持 Base64 编码与公网 URL 进行传入。以下示例代码均以传入公网 URL 为例，如果需要传入 Base64 编码，请参见输入 Base64 编码的本地文件。

输出
当前仅支持以流式输出的形式调用 Qwen-Omni 模型。

支持的输出模态
输出可以包含文本与音频数据，您可以通过modalities参数控制。




输出模态

modalities参数值

回复风格

文本

["text"]（默认值）

比较书面化，回复内容较为正式。

文本+音频

["text","audio"]

比较口语化，回复内容包含语气词，会引导用户与其进一步交流。

输出模态包括音频时不支持设定 System Message。
输出的音频为 Base64 编码数据，您需要在接收后进行解码，解码方法请参见解析输出的Base64 编码的音频数据。
支持输出的音频语言
当前输出音频仅支持汉语（普通话）和英语。

支持的音频音色
输出音频的音色与文件格式（只支持设定为"wav"）通过audio参数来配置，如：audio={"voice": "Cherry", "format": "wav"}，其中商业版模型voice参数可选值为：["Cherry", "Serena", "Ethan", "Chelsie"]，开源版模型voice参数可选值为：["Ethan", "Chelsie"]。



音色名称

音色效果

Cherry

不支持开源版模型。
Serena

不支持开源版模型。
Ethan

Chelsie

开始使用
前提条件
Qwen-Omni 系列模型仅支持 OpenAI 兼容方式调用。您需要已获取API Key并配置API Key到环境变量。如果通过 OpenAI SDK 调用，需要安装SDK（建议参考该文档安装最新SDK，否则可能运行失败）。

OpenAI Python SDK 最低版本为 1.52.0， Node.js SDK 最低版本为 4.68.0。
文本输入
Qwen-Omni 模型支持接收纯文本作为输入。当前只支持以流式输出的方式进行调用。

OpenAI 兼容
PythonNode.jscurl

 
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-omni-turbo",
    messages=[{"role": "user", "content": "你是谁"}],
    # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
    modalities=["text", "audio"],
    audio={"voice": "Cherry", "format": "wav"},
    # stream 必须设置为 True，否则会报错
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta)
    else:
        print(chunk.usage)

图片+文本输入
Qwen-Omni 模型支持传入多张图片。对输入图片的要求如下：

单个图片文件的大小不超过10 MB;

图片数量受模型图文总 Token 上限（即最大输入）的限制，所有图片的总 Token 数必须小于模型的最大输入;

图片的宽度和高度均应大于10像素，宽高比不应超过200:1或1:200。

当前只支持以流式输出的方式进行调用。

OpenAI 兼容
PythonNode.jscurl

 
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-omni-turbo",
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"
                    },
                },
                {"type": "text", "text": "图中描绘的是什么景象？"},
            ],
        },
    ],
    # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
    modalities=["text", "audio"],
    audio={"voice": "Chelsie", "format": "wav"},
    # stream 必须设置为 True，否则会报错
    stream=True,
    stream_options={
        "include_usage": True
    }
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta)
    else:
        print(chunk.usage)

音频+文本输入
只可以输入一个音频文件，大小不能超过 10 MB，时长最长 3 分钟。当前只支持以流式输出的方式进行调用。

OpenAI 兼容
PythonNode.jscurl

 
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-omni-turbo",
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3",
                        "format": "mp3",
                    },
                },
                {"type": "text", "text": "这段音频在说什么"},
            ],
        },
    ],
    # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
    modalities=["text", "audio"],
    audio={"voice": "Cherry", "format": "wav"},
    # stream 必须设置为 True，否则会报错
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta)
    else:
        print(chunk.usage)

视频+文本输入
视频的传入方式可以为图片列表形式或视频文件形式（可理解视频中的音频）。当前只支持以流式输出的方式进行调用。

图片列表形式

最少传入4张图片，最多可传入80张图片。

视频文件形式

视频文件只能输入一个，大小限制为 150 MB，时长限制为 40s。

视频文件中的视觉信息与音频信息会分开计费。
图片列表形式
OpenAI 兼容
PythonNode.jscurl

 
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-omni-turbo",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "video",
                    "video": [
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/xzsgiz/football1.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/tdescd/football2.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/zefdja/football3.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/aedbqh/football4.jpg",
                    ],
                },
                {"type": "text", "text": "描述这个视频的具体过程"},
            ],
        }
    ],
    # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
    modalities=["text", "audio"],
    audio={"voice": "Chelsie", "format": "wav"},
    # stream 必须设置为 True，否则会报错
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta)
    else:
        print(chunk.usage)

视频文件形式（可理解视频中的音频）
OpenAI 兼容
PythonNode.jscurl

 
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-omni-turbo",
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {
                        "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241115/cqqkru/1.mp4"
                    },
                },
                {"type": "text", "text": "视频的内容是什么?"},
            ],
        },
    ],
    # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
    modalities=["text", "audio"],
    audio={"voice": "Cherry", "format": "wav"},
    # stream 必须设置为 True，否则会报错
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta)
    else:
        print(chunk.usage)

多轮对话
您在使用 Qwen-Omni 模型的多轮对话功能时，需要注意：

Assistant Message

添加到 messages 数组中的 Assistant Message 只可以包含文本数据。

User Message

一条 User Message 只可以包含文本和一种模态的数据，在多轮对话中您可以在不同的 User Message 中输入不同模态的数据。

OpenAI 兼容
PythonNode.jscurl

 
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-omni-turbo",
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3",
                        "format": "mp3",
                    },
                },
                {"type": "text", "text": "这段音频在说什么"},
            ],
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "这段音频在说：欢迎使用阿里云"}],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": "介绍一下这家公司？"}],
        },
    ],
    # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
    modalities=["text"],
    # stream 必须设置为 True，否则会报错
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta)
    else:
        print(chunk.usage)

解析输出的Base64 编码的音频数据
Qwen-Omni 模型输出的音频为流式输出的 Base64 编码数据。您可以在模型生成过程中维护一个字符串变量，将每个返回片段的 Base64 编码添加到字符串变量后，待生成结束后进行 Base64 解码，得到音频文件；也可以将每个返回片段的 Base64 编码数据实时解码并播放。

PythonNode.js

 
# Installation instructions for pyaudio:
# APPLE Mac OS X
#   brew install portaudio
#   pip install pyaudio
# Debian/Ubuntu
#   sudo apt-get install python-pyaudio python3-pyaudio
#   or
#   pip install pyaudio
# CentOS
#   sudo yum install -y portaudio portaudio-devel && pip install pyaudio
# Microsoft Windows
#   python -m pip install pyaudio

import os
from openai import OpenAI
import base64
import numpy as np
import soundfile as sf

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-omni-turbo",
    messages=[{"role": "user", "content": "你是谁"}],
    # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
    modalities=["text", "audio"],
    audio={"voice": "Cherry", "format": "wav"},
    # stream 必须设置为 True，否则会报错
    stream=True,
    stream_options={"include_usage": True},
)

# 方式1: 待生成结束后再进行解码
audio_string = ""
for chunk in completion:
    if chunk.choices:
        if hasattr(chunk.choices[0].delta, "audio"):
            try:
                audio_string += chunk.choices[0].delta.audio["data"]
            except Exception as e:
                print(chunk.choices[0].delta.audio["transcript"])
    else:
        print(chunk.usage)

wav_bytes = base64.b64decode(audio_string)
audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
sf.write("audio_assistant_py.wav", audio_np, samplerate=24000)

# 方式2: 边生成边解码(使用方式2请将方式1的代码进行注释)
# # 初始化 PyAudio
# import pyaudio
# import time
# p = pyaudio.PyAudio()
# # 创建音频流
# stream = p.open(format=pyaudio.paInt16,
#                 channels=1,
#                 rate=24000,
#                 output=True)

# for chunk in completion:
#     if chunk.choices:
#         if hasattr(chunk.choices[0].delta, "audio"):
#             try:
#                 audio_string = chunk.choices[0].delta.audio["data"]
#                 wav_bytes = base64.b64decode(audio_string)
#                 audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
#                 # 直接播放音频数据
#                 stream.write(audio_np.tobytes())
#             except Exception as e:
#                 print(chunk.choices[0].delta.audio["transcript"])

# time.sleep(0.8)
# # 清理资源
# stream.stop_stream()
# stream.close()
# p.terminate()

输入 Base64 编码的本地文件
图片音频视频
以保存在本地的eagle.png为例。

PythonNode.js

 
import os
from openai import OpenAI
import base64

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


#  Base64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image = encode_image("eagle.png")

completion = client.chat.completions.create(
    model="qwen-omni-turbo",
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
                {"type": "text", "text": "图中描绘的是什么景象？"},
            ],
        },
    ],
    # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
    modalities=["text", "audio"],
    audio={"voice": "Cherry", "format": "wav"},
    # stream 必须设置为 True，否则会报错
    stream=True,
    stream_options={"include_usage": True},
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta)
    else:
        print(chunk.usage)

错误码
如果模型调用失败并返回报错信息，请参见错误信息进行解决。
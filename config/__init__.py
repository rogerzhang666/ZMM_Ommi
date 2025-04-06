"""
配置模块
功能：集中管理应用配置，提供全局配置单例
"""
import os
import json

def load_config():
    """
    加载配置文件
    工作流程：
    1. 尝试读取config.json
    2. 成功则返回配置字典
    3. 失败时打印错误日志并返回默认配置
    4. 保证配置包含必要参数
    """
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return {
            "system_prompt": "你的名字是赵敏敏，一个活泼可爱的女孩。",
            "text_length_threshold": 300,  # 文本长度阈值，超过此值使用语音
            "voice": "Cherry",  # 默认语音角色
            "timeout": 60  # 默认超时时间（秒）
        }

# 全局配置单例
config = load_config()

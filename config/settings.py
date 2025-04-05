import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """
    应用配置基类
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-zmm-app')
    MODEL_NAME = "qwen-omni-turbo"

class DevelopmentConfig(Config):
    """
    开发环境配置
    """
    DEBUG = True

class ProductionConfig(Config):
    """
    生产环境配置
    """
    DEBUG = False

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """
    获取当前环境的配置
    """
    config_name = os.getenv('FLASK_ENV', 'default')
    return config[config_name]

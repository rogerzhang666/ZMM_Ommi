from flask import Flask
import os

def create_app():
    """
    应用工厂函数，创建并配置Flask应用实例
    """
    # 静态文件目录配置
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

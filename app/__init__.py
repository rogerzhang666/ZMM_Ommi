from flask import Flask

def create_app():
    """
    应用工厂函数，创建并配置Flask应用实例
    """
    app = Flask(__name__)
    
    # 注册蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

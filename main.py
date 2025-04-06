# 应用入口脚本
# 工作流程：
# 1. 加载环境变量 -> .env文件
# 2. 创建Flask应用实例 -> 来自app模块
# 3. 配置运行参数 -> 从环境变量或默认值
# 4. 启动开发服务器 -> 带调试模式检测

import os
from app import create_app
from dotenv import load_dotenv

# 加载环境变量
# 优先级：.env文件 > 系统环境变量
load_dotenv()

# 创建应用实例
# 通过工厂模式初始化Flask应用配置
app = create_app()

if __name__ == '__main__':
    # 服务器配置参数获取
    host = os.getenv('FLASK_HOST', '0.0.0.0')  # 默认监听所有接口
    port = int(os.getenv('FLASK_PORT', 5000))   # 默认端口5000
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'  # 调试模式开关
    
    # 启动Flask开发服务器
    # 注意：生产环境应使用WSGI服务器（如gunicorn）
    app.run(
        host=host,
        port=port,
        debug=debug,  # 调试模式特性：自动重载、错误详情页等
        use_reloader=debug  # 仅在调试模式启用代码热重载
    )

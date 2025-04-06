"""
应用入口文件
功能：使用app包提供的工厂函数创建应用实例

此文件作为直接运行的入口点，通常用于开发环境
生产环境推荐使用main.py或WSGI服务器
"""
from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发环境直接运行
    app.run(debug=True)

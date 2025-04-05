# 赵敏敏项目结构优化计划

## 当前结构
```
ZMM_Ommi/
│
├── reference/           # 参考文件
├── static/              # 静态资源
├── templates/           # HTML模板
├── venv/                # 虚拟环境（保留）
├── %USERPROFILE%/       # 异常创建的目录（待处理）
├── __pycache__/         # Python缓存
├── .env                 # 环境变量
├── .env.example         # 环境变量示例
├── .gitignore           # Git忽略文件
├── app.py               # 主应用程序
├── config.json          # 系统提示配置
├── README.md            # 项目说明
└── requirements.txt     # 依赖列表
```

## 优化后的结构
```
ZMM_Ommi/
│
├── app/                     # 应用代码
│   ├── __init__.py          # 包初始化
│   ├── routes.py            # 路由定义
│   ├── services/            # 服务层
│   │   ├── __init__.py      
│   │   └── chat_service.py  # 聊天服务
│   ├── static/              # 静态资源
│   └── templates/           # HTML模板
│
├── config/                  # 配置文件目录
│   ├── __init__.py
│   └── settings.py          # 应用配置
│
├── reference/               # 参考文件（保留）
├── venv/                    # 虚拟环境（保留）
├── .env                     # 环境变量
├── .env.example             # 环境变量示例
├── .gitignore               # Git忽略文件
├── config.json              # 系统提示配置
├── main.py                  # 入口文件
├── README.md                # 项目说明
└── requirements.txt         # 依赖列表
```

## 优化计划
1. 创建清晰的代码分层结构
2. 将应用逻辑与入口点分离
3. 改进配置管理
4. 保留虚拟环境但规范使用方式
5. 清理临时和缓存文件

## 注意事项
- 确保所有环境变量和密钥信息仅存储在`.env`文件中
- 更新`.gitignore`确保敏感信息不被提交
- 确保代码迁移过程中功能保持一致

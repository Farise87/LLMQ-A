import os
from flask import Flask
from flask_cors import CORS
# import secrets  # 不再需要动态生成密钥

# 导入自定义模块
from model_manager import ModelManager
from knowledge_base import KnowledgeBase
from generation_manager import GenerationManager
from api_routes import ApiRoutes
from tool_manager import ToolManager

# 导入配置
from config import DEEPSEEK_CONFIG, KNOWLEDGE_BASE_CONFIG

def create_app():
    """创建并配置Flask应用"""
    # 创建Flask应用
    app = Flask(__name__, static_folder='static', template_folder='templates')
    CORS(app)
    
    # 设置固定的密钥用于session加密
    app.secret_key = 'AiQA_admin_secret_key_2024'  # 使用固定的密钥
    
    # 初始化模型管理器
    model_manager = ModelManager()
    
    # 初始化知识库管理器
    knowledge_base = KnowledgeBase(KNOWLEDGE_BASE_CONFIG['csv_path'])
    
    # 初始化生成任务管理器
    generation_manager = GenerationManager()
    
    # 初始化API路由
    api_routes = ApiRoutes(app, model_manager, knowledge_base, generation_manager)
    
    # 打印MCP系统初始化信息
    print("MCP系统已初始化，DeepSeek模型可以调用工具系统")
    print(f"已注册工具数量: {len(model_manager.tool_manager.tools)}")
    
    return app, model_manager, knowledge_base

def main():
    """主函数，启动应用"""
    # 创建应用
    app, model_manager, knowledge_base = create_app()
    
    # 启动时加载模型和知识库
    model_manager.load_model()
    knowledge_base.load_knowledge_base()
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
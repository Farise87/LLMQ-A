# 项目配置文件

# MySQL数据库配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '2025',  # 请修改为实际的数据库密码
    'database': 'fangji',
    'charset': 'utf8mb4'
}

# Neo4j数据库配置
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': '2025'  # 请修改为实际的Neo4j密码
}

# DeepSeek API配置
DEEPSEEK_CONFIG = {
    'api_key': 'sk-fef9107166bc48dd924c5b030f0b38eb',  # 请替换为实际的API密钥
    'model_type': 'deepseek_api'
}

# 服务器配置
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True
}

# 知识库配置
KNOWLEDGE_BASE_CONFIG = {
    'csv_path': '最终方剂.csv'  # 方剂知识库CSV文件路径
}
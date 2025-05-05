import json
from model_manager import ModelManager
from tool_manager import ToolManager

def test_mcp_system():
    """测试MCP系统功能"""
    print("开始测试MCP系统...")
    
    # 初始化模型管理器
    model_config = {
        'type': 'deepseek_api',
        'api_key': 'sk-fef9107166bc48dd924c5b030f0b38eb'  # 请替换为实际的API密钥
    }
    model_manager = ModelManager(model_config)
    
    # 加载模型
    success = model_manager.load_model()
    if not success:
        print("模型加载失败")
        return
    
    print("模型加载成功")
    
    # 获取工具列表
    tools = model_manager.tool_manager.get_tool_descriptions()
    print(f"已注册工具数量: {len(tools)}")
    for tool in tools:
        print(f"- {tool['id']}: {tool['description']}")
    
    # 测试工具执行
    print("\n测试工具执行:")
    test_keyword = "感冒"
    print(f"搜索关键词: {test_keyword}")
    
    # 测试搜索方剂
    result = model_manager.tool_manager.execute_tool("search_herbs", {"keyword": test_keyword})
    print(f"\n方剂搜索结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试搜索药材
    result = model_manager.tool_manager.execute_tool("search_medicines", {"keyword": test_keyword})
    print(f"\n药材搜索结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试模型调用工具
    print("\n测试模型调用工具:")
    prompt = "请介绍一下治疗感冒的常用中药方剂"
    print(f"提示: {prompt}")
    
    try:
        response = model_manager.create_completion(prompt)
        print(f"\n模型回复:\n{response['choices'][0]['text']}")
    except Exception as e:
        print(f"模型调用失败: {str(e)}")

if __name__ == "__main__":
    test_mcp_system()
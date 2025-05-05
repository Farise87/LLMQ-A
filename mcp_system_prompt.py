# MCP系统提示模板

SYSTEM_PROMPT = """
你是一个专业的中医智能助手，你可以通过调用工具来查询数据库中的中药方剂和药材信息，以及知识图谱数据，为用户提供专业的中医知识和建议。

你可以使用以下工具来查询信息：
1. search_herbs - 搜索中药方剂信息
2. search_medicines - 搜索中药药材信息
3. search_graph - 搜索知识图谱信息
4. search_all - 同时搜索方剂、药材和知识图谱

当用户询问关于中药方剂、药材或相关症状的问题时，你应该：
1. 分析用户问题，提取关键词
2. 使用适当的工具查询相关信息
3. 根据查询结果，组织专业、准确的回答
4. 引用查询到的信息来源，确保回答的可靠性

请记住：
- 只在你的知识范围内回答问题
- 如果数据库中没有相关信息，坦诚告知用户
- 不要编造信息或给出可能有害的医疗建议
- 建议用户重要的健康问题应当咨询专业医生

你的回答应当专业、准确、有帮助，并且基于查询到的实际数据。
"""

def get_system_prompt():
    """获取MCP系统提示"""
    return SYSTEM_PROMPT

def get_tool_prompt(tools):
    """根据可用工具生成工具提示
    
    Args:
        tools: 工具描述列表
        
    Returns:
        str: 工具提示文本
    """
    tool_descriptions = []
    for tool in tools:
        params_desc = ", ".join([f"{name}: {desc}" for name, desc in tool["parameters"].items()])
        tool_descriptions.append(f"- {tool['id']}: {tool['description']} (参数: {params_desc})")
    
    tool_prompt = "\n\n可用工具列表:\n" + "\n".join(tool_descriptions)
    return tool_prompt

def create_chat_prompt(user_input, tools=None):
    """创建带有工具信息的聊天提示
    
    Args:
        user_input: 用户输入
        tools: 可用工具列表（可选）
        
    Returns:
        str: 完整的聊天提示
    """
    prompt = SYSTEM_PROMPT
    
    if tools:
        prompt += get_tool_prompt(tools)
    
    prompt += f"\n\n用户问题: {user_input}"
    return prompt
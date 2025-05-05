import json
from db_manager import DBManager
from neo4j_manager import Neo4jManager

class ToolManager:
    """工具管理器，负责注册和管理可供大模型调用的工具"""
    
    def __init__(self):
        """初始化工具管理器"""
        self.tools = {}
        self.db_manager = None
        self.neo4j_manager = None
        self.register_default_tools()
    
    def register_default_tools(self):
        """注册默认工具"""
        # 初始化数据库管理器
        self.db_manager = DBManager()
        self.neo4j_manager = Neo4jManager()
        
        # 注册MySQL数据库查询工具
        self.register_tool(
            "search_herbs", 
            "搜索中药方剂信息", 
            self._search_herbs,
            {"keyword": "搜索关键词"}
        )
        
        self.register_tool(
            "search_medicines", 
            "搜索中药药材信息", 
            self._search_medicines,
            {"keyword": "搜索关键词"}
        )
        
        # 注册Neo4j图数据库查询工具
        self.register_tool(
            "search_graph", 
            "搜索知识图谱信息", 
            self._search_graph,
            {"keyword": "搜索关键词"}
        )
        
        # 注册统一搜索工具
        self.register_tool(
            "search_all", 
            "同时搜索方剂、药材和知识图谱", 
            self._search_all,
            {"keyword": "搜索关键词"}
        )
    
    def register_tool(self, tool_id, description, function, parameters=None):
        """注册一个新工具
        
        Args:
            tool_id: 工具唯一标识符
            description: 工具描述
            function: 工具执行函数
            parameters: 工具参数说明（可选）
        """
        self.tools[tool_id] = {
            "id": tool_id,
            "description": description,
            "function": function,
            "parameters": parameters or {}
        }
    
    def get_tool_descriptions(self):
        """获取所有工具的描述，用于提供给大模型
        
        Returns:
            list: 工具描述列表
        """
        descriptions = []
        for tool_id, tool in self.tools.items():
            descriptions.append({
                "id": tool_id,
                "description": tool["description"],
                "parameters": tool["parameters"]
            })
        return descriptions
    
    def execute_tool(self, tool_id, parameters):
        """执行指定的工具
        
        Args:
            tool_id: 工具ID
            parameters: 工具参数
            
        Returns:
            dict: 工具执行结果
        """
        if tool_id not in self.tools:
            return {"error": f"未找到工具: {tool_id}"}
        
        try:
            tool = self.tools[tool_id]
            result = tool["function"](**parameters)
            return {"result": result}
        except Exception as e:
            return {"error": f"工具执行失败: {str(e)}"}
    
    def _search_herbs(self, keyword):
        """搜索方剂信息
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 匹配的方剂列表
        """
        if not self.db_manager.connection or not self.db_manager.connection.is_connected():
            self.db_manager.connect()
        return self.db_manager.search_herbs(keyword)
    
    def _search_medicines(self, keyword):
        """搜索药材信息
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            list: 匹配的药材列表
        """
        if not self.db_manager.connection or not self.db_manager.connection.is_connected():
            self.db_manager.connect()
        return self.db_manager.search_medicines(keyword)
    
    def _search_graph(self, keyword):
        """搜索知识图谱
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            dict: 匹配的图谱节点和关系
        """
        if not self.neo4j_manager.driver:
            self.neo4j_manager.connect()
        return self.neo4j_manager.search_by_keyword(keyword)
    
    def _search_all(self, keyword):
        """统一搜索所有数据源
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            dict: 包含所有数据源搜索结果的字典
        """
        herbs = self._search_herbs(keyword)
        medicines = self._search_medicines(keyword)
        graph_data = self._search_graph(keyword)
        
        return {
            "herbs": herbs,
            "medicines": medicines,
            "graph_data": graph_data
        }
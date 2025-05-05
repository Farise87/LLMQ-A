import os

class KnowledgeBase:
    """知识库管理类，负责加载和检索知识库"""
    
    def __init__(self, csv_path=None):
        """初始化知识库管理器
        
        Args:
            csv_path: CSV方剂知识库路径
        """
        # 保留CSV路径以兼容现有代码
        self.csv_path = csv_path
    
    def set_csv_path(self, csv_path):
        """设置CSV方剂知识库路径
        
        Args:
            csv_path: CSV方剂知识库路径
        """
        self.csv_path = csv_path
    

    
    def load_knowledge_base(self):
        """加载知识库（已简化，不再使用向量索引）"""
        # 返回True表示加载成功，实际上不再需要加载任何内容
        print("知识库管理器已初始化（MCP模式）")
        return True
    
    def load_csv_knowledge(self):
        """加载CSV方剂知识库（已简化，不再实际加载）"""
        # 保留此方法以兼容现有代码
        print("知识库已切换为MCP模式，不再使用本地CSV文件")
        return True
    

    
    def retrieve_relevant_info(self, query, top_k=3):
        """检索与查询相关的方剂信息（已简化，不再使用向量检索）
        
        Args:
            query: 查询文本
            top_k: 返回的最大结果数
            
        Returns:
            str: 检索到的相关信息
        """
        # 不再使用本地检索，返回空字符串
        # MCP系统将通过工具API直接查询数据库
        return ""
    
    def retrieve_prescription_info(self, query, top_k=3):
        """检索与查询相关的方剂信息（已简化，不再使用向量检索）
        
        Args:
            query: 查询文本
            top_k: 返回的最大结果数
            
        Returns:
            str: 检索到的方剂信息
        """
        # 不再使用本地检索，返回空字符串
        # MCP系统将通过工具API直接查询数据库
        return ""
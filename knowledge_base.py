import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KnowledgeBase:
    """知识库管理类，负责加载和检索知识库"""
    
    def __init__(self, csv_path=None):
        """初始化知识库管理器
        
        Args:
            csv_path: CSV方剂知识库路径
        """
        # CSV方剂知识库相关变量
        self.csv_path = csv_path
        self.df_prescriptions = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
    
    def set_csv_path(self, csv_path):
        """设置CSV方剂知识库路径
        
        Args:
            csv_path: CSV方剂知识库路径
        """
        self.csv_path = csv_path
    

    
    def load_knowledge_base(self):
        """加载CSV方剂知识库并构建向量索引"""
        csv_success = self.load_csv_knowledge()
        
        return csv_success
    
    def load_csv_knowledge(self):
        """加载CSV方剂知识库"""
        try:
            # 检查CSV文件是否存在
            if not os.path.exists(self.csv_path):
                print(f"错误：方剂知识库文件不存在于路径 {self.csv_path}")
                return False
                
            print(f"加载方剂知识库: {self.csv_path}")
            
            # 读取CSV文件
            self.df_prescriptions = pd.read_csv(self.csv_path)
            
            # 合并相关字段作为检索文本
            self.df_prescriptions['combined_text'] = self.df_prescriptions.apply(
                lambda row: ' '.join([str(val) for val in row.values if pd.notna(val) and val != '']), 
                axis=1
            )
            
            # 创建TF-IDF向量
            self.tfidf_vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df_prescriptions['combined_text'])
            
            print(f"方剂知识库加载成功! 共 {len(self.df_prescriptions)} 条记录")
            return True
        except Exception as e:
            print(f"方剂知识库加载失败: {str(e)}")
            return False
    

    
    def retrieve_relevant_info(self, query, top_k=3):
        """检索与查询相关的方剂信息
        
        Args:
            query: 查询文本
            top_k: 返回的最大结果数
            
        Returns:
            str: 检索到的相关信息
        """
        # 检索方剂信息
        prescription_info = self.retrieve_prescription_info(query, top_k)
        
        # 返回信息
        if prescription_info:
            return f"【方剂知识】\n{prescription_info}"
        else:
            return ""
    
    def retrieve_prescription_info(self, query, top_k=3):
        """检索与查询相关的方剂信息
        
        Args:
            query: 查询文本
            top_k: 返回的最大结果数
            
        Returns:
            str: 检索到的方剂信息
        """
        if self.tfidf_vectorizer is None or self.tfidf_matrix is None or self.df_prescriptions is None:
            return ""
        
        # 将查询转换为TF-IDF向量
        query_vector = self.tfidf_vectorizer.transform([query])
        
        # 计算余弦相似度
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # 获取相似度最高的top_k个索引
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # 提取相关方剂信息
        relevant_info = ""
        for idx in top_indices:
            if similarities[idx] > 0.1:  # 设置相似度阈值
                prescription = self.df_prescriptions.iloc[idx]
                relevant_info += f"方剂名称: {prescription['药剂']}\n"
                relevant_info += f"配方: {prescription['配方']}\n"
                relevant_info += f"功用: {prescription['功用']}\n"
                relevant_info += f"适用症状: {prescription['症状']}\n"
                relevant_info += f"使用注意: {prescription['使用注意']}\n"
                relevant_info += f"用法用量: {prescription['用法用量']}\n\n"
        
        return relevant_info
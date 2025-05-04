from neo4j import GraphDatabase

class Neo4jManager:
    """Neo4j图数据库管理类，负责处理Neo4j数据库连接和查询"""
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """初始化Neo4j数据库管理器
        
        Args:
            uri: Neo4j数据库URI
            user: 数据库用户名
            password: 数据库密码
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
    
    def connect(self):
        """连接到Neo4j数据库"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # 测试连接
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            print(f"Neo4j数据库连接错误: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
    
    def get_all_nodes(self):
        """获取所有节点"""
        if not self.driver:
            if not self.connect():
                return []
        
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (n) RETURN n")
                return [record["n"] for record in result]
        except Exception as e:
            print(f"查询Neo4j节点时出错: {e}")
            return []
    
    def get_all_relationships(self):
        """获取所有关系"""
        if not self.driver:
            if not self.connect():
                return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n)-[r]->(m) 
                    RETURN n.name AS source, m.name AS target, type(r) AS relationship, 
                    properties(n) AS source_props, properties(m) AS target_props, properties(r) AS rel_props
                """)
                return [record for record in result]
        except Exception as e:
            print(f"查询Neo4j关系时出错: {e}")
            return []
    
    def get_graph_data(self):
        """获取完整的图数据用于可视化"""
        if not self.driver:
            if not self.connect():
                return {"nodes": [], "links": []}
        
        try:
            with self.driver.session() as session:
                # 获取所有节点
                node_result = session.run("""
                    MATCH (n) 
                    RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties
                """)
                nodes = []
                for record in node_result:
                    node = {
                        "id": record["id"],
                        "labels": record["labels"],
                        "properties": record["properties"]
                    }
                    # 确保节点有名称属性
                    if "name" in record["properties"]:
                        node["name"] = record["properties"]["name"]
                    elif "名称" in record["properties"]:
                        node["name"] = record["properties"]["名称"]
                    else:
                        # 使用第一个属性作为名称
                        for key, value in record["properties"].items():
                            if isinstance(value, str):
                                node["name"] = value
                                break
                        # 如果没有找到合适的属性，使用ID
                        if "name" not in node:
                            node["name"] = f"Node {record['id']}"
                    
                    nodes.append(node)
                
                # 获取所有关系
                rel_result = session.run("""
                    MATCH (n)-[r]->(m) 
                    RETURN id(r) AS id, id(n) AS source, id(m) AS target, type(r) AS type, properties(r) AS properties
                """)
                links = []
                for record in rel_result:
                    link = {
                        "id": record["id"],
                        "source": record["source"],
                        "target": record["target"],
                        "type": record["type"],
                        "properties": record["properties"]
                    }
                    links.append(link)
                
                return {"nodes": nodes, "links": links}
        except Exception as e:
            print(f"获取Neo4j图数据时出错: {e}")
            return {"nodes": [], "links": []}
    
    def search_by_keyword(self, keyword):
        """根据关键词搜索节点
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的节点和它们的关系
        """
        if not self.driver:
            if not self.connect():
                return {"nodes": [], "links": []}
        
        try:
            with self.driver.session() as session:
                # 首先找到包含关键词的节点
                node_result = session.run("""
                    MATCH (n)
                    WHERE any(key IN keys(n) WHERE toString(n[key]) CONTAINS $keyword)
                    RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties
                """, keyword=keyword)
                
                nodes = []
                node_ids = set()
                
                for record in node_result:
                    node_ids.add(record["id"])
                    node = {
                        "id": record["id"],
                        "labels": record["labels"],
                        "properties": record["properties"]
                    }
                    # 确保节点有名称属性
                    if "name" in record["properties"]:
                        node["name"] = record["properties"]["name"]
                    elif "名称" in record["properties"]:
                        node["name"] = record["properties"]["名称"]
                    else:
                        # 使用第一个属性作为名称
                        for key, value in record["properties"].items():
                            if isinstance(value, str):
                                node["name"] = value
                                break
                        # 如果没有找到合适的属性，使用ID
                        if "name" not in node:
                            node["name"] = f"Node {record['id']}"
                    
                    nodes.append(node)
                
                # 如果没有找到节点，返回空结果
                if not node_ids:
                    return {"nodes": [], "links": []}
                
                # 查找与这些节点直接相关的其他节点和关系
                expanded_result = session.run("""
                    MATCH (n)-[r]-(m)
                    WHERE id(n) IN $node_ids
                    RETURN id(n) AS source_id, id(m) AS target_id, id(r) AS rel_id,
                           labels(n) AS source_labels, labels(m) AS target_labels,
                           properties(n) AS source_props, properties(m) AS target_props,
                           type(r) AS rel_type, properties(r) AS rel_props
                """, node_ids=list(node_ids))
                
                # 处理扩展节点和关系
                links = []
                for record in expanded_result:
                    # 添加目标节点（如果不在列表中）
                    if record["target_id"] not in node_ids:
                        node_ids.add(record["target_id"])
                        target_node = {
                            "id": record["target_id"],
                            "labels": record["target_labels"],
                            "properties": record["target_props"]
                        }
                        # 设置节点名称
                        if "name" in record["target_props"]:
                            target_node["name"] = record["target_props"]["name"]
                        elif "名称" in record["target_props"]:
                            target_node["name"] = record["target_props"]["名称"]
                        else:
                            for key, value in record["target_props"].items():
                                if isinstance(value, str):
                                    target_node["name"] = value
                                    break
                            if "name" not in target_node:
                                target_node["name"] = f"Node {record['target_id']}"
                        
                        nodes.append(target_node)
                    
                    # 添加关系
                    link = {
                        "id": record["rel_id"],
                        "source": record["source_id"],
                        "target": record["target_id"],
                        "type": record["rel_type"],
                        "properties": record["rel_props"]
                    }
                    links.append(link)
                
                return {"nodes": nodes, "links": links}
        except Exception as e:
            print(f"搜索Neo4j数据时出错: {e}")
            return {"nodes": [], "links": []} 
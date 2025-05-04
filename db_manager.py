import mysql.connector
from mysql.connector import Error

class DBManager:
    """数据库管理类，负责处理MySQL数据库连接和查询"""
    
    def __init__(self, host="localhost", user="root", password="2025", database="fangji"):
        """初始化数据库管理器
        
        Args:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            return True
        except Error as e:
            print(f"数据库连接错误: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def get_all_herbs(self):
        """获取所有方剂信息"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM chinese_medicine"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"查询数据时出错: {e}")
            return []
    
    def search_herbs(self, keyword):
        """搜索方剂信息
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的方剂列表
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            # 在多个字段中搜索关键词
            query = """SELECT * FROM chinese_medicine 
                     WHERE 药剂 LIKE %s 
                     OR 功用 LIKE %s 
                     OR 症状 LIKE %s 
                     OR 组成 LIKE %s"""
            search_param = f"%{keyword}%"
            cursor.execute(query, (search_param, search_param, search_param, search_param))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"搜索数据时出错: {e}")
            return []
    
    def get_herbs_by_category(self, category):
        """按分类获取方剂
        
        Args:
            category: 方剂分类名称
        
        Returns:
            该分类下的方剂列表
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            # 在功用字段中搜索分类关键词
            query = "SELECT * FROM chinese_medicine WHERE 功用 LIKE %s"
            search_param = f"%{category}%"
            cursor.execute(query, (search_param,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"按分类查询数据时出错: {e}")
            return []

    # 新增药材相关方法
    def get_all_medicines(self):
        """获取所有药材信息"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM medicine_data"
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"查询药材数据时出错: {e}")
            return []
    
    def search_medicines(self, keyword):
        """搜索药材信息
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的药材列表
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            # 在多个字段中搜索关键词
            query = """SELECT * FROM medicine_data 
                     WHERE 药材 LIKE %s 
                     OR 别名 LIKE %s 
                     OR 功用 LIKE %s 
                     OR 症状 LIKE %s"""
            search_param = f"%{keyword}%"
            cursor.execute(query, (search_param, search_param, search_param, search_param))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"搜索药材数据时出错: {e}")
            return []
    
    def get_medicines_by_function(self, function):
        """按功用分类获取药材
        
        Args:
            function: 药材功用关键词
        
        Returns:
            该功用分类下的药材列表
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            # 在功用字段中搜索分类关键词
            query = "SELECT * FROM medicine_data WHERE 功用 LIKE %s"
            search_param = f"%{function}%"
            cursor.execute(query, (search_param,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"按功用查询药材数据时出错: {e}")
            return []

    def search_all(self, keyword):
        """搜索方剂和药材信息

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的方剂和药材列表
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return {'herbs': [], 'medicines': []}

        results = {'herbs': [], 'medicines': []}
        search_param = f"%{keyword}%"

        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 搜索方剂 (chinese_medicine)
            herb_query = """SELECT * FROM chinese_medicine 
                          WHERE 药剂 LIKE %s 
                          OR 功用 LIKE %s 
                          OR 症状 LIKE %s 
                          OR 组成 LIKE %s"""
            cursor.execute(herb_query, (search_param, search_param, search_param, search_param))
            results['herbs'] = cursor.fetchall()

            # 搜索药材 (medicine_data)
            medicine_query = """SELECT * FROM medicine_data 
                              WHERE 药材 LIKE %s 
                              OR 别名 LIKE %s 
                              OR 功用 LIKE %s 
                              OR 症状 LIKE %s"""
            cursor.execute(medicine_query, (search_param, search_param, search_param, search_param))
            results['medicines'] = cursor.fetchall()
            
            cursor.close()
            return results
        except Error as e:
            print(f"搜索方剂和药材数据时出错: {e}")
            return {'herbs': [], 'medicines': []}

    def get_medicine_functions(self):
        """获取所有药材功用分类
        
        Returns:
            药材功用分类列表
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            # 获取功用字段的不同值
            query = "SELECT DISTINCT 功用 FROM medicine_data"
            cursor.execute(query)
            result = [row[0] for row in cursor.fetchall() if row[0]]
            cursor.close()
            return result
        except Error as e:
            print(f"获取药材功用分类时出错: {e}")
            return []
            
    # 药材管理方法
    def add_medicine(self, medicine_data):
        """添加新药材
        
        Args:
            medicine_data: 包含药材信息的字典
            
        Returns:
            成功返回True，失败返回False
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
                
        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO medicine_data 
                    (药材, 别名, 性味归经, 功用, 症状, 药材分类, 用法用量, 注意事项) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (
                medicine_data.get('药材', ''),
                medicine_data.get('别名', ''),
                medicine_data.get('性味归经', ''),
                medicine_data.get('功用', ''),
                medicine_data.get('症状', ''),
                medicine_data.get('药材分类', ''),
                medicine_data.get('用法用量', ''),
                medicine_data.get('注意事项', '')
            )
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"添加药材时出错: {e}")
            return False
            
    def update_medicine(self, medicine_id, medicine_data):
        """更新药材信息
        
        Args:
            medicine_id: 药材ID
            medicine_data: 包含药材更新信息的字典
            
        Returns:
            成功返回True，失败返回False
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
                
        try:
            cursor = self.connection.cursor()
            query = """UPDATE medicine_data 
                    SET 药材 = %s, 别名 = %s, 性味归经 = %s, 功用 = %s, 症状 = %s, 药材分类 = %s, 用法用量 = %s, 注意事项 = %s
                    WHERE id = %s"""
            values = (
                medicine_data.get('药材', ''),
                medicine_data.get('别名', ''),
                medicine_data.get('性味归经', ''),
                medicine_data.get('功用', ''),
                medicine_data.get('症状', ''),
                medicine_data.get('药材分类', ''),
                medicine_data.get('用法用量', ''),
                medicine_data.get('注意事项', ''),
                medicine_id
            )
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"更新药材时出错: {e}")
            return False
            
    def delete_medicine(self, medicine_id):
        """删除药材
        
        Args:
            medicine_id: 药材ID
            
        Returns:
            成功返回True，失败返回False
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
                
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM medicine_data WHERE id = %s"
            cursor.execute(query, (medicine_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"删除药材时出错: {e}")
            return False
            
    # 方剂管理方法
    def add_herb(self, herb_data):
        """添加新方剂
        
        Args:
            herb_data: 包含方剂信息的字典
            
        Returns:
            成功返回True，失败返回False
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
                
        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO chinese_medicine 
                    (药剂, 功用, 症状, 组成) 
                    VALUES (%s, %s, %s, %s)"""
            values = (
                herb_data.get('药剂', ''),
                herb_data.get('功用', ''),
                herb_data.get('症状', ''),
                herb_data.get('组成', '')
            )
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"添加方剂时出错: {e}")
            return False
            
    def update_herb(self, herb_id, herb_data):
        """更新方剂信息
        
        Args:
            herb_id: 方剂ID
            herb_data: 包含方剂更新信息的字典
            
        Returns:
            成功返回True，失败返回False
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
                
        try:
            cursor = self.connection.cursor()
            query = """UPDATE chinese_medicine 
                    SET 药剂 = %s, 功用 = %s, 症状 = %s, 组成 = %s
                    WHERE id = %s"""
            values = (
                herb_data.get('药剂', ''),
                herb_data.get('功用', ''),
                herb_data.get('症状', ''),
                herb_data.get('组成', ''),
                herb_id
            )
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"更新方剂时出错: {e}")
            return False
            
    def delete_herb(self, herb_id):
        """删除方剂
        
        Args:
            herb_id: 方剂ID
            
        Returns:
            成功返回True，失败返回False
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
                
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM chinese_medicine WHERE id = %s"
            cursor.execute(query, (herb_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"删除方剂时出错: {e}")
            return False
            
    def get_herb_by_id(self, herb_id):
        """通过ID获取方剂信息
        
        Args:
            herb_id: 方剂ID
            
        Returns:
            方剂信息字典
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
                
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM chinese_medicine WHERE id = %s"
            cursor.execute(query, (herb_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"获取方剂信息时出错: {e}")
            return None
            
    def get_medicine_by_id(self, medicine_id):
        """通过ID获取药材信息
        
        Args:
            medicine_id: 药材ID
            
        Returns:
            药材信息字典
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
                
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM medicine_data WHERE id = %s"
            cursor.execute(query, (medicine_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"获取药材信息时出错: {e}")
            return None
            
    def get_medicine_count(self):
        """获取药材总数"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return 0
        
        try:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM medicine_data"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
        except Error as e:
            print(f"获取药材总数时出错: {e}")
            return 0
            
    def get_herb_count(self):
        """获取方剂总数"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return 0
        
        try:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM chinese_medicine"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
        except Error as e:
            print(f"获取方剂总数时出错: {e}")
            return 0
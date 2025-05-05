import os
import threading
import json
from flask import request, jsonify, render_template, redirect, url_for, session
from db_manager import DBManager
from neo4j_manager import Neo4jManager
from tool_manager import ToolManager

class ApiRoutes:
    """API路由处理类，负责处理Web API请求"""
    
    def __init__(self, app, model_manager, knowledge_base, generation_manager):
        """初始化API路由处理器
        
        Args:
            app: Flask应用实例
            model_manager: 模型管理器实例
            knowledge_base: 知识库管理器实例
            generation_manager: 生成任务管理器实例
        """
        self.app = app
        self.model_manager = model_manager
        self.knowledge_base = knowledge_base
        self.generation_manager = generation_manager
        self.db_manager = DBManager()
        self.neo4j_manager = Neo4jManager()
        
        # 注册路由
        self.register_routes()
    
    def register_routes(self):
        """注册所有API路由"""
        # 页面路由
        self.app.route('/')(self.home)
        self.app.route('/assistant')(self.assistant)
        self.app.route('/herbs')(self.herbs)
        self.app.route('/knowledge-graph')(self.knowledge_graph)
        self.app.route('/药材百科.html')(self.herbs_encyclopedia)
        self.app.route('/herbs.html')(self.herbs)
        self.app.route('/方剂大全.html')(self.herbs)
        self.app.route('/中医资讯.html')(self.zhongyi_news)
        self.app.route('/资讯目录.html')(self.news_list)
        self.app.route('/index.html')(self.assistant)
        self.app.route('/newhome.html')(self.home)
        self.app.route('/admin')(self.admin)
        self.app.route('/login')(self.login)  
        self.app.route('/login', methods=['POST'])(self.authenticate)
        self.app.route('/logout')(self.logout)
        
        # API路由
        self.app.route('/api/chat', methods=['POST'])(self.chat)
        self.app.route('/api/generation_status', methods=['GET'])(self.generation_status)
        self.app.route('/api/cancel_generation', methods=['POST'])(self.cancel_generation)
        self.app.route('/api/model_status')(self.model_status)
        
        # 方剂数据库API路由
        self.app.route('/api/herbs', methods=['GET'])(self.get_herbs)
        self.app.route('/api/herbs/search', methods=['GET'])(self.search_herbs)
        self.app.route('/api/herbs/category', methods=['GET'])(self.get_herbs_by_category)
        
        # 药材数据库API路由
        self.app.route('/api/medicines', methods=['GET'])(self.get_medicines)
        self.app.route('/api/medicines/search', methods=['GET'])(self.search_medicines)
        self.app.route('/api/medicines/function', methods=['GET'])(self.get_medicines_by_function)
        self.app.route('/api/medicines/functions', methods=['GET'])(self.get_medicine_functions)
        
        # 新增：统一搜索API路由
        self.app.route('/api/search_all', methods=['GET'])(self.search_all)
        
        # 知识图谱API路由
        self.app.route('/api/graph/data', methods=['GET'])(self.get_graph_data)
        self.app.route('/api/graph/search', methods=['GET'])(self.search_graph)
        
        # 管理后台API路由 - 药材管理
        self.app.route('/api/admin/medicines', methods=['GET'])(self.admin_get_medicines)
        self.app.route('/api/admin/medicines/<int:medicine_id>', methods=['GET'])(self.admin_get_medicine_by_id)
        self.app.route('/api/admin/medicines', methods=['POST'])(self.admin_add_medicine)
        self.app.route('/api/admin/medicines/<int:medicine_id>', methods=['PUT'])(self.admin_update_medicine)
        self.app.route('/api/admin/medicines/<int:medicine_id>', methods=['DELETE'])(self.admin_delete_medicine)
        
        # 管理后台API路由 - 方剂管理
        self.app.route('/api/admin/herbs', methods=['GET'])(self.admin_get_herbs)
        self.app.route('/api/admin/herbs/<int:herb_id>', methods=['GET'])(self.admin_get_herb_by_id)
        self.app.route('/api/admin/herbs', methods=['POST'])(self.admin_add_herb)
        self.app.route('/api/admin/herbs/<int:herb_id>', methods=['PUT'])(self.admin_update_herb)
        self.app.route('/api/admin/herbs/<int:herb_id>', methods=['DELETE'])(self.admin_delete_herb)

        # 管理后台API路由 - 统计数据
        self.app.route('/api/admin/counts', methods=['GET'])(self.get_medicine_and_herb_counts)
        
        # 工具系统API路由
        self.app.route('/api/tools', methods=['GET'])(self.get_tools)
        self.app.route('/api/tools/execute', methods=['POST'])(self.execute_tool)
        
        # 资讯相关API路由
        self.app.route('/api/news', methods=['GET'])(self.get_news)
        self.app.route('/api/news/<int:news_id>', methods=['GET'])(self.get_news_detail)
        self.app.route('/news/<int:news_id>')(self.news_detail)
    
    def home(self):
        """渲染主页"""
        return render_template('newhome.html')
        
    def assistant(self):
        """渲染智能助手页面"""
        return render_template('index.html')
        
    def herbs(self):
        """渲染方剂知识库页面"""
        return render_template('方剂大全.html')
        
    def herbs_encyclopedia(self):
        """渲染药材百科页面"""
        return render_template('药材百科.html')
    
    def zhongyi_news(self):
        """渲染中医资讯页面"""
        return render_template('中医资讯.html')
    
    def knowledge_graph(self):
        """渲染知识图谱页面"""
        return render_template('knowledge_graph.html')
    
    def admin(self):
        """渲染管理后台页面"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return redirect(url_for('login'))
        return render_template('admin.html')
    
    def login(self):
        """渲染登录页面"""
        return render_template('后台管理进入.html')
    
    def authenticate(self):
        """处理登录验证"""
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 验证用户名和密码 (可以根据实际需求改为数据库查询)
        if username == '123' and password == '123':
            session['admin_logged_in'] = True
            session['username'] = username
            return redirect(url_for('admin'))
        
        # 返回登录失败信息，可以通过JavaScript显示
        return render_template('后台管理进入.html', error='用户名或密码错误')
    
    def logout(self):
        """处理登出"""
        session.pop('admin_logged_in', None)
        session.pop('username', None)
        return redirect(url_for('login'))
    
    def get_herbs(self):
        """获取所有方剂信息"""
        herbs = self.db_manager.get_all_herbs()
        return jsonify(herbs)
    
    def search_herbs(self):
        """搜索方剂信息"""
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify([]), 400
        
        herbs = self.db_manager.search_herbs(keyword)
        return jsonify(herbs)
    
    def get_herbs_by_category(self):
        """按分类获取方剂"""
        category = request.args.get('category', '')
        if not category:
            return jsonify([]), 400
        
        herbs = self.db_manager.get_herbs_by_category(category)
        return jsonify(herbs)
    
    # 药材数据API处理方法
    def get_medicines(self):
        """获取所有药材信息"""
        medicines = self.db_manager.get_all_medicines()
        return jsonify(medicines)
    
    def search_medicines(self):
        """搜索药材信息"""
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify([]), 400
        
        medicines = self.db_manager.search_medicines(keyword)
        return jsonify(medicines)
    
    def get_medicines_by_function(self):
        """按功用分类获取药材"""
        function = request.args.get('function', '')
        if not function:
            return jsonify([]), 400
        
        medicines = self.db_manager.get_medicines_by_function(function)
        return jsonify(medicines)
    
    def get_medicine_functions(self):
        """获取所有药材功用分类"""
        functions = self.db_manager.get_medicine_functions()
        return jsonify(functions)
    
    # 新增：统一搜索处理方法
    def search_all(self):
        """搜索方剂和药材信息"""
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({'herbs': [], 'medicines': []}), 400
        
        results = self.db_manager.search_all(keyword)
        return jsonify(results)
        
    # 资讯相关API处理方法
    def get_news(self):
        """获取所有资讯信息"""
        news = self.db_manager.get_all_news()
        return jsonify(news)
    
    def get_news_detail(self, news_id):
        """获取资讯详情API"""
        news = self.db_manager.get_news_by_id(news_id)
        if not news:
            return jsonify({"error": "找不到指定资讯"}), 404
        return jsonify(news)
    
    def news_detail(self, news_id):
        """渲染资讯详情页面"""
        news = self.db_manager.get_news_by_id(news_id)
        if not news:
            return redirect(url_for('zhongyi_news'))
        return render_template('最新资讯详情.html', news=news)
        
    def news_list(self):
        """渲染资讯目录页面"""
        return render_template('资讯目录.html')

    def get_graph_data(self):
        """获取知识图谱数据"""
        try:
            data = self.neo4j_manager.get_graph_data()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def search_graph(self):
        """搜索知识图谱"""
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({"nodes": [], "links": []}), 400
        
        try:
            data = self.neo4j_manager.search_by_keyword(keyword)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def chat(self):
        """处理聊天请求"""
        # 如果模型未加载，尝试加载
        if not self.model_manager.is_model_loaded():
            success = self.model_manager.load_model()
            if not success:
                return jsonify({"error": "模型加载失败，请检查模型路径"}), 500
        
        # 获取请求数据
        data = request.json
        user_input = data.get('message', '')
        session_id = data.get('session_id', str(hash(user_input + str(os.urandom(4)))))
        
        # 清理已完成的生成任务
        self.generation_manager.clean_completed_generations()
        
        try:
            # 导入MCP系统提示模块
            from mcp_system_prompt import create_chat_prompt
            
            # 获取工具描述
            tools = self.model_manager.tool_manager.get_tool_descriptions()
            
            # 创建带有MCP系统提示和工具信息的提示
            prompt = create_chat_prompt(user_input, tools)
            
            # 不再使用知识库检索，完全依赖MCP系统通过工具API查询数据库
            # 创建新的生成任务，knowledge_info参数传入空字符串
            self.generation_manager.create_generation_task(session_id, prompt, "")
            
            # 在单独线程中启动生成任务
            thread = threading.Thread(
                target=self.generation_manager.generate_response_thread,
                args=(self.model_manager, session_id, prompt)
            )
            thread.daemon = True  # 设置为守护线程，这样主程序退出时线程会自动结束
            thread.start()
            
            # 立即返回会话ID，客户端可以用它来查询状态
            return jsonify({
                "session_id": session_id,
                "status": "running"
            })
        except Exception as e:
            return jsonify({"error": f"处理请求时出错: {str(e)}"}), 500
    
    def get_tools(self):
        """获取可用工具列表"""
        try:
            # 从模型管理器获取工具描述
            tool_descriptions = self.model_manager.tool_manager.get_tool_descriptions()
            return jsonify({
                'tools': tool_descriptions
            })
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500
    
    def execute_tool(self):
        """执行工具"""
        try:
            # 获取请求数据
            data = request.get_json()
            tool_id = data.get('tool_id')
            parameters = data.get('parameters', {})
            
            if not tool_id:
                return jsonify({
                    'error': '未提供工具ID'
                }), 400
            
            # 执行工具
            result = self.model_manager.tool_manager.execute_tool(tool_id, parameters)
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500
    
    def generation_status(self):
        """获取生成任务的状态"""
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({"error": "缺少session_id参数"}), 400
        
        generation_info = self.generation_manager.get_generation_status(session_id)
        if generation_info is None:
            return jsonify({"error": "找不到指定的生成任务"}), 404
        
        if generation_info['status'] == 'running':
            return jsonify({
                "status": "running"
            })
        elif generation_info['status'] == 'completed':
            # 任务完成，返回结果
            # 不再返回knowledge_info，因为已经移除RAG，所有知识信息将通过MCP工具API直接获取
            result = {
                "status": "completed",
                "response": generation_info['result']
            }
            return jsonify(result)
        elif generation_info['status'] == 'error':
            # 任务出错
            result = {
                "status": "error",
                "error": generation_info['error']
            }
            return jsonify(result)
        elif generation_info['status'] == 'cancelled':
            # 任务被取消
            result = {
                "status": "cancelled"
            }
            return jsonify(result)
    
    def cancel_generation(self):
        """取消正在进行的生成任务"""
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"error": "缺少session_id参数"}), 400
        
        success = self.generation_manager.cancel_generation(session_id)
        if not success:
            return jsonify({"error": "找不到指定的生成任务"}), 404
        
        return jsonify({"status": "cancelled"})
    
    def model_status(self):
        """检查模型状态"""
        if not self.model_manager.is_model_loaded():
            # 尝试加载模型
            success = self.model_manager.load_model()
            return jsonify({"loaded": success})
        else:
            return jsonify({"loaded": True})
    
    # 管理后台API方法 - 药材管理
    def admin_get_medicines(self):
        """管理后台获取所有药材"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        medicines = self.db_manager.get_all_medicines()
        return jsonify(medicines)
    
    def admin_get_medicine_by_id(self, medicine_id):
        """管理后台通过ID获取药材"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        medicine = self.db_manager.get_medicine_by_id(medicine_id)
        if not medicine:
            return jsonify({"error": "找不到指定药材"}), 404
        
        return jsonify(medicine)
    
    def admin_add_medicine(self):
        """管理后台添加药材"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        data = request.json
        if not data:
            return jsonify({"error": "缺少药材数据"}), 400
        
        success = self.db_manager.add_medicine(data)
        if not success:
            return jsonify({"error": "添加药材失败"}), 500
        
        return jsonify({"message": "添加药材成功"})
    
    def admin_update_medicine(self, medicine_id):
        """管理后台更新药材"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        data = request.json
        if not data:
            return jsonify({"error": "缺少药材数据"}), 400
        
        # 检查药材是否存在
        medicine = self.db_manager.get_medicine_by_id(medicine_id)
        if not medicine:
            return jsonify({"error": "找不到指定药材"}), 404
        
        success = self.db_manager.update_medicine(medicine_id, data)
        if not success:
            return jsonify({"error": "更新药材失败"}), 500
        
        return jsonify({"message": "更新药材成功"})
    
    def admin_delete_medicine(self, medicine_id):
        """管理后台删除药材"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        # 检查药材是否存在
        medicine = self.db_manager.get_medicine_by_id(medicine_id)
        if not medicine:
            return jsonify({"error": "找不到指定药材"}), 404
        
        success = self.db_manager.delete_medicine(medicine_id)
        if not success:
            return jsonify({"error": "删除药材失败"}), 500
        
        return jsonify({"message": "删除药材成功"})
    
    # 管理后台API方法 - 方剂管理
    def admin_get_herbs(self):
        """管理后台获取所有方剂"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        herbs = self.db_manager.get_all_herbs()
        return jsonify(herbs)
    
    def admin_get_herb_by_id(self, herb_id):
        """管理后台通过ID获取方剂"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        herb = self.db_manager.get_herb_by_id(herb_id)
        if not herb:
            return jsonify({"error": "找不到指定方剂"}), 404
        
        return jsonify(herb)
    
    def admin_add_herb(self):
        """管理后台添加方剂"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        data = request.json
        if not data:
            return jsonify({"error": "缺少方剂数据"}), 400
        
        success = self.db_manager.add_herb(data)
        if not success:
            return jsonify({"error": "添加方剂失败"}), 500
        
        return jsonify({"message": "添加方剂成功"})
    
    def admin_update_herb(self, herb_id):
        """管理后台更新方剂"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        data = request.json
        if not data:
            return jsonify({"error": "缺少方剂数据"}), 400
        
        # 检查方剂是否存在
        herb = self.db_manager.get_herb_by_id(herb_id)
        if not herb:
            return jsonify({"error": "找不到指定方剂"}), 404
        
        success = self.db_manager.update_herb(herb_id, data)
        if not success:
            return jsonify({"error": "更新方剂失败"}), 500
        
        return jsonify({"message": "更新方剂成功"})
    
    def admin_delete_herb(self, herb_id):
        """管理后台删除方剂"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401
        
        # 检查方剂是否存在
        herb = self.db_manager.get_herb_by_id(herb_id)
        if not herb:
            return jsonify({"error": "找不到指定方剂"}), 404
        
        success = self.db_manager.delete_herb(herb_id)
        if not success:
            return jsonify({"error": "删除方剂失败"}), 500
        
        return jsonify({"message": "删除方剂成功"})

    def get_medicine_and_herb_counts(self):
        """获取药材和方剂总数"""
        # 检查用户是否已登录
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({"error": "未授权"}), 401

        medicine_count = self.db_manager.get_medicine_count()
        herb_count = self.db_manager.get_herb_count()
        return jsonify({"medicine_count": medicine_count, "herb_count": herb_count})
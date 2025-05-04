import threading

class GenerationManager:
    """生成任务管理器，负责管理和跟踪生成任务"""
    
    def __init__(self):
        """初始化生成任务管理器"""
        # 用于存储和管理生成任务的字典
        self.active_generations = {}
        # 线程锁，用于保护active_generations字典的并发访问
        self.generation_lock = threading.Lock()
    
    def create_generation_task(self, session_id, prompt, knowledge_info=""):
        """创建新的生成任务
        
        Args:
            session_id: 会话ID
            prompt: 提示文本
            knowledge_info: 相关知识信息
            
        Returns:
            bool: 任务是否创建成功
        """
        with self.generation_lock:
            # 检查是否已存在相同会话ID的任务
            if session_id in self.active_generations:
                return False
                
            # 创建新的生成任务
            self.active_generations[session_id] = {
                'status': 'running',
                'prompt': prompt,
                'result': None,
                'error': None,
                'knowledge_info': knowledge_info
            }
            return True
    
    def get_generation_status(self, session_id):
        """获取生成任务的状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            dict: 任务状态信息，如果任务不存在则返回None
        """
        with self.generation_lock:
            if session_id not in self.active_generations:
                return None
                
            return self.active_generations[session_id].copy()
    
    def update_generation_result(self, session_id, result):
        """更新生成任务的结果
        
        Args:
            session_id: 会话ID
            result: 生成的结果
            
        Returns:
            bool: 更新是否成功
        """
        with self.generation_lock:
            if session_id not in self.active_generations:
                return False
            
            # 如果结果中包含</think>标记，只保留标记后面的内容
            if '</think>' in result:
                result = result.split('</think>')[-1].lstrip()
                
            self.active_generations[session_id]['status'] = 'completed'
            self.active_generations[session_id]['result'] = result
            return True
    
    def update_generation_error(self, session_id, error):
        """更新生成任务的错误信息
        
        Args:
            session_id: 会话ID
            error: 错误信息
            
        Returns:
            bool: 更新是否成功
        """
        with self.generation_lock:
            if session_id not in self.active_generations:
                return False
                
            self.active_generations[session_id]['status'] = 'error'
            self.active_generations[session_id]['error'] = error
            return True
    
    def cancel_generation(self, session_id):
        """取消生成任务
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 取消是否成功
        """
        with self.generation_lock:
            if session_id not in self.active_generations:
                return False
                
            self.active_generations[session_id]['status'] = 'cancelled'
            return True
    
    def clean_completed_generations(self):
        """清理已完成或出错的生成任务"""
        with self.generation_lock:
            for session_id in list(self.active_generations.keys()):
                status = self.active_generations[session_id]['status']
                if status in ['completed', 'error', 'cancelled']:
                    self.active_generations.pop(session_id, None)
    
    def generate_response_thread(self, model, session_id, prompt, max_tokens=1024, temperature=0, top_p=0.95, stop=None, echo=False):
        """在单独线程中执行模型推理
        
        Args:
            model: 模型实例
            session_id: 会话ID
            prompt: 提示文本
            max_tokens: 生成的最大token数
            temperature: 温度参数
            top_p: top-p采样参数
            stop: 停止标记列表
            echo: 是否回显提示文本
        """
        try:
            # 生成回复
            response = model.create_completion(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                echo=echo
            )
            
            # 提取生成的文本
            generated_text = response['choices'][0]['text'].strip()
            
            # 更新生成状态
            self.update_generation_result(session_id, generated_text)
        except Exception as e:
            # 更新错误状态
            self.update_generation_error(session_id, str(e))
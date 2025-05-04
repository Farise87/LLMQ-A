from model_loaders.deepseek_api_loader import DeepseekAPILoader

class ModelManager:
    """模型管理器，负责API模型的配置和调用"""
    
    def __init__(self, config=None):
        """初始化模型管理器
        
        Args:
            config: API配置信息，包含api_key和可选的api_base
        """
        self.model = None
        self.config = config
    
    def set_config(self, config):
        """设置API配置
        
        Args:
            config: API配置信息，包含api_key和可选的api_base
        """
        self.config = config
    
    def load_model(self):
        """初始化API模型配置"""
        try:
            if self.config is None:
                print("错误：未设置API配置")
                return False
            
            if not isinstance(self.config, dict) or 'api_key' not in self.config:
                print("错误：API配置格式不正确，需要包含api_key")
                return False
            
            # 创建DeepSeek API加载器
            loader = DeepseekAPILoader()
            
            # 配置API
            success = loader.load_model(
                api_key=self.config['api_key'],
                api_base=self.config.get('api_base')
            )
            
            if not success:
                return False
            
            # 保存加载器实例
            self.model = loader
            print("API配置成功!")
            return True
            
        except Exception as e:
            print(f"API配置失败: {str(e)}")
            return False
    
    def is_model_loaded(self):
        """检查API是否已配置
        
        Returns:
            bool: API是否已配置
        """
        return self.model is not None
    
    def create_completion(self, prompt, max_tokens=2048, temperature=0, top_p=0.95, stop=None, echo=False):
        """使用API生成回复
        
        Args:
            prompt: 提示文本
            max_tokens: 生成的最大token数
            temperature: 温度参数
            top_p: top-p采样参数
            stop: 停止标记列表
            echo: 是否回显提示文本
            
        Returns:
            dict: 生成的回复
        """
        if not self.is_model_loaded():
            raise ValueError("API未配置，请先调用load_model方法")
            
        return self.model.create_completion(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
            echo=echo
        )
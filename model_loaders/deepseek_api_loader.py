import requests

class DeepseekAPILoader:
    """DeepSeek API加载器，用于调用DeepSeek API服务"""
    
    def __init__(self):
        """初始化DeepSeek API加载器"""
        self.api_key = None
        self.api_base = "https://api.deepseek.com/v1"
    
    def load_model(self, api_key=None, api_base=None):
        """设置API密钥和基础URL
        
        Args:
            api_key: DeepSeek API密钥
            api_base: API基础URL（可选）
            
        Returns:
            bool: 配置是否成功
        """
        if api_key is None:
            print("错误：未提供API密钥")
            return False
            
        self.api_key = api_key
        if api_base:
            self.api_base = api_base
        return True
    
    def create_completion(self, prompt, max_tokens=2048, temperature=0, top_p=0.95, stop=None, echo=False):
        """调用DeepSeek API生成回复
        
        Args:
            prompt: 提示文本
            max_tokens: 生成的最大token数
            temperature: 温度参数
            top_p: top-p采样参数
            stop: 停止标记列表
            echo: 是否回显提示文本
            
        Returns:
            dict: API返回的结果
        """
        if not self.api_key:
            raise ValueError("API密钥未设置，请先调用load_model方法设置API密钥")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": stop,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # 转换为与本地模型相同的输出格式
            return {
                "choices": [{
                    "text": result["choices"][0]["message"]["content"],
                    "finish_reason": result["choices"][0]["finish_reason"]
                }]
            }
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")
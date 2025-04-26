import os
from llama_cpp import Llama

class GGUFModelLoader:
    """GGUF模型加载器"""
    
    def __init__(self):
        self.model = None
        
    def load_model(self, model_path, n_ctx=2048, n_threads=4, n_gpu_layers=0, verbose=True):
        """加载GGUF模型
        
        Args:
            model_path: 模型文件路径
            n_ctx: 上下文窗口大小
            n_threads: 使用的线程数
            n_gpu_layers: GPU加速层数，0表示禁用GPU加速
            verbose: 是否启用详细日志
            
        Returns:
            bool: 加载是否成功
        """
        try:
            # 检查模型文件是否存在
            if not os.path.exists(model_path):
                print(f"错误：模型文件不存在于路径 {model_path}")
                return False
                
            print(f"尝试加载GGUF模型: {model_path}")
            print(f"llama-cpp-python版本: {Llama.__version__ if hasattr(Llama, '__version__') else '未知'}")
            
            # 尝试使用不同的参数组合加载模型
            try:
                # 方法1：使用基本参数
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=n_ctx,
                    n_threads=n_threads,
                    n_gpu_layers=n_gpu_layers,
                    verbose=verbose
                )
            except Exception as e1:
                print(f"尝试方法1失败: {str(e1)}")
                try:
                    # 方法2：使用legacy参数
                    self.model = Llama(
                        model_path=model_path,
                        n_ctx=n_ctx,
                        n_threads=n_threads,
                        n_gpu_layers=n_gpu_layers,
                        verbose=verbose,
                        legacy=True  # 尝试使用legacy模式加载
                    )
                except Exception as e2:
                    print(f"尝试方法2失败: {str(e2)}")
                    # 方法3：使用最小参数集
                    self.model = Llama(model_path=model_path)
                    
            print("GGUF模型加载成功!")
            return True
        except Exception as e:
            print(f"GGUF模型加载失败: {str(e)}")
            print("请检查模型格式是否与llama-cpp-python版本兼容")
            print("可能需要更新llama-cpp-python库或使用兼容的模型文件")
            return False
    
    def get_model(self):
        """获取加载的模型实例
        
        Returns:
            Llama: 模型实例，如果未加载则返回None
        """
        return self.model
    
    def create_completion(self, prompt, max_tokens=1024, temperature=0, top_p=0.95, stop=None, echo=False):
        """使用模型生成回复
        
        Args:
            prompt: 提示文本
            max_tokens: 生成的最大token数
            temperature: 温度参数
            top_p: top-p采样参数
            stop: 停止标记
            echo: 是否回显提示文本
            
        Returns:
            dict: 生成的回复
        """
        if self.model is None:
            raise ValueError("模型未加载，请先调用load_model方法")
            
        return self.model.create_completion(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
            echo=echo
        )
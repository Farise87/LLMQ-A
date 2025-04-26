import os
from .gguf_loader import GGUFModelLoader
from .safetensors_loader import SafetensorsModelLoader

class ModelLoaderFactory:
    """模型加载器工厂，根据模型格式自动选择合适的加载器"""
    
    @staticmethod
    def create_loader(model_path):
        """创建合适的模型加载器
        
        Args:
            model_path: 模型文件路径或目录
            
        Returns:
            适合的模型加载器实例
        """
        # 检查模型路径是否存在
        if not os.path.exists(model_path):
            print(f"错误：模型路径不存在 {model_path}")
            return None
            
        # 判断模型类型
        if os.path.isdir(model_path) or model_path.endswith('.safetensors'):
            # 目录或.safetensors文件视为Safetensors格式
            print(f"检测到Safetensors格式模型: {model_path}")
            return SafetensorsModelLoader()
        elif model_path.endswith('.gguf'):
            # .gguf文件视为GGUF格式
            print(f"检测到GGUF格式模型: {model_path}")
            return GGUFModelLoader()
        else:
            # 默认尝试GGUF格式
            print(f"未知模型格式，默认尝试GGUF格式: {model_path}")
            return GGUFModelLoader()
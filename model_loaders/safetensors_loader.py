import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class SafetensorsModelLoader:
    """Safetensors模型加载器"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None

    def load_model(self, model_path, device="cpu", load_in_8bit=False, torch_dtype=None, **kwargs):
        """加载Safetensors模型

        Args:
            model_path: 模型文件路径或Hugging Face模型ID
            device: 设备，可以是'cpu'或'cuda'
            load_in_8bit: 是否以8位精度加载模型
            torch_dtype: PyTorch数据类型，如torch.float16

        Returns:
            bool: 加载是否成功
        """
        try:
            # 检查模型路径是否存在（如果是本地路径）
            if os.path.exists(model_path) and not (os.path.isdir(model_path) or model_path.endswith('.safetensors')):
                print(f"错误：模型路径应该是目录或.safetensors文件: {model_path}")
                return False

            print(f"尝试加载Safetensors模型: {model_path}")

            # 设置设备
            if device == "cuda" and not torch.cuda.is_available():
                print("警告：CUDA不可用，将使用CPU")
                device = "cpu"

            # 设置数据类型
            if torch_dtype is None:
                torch_dtype = torch.float16 if device == "cuda" else torch.float32

            # 加载分词器
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)

            # 加载模型的配置
            model_kwargs = {
                "torch_dtype": torch_dtype,
            }

            # 特殊处理CPU和meta设备问题
            if device == "cpu":
                model_kwargs.update({
                    "device_map": None,  # 禁用device_map
                    "low_cpu_mem_usage": True,
                })
            else:
                model_kwargs["device_map"] = "auto"

            if load_in_8bit:
                model_kwargs["load_in_8bit"] = True
            else:
                model_kwargs["low_cpu_mem_usage"] = True

            # 确保不使用meta设备初始化
            model_kwargs["use_safetensors"] = True

            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                **model_kwargs
            )

            # 对于CPU情况，确保模型完全加载到内存
            if device == "cpu":
                self.model = self.model.to('cpu')
                # 确保所有参数都已加载
                for param in self.model.parameters():
                    if param.is_meta:
                        param.data = torch.nn.Parameter(torch.empty_like(param.data, device='cpu'))

            print("Safetensors模型加载成功!")
            return True
        except Exception as e:
            print(f"Safetensors模型加载失败: {str(e)}")
            return False



    def get_model(self):
        """获取加载的模型实例
        
        Returns:
            模型实例，如果未加载则返回None
        """
        return self.model
    
    def get_tokenizer(self):
        """获取加载的分词器实例
        
        Returns:
            分词器实例，如果未加载则返回None
        """
        return self.tokenizer
    
    def create_completion(self, prompt, max_tokens=1024, temperature=0, top_p=0.95, stop=None, echo=False):
        """使用模型生成回复
        
        Args:
            prompt: 提示文本
            max_tokens: 生成的最大token数
            temperature: 温度参数
            top_p: top-p采样参数
            stop: 停止标记列表
            echo: 是否回显提示文本
            
        Returns:
            dict: 生成的回复，格式与llama-cpp的create_completion兼容
        """
        if self.model is None or self.tokenizer is None:
            raise ValueError("模型未加载，请先调用load_model方法")
        
        # 编码输入
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # 生成参数
        gen_kwargs = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
        }
        
        # 处理停止标记
        if stop:
            gen_kwargs["stopping_criteria"] = self._create_stopping_criteria(stop, prompt)
        
        # 生成文本
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)
        
        # 解码输出
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 如果不需要回显提示，则移除提示部分
        if not echo and generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].lstrip()
        
        # 返回与llama-cpp兼容的格式
        return {
            "choices": [
                {
                    "text": generated_text,
                    "finish_reason": "stop"
                }
            ]
        }
    
    def _create_stopping_criteria(self, stop_strings, prompt):
        """创建停止标准
        
        Args:
            stop_strings: 停止字符串列表
            prompt: 提示文本
            
        Returns:
            停止标准
        """
        from transformers import StoppingCriteria, StoppingCriteriaList
        
        class StopStringCriteria(StoppingCriteria):
            def __init__(self, tokenizer, stop_strings, prompt_length):
                self.tokenizer = tokenizer
                self.stop_strings = stop_strings
                self.prompt_length = prompt_length
                
            def __call__(self, input_ids, scores, **kwargs):
                decoded = self.tokenizer.decode(input_ids[0][self.prompt_length:])
                return any(stop_string in decoded for stop_string in self.stop_strings)
        
        prompt_length = len(self.tokenizer(prompt, return_tensors="pt").input_ids[0])
        criteria = StopStringCriteria(self.tokenizer, stop_strings, prompt_length)
        return StoppingCriteriaList([criteria])
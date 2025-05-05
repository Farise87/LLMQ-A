import requests
import json
import re

class DeepseekAPILoader:
    """DeepSeek API加载器，用于调用DeepSeek API服务"""
    
    def __init__(self):
        """初始化DeepSeek API加载器"""
        self.api_key = None
        self.api_base = "https://api.deepseek.com/v1"
        self.tool_manager = None
    
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
    
    def set_tool_manager(self, tool_manager):
        """设置工具管理器
        
        Args:
            tool_manager: 工具管理器实例
        """
        self.tool_manager = tool_manager
    
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
        
        # 准备消息内容
        messages = [{"role": "user", "content": prompt}]
        
        # 如果有工具管理器，添加工具定义
        tools = None
        if self.tool_manager:
            tools = []
            for tool_desc in self.tool_manager.get_tool_descriptions():
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool_desc["id"],
                        "description": tool_desc["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {
                                param_name: {"type": "string", "description": param_desc}
                                for param_name, param_desc in tool_desc["parameters"].items()
                            },
                            "required": list(tool_desc["parameters"].keys())
                        }
                    }
                })
        
        # 构建请求数据
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": stop,
            "stream": False
        }
        
        # 如果有工具定义，添加到请求中
        if tools:
            data["tools"] = tools
            data["tool_choice"] = "auto"
        
        try:
            # 发送请求
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # 检查是否有工具调用
            if "tool_calls" in result["choices"][0]["message"]:
                # 处理工具调用
                return self._handle_tool_calls(result, messages, data)
            else:
                # 转换为与本地模型相同的输出格式
                return {
                    "choices": [{
                        "text": result["choices"][0]["message"]["content"],
                        "finish_reason": result["choices"][0]["finish_reason"]
                    }]
                }
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")
    
    def _handle_tool_calls(self, result, messages, data):
        """处理工具调用
        
        Args:
            result: API返回的结果
            messages: 当前的消息列表
            data: 原始请求数据
            
        Returns:
            dict: 处理后的结果
        """
        if not self.tool_manager:
            raise ValueError("未设置工具管理器，无法处理工具调用")
        
        # 获取工具调用信息
        tool_calls = result["choices"][0]["message"]["tool_calls"]
        assistant_message = result["choices"][0]["message"]
        
        # 添加助手消息到消息历史
        messages.append({
            "role": "assistant",
            "content": assistant_message.get("content", ""),
            "tool_calls": tool_calls
        })
        
        # 处理每个工具调用
        for tool_call in tool_calls:
            function_call = tool_call["function"]
            tool_id = function_call["name"]
            
            try:
                # 解析参数
                arguments = json.loads(function_call["arguments"])
                
                # 执行工具
                tool_result = self.tool_manager.execute_tool(tool_id, arguments)
                
                # 添加工具响应到消息历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            except Exception as e:
                # 工具执行失败，添加错误信息
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_id,
                    "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                })
        
        # 再次调用API获取最终回复
        data["messages"] = messages
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            final_result = response.json()
            
            # 转换为与本地模型相同的输出格式
            return {
                "choices": [{
                    "text": final_result["choices"][0]["message"]["content"],
                    "finish_reason": final_result["choices"][0]["finish_reason"]
                }]
            }
        except Exception as e:
            raise Exception(f"工具调用后API请求失败: {str(e)}")
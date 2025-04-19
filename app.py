import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from llama_cpp import Llama

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 模型路径
MODEL_PATH = "D:\\unsloth.Q8_0.gguf"

# 检查模型文件是否存在
if not os.path.exists(MODEL_PATH):
    print(f"错误：模型文件不存在于路径 {MODEL_PATH}")
    # 可以设置一个默认路径或提示用户

# 全局变量存储模型实例
model = None

def load_model():
    """加载GGUF模型"""
    global model
    try:
        # 检查模型文件是否存在
        if not os.path.exists(MODEL_PATH):
            print(f"错误：模型文件不存在于路径 {MODEL_PATH}")
            return False
            
        print(f"尝试加载模型: {MODEL_PATH}")
        print(f"llama-cpp-python版本: {Llama.__version__ if hasattr(Llama, '__version__') else '未知'}")
        
        # 尝试使用不同的参数组合加载模型
        try:
            # 方法1：使用基本参数
            model = Llama(
                model_path=MODEL_PATH,
                n_ctx=2048,  # 上下文窗口大小
                n_threads=4,  # 使用的线程数
                n_gpu_layers=0,  # 禁用GPU加速
                verbose=True  # 启用详细日志以便调试
            )
        except Exception as e1:
            print(f"尝试方法1失败: {str(e1)}")
            try:
                # 方法2：使用legacy参数
                model = Llama(
                    model_path=MODEL_PATH,
                    n_ctx=2048,
                    n_threads=4,
                    n_gpu_layers=0,
                    verbose=True,
                    legacy=True  # 尝试使用legacy模式加载
                )
            except Exception as e2:
                print(f"尝试方法2失败: {str(e2)}")
                # 方法3：使用最小参数集
                model = Llama(model_path=MODEL_PATH)
                
        print("模型加载成功!")
        return True
    except Exception as e:
        print(f"模型加载失败: {str(e)}")
        print("请检查模型格式是否与llama-cpp-python版本兼容")
        print("可能需要更新llama-cpp-python库或使用兼容的模型文件")
        return False

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    global model
    
    # 如果模型未加载，尝试加载
    if model is None:
        success = load_model()
        if not success:
            return jsonify({"error": "模型加载失败，请检查模型路径"}), 500
    
    # 获取请求数据
    data = request.json
    user_input = data.get('message', '')
    
    try:
        # 生成回复
        response = model.create_completion(
            user_input,
            max_tokens=512,
            temperature=0.7,
            top_p=0.95,
            stop=["\n\n"],
            echo=False
        )
        
        # 提取生成的文本
        generated_text = response['choices'][0]['text']
        
        return jsonify({"response": generated_text})
    except Exception as e:
        return jsonify({"error": f"生成回复时出错: {str(e)}"}), 500

@app.route('/api/model_status')
def model_status():
    """检查模型状态"""
    global model
    
    if model is None:
        # 尝试加载模型
        success = load_model()
        return jsonify({"loaded": success})
    else:
        return jsonify({"loaded": True})

if __name__ == '__main__':
    # 启动时加载模型
    load_model()
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)
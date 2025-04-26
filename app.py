import os
import json
import pandas as pd
import numpy as np
import threading
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from model_loaders import ModelLoaderFactory

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 模型路径 - 支持GGUF和Safetensors两种格式
# MODEL_PATH = "D:\\unsloth.Q8_0.gguf"
MODEL_PATH = "C:/Users/22728\Desktop\作品\AiQA\model/"
# 如果需要使用Safetensors格式的模型，可以设置为目录路径或.safetensors文件
# MODEL_PATH = "D:\\safetensors_model_dir"

# 方剂知识库路径
CSV_PATH = "最终方剂.csv"

# 检查模型文件是否存在
if not os.path.exists(MODEL_PATH):
    print(f"错误：模型文件不存在于路径 {MODEL_PATH}")
    # 可以设置一个默认路径或提示用户

# 全局变量
model = None
df_prescriptions = None
tfidf_vectorizer = None
tfidf_matrix = None

# 用于存储和管理生成任务的字典
active_generations = {}
# 线程锁，用于保护active_generations字典的并发访问
generation_lock = threading.Lock()

# 加载并处理CSV知识库
def load_knowledge_base():
    """加载CSV方剂知识库并构建向量索引"""
    global df_prescriptions, tfidf_vectorizer, tfidf_matrix
    
    try:
        # 检查CSV文件是否存在
        if not os.path.exists(CSV_PATH):
            print(f"错误：方剂知识库文件不存在于路径 {CSV_PATH}")
            return False
            
        print(f"加载方剂知识库: {CSV_PATH}")
        
        # 读取CSV文件
        df_prescriptions = pd.read_csv(CSV_PATH)
        
        # 合并相关字段作为检索文本
        df_prescriptions['combined_text'] = df_prescriptions.apply(
            lambda row: ' '.join([str(val) for val in row.values if pd.notna(val) and val != '']), 
            axis=1
        )
        
        # 创建TF-IDF向量
        tfidf_vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
        tfidf_matrix = tfidf_vectorizer.fit_transform(df_prescriptions['combined_text'])
        
        print(f"方剂知识库加载成功! 共 {len(df_prescriptions)} 条记录")
        return True
    except Exception as e:
        print(f"方剂知识库加载失败: {str(e)}")
        return False

# 检索相关方剂信息
def retrieve_relevant_info(query, top_k=3):
    """检索与查询相关的方剂信息"""
    global tfidf_vectorizer, tfidf_matrix, df_prescriptions
    
    if tfidf_vectorizer is None or tfidf_matrix is None or df_prescriptions is None:
        return ""
    
    # 将查询转换为TF-IDF向量
    query_vector = tfidf_vectorizer.transform([query])
    
    # 计算余弦相似度
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # 获取相似度最高的top_k个索引
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    # 提取相关方剂信息
    relevant_info = ""
    for idx in top_indices:
        if similarities[idx] > 0.1:  # 设置相似度阈值
            prescription = df_prescriptions.iloc[idx]
            relevant_info += f"方剂名称: {prescription['药剂']}\n"
            relevant_info += f"配方: {prescription['配方']}\n"
            relevant_info += f"功用: {prescription['功用']}\n"
            relevant_info += f"适用症状: {prescription['症状']}\n"
            relevant_info += f"使用注意: {prescription['使用注意']}\n"
            relevant_info += f"用法用量: {prescription['用法用量']}\n\n"
    
    return relevant_info

def load_model():
    """根据模型格式自动加载合适的模型"""
    global model
    try:
        # 使用模型加载器工厂创建合适的加载器
        loader = ModelLoaderFactory.create_loader(MODEL_PATH)
        if loader is None:
            print(f"错误：无法为模型路径创建加载器 {MODEL_PATH}")
            return False
        
        # 加载模型
        # 检查CUDA是否可用
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print("检测到CUDA可用，将使用GPU加速")
        else:
            print("未检测到CUDA，将使用CPU")
            
        if MODEL_PATH.endswith('.gguf'):
            # GGUF模型加载参数 - 确保优先使用GPU
            # 对于GGUF模型，n_gpu_layers参数控制使用GPU加速的层数
            # 设置为较大值（如32或更高）可以最大化GPU利用率
            success = loader.load_model(
                model_path=MODEL_PATH,
                n_ctx=2048,  # 上下文窗口大小
                n_threads=4,  # 使用的线程数
                n_gpu_layers=40 if cuda_available else 0,  # 增加GPU层数以提高性能
                verbose=True  # 启用详细日志以便调试
            )
        else:
            # Safetensors模型加载参数
            success = loader.load_model(
                model_path=MODEL_PATH,
                device="cuda" if cuda_available else "cpu"  # 优先使用CUDA
            )
        
        if not success:
            return False
            
        # 获取加载的模型
        model = loader
        print("模型加载成功!")
        return True
    except Exception as e:
        print(f"模型加载失败: {str(e)}")
        print("请检查模型格式是否与加载器兼容")
        return False

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

# 在单独线程中执行模型推理的函数
def generate_response_thread(session_id, prompt, max_tokens=1024, temperature=0, top_p=0.95):
    """在单独线程中执行模型推理"""
    global model, active_generations
    
    try:
        # 生成回复
        response = model.create_completion(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=["\n\n\n"],
            echo=False
        )
        
        # 提取生成的文本
        generated_text = response['choices'][0]['text'].strip()
        
        # 更新生成状态
        with generation_lock:
            if session_id in active_generations:  # 确保任务没有被取消
                active_generations[session_id]['status'] = 'completed'
                active_generations[session_id]['result'] = generated_text
    except Exception as e:
        # 更新错误状态
        with generation_lock:
            if session_id in active_generations:  # 确保任务没有被取消
                active_generations[session_id]['status'] = 'error'
                active_generations[session_id]['error'] = str(e)

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    global model, df_prescriptions, active_generations
    
    # 如果模型未加载，尝试加载
    if model is None:
        success = load_model()
        if not success:
            return jsonify({"error": "模型加载失败，请检查模型路径"}), 500
    
    # 如果知识库未加载，尝试加载
    if df_prescriptions is None:
        success = load_knowledge_base()
        if not success:
            print("警告：方剂知识库加载失败，将使用模型原始回答")
    
    # 获取请求数据
    data = request.json
    user_input = data.get('message', '')
    session_id = data.get('session_id', str(hash(user_input + str(os.urandom(4)))))
    
    # 检查是否已经有正在进行的生成任务
    with generation_lock:
        for existing_id, generation_info in list(active_generations.items()):
            # 清理已完成或出错的任务
            if generation_info['status'] in ['completed', 'error', 'cancelled']:
                active_generations.pop(existing_id, None)
    
    try:
        # 检索相关方剂信息
        relevant_info = retrieve_relevant_info(user_input)
        
        # 构建带有上下文的提示
        if relevant_info:
            prompt = f"以下是与问题相关的中医方剂知识：\n\n{relevant_info}\n\n根据上述信息，请回答问题：{user_input}\n\n在回答后，请附上你引用的方剂信息：\n{relevant_info}"
        else:
            prompt = user_input
        
        # 创建新的生成任务
        with generation_lock:
            active_generations[session_id] = {
                'status': 'running',
                'prompt': prompt,
                'result': None,
                'error': None,
                'knowledge_info': relevant_info
            }
        
        # 在单独线程中启动生成任务
        thread = threading.Thread(
            target=generate_response_thread,
            args=(session_id, prompt)
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

@app.route('/api/generation_status', methods=['GET'])
def generation_status():
    """获取生成任务的状态"""
    global active_generations
    
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "缺少session_id参数"}), 400
    
    with generation_lock:
        if session_id not in active_generations:
            return jsonify({"error": "找不到指定的生成任务"}), 404
        
        generation_info = active_generations[session_id]
        
        if generation_info['status'] == 'running':
            return jsonify({
                "status": "running"
            })
        elif generation_info['status'] == 'completed':
            # 任务完成，返回结果
            result = {
                "status": "completed",
                "response": generation_info['result'],
                "knowledge_info": generation_info['knowledge_info'] if generation_info['knowledge_info'] else ""
            }
            # 可以选择在这里清理任务
            # active_generations.pop(session_id, None)
            return jsonify(result)
        elif generation_info['status'] == 'error':
            # 任务出错
            result = {
                "status": "error",
                "error": generation_info['error']
            }
            # 可以选择在这里清理任务
            # active_generations.pop(session_id, None)
            return jsonify(result)
        elif generation_info['status'] == 'cancelled':
            # 任务被取消
            result = {
                "status": "cancelled"
            }
            # 可以选择在这里清理任务
            # active_generations.pop(session_id, None)
            return jsonify(result)

@app.route('/api/cancel_generation', methods=['POST'])
def cancel_generation():
    """取消正在进行的生成任务"""
    global active_generations
    
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({"error": "缺少session_id参数"}), 400
    
    with generation_lock:
        if session_id not in active_generations:
            return jsonify({"error": "找不到指定的生成任务"}), 404
        
        # 标记任务为已取消
        # 注意：这不会立即停止正在进行的推理，但会阻止结果返回给用户
        active_generations[session_id]['status'] = 'cancelled'
        
        return jsonify({"status": "cancelled"})

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
    # 启动时加载模型和知识库
    load_model()
    load_knowledge_base()
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)
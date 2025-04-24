import os
import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from llama_cpp import Llama

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 模型路径
MODEL_PATH = "D:\\unsloth.Q8_0.gguf"

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
    global model, df_prescriptions
    
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
    
    try:
        # 检索相关方剂信息
        relevant_info = retrieve_relevant_info(user_input)
        
        # 构建带有上下文的提示
        if relevant_info:
            prompt = f"以下是与问题相关的中医方剂知识：\n\n{relevant_info}\n\n根据上述信息，请回答问题：{user_input}\n\n在回答后，请附上你引用的方剂信息：\n{relevant_info}"
        else:
            prompt = user_input
        
        # 生成回复
        response = model.create_completion(
            prompt,
            max_tokens=1024,  # 增加最大token数以容纳更长回答
            temperature=0.7,
            top_p=0.95,
            stop=["\n\n\n"],  # 修改停止标记以允许包含引用信息
            echo=False
        )
        
        # 提取生成的文本
        generated_text = response['choices'][0]['text']
        
        # 返回生成的文本和知识库信息
        return jsonify({
            "response": generated_text,
            "knowledge_info": relevant_info if relevant_info else ""
        })
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
    # 启动时加载模型和知识库
    load_model()
    load_knowledge_base()
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)
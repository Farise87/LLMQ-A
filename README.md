# AiQA - 中医方剂知识增强系统

这是一个基于大语言模型的中医方剂知识增强系统，支持GGUF和Safetensors两种格式的模型，通过网页界面实现与AI模型的对话功能，并结合中医方剂知识库提供专业的中医咨询服务。

## 功能特点

- **双模型格式支持**：同时支持GGUF和Safetensors两种格式的大语言模型
- **自动模型加载**：根据模型格式自动选择合适的加载器
- **中医方剂知识库**：集成中医方剂数据，提供专业的中医知识支持
- **智能检索匹配**：使用TF-IDF向量化和余弦相似度算法实现精准的方剂推荐
- **简洁美观的界面**：提供直观的网页对话界面
- **实时状态显示**：显示模型加载状态
- **连续对话支持**：保持上下文的连贯性

## 系统架构

系统由以下主要组件构成：

1. **模型加载器工厂**：根据模型格式自动选择合适的加载器
   - GGUF模型加载器：基于llama-cpp-python库加载GGUF格式模型
   - Safetensors模型加载器：基于Transformers库加载Safetensors格式模型

2. **知识库管理**：加载和处理中医方剂CSV知识库

3. **检索引擎**：使用TF-IDF向量化和余弦相似度算法实现相关方剂检索

4. **Web服务**：基于Flask的Web应用，提供RESTful API和用户界面

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/Farise87/LLMQ-A.git
cd LLMQ-A
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置模型路径

在`app.py`文件中，根据您的模型位置修改`MODEL_PATH`变量：

```python
# GGUF格式模型
MODEL_PATH = "D:\\your_model.gguf"

# 或者Safetensors格式模型
# MODEL_PATH = "D:\\safetensors_model_dir"
```

## 使用方法

### 启动服务

```bash
python app.py
```

启动后，服务将在 http://localhost:5000 运行。

### 使用界面

1. 打开浏览器访问 http://localhost:5000
2. 等待模型加载完成（状态指示器变为绿色）
3. 在输入框中输入中医相关问题并发送
4. 系统会结合AI模型和中医方剂知识库提供回答

## 模型支持说明

### GGUF格式模型

- 使用llama-cpp-python库加载
- 支持参数配置：上下文窗口大小、线程数、GPU加速等
- 适合在CPU环境运行的量化模型

### Safetensors格式模型

- 使用Transformers库加载
- 支持参数配置：设备选择、精度设置等
- 适合在GPU环境运行的完整模型

## 知识库集成

系统集成了中医方剂知识库（CSV格式），包含以下信息：

- 方剂名称
- 配方组成
- 功用主治
- 适用症状
- 使用注意事项
- 用法用量

系统使用TF-IDF向量化和余弦相似度算法，根据用户的问题自动检索相关的方剂信息，并结合大语言模型的回答提供专业的中医咨询服务。

## 系统要求

- Python 3.8 或更高版本
- 足够的内存来加载大语言模型（建议至少8GB RAM）
- 如需GPU加速，请确保有兼容的NVIDIA GPU并安装相应的CUDA工具包

## 自定义配置

在`app.py`中，您可以调整以下参数：

### GGUF模型参数

```python
n_ctx=2048      # 上下文窗口大小
n_threads=4      # 使用的CPU线程数
n_gpu_layers=0   # 使用的GPU层数（如果有GPU）
```

### Safetensors模型参数

```python
device="cpu"     # 设备选择，可以是'cpu'或'cuda'
load_in_8bit=False  # 是否以8位精度加载模型
```

### 知识库检索参数

```python
top_k=3          # 检索的方剂数量
similarity_threshold=0.1  # 相似度阈值
```

## 故障排除

- 如果模型加载失败，请检查模型路径是否正确，以及模型格式是否与加载器兼容
- 如果遇到内存不足错误，请尝试减小`n_ctx`参数或使用更小的模型
- 如果生成速度太慢，可以尝试增加`n_threads`或启用GPU加速
- 如果知识库加载失败，请检查CSV文件路径是否正确，以及文件格式是否符合要求

## 贡献指南

欢迎提交问题和改进建议！请通过GitHub Issues或Pull Requests参与项目开发。

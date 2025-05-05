# MCP系统（Model-Controller-Processor）

## 系统概述

MCP系统是一个为DeepSeek大模型提供工具调用能力的框架，使模型能够自由调用项目中的各种工具，特别是查询MySQL和Neo4j数据库的信息。当用户有需求时，大模型可以通过查询工具获取相关信息，并根据查询到的信息生成对应回答。

## 系统架构

### 核心组件

1. **工具管理器（ToolManager）**
   - 负责注册和管理可供大模型调用的工具
   - 提供工具描述和执行接口
   - 集成数据库查询功能

2. **模型加载器（DeepseekAPILoader）**
   - 负责与DeepSeek API通信
   - 支持工具调用功能
   - 处理工具调用结果

3. **模型管理器（ModelManager）**
   - 管理API模型配置
   - 集成工具管理器
   - 提供统一的模型调用接口

4. **API路由（ApiRoutes）**
   - 提供工具系统相关的Web API
   - 集成MCP系统提示
   - 处理聊天请求和工具执行

5. **系统提示（MCP System Prompt）**
   - 指导大模型如何使用工具系统
   - 提供专业的回答模板

## 功能特点

- **数据库查询工具**：支持查询MySQL中的中药方剂和药材信息
- **知识图谱查询**：支持查询Neo4j中的知识图谱数据
- **统一搜索**：支持同时搜索多个数据源
- **工具注册机制**：可以方便地注册新工具
- **工具调用接口**：提供标准化的工具调用接口

## 使用方法

### 启动系统

```bash
python app.py
```

### 测试MCP系统

```bash
python test_mcp_system.py
```

### API接口

- **聊天接口**：`/api/chat`（POST）
  - 输入：用户消息
  - 输出：大模型回复（可能包含工具调用结果）

- **获取工具列表**：`/api/tools`（GET）
  - 输出：可用工具描述列表

- **执行工具**：`/api/tools/execute`（POST）
  - 输入：工具ID和参数
  - 输出：工具执行结果

## 注册新工具

在`tool_manager.py`中的`register_default_tools`方法中添加新工具：

```python
self.register_tool(
    "tool_id",
    "工具描述",
    self._tool_function,
    {"param_name": "参数描述"}
)
```

然后实现对应的工具函数：

```python
def _tool_function(self, param_name):
    # 工具实现代码
    return result
```

## 系统流程

1. 用户发送问题
2. 系统使用MCP系统提示构建完整提示
3. 大模型分析问题并决定是否调用工具
4. 如果需要，大模型调用相应工具获取信息
5. 大模型根据工具返回的信息生成最终回答
6. 系统将回答返回给用户

## 注意事项

- 确保数据库连接配置正确
- API密钥需要替换为实际的DeepSeek API密钥
- 工具执行可能需要一定时间，请耐心等待
- 大模型可能不会在所有情况下都调用工具，这取决于它对问题的理解
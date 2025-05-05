# 中医药智能助手系统

## 项目简介

本项目是一个基于Python和Flask框架开发的中医药智能助手系统，集成了中医药知识库、智能问答、药材管理等功能。系统采用MCP（Model-Controller-Processor）架构，结合DeepSeek API实现智能交互，为用户提供专业的中医药咨询服务。

## 功能特点

- **智能问答系统**：基于DeepSeek API的智能对话功能
- **中药知识库**：包含丰富的方剂和药材数据
- **药材管理系统**：支持药材的增删改查
- **方剂检索**：多维度的方剂搜索功能
- **中医资讯**：提供最新中医药相关资讯
- **后台管理**：完整的数据管理功能

## 技术架构

### 后端技术

- **Web框架**：Flask 3.1.0
- **数据库**：MySQL
- **API集成**：DeepSeek API
- **跨域支持**：Flask-CORS

### 核心组件

1. **工具管理器（ToolManager）**
   - 注册和管理工具系统
   - 提供工具执行接口

2. **模型管理器（ModelManager）**
   - DeepSeek API集成
   - 工具系统调用

3. **数据库管理器（DBManager）**
   - MySQL数据库操作
   - 数据CRUD接口

4. **API路由（ApiRoutes）**
   - RESTful API设计
   - 请求处理和响应

## 数据库设计

### 主要数据表

1. **chinese_medicine（方剂表）**
   - 药剂名称
   - 功用
   - 症状
   - 组成

2. **medicine_data（药材表）**
   - 药材名称
   - 别名
   - 性味归经
   - 功用
   - 症状
   - 用法用量
   - 注意事项

3. **medicine_news（资讯表）**
   - 资讯标题
   - 内容
   - 发布时间

## API接口说明

### 方剂相关接口

- `GET /api/herbs`：获取所有方剂信息
- `GET /api/herbs/search`：搜索方剂
- `GET /api/herbs/category`：按分类获取方剂

### 药材相关接口

- `GET /api/medicines`：获取所有药材信息
- `GET /api/medicines/search`：搜索药材
- `GET /api/medicines/function`：按功用获取药材

### 智能助手接口

- `POST /api/chat`：智能对话
- `GET /api/generation_status`：获取生成状态
- `POST /api/cancel_generation`：取消生成任务

## 部署指南

### 环境要求

- Python 3.x
- MySQL数据库
- 所需Python包见requirements.txt

### 安装步骤

1. 克隆项目代码
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置数据库连接：
   - 修改db_manager.py中的数据库连接参数

4. 配置DeepSeek API：
   - 在app.py中设置API密钥

5. 启动应用：
   ```bash
   python app.py
   ```

### 访问地址

- 主页：http://localhost:5000
- 管理后台：http://localhost:5000/admin

## 注意事项

- 首次使用需要导入数据库文件
- 确保DeepSeek API密钥配置正确
- 管理后台默认账号：123，密码：123

## 技术支持

- 数据库问题请检查MySQL连接配置
- API调用问题请确认DeepSeek API密钥是否有效
- 建议定期备份数据库
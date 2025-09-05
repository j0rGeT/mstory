# 小说故事创作系统

基于Python和Streamlit开发的智能小说创作系统，集成DeepSeek大模型，支持人物关系图、时间线设置和智能故事生成。

## 功能特点

### 🎭 人物角色管理
- 添加和管理小说角色
- 详细的角色信息（外貌、性格、背景）
- 角色信息的增删改查

### 🕸️ 人物关系图
- 可视化的关系图编辑
- 支持多种关系类型（朋友、恋人、敌人等）
- 交互式图形界面，支持拖拽操作

### ⏰ 时间线设置
- 创建和管理故事时间线
- 事件与角色的关联
- 时间线可视化展示

### ✍️ 智能故事创作
- 基于DeepSeek大模型的故事生成
- 根据人物关系图自动创作
- 支持多种故事类型和长度
- 自定义提示词功能

### 🎯 高级功能
- 故事历史记录和管理
- 提示词模板库
- 故事导出功能
- SQLite数据库存储

## 安装说明

1. 克隆项目到本地
```bash
git clone <your-repo-url>
cd mstory
```

2. 安装Python依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
streamlit run app.py
```

## 使用指南

### 1. 配置API密钥
在侧边栏输入您的DeepSeek API密钥

### 2. 创建角色
- 在"人物管理"页面添加小说角色
- 填写角色的基本信息、性格特点和背景故事

### 3. 设置关系
- 在"关系图编辑"页面建立角色间的关系
- 可视化查看人物关系网络

### 4. 创建时间线
- 在"时间线设置"页面添加关键事件
- 将事件与相关角色关联

### 5. 生成故事
- 选择参与故事的主要角色
- 设置故事类型和长度
- 添加自定义提示词
- 点击生成按钮创作故事

## 技术架构

- **前端框架**: Streamlit
- **数据库**: SQLite
- **可视化**: streamlit-agraph, Plotly
- **AI模型**: DeepSeek API
- **后端语言**: Python

## 数据库结构

### characters（角色表）
- id: 角色ID
- name: 角色姓名
- description: 外貌描述
- personality: 性格特点
- background: 背景故事

### relationships（关系表）
- id: 关系ID
- from_character_id: 起始角色ID
- to_character_id: 目标角色ID
- relationship_type: 关系类型
- description: 关系描述

### timeline（时间线表）
- id: 事件ID
- event_name: 事件名称
- event_description: 事件描述
- event_time: 事件时间
- characters_involved: 涉及角色

### stories（故事表）
- id: 故事ID
- title: 故事标题
- content: 故事内容
- prompt_used: 使用的提示词
- characters_used: 参与的角色

## 开发计划

- [ ] 增强关系图的交互功能
- [ ] 添加更多故事类型模板
- [ ] 支持故事章节管理
- [ ] 集成更多AI模型选择
- [ ] 添加故事评分和反馈机制

## 许可证

MIT License
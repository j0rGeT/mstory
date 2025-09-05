import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json
import sqlite3
import requests
from datetime import datetime
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# 页面配置
st.set_page_config(
    page_title="小说故事创作系统",
    page_icon="📖",
    layout="wide"
)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('story_system.db')
    cursor = conn.cursor()
    
    # 创建人物表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            personality TEXT,
            background TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建关系表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_character_id INTEGER,
            to_character_id INTEGER,
            relationship_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_character_id) REFERENCES characters (id),
            FOREIGN KEY (to_character_id) REFERENCES characters (id)
        )
    ''')
    
    # 创建时间线表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_description TEXT,
            event_time TEXT,
            characters_involved TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建故事表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            prompt_used TEXT,
            characters_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# DeepSeek API调用
def call_deepseek_api(prompt, api_key):
    # 如果没有API密钥，返回模拟内容
    if not api_key or api_key.strip() == "":
        return generate_demo_story(prompt)
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的小说创作助手，擅长根据人物关系和情节设定创作精彩的故事。"},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=600)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"API调用失败: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API调用错误: {str(e)}"

def generate_demo_story(prompt):
    """生成演示故事（当没有API密钥时使用）"""
    return """【演示模式 - 模拟生成的故事】

在一个春暖花开的早晨，故事的主人公踏上了一段不平凡的旅程。阳光透过薄雾洒在古老的石板路上，预示着新的开始。

随着情节的展开，角色之间的关系逐渐明朗。他们在命运的安排下相遇，经历了种种考验和挑战。每个人物都有着鲜明的性格特点，在故事中发挥着重要的作用。

经过一番波折，故事迎来了高潮。紧张的氛围中，主角们必须做出关键的决定。他们的选择不仅关系到自己的命运，也影响着整个故事的走向。

最终，在智慧和勇气的指引下，所有的矛盾得到了化解。故事以一个圆满的结局收场，给读者留下了深刻的印象和无限的思考空间。

---
注意：这是演示内容。要获得真正的AI生成故事，请在侧边栏配置DeepSeek API密钥。"""

# 主界面
def main():
    init_db()
    
    st.title("📖 小说故事创作系统")
    
    # 侧边栏 - API配置
    with st.sidebar:
        st.header("🔧 配置")
        api_key = st.text_input("DeepSeek API Key", type="password", 
                               help="请输入您的DeepSeek API密钥")
        
        st.header("📚 功能导航")
        selected_tab = st.radio("选择功能", [
            "人物管理", 
            "关系图编辑", 
            "时间线设置", 
            "故事创作",
            "提示词设置"
        ])
    
    # 主界面内容
    if selected_tab == "人物管理":
        character_management()
    elif selected_tab == "关系图编辑":
        relationship_graph()
    elif selected_tab == "时间线设置":
        timeline_management()
    elif selected_tab == "故事创作":
        story_creation(api_key)
    elif selected_tab == "提示词设置":
        prompt_settings()

def character_management():
    st.header("👥 人物角色管理")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("添加新角色")
        with st.form("add_character"):
            name = st.text_input("角色姓名")
            description = st.text_area("外貌描述")
            personality = st.text_area("性格特点")
            background = st.text_area("背景故事")
            
            if st.form_submit_button("添加角色"):
                if name:
                    conn = sqlite3.connect('story_system.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO characters (name, description, personality, background)
                        VALUES (?, ?, ?, ?)
                    ''', (name, description, personality, background))
                    conn.commit()
                    conn.close()
                    st.success(f"角色 {name} 添加成功！")
    
    with col2:
        st.subheader("现有角色")
        conn = sqlite3.connect('story_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM characters ORDER BY created_at DESC')
        characters = cursor.fetchall()
        conn.close()
        
        for char in characters:
            with st.expander(f"🎭 {char[1]}"):
                st.write(f"**描述:** {char[2] or '暂无'}")
                st.write(f"**性格:** {char[3] or '暂无'}")
                st.write(f"**背景:** {char[4] or '暂无'}")
                if st.button(f"删除 {char[1]}", key=f"del_{char[0]}"):
                    conn = sqlite3.connect('story_system.db')
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM characters WHERE id = ?', (char[0],))
                    conn.commit()
                    conn.close()
                    st.success(f"角色 {char[1]} 已删除")

def relationship_graph():
    st.header("🕸️ 人物关系图编辑")
    
    # 获取所有角色
    conn = sqlite3.connect('story_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM characters')
    characters = cursor.fetchall()
    
    if not characters:
        st.warning("请先在人物管理中添加角色")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("添加关系")
        with st.form("add_relationship"):
            char_names = [char[1] for char in characters]
            char_dict = {char[1]: char[0] for char in characters}
            
            from_char = st.selectbox("选择角色A", char_names)
            to_char = st.selectbox("选择角色B", char_names)
            relationship_type = st.selectbox("关系类型", [
                "朋友", "恋人", "敌人", "亲人", "师父", "徒弟", 
                "同事", "邻居", "陌生人", "竞争对手", "盟友"
            ])
            description = st.text_area("关系描述")
            
            if st.form_submit_button("添加关系"):
                if from_char != to_char:
                    cursor.execute('''
                        INSERT INTO relationships (from_character_id, to_character_id, relationship_type, description)
                        VALUES (?, ?, ?, ?)
                    ''', (char_dict[from_char], char_dict[to_char], relationship_type, description))
                    conn.commit()
                    st.success("关系添加成功！")
                else:
                    st.error("不能选择相同的角色")
    
    with col1:
        st.subheader("关系图可视化")
        
        # 获取关系数据
        cursor.execute('''
            SELECT r.*, c1.name as from_name, c2.name as to_name
            FROM relationships r
            JOIN characters c1 ON r.from_character_id = c1.id
            JOIN characters c2 ON r.to_character_id = c2.id
        ''')
        relationships = cursor.fetchall()
        
        if relationships:
            # 创建节点和边
            nodes = []
            edges = []
            
            # 添加所有角色作为节点
            for char in characters:
                nodes.append(Node(
                    id=str(char[0]), 
                    label=char[1],
                    size=25,
                    shape="circularImage",
                    image="https://via.placeholder.com/50/4287f5/FFFFFF?text=" + char[1][0]
                ))
            
            # 添加关系作为边
            for rel in relationships:
                edges.append(Edge(
                    source=str(rel[1]), 
                    target=str(rel[2]),
                    label=rel[3],
                    type="CURVE_SMOOTH"
                ))
            
            # 配置图形显示
            config = Config(
                width=700,
                height=500,
                directed=False,
                physics=True,
                hierarchical=False
            )
            
            # 显示图形
            agraph(nodes=nodes, edges=edges, config=config)
        else:
            st.info("暂无关系数据，请添加角色关系")
    
    conn.close()

def timeline_management():
    st.header("⏰ 时间线设置")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("添加时间线事件")
        with st.form("add_timeline_event"):
            event_name = st.text_input("事件名称")
            event_description = st.text_area("事件描述")
            event_time = st.text_input("事件时间", placeholder="例如: 2024年春天 / 第一章 / 故事开始")
            
            # 获取角色列表
            conn = sqlite3.connect('story_system.db')
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM characters')
            characters = [char[0] for char in cursor.fetchall()]
            
            characters_involved = st.multiselect("涉及角色", characters)
            
            if st.form_submit_button("添加事件"):
                if event_name:
                    cursor.execute('''
                        INSERT INTO timeline (event_name, event_description, event_time, characters_involved)
                        VALUES (?, ?, ?, ?)
                    ''', (event_name, event_description, event_time, json.dumps(characters_involved)))
                    conn.commit()
                    st.success("事件添加成功！")
            
            conn.close()
    
    with col2:
        st.subheader("时间线预览")
        conn = sqlite3.connect('story_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM timeline ORDER BY created_at')
        events = cursor.fetchall()
        conn.close()
        
        for event in events:
            with st.expander(f"📅 {event[1]} ({event[3] or '未设定时间'})"):
                st.write(f"**描述:** {event[2] or '暂无'}")
                if event[4]:
                    characters = json.loads(event[4])
                    st.write(f"**涉及角色:** {', '.join(characters)}")
                if st.button(f"删除事件", key=f"del_event_{event[0]}"):
                    conn = sqlite3.connect('story_system.db')
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM timeline WHERE id = ?', (event[0],))
                    conn.commit()
                    conn.close()
                    st.success("事件已删除")

def story_creation(api_key):
    st.header("✍️ 故事创作")
    
    if not api_key:
        st.info("💡 提示：您可以不配置API密钥直接测试系统功能（将使用演示模式）")
    
    # 获取角色和关系数据
    conn = sqlite3.connect('story_system.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, description, personality, background FROM characters')
    characters = cursor.fetchall()
    
    cursor.execute('''
        SELECT r.*, c1.name as from_name, c2.name as to_name
        FROM relationships r
        JOIN characters c1 ON r.from_character_id = c1.id
        JOIN characters c2 ON r.to_character_id = c2.id
    ''')
    relationships = cursor.fetchall()
    
    cursor.execute('SELECT * FROM timeline ORDER BY created_at')
    timeline_events = cursor.fetchall()
    
    if not characters:
        st.warning("请先添加角色和关系")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("生成设置")
        
        # 选择参与的角色
        char_names = [char[1] for char in characters]
        default_chars = char_names[:min(3, len(char_names))] if char_names else []
        selected_chars = st.multiselect("选择故事主要角色", char_names, default=default_chars)
        
        # 故事类型和风格
        story_genre = st.selectbox("故事类型", [
            "言情小说", "悬疑推理", "科幻小说", "武侠小说", 
            "都市小说", "历史小说", "奇幻小说", "青春小说"
        ])
        
        story_length = st.selectbox("故事长度", ["短篇(500字)", "中篇(1000字)", "长篇(2000字)"])
        
        # 额外提示词
        additional_prompt = st.text_area("额外提示词", 
                                       placeholder="例如: 故事要包含悬疑元素，结尾要有反转...")
        
        # 生成故事按钮
        if st.button("🎨 生成故事", type="primary"):
            if not selected_chars:
                st.error("请至少选择一个角色！")
            else:
                # 构建提示词
                prompt = build_story_prompt(selected_chars, characters, relationships, 
                                          timeline_events, story_genre, story_length, 
                                          additional_prompt)
                
                # 显示生成的提示词（调试用）
                with st.expander("查看生成的提示词", expanded=False):
                    st.text(prompt)
                
                with st.spinner("正在创作故事..."):
                    try:
                        story_content = call_deepseek_api(prompt, api_key)
                        
                        if story_content and not story_content.startswith("API调用"):
                            # 保存故事到数据库
                            cursor.execute('''
                                INSERT INTO stories (title, content, prompt_used, characters_used)
                                VALUES (?, ?, ?, ?)
                            ''', (f"{story_genre} - {datetime.now().strftime('%Y%m%d_%H%M%S')}", 
                                 story_content, prompt, json.dumps(selected_chars)))
                            conn.commit()
                            
                            st.session_state.current_story = story_content
                            st.success("故事生成成功！")
                        else:
                            st.error(f"故事生成失败: {story_content}")
                    except Exception as e:
                        st.error(f"生成故事时出错: {str(e)}")
    
    with col2:
        st.subheader("生成的故事")
        
        if 'current_story' in st.session_state:
            st.markdown("### 📖 最新生成的故事")
            st.write(st.session_state.current_story)
            
            # 下载按钮
            st.download_button(
                label="💾 下载故事",
                data=st.session_state.current_story,
                file_name=f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        # 显示历史故事
        st.markdown("### 📚 历史故事")
        cursor.execute('SELECT * FROM stories ORDER BY created_at DESC LIMIT 5')
        past_stories = cursor.fetchall()
        
        for story in past_stories:
            with st.expander(f"📝 {story[1]}"):
                st.write(story[2][:200] + "..." if len(story[2]) > 200 else story[2])
                if st.button(f"查看完整故事", key=f"view_{story[0]}"):
                    st.session_state.current_story = story[2]
    
    conn.close()

def build_story_prompt(selected_chars, all_characters, relationships, timeline_events, 
                      genre, length, additional_prompt):
    prompt = f"请创作一个{genre}，{length}。\n\n"
    
    # 添加角色信息
    prompt += "### 主要角色:\n"
    for char_name in selected_chars:
        for char in all_characters:
            if char[1] == char_name:
                prompt += f"- **{char[1]}**: {char[2] or ''}，{char[3] or ''}，{char[4] or ''}\n"
    
    # 添加关系信息
    prompt += "\n### 角色关系:\n"
    for rel in relationships:
        if rel[5] in selected_chars and rel[6] in selected_chars:
            prompt += f"- {rel[5]}和{rel[6]}的关系是{rel[3]}: {rel[4] or ''}\n"
    
    # 添加时间线
    if timeline_events:
        prompt += "\n### 时间线参考:\n"
        for event in timeline_events:
            if event[4]:
                involved_chars = json.loads(event[4])
                if any(char in selected_chars for char in involved_chars):
                    prompt += f"- {event[3] or '某时'}: {event[1]} - {event[2] or ''}\n"
    
    # 添加额外提示
    if additional_prompt:
        prompt += f"\n### 特殊要求:\n{additional_prompt}\n"
    
    prompt += "\n请根据以上信息创作一个完整的故事，要求情节生动，人物性格鲜明，符合所选类型的特点。"
    
    return prompt

def prompt_settings():
    st.header("🎯 提示词设置")
    
    st.subheader("系统提示词")
    system_prompt = st.text_area("系统提示词", 
                                value="你是一个专业的小说创作助手，擅长根据人物关系和情节设定创作精彩的故事。",
                                height=100)
    
    st.subheader("常用提示词模板")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**情节类模板:**")
        templates = [
            "故事要有悬疑元素，保持读者的紧张感",
            "结尾要有意想不到的反转",
            "加入幽默元素，让故事更加轻松有趣",
            "描写要细腻，特别是情感和心理描写",
            "加入冲突和矛盾，推动情节发展"
        ]
        
        for template in templates:
            if st.button(f"📋 {template}", key=f"template_{hash(template)}"):
                st.session_state.selected_template = template
    
    with col2:
        st.write("**风格类模板:**")
        style_templates = [
            "文字要优美诗意，富有文学性",
            "语言要简洁明快，节奏紧凑",
            "多用对话推进情节发展",
            "加入环境描写，营造氛围",
            "采用第一人称视角叙述"
        ]
        
        for template in style_templates:
            if st.button(f"🎨 {template}", key=f"style_{hash(template)}"):
                st.session_state.selected_template = template
    
    if 'selected_template' in st.session_state:
        st.success(f"已选择模板: {st.session_state.selected_template}")

if __name__ == "__main__":
    main()
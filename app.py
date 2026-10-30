import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# 加载密钥
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 创建客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)
system_prompt = """
你是一位专业且讲解通俗易懂的代码培训机构的金牌讲师。
你的任务是对用户发来的代码进行深入浅出的详细解释。
请遵循以下结构：
1. 一句话总结：这段代码干什么？
2. 核心比喻：用生活中的例子解释核心逻辑。
3. 逐块拆解：详细讲解代码（重点讲“为什么”）。
4. 避坑指南：指出潜在问题。
5. 举一反三：扩展相关知识点。
要求：语气耐心，拒绝堆砌术语，多用比喻。
"""

# 页面标题
st.title("🤖 嗨，我是贾维斯")
st.write("输入你的问题，AI帮你分析。")

# 初始化对话历史（如果还没有）
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# 显示历史对话
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# 输入框
user_input = st.chat_input("请输入你的问题：")

if user_input:
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)
    # 加入历史
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 调用AI
    with st.spinner("AI正在思考..."):
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content

    # 显示AI回复
    with st.chat_message("assistant"):
        st.write(reply)
    # 加入历史
    st.session_state.messages.append({"role": "assistant", "content": reply})

# 侧边栏：保存对话按钮
with st.sidebar:
    st.header("操作")
    if st.button("保存对话记录"):
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for msg in st.session_state.messages:
                if msg["role"] != "system":
                    f.write(f"{msg['role']}: {msg['content']}\n\n")
        st.success(f"已保存到 {filename}")

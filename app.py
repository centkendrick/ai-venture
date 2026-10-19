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

# 页面标题
st.title("🤖 AI创业助手")
st.write("输入你的问题，AI帮你分析。")

# 初始化对话历史（如果还没有）
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一位AI创业导师，回答要具体、可执行。"}
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
            model="deepseek-chat",
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
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载密钥
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 页面配置
st.set_page_config(page_title="AI 金牌讲师", page_icon="👨‍🏫")
st.title("👨‍🏫 AI 金牌讲师：代码拆解助手")
st.write("把你不懂的代码粘贴到下面，我用最通俗的方式给你讲明白。")

# 核心：你的专属 System Prompt
SYSTEM_PROMPT = """
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

# 初始化对话状态
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# 侧边栏：清空对话功能
with st.sidebar:
    st.header("操作面板")
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()

# 渲染历史对话
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 用户输入区 (把提示词改成专门针对代码的)
if user_input := st.chat_input("请把你需要解释的代码粘贴到这里..."):
    
    # 1. 显示用户输入
    with st.chat_message("user"):
        st.markdown(f"```python\n{user_input}\n```") # 用代码块包裹，防止格式乱
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. 调用大模型
    with st.chat_message("assistant"):
        with st.spinner("讲师正在深度拆解代码，请稍候..."):
            response = client.chat.completions.create(
                model="deepseek-chat", # 建议用 chat 模型，reasoner 可能会啰嗦
                messages=st.session_state.messages,
                temperature=0.4 # 稍微给点温度，让比喻更生动
            )
            reply = response.choices[0].message.content
            
            # 3. 流式输出展示结果 (打字机效果)
            st.markdown(reply)
    
    # 4. 记录 AI 的回答
    st.session_state.messages.append({"role": "assistant", "content": reply})

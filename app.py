import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# ==========================================
# 1. 配置页面 (必须在最前面)
# ==========================================
st.set_page_config(page_title="AI 金牌讲师", page_icon="👨‍🏫")

# ==========================================
# 2. 安全读取密钥（兼容本地 .env 和云端 Secrets）
# ==========================================
load_dotenv()  # 尝试读取本地 .env
api_key = os.getenv("DEEPSEEK_API_KEY")

# 如果本地没有，去云端 Secrets 找
if not api_key:
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        pass

# 如果都找不到，直接拦截报错
if not api_key:
    st.error("❌ 未找到 DEEPSEEK_API_KEY，请检查本地 .env 文件或云端 Secrets 配置。")
    st.stop()  # 停止运行后续代码

# ==========================================
# 3. 初始化客户端 (拿到 key 后立刻初始化)
# ==========================================
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# ==========================================
# 4. 页面标题与角色设定
# ==========================================
st.title("👨‍🏫 AI 金牌讲师：代码拆解助手")
st.write("把你不懂的代码粘贴到下面，我用最通俗的方式给你讲明白。")

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

# ==========================================
# 5. 初始化对话状态
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# ==========================================
# 6. 侧边栏：清空对话
# ==========================================
with st.sidebar:
    st.header("操作面板")
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()

# ==========================================
# 7. 渲染历史对话
# ==========================================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ==========================================
# 8. 用户输入与主逻辑
# ==========================================
if user_input := st.chat_input("请把你需要解释的代码粘贴到这里..."):
    
    # 显示用户输入 (用代码块包裹)
    with st.chat_message("user"):
        st.markdown(f"```python\n{user_input}\n```")
    
    # 将用户输入加入历史
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 调用大模型
    with st.chat_message("assistant"):
        with st.spinner("讲师正在深度拆解代码，请稍候..."):
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=st.session_state.messages,
                    temperature=0.4
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                
                # 记录 AI 回答
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"❌ 调用 AI 失败，错误信息: {e}")

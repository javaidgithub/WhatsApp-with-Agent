# import os
# import streamlit as st
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI 
# from langchain_groq import ChatGroq
# from langchain.agents import create_agent

# load_dotenv()



# # =========================
# # Model Selector
# # =========================
# MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "groq")  # "groq" or "openai"

# if MODEL_PROVIDER == "openai":
#     llm = ChatOpenAI(
#         api_key=os.getenv("OPENAI_API_KEY"),
#         model="gpt-4o-mini",
#         temperature=0,
#         max_retries=2,
#     )
# else:
#     llm = ChatGroq(
#         api_key=os.getenv("GROQ_API_KEY"),
#         model_name="llama-3.1-8b-instant",
#         temperature=0,
#         max_retries=2,
#     )


# # response = llm.invoke("Hello, how are you?")
# # print(response.content)


# # =========================
# # Professional News Prompt
# # =========================
# prompt = """
# آپ ایک پروفیشنل سینئر اردو صحافی ہیں۔

# آپ کا کام دیے گئے خام خبر کے متن کو ایک مکمل، معیاری اور پیشہ ورانہ اردو خبر میں تبدیل کرنا ہے۔

# اہم ہدایات:

# 1. خبر کو واضح، بامعنی اور پیشہ ورانہ انداز میں دوبارہ لکھیں۔
# 2. غیر ضروری یا غیر متعلقہ معلومات شامل نہ کریں۔
# 3. زبان سادہ، رواں اور صحافتی معیار کے مطابق ہونی چاہیے۔
# 4. خبر کو منطقی ترتیب اور پیراگراف کی شکل میں پیش کریں۔

# آؤٹ پٹ فارمیٹ:

# 🔴 ہیڈلائن:
# مختصر اور پرکشش سرخی لکھیں۔

# 🟠 ذیلی سرخی:
# ہیڈلائن کی وضاحت 1–2 جملوں میں کریں۔

# 🟢 خبر کی تفصیل:
# مکمل خبر کو پیراگراف کی صورت میں پیش کریں۔

# اہم:
# حتمی جواب مکمل طور پر اردو زبان میں ہونا چاہیے۔
# """

# # =========================
# # Agent
# # =========================
# agent = create_agent(
#     model=llm,
#     system_prompt=prompt
# )

# # =========================
# # Streamlit UI
# # =========================
# st.set_page_config(
#     page_title="Urdu News Research Agent",
#     page_icon="📰",
#     layout="centered"
# )

# st.markdown(
#     "<h1 style='text-align: center;'>📰 Urdu News Research Agent</h1>",
#     unsafe_allow_html=True
# )

# st.markdown(
#     "<p style='text-align: center; color: gray;'>Convert raw text into a professional Urdu news article</p>",
#     unsafe_allow_html=True
# )

# st.divider()

# # =========================
# # Input
# # =========================
# urdu_text = st.text_area(
#     label="📝 Enter raw news text in Urdu",
#     placeholder="Enter raw news text in Urdu",
#     height=180
# )

# # =========================
# # Button
# # =========================
# if st.button("🚀 Convert to Professional News", use_container_width=True):

#     if not urdu_text.strip():
#         st.warning("⚠️ Please enter raw news text in Urdu.")

#     else:

#         with st.spinner("🔎 Researching and preparing the news..."):

#             response = agent.invoke({
#                 "messages": [
#                     {
#                         "role": "user",
#                         "content": f"""
#             درج ذیل خام خبر کو ایک مکمل اور پیشہ ورانہ اردو خبر میں تبدیل کریں۔

#             ہدایات:
#             - خبر کو واضح، رواں اور صحافتی انداز میں لکھیں
#             - غیر ضروری معلومات شامل نہ کریں
#             - مناسب ہیڈلائن، ذیلی سرخی اور تفصیل دیں
#             - خبر کو پیراگراف کی شکل میں پیش کریں

#             متن:
#             {urdu_text}
#             """
#                     }
#                 ]
#             })
#             messages = response.get("messages", [])
#             # print(messages)

#             final_output = "No response found"

#             for msg in reversed(messages):
#                 if hasattr(msg, "content") and msg.content:

#                     # Gemini case (list of blocks)
#                     if MODEL_PROVIDER == "gemini" and isinstance(msg.content, list):
#                         texts = []
#                         for block in msg.content:
#                             if isinstance(block, dict) and block.get("type") == "text":
#                                 texts.append(block.get("text", ""))
#                         final_output = "\n".join(texts).strip()
#                         break

#                     # Normal models (Groq/OpenAI)
#                     elif isinstance(msg.content, str):
#                         final_output = msg.content.strip()
#                         break
#         st.divider()

#         st.markdown("### 📰 Prepared Professional News:")

#         st.markdown(
#             f"""
# <div style='text-align: right;
# direction: rtl;
# font-size: 18px;
# line-height: 2;'>
# {final_output}
# </div>
# """,
#             unsafe_allow_html=True
#         )

###############################################################################################################
###############################################################################################################
###############################################################################################################

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.agents import create_agent

load_dotenv()

# =========================
# Model Selector
# =========================
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "groq")  # "groq" or "openai"

if MODEL_PROVIDER == "openai":
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=0,
        max_retries=2,
    )
else:
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",
        temperature=0,
        max_retries=2,
    )


# =========================
# Professional News Prompt
# =========================
prompt = """
آپ ایک پروفیشنل سینئر اردو صحافی ہیں۔

آپ کا کام دیے گئے خام خبر کے متن کو ایک مکمل، معیاری اور پیشہ ورانہ اردو خبر میں تبدیل کرنا ہے۔

اہم ہدایات:

1. خبر کو واضح، بامعنی اور پیشہ ورانہ انداز میں دوبارہ لکھیں۔
2. غیر ضروری یا غیر متعلقہ معلومات شامل نہ کریں۔
3. زبان سادہ، رواں اور صحافتی معیار کے مطابق ہونی چاہیے۔
4. خبر کو منطقی ترتیب اور پیراگراف کی شکل میں پیش کریں۔

آؤٹ پٹ فارمیٹ:

🔴 ہیڈلائن:
مختصر اور پرکشش سرخی لکھیں۔

🟠 ذیلی سرخی:
ہیڈلائن کی وضاحت 1–2 جملوں میں کریں۔

🟢 خبر کی تفصیل:
مکمل خبر کو پیراگراف کی صورت میں پیش کریں۔

اہم:
حتمی جواب مکمل طور پر اردو زبان میں ہونا چاہیے۔
"""

# =========================
# Agent
# =========================
agent = create_agent(
    model=llm,
    system_prompt=prompt
)


# =========================
# Helper: Run Agent
# =========================
def run_agent(raw_text: str, extra_instructions: str = "") -> str:
    """Invoke the agent and extract the final text response."""
    improvement_block = ""
    if extra_instructions.strip():
        improvement_block = f"""
بہتری کی ہدایات:
{extra_instructions}
"""

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""
درج ذیل خام خبر کو ایک مکمل اور پیشہ ورانہ اردو خبر میں تبدیل کریں۔

ہدایات:
- خبر کو واضح، رواں اور صحافتی انداز میں لکھیں
- غیر ضروری معلومات شامل نہ کریں
- مناسب ہیڈلائن، ذیلی سرخی اور تفصیل دیں
- خبر کو پیراگراف کی شکل میں پیش کریں
{improvement_block}

متن:
{raw_text}
"""
            }
        ]
    })

    messages = response.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if MODEL_PROVIDER == "gemini" and isinstance(msg.content, list):
                texts = [
                    block.get("text", "")
                    for block in msg.content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                return "\n".join(texts).strip()
            elif isinstance(msg.content, str):
                return msg.content.strip()

    return "No response found"


# =========================
# Streamlit UI
# =========================
st.set_page_config(
    page_title="Urdu News Research Agent",
    page_icon="📰",
    layout="centered"
)

st.markdown(
    "<h1 style='text-align: center;'>📰 Urdu News Research Agent</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: gray;'>Convert raw text into a professional Urdu news article</p>",
    unsafe_allow_html=True
)
st.divider()

# =========================
# Session State Init
# =========================
if "generated_news" not in st.session_state:
    st.session_state.generated_news = None          # current generated article
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""                  # original raw input
if "approval_status" not in st.session_state:
    st.session_state.approval_status = None         # None | "approved" | "improve"
if "show_improve_box" not in st.session_state:
    st.session_state.show_improve_box = False

# =========================
# Input — only shown before first generation
# =========================
if st.session_state.generated_news is None:
    urdu_text = st.text_area(
        label="📝 Enter raw news text in Urdu",
        placeholder="Enter raw news text in Urdu",
        height=180
    )

    if st.button("🚀 Convert to Professional News", use_container_width=True):
        if not urdu_text.strip():
            st.warning("⚠️ Please enter raw news text in Urdu.")
        else:
            with st.spinner("🔎 Researching and preparing the news..."):
                result = run_agent(urdu_text)
            st.session_state.raw_text = urdu_text
            st.session_state.generated_news = result
            st.session_state.approval_status = None
            st.session_state.show_improve_box = False
            st.rerun()

# =========================
# Output + Human Approval
# =========================
if st.session_state.generated_news is not None:

    st.divider()
    st.markdown("### 📰 Prepared Professional News:")
    st.markdown(
        f"""
<div style='text-align: right; direction: rtl; font-size: 18px; line-height: 2;'>
{st.session_state.generated_news}
</div>
""",
        unsafe_allow_html=True
    )

    st.divider()

    # ---------- Approval Status Banner ----------
    if st.session_state.approval_status == "approved":
        st.success("✅ News approved and forwarded to the next step!")
        if st.button("🔄 Start Over", use_container_width=True):
            for key in ["generated_news", "raw_text", "approval_status", "show_improve_box"]:
                st.session_state[key] = None if key != "show_improve_box" else False
            st.rerun()

    elif st.session_state.approval_status is None or st.session_state.approval_status == "improve":

        st.markdown("#### 🧑‍💼 Human Review — What would you like to do?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Approve & Forward", use_container_width=True):
                st.session_state.approval_status = "approved"
                st.session_state.show_improve_box = False
                st.rerun()

        with col2:
            if st.button("✏️ Improve", use_container_width=True):
                st.session_state.approval_status = "improve"
                st.session_state.show_improve_box = True
                st.rerun()

        # ---------- Improve Input ----------
        if st.session_state.show_improve_box:
            st.markdown("---")
            st.markdown("#### ✏️ Improvement Instructions")
            extra = st.text_area(
                label="Add extra instructions for the agent (in Urdu or English):",
                placeholder="e.g. مزید تفصیل شامل کریں / Make the headline more impactful / Add more context about the event",
                height=120,
                key="improve_input"
            )

            if st.button("🔁 Regenerate News", use_container_width=True):
                if not extra.strip():
                    st.warning("⚠️ Please enter improvement instructions before regenerating.")
                else:
                    with st.spinner("🔎 Improving the news article..."):
                        result = run_agent(st.session_state.raw_text, extra)
                    st.session_state.generated_news = result
                    st.session_state.approval_status = None
                    st.session_state.show_improve_box = False
                    st.rerun()
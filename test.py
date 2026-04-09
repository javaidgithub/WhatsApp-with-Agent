
import os
import json
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
import redis

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
tavily_tool = TavilySearchResults(max_results=5)

agent = create_agent(
    model=llm,
    tools=[tavily_tool],
    system_prompt=prompt
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QUEUE_KEY = os.getenv("QUEUE_KEY", "whatsapp:messages")


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

def _format_queue_item(item: dict) -> str:
    source = item.get("source") or "unknown"
    if source == "group":
        name = item.get("group_name") or "Unknown Group"
        sender = item.get("sender") or ""
        msg = item.get("message") or ""
        return f"[group] {name}{(' · ' + sender) if sender else ''}: {msg}"
    if source == "channel":
        name = item.get("channel_name") or "Channel"
        msg = item.get("message") or ""
        return f"[channel] {name}: {msg}"
    return json.dumps(item, ensure_ascii=False)


def drain_redis_queue(redis_url: str, queue_key: str, max_items: int = 50) -> list[dict]:
    """
    Drain up to max_items messages from Redis list queue.
    Note: This consumes messages (LPOP).
    """
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    out: list[dict] = []
    for _ in range(max_items):
        raw = client.lpop(queue_key)
        if raw is None:
            break
        try:
            out.append(json.loads(raw))
        except Exception:
            out.append({"source": "unknown", "message": str(raw)})
    return out


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
if "queue_items" not in st.session_state:
    st.session_state.queue_items = []
if "generated_news" not in st.session_state:
    st.session_state.generated_news = None          # current generated article
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""                  # original raw input
if "approval_status" not in st.session_state:
    st.session_state.approval_status = None         # None | "approved" | "improve"
if "show_improve_box" not in st.session_state:
    st.session_state.show_improve_box = False


def _reset_article_state():
    for key in ["generated_news", "raw_text", "approval_status", "show_improve_box"]:
        st.session_state[key] = None if key != "show_improve_box" else False


tab_manual, tab_queue = st.tabs(["✍️ Manual input", "📥 From WhatsApp queue"])

with tab_queue:
    st.markdown("### 📥 WhatsApp queued messages → News")
    st.caption("This consumes messages from Redis (LPOP). Start FastAPI + Redis + Node ingesters first.")

    col_a, col_b = st.columns(2)
    with col_a:
        redis_url = st.text_input("Redis URL", value=REDIS_URL)
    with col_b:
        queue_key = st.text_input("Queue key", value=QUEUE_KEY)

    col1, col2, col3 = st.columns(3)
    with col1:
        max_items = st.number_input("Max to pull", min_value=1, max_value=500, value=50, step=10)
    with col2:
        if st.button("⬇️ Pull from queue", use_container_width=True):
            try:
                new_items = drain_redis_queue(redis_url, queue_key, int(max_items))
                if new_items:
                    st.session_state.queue_items = new_items + st.session_state.queue_items
                    st.success(f"Pulled {len(new_items)} message(s).")
                else:
                    st.info("No new messages in queue.")
            except Exception as e:
                st.error(f"Failed to pull from Redis: {e}")
    with col3:
        if st.button("🧹 Clear list", use_container_width=True):
            st.session_state.queue_items = []
            st.rerun()

    st.markdown(f"**Loaded messages:** {len(st.session_state.queue_items)}")

    if st.session_state.queue_items:
        labels = [_format_queue_item(i) for i in st.session_state.queue_items]
        selected_idx = st.selectbox(
            "Select a message to convert",
            options=list(range(len(labels))),
            format_func=lambda i: labels[i][:200] + ("…" if len(labels[i]) > 200 else ""),
        )
        selected = st.session_state.queue_items[int(selected_idx)]

        st.markdown("#### Selected message")
        st.code(_format_queue_item(selected), language="text")

        extra_queue = st.text_area(
            "Extra instructions (optional)",
            placeholder="e.g. مزید تفصیل شامل کریں / Add more context / Make the headline more impactful",
            height=90,
            key="queue_extra",
        )

        if st.button("📰 Generate news from this message", use_container_width=True):
            with st.spinner("🔎 Generating news..."):
                payload_text = _format_queue_item(selected)
                result = run_agent(payload_text, extra_queue or "")
            st.session_state.raw_text = payload_text
            st.session_state.generated_news = result
            st.session_state.approval_status = None
            st.session_state.show_improve_box = False
            st.rerun()
    else:
        st.info("No messages loaded yet. Click “Pull from queue”.")


with tab_manual:

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
            _reset_article_state()
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
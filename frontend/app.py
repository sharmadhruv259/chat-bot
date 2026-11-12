"""Render the Streamlit chatbot with configurable safety checks."""

import os

import requests
import streamlit as st


API_URL = os.getenv(
    "CHAT_API_URL",
    "http://127.0.0.1:8000/api/chat/",
)

GUARDRAIL_OPTIONS = {
    "Code-based Guardrails": "code",
    "LLM-based Guardrails": "llm",
    "OpenAI Moderation": "moderation",
}

st.set_page_config(
    page_title="Chat Bot",
    page_icon="💬",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Styling only: no layout or logic changes below this block.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=DM+Sans:wght@400;500;600&display=swap');

    :root {
        --bg: #080c18;
        --panel: #0e1424;
        --card: #121a2e;
        --line: #1f2a44;
        --text: #e8ecf8;
        --muted: #8b97b5;
        --accent: #5eead4;
        --accent-2: #818cf8;
    }

    html, body, .stApp, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp {
        background:
            radial-gradient(900px 420px at 50% -8%, rgba(129,140,248,.20), transparent 70%),
            radial-gradient(600px 300px at 85% 10%, rgba(94,234,212,.10), transparent 70%),
            var(--bg);
        color: var(--text);
    }

    /* Keep the header (it holds the sidebar toggle); hide only Deploy/menu */
    header[data-testid="stHeader"] { background: transparent; }
    [data-testid="stDecoration"], [data-testid="stStatusWidget"],
    [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"],
    [data-testid="stMainMenu"], .stDeployButton, #MainMenu, footer {
        display: none !important;
    }
    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button {
        color: var(--accent) !important;
        background: var(--card) !important;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
    }

    .block-container { max-width: 820px; padding-top: 3rem; padding-bottom: 7rem; }
    [data-testid="stBottomBlockContainer"] { max-width: 820px; }
    [data-testid="stBottom"] > div { background: transparent; }

    /* Title + caption */
    h1 {
        font-family: 'Bricolage Grotesque', sans-serif !important;
        font-weight: 800 !important; letter-spacing: -1px !important;
        background: linear-gradient(90deg, var(--accent), var(--accent-2) 65%, #c084fc);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    [data-testid="stCaptionContainer"] { color: var(--muted); }

    /* Sidebar */
    [data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-family: 'Bricolage Grotesque', sans-serif; color: var(--text);
        letter-spacing: -.3px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px; border: 1px solid rgba(129,140,248,.4);
        background: linear-gradient(135deg, rgba(94,234,212,.14), rgba(129,140,248,.18));
        color: var(--text); font-weight: 500; transition: all .2s ease;
    }
    .stButton > button:hover { border-color: var(--accent); color: #fff; }

    /* Multiselect: replace default red tags */
    span[data-baseweb="tag"] {
        background: rgba(129,140,248,.18) !important;
        border: 1px solid rgba(129,140,248,.45);
        border-radius: 8px !important;
    }
    span[data-baseweb="tag"], span[data-baseweb="tag"] span { color: #c7d2fe !important; }
    div[data-baseweb="select"] > div {
        background: var(--card); border-color: var(--line); border-radius: 12px;
    }

    /* Guardrail status rows (green dot = active) */
    .guard-row {
        display: flex; gap: .6rem; align-items: flex-start;
        padding: .55rem .7rem; margin-bottom: .45rem;
        border: 1px solid var(--line); border-radius: 12px;
        background: var(--card); font-size: .8rem; color: var(--muted);
    }
    .guard-row b { color: var(--text); font-weight: 600; display: block; }
    .dot { width: 8px; height: 8px; border-radius: 50%; margin-top: .38rem; flex: none; }
    .dot.on  { background: #34d399; box-shadow: 0 0 8px #34d399; }
    .dot.off { background: #3b4562; }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: var(--card); border: 1px solid var(--line);
        border-radius: 16px; padding: 1rem 1.1rem; margin-bottom: .9rem;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: linear-gradient(135deg, rgba(129,140,248,.14), rgba(94,234,212,.06));
        border-color: rgba(129,140,248,.30);
    }
    [data-testid="stChatMessage"] p { line-height: 1.65; }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 18px; border: 1px solid var(--line); background: var(--card);
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent-2); box-shadow: 0 0 0 3px rgba(129,140,248,.18);
    }
    [data-testid="stChatInput"] textarea { color: var(--text); }

    div[data-testid="stAlert"] { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Chat Bot")
st.caption("Powered by Django, Groq, and OpenAI Moderation")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Chat Controls")

    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Safety Settings")

    selected_guardrails = st.multiselect(
        "Enable Guardrails",
        options=list(GUARDRAIL_OPTIONS),
        default=["Code-based Guardrails"],
        help="Checks run automatically at their appropriate stages.",
    )

    enabled_guardrails = [
        GUARDRAIL_OPTIONS[name]
        for name in selected_guardrails
    ]

    st.caption(
        f"{len(enabled_guardrails)} optional guardrail(s) enabled"
    )

    guardrail_descriptions = {
        "Code-based Guardrails": "Checks message length and invalid characters.",
        "LLM-based Guardrails": "A Groq safety model reviews the content.",
        "OpenAI Moderation": "Classifies potentially harmful content.",
    }

    for name, description in guardrail_descriptions.items():
        state = "on" if name in selected_guardrails else "off"
        st.markdown(
            f'<div class="guard-row"><span class="dot {state}"></span>'
            f"<div><b>{name}</b>{description}</div></div>",
            unsafe_allow_html=True,
        )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("error"):
            st.error(message["content"])
        else:
            st.markdown(message["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:
    history = [
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in st.session_state.messages
        if not message.get("error") and not message.get("blocked")
    ][-20:]

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    answer = None
    error_message = None
    result = {}

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    API_URL,
                    json={
                        "message": prompt,
                        "history": history,
                        "enabled_guardrails": enabled_guardrails,
                    },
                    timeout=120,
                )

                result = response.json()

                if response.status_code >= 400:
                    error_message = result.get(
                        "error",
                        "The chatbot service could not complete the request.",
                    )

                elif result.get("blocked"):
                    guardrail = result.get("guardrail_result") or {}

                    guardrail_name = guardrail.get(
                        "guardrail",
                        "Unknown",
                    )
                    stage = guardrail.get("stage", "unknown")
                    reason = guardrail.get(
                        "message",
                        "The content was blocked.",
                    )

                    error_message = (
                        f"Guardrail triggered: {guardrail_name}\n\n"
                        f"Stage: {stage}\n\n"
                        f"{reason}"
                    )

                else:
                    answer = result.get("answer")

                    if not answer:
                        error_message = (
                            "The chatbot returned an empty response."
                        )

            except requests.RequestException:
                error_message = (
                    "Unable to connect to the chatbot service."
                )
            except (ValueError, TypeError):
                error_message = (
                    "Unable to process the chatbot response."
                )

        if error_message:
            st.error(error_message)
        else:
            st.markdown(answer)

    if error_message:
        st.session_state.messages[-1]["blocked"] = True

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message,
                "error": True,
            }
        )
    else:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )
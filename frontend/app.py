"""Render the Streamlit chatbot with configurable safety checks."""

import html
import os
from pathlib import Path

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
# Styling lives in style.css (no logic changes).
# ---------------------------------------------------------------------------
def load_css(path="style.css"):
    """Load the stylesheet that sits next to this file."""
    css_file = Path(__file__).parent / path
    st.markdown(
        f"<style>{css_file.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


load_css()

TYPING_HTML = '<div class="typing"><span></span><span></span><span></span></div>'


def render_block_card(info):
    """Show a guardrail block as an amber card with the guardrail as a badge."""
    name = html.escape(str(info["name"]))
    stage = html.escape(str(info["stage"]))
    reason = html.escape(str(info["reason"]))

    st.markdown(
        '<div class="block-card">'
        '<div class="block-head">'
        '<span class="block-icon">🛡️</span>'
        '<span class="block-title">Message blocked</span>'
        f'<span class="badge">{name}</span>'
        f'<span class="badge stage">stage: {stage}</span>'
        "</div>"
        f'<div class="block-reason">{reason}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_message(message):
    if message.get("guardrail"):
        render_block_card(message["guardrail"])
    elif message.get("error"):
        st.error(message["content"])
    else:
        st.markdown(message["content"])


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

    GUARDRAIL_DESCRIPTIONS = {
        "Code-based Guardrails": "Checks message length and invalid characters.",
        "LLM-based Guardrails": "A Groq safety model reviews the content.",
        "OpenAI Moderation": "Classifies potentially harmful content.",
    }

    if "guardrails" not in st.session_state:
        st.session_state["guardrails"] = ["Code-based Guardrails"]

    def toggle_guardrail(name):
        selected = st.session_state["guardrails"]
        if name in selected:
            selected.remove(name)
        else:
            selected.append(name)

    def select_all_guardrails():
        st.session_state["guardrails"] = list(GUARDRAIL_OPTIONS)

    def clear_guardrails():
        st.session_state["guardrails"] = []

    st.caption("Click a guardrail to turn it on or off.")

    # Each guardrail is a clickable card. The key changes with the state so
    # style.css can show a green dot (on) or a grey dot (off).
    for name, description in GUARDRAIL_DESCRIPTIONS.items():
        is_on = name in st.session_state["guardrails"]
        st.button(
            name,
            key=f"guard_{'on' if is_on else 'off'}_{GUARDRAIL_OPTIONS[name]}",
            on_click=toggle_guardrail,
            args=(name,),
            help=description,
            use_container_width=True,
        )

    select_col, clear_col = st.columns(2, gap="small")
    with select_col:
        st.button(
            "Select all",
            key="select_all_guardrails",
            on_click=select_all_guardrails,
            use_container_width=True,
        )
    with clear_col:
        st.button(
            "Unselect all",
            key="clear_guardrails",
            on_click=clear_guardrails,
            use_container_width=True,
        )

    selected_guardrails = st.session_state["guardrails"]

    enabled_guardrails = [
        GUARDRAIL_OPTIONS[name]
        for name in selected_guardrails
    ]

    st.caption(
        f"{len(enabled_guardrails)} optional guardrail(s) enabled"
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_message(message)

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
    guardrail_info = None
    result = {}

    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown(TYPING_HTML, unsafe_allow_html=True)

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
                guardrail_info = {
                    "name": guardrail_name,
                    "stage": stage,
                    "reason": reason,
                }

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

        typing_placeholder.empty()

        if guardrail_info:
            render_block_card(guardrail_info)
        elif error_message:
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
                "guardrail": guardrail_info,
            }
        )
    else:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )
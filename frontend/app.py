
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

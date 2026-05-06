import json
import streamlit as st
import requests


def main():
    """
    Entry point for the Streamlit app. Sets up the UI, handles user input, and manages the chat history.
    """
    # Page Configuration
    st.set_page_config(page_title="AI Employee Assistant", page_icon="🤖", layout="centered")

    # UI Styling
    st.markdown("""
                    <style>
                    [data-tested="stSidebar"] { display: none; }
                    .block-container { padding-top: 2rem; }
                    [data-tested="stChatMessage"] { border-radius: 15px; margin-bottom: 10px; }
                    </style>
                      """,
                unsafe_allow_html=True
                )

    st.title("AI Employee Assistant",text_alignment="center")

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ideal state (Welcome Screen)
    if not st.session_state.messages:
        st.markdown("### Welcome, Alok  !")
        st.info("I'm your AI assistant. You can ask me about company policies, Employee related details etc.")

    # display history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])

    # input and response logic
    prompt = st.chat_input("How can I help you today?")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "👤"})
        st.rerun()

    # If the last message is from the user, trigger the AI response
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_query = st.session_state.messages[-1]["content"]

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            full_response = ""

            with st.spinner("🤔 Thinking..."):
                try:
                    with requests.post("http://localhost:8000/user",
                                       json={"query": user_query}, stream=True) as response:
                        for line in response.iter_lines():
                            if line:
                                decoded = line.decode('utf-8').replace("data: ", "").strip()
                                try:
                                    data = json.loads(decoded)
                                    if "response" in data:
                                        full_response += data["response"]
                                        placeholder.markdown(full_response + "|")
                                except Exception as e:
                                    st.error(e)
                                    continue
                except Exception as e:
                    st.error(f"Connection failed: {e}")

            if full_response:
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response, "avatar": "🤖"})


main()

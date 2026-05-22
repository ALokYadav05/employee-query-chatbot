import json
import streamlit as st
import requests


def user_interface():
    """
    Entry point for the Streamlit app. Sets up the UI, handles user input, and manages the chat history.
    """
    # Page Configuration
    st.set_page_config(page_title="AI Employee Assistant", page_icon="🤖", layout="centered")

    # UI Styling
    st.markdown(
        """
        <style>
            /* Move content higher up the page */
            .main .block-container {
                padding-top: 1rem; 
            }

            /* Make chat bubbles look rounded */
            .stChatMessage {
                border-radius: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_list" not in st.session_state:
        st.session_state.chat_list = []
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

    # Sidebar
    with st.sidebar:
        st.title("Chats", help="Your conversation history", width="content")

        if st.button("New Chat", use_container_width=True, icon="➕"):
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # Display chat history
        if st.session_state.chat_list:
            for idx, chat in enumerate(st.session_state.chat_list):
                chat_preview = chat["preview"][:10] + "..." if len(chat["preview"]) > 40 else chat["preview"]
                if st.button(chat_preview, use_container_width=True, key=f"chat_{idx}"):
                    st.session_state.current_chat_id = idx
                    st.session_state.messages = chat["messages"].copy()
                    st.rerun()

    st.title("AI Employee Assistant", text_alignment="center")

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

        # If this is a new chat, add it to chat history immediately
        if st.session_state.current_chat_id is None:
            st.session_state.chat_list.insert(0, {
                "preview": prompt,
                "messages": st.session_state.messages.copy()
            })
            st.session_state.current_chat_id = 0
            # Update indices for existing chats
            for i in range(1, len(st.session_state.chat_list)):
                st.session_state.chat_list[i]["id"] = i

        st.rerun()

    # If the last message is from the user, trigger the AI response
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_query = st.session_state.messages[-1]["content"]

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            full_response = ""

            with st.spinner("🤔 Thinking..."):  # type: ignore
                try:
                    with requests.post("http://localhost:8000/user",
                                       json={"query": user_query}, stream=True) as response:

                        if response.status_code != 200:
                            st.error(f"Backend Error: {response.status_code} - {response.reason}")

                        for line in response.iter_lines(decode_unicode=True):
                            try:
                                data = json.loads(line)
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

                # Update existing chat with the new response
                if st.session_state.current_chat_id is not None:
                    st.session_state.chat_list[st.session_state.current_chat_id][
                        "messages"] = st.session_state.messages.copy()  # type: ignore


if __name__ == "__main__":
    user_interface()

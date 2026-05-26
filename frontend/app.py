import json
import streamlit as st
import requests
from src import Config

API_URL = Config().API_URL


def fetch_sessions():
    """
    Gets all chat sessions from the backend API.
    """
    try:
        resp = requests.get(f"{API_URL}/sessions")
        if resp.status_code == 200:
            return resp.json()[::-1]
    except Exception as e:
        st.error(f"Failed to fetch sessions from backend: {e}")
    return []


def create_session(title="New Chat"):
    """
    Creates a new chat session on the backend.
    """
    try:
        resp = requests.post(f"{API_URL}/sessions", json={"title": title})
        if resp.status_code == 201:
            return resp.json()
    except Exception as e:
        st.error(f"Failed to create backend session: {e}")
    return None


def delete_session(session_id):
    """
    Deletes a specific chat session by its ID.
    """
    try:
        resp = requests.delete(f"{API_URL}/sessions/{session_id}")
        return resp.status_code == 200
    except Exception as e:
        st.error(f"Failed to delete session: {e}")
    return False


def rename_session(session_id, new_title):
    """
    Changes the title of an existing chat session.
    """
    try:
        resp = requests.patch(f"{API_URL}/sessions/{session_id}", json={"title": new_title})
        return resp.status_code == 200
    except Exception as e:
        st.error(f"Failed to rename session: {e}")
    return False


@st.dialog("Rename Chat")
def rename_dialog(chat_id, current_title):
    """
    Displays a popup dialog box to rename a chat session.
    """
    new_title = st.text_input("Enter new chat title:", value=current_title)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save", use_container_width=True, type="primary"):
            cleaned_title = new_title.strip()
            if cleaned_title and rename_session(chat_id, cleaned_title):
                # OPTIMIZATION: Update local memory state instantly instead of blocking API calls
                for chat in st.session_state.chat_list:
                    if chat["id"] == chat_id:
                        chat["title"] = cleaned_title
                        break
                st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


def user_interface():
    """
    Builds and runs the entire Streamlit chat application UI.
    """
    # Page Configuration
    st.set_page_config(page_title="AI Employee Assistant", page_icon="🤖", layout="centered")

    # UI Styling
    st.markdown(
        """
        <style>
            .main .block-container { padding-top: 1rem; }
            .stChatMessage { border-radius: 20px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize State Variables via State Checking
    if "chat_list" not in st.session_state:
        st.session_state.chat_list = fetch_sessions()
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

    # Sidebar Rendering
    with st.sidebar:
        st.title("Chats", help="Your conversation history", width="content")

        if st.button("New Chat", use_container_width=True, icon="➕"):
            st.session_state.current_chat_id = None
            st.rerun()

        st.divider()

        # Display list from state cache
        for chat in st.session_state.chat_list:
            chat_id = chat["id"]
            title = chat.get("title", "New Chat")
            chat_preview = title[:20] + "..." if len(title) > 20 else title

            col_btn, col_ren, col_del = st.columns([0.76, 0.13, 0.17], gap="small")

            with col_btn:
                if st.button(chat_preview, use_container_width=True, key=f"chat_{chat_id}"):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()

            with col_ren:
                if st.button("🖋", key=f"ren_{chat_id}", help="Rename Chat", use_container_width=True):
                    rename_dialog(chat_id, title)

            with col_del:
                if st.button("🗑️", key=f"del_{chat_id}", help="Delete Chat", use_container_width=True):
                    if delete_session(chat_id):
                        # Mutate local memory index state instantly
                        st.session_state.chat_list = [c for c in st.session_state.chat_list if c["id"] != chat_id]
                        if st.session_state.current_chat_id == chat_id:
                            st.session_state.current_chat_id = None
                        st.rerun()

    st.title("AI Employee Assistant", text_alignment="center")

    # Fetch live messages from active chat context
    messages = []
    if st.session_state.current_chat_id:
        resp = requests.get(f"{API_URL}/sessions/{st.session_state.current_chat_id}")
        if resp.status_code == 200:
            messages = resp.json().get("messages", [])

    # Welcome Screen Configuration
    welcome_placeholder = st.empty()
    if not messages:
        with welcome_placeholder.container():
            st.markdown("### Welcome, Alok!")
            st.info("I'm your AI assistant. You can ask me about company policies, Employee related details etc.")

    # Render Historical Log Nodes Instantly
    for message in messages:
        raw_role = message.get("role", "assistant")
        content = message.get("content", "")
        st_role = "user" if raw_role in ["user", "human"] else "assistant"
        avatar = "👤" if st_role == "user" else "🤖"

        with st.chat_message(st_role, avatar=avatar):
            st.markdown(content)

    # Input Stream Handling Logic
    prompt = st.chat_input("How can I help you today?")

    if prompt:
        welcome_placeholder.empty()

        # Handle initialization lazily inline
        is_new_chat = st.session_state.current_chat_id is None
        if is_new_chat:
            new_sess = create_session(title=prompt)
            if new_sess:
                st.session_state.current_chat_id = new_sess["id"]
                # Insert directly to local state cache to avoid reloading
                st.session_state.chat_list.insert(0,
                                                  {"id": new_sess["id"], "title": prompt, "messages": []})

        # Render input block to user immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Handle Stream pipelines
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            full_response = ""

            with st.spinner(" Thinking..."):  # type: ignore
                try:
                    stream_url = f"{API_URL}/chat/{st.session_state.current_chat_id}"
                    with requests.post(stream_url, json={"query": prompt}, stream=True) as response:
                        if response.status_code == 200:
                            for line in response.iter_lines(decode_unicode=True):
                                try:
                                    data = json.loads(line)
                                    if "response" in data:
                                        full_response += data["response"]
                                        placeholder.markdown(full_response + "|")
                                except Exception as e:
                                    st.error(e)
                                    continue
                        else:
                            st.error(f"Backend Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

            if full_response:
                placeholder.markdown(full_response)

        # rerun layout configuration to update text logs natively
        st.rerun()


if __name__ == "__main__":
    user_interface()

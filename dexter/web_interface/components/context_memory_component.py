import streamlit as st
import requests

def context_memory_component():
    st.header("Context & Memory Management")
    
    API_BASE_URL = "http://localhost:8080"
    
    st.subheader("Session Tagging")
    
    try:
        response = requests.get(f"{API_BASE_URL}/session-tag")
        current_session = response.json().get("session_tag") if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        current_session = None
    
    try:
        response = requests.get(f"{API_BASE_URL}/sessions")
        available_sessions = response.json().get("sessions", []) if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        available_sessions = []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        new_session_tag = st.text_input(
            "Session being tagged with:",
            value=current_session or "",
            placeholder="e.g., electronics_project, medical_results",
            help="Tag to group related conversations by topic"
        )
        
        if current_session:
            st.info(f"💾 Current session: **{current_session}**")
        else:
            st.info("💬 No active session tagging")
    
    with col2:
        st.markdown("**Actions:**")
        if st.button("Set Session Tag", type="primary"):
            try:
                tag_to_set = new_session_tag.strip() if new_session_tag.strip() else None
                response = requests.post(f"{API_BASE_URL}/session-tag", json={"session_tag": tag_to_set})
                if response.status_code == 200:
                    if tag_to_set:
                        st.success(f"✅ Session set to: {tag_to_set}")
                    else:
                        st.success("✅ Session cleared")
                    st.rerun()
                else:
                    st.error("❌ Failed to set session tag")
            except requests.exceptions.RequestException as e:
                st.error(f"🔌 API connection error: {e}")
        
        if st.button("Clear Session", type="secondary"):
            try:
                response = requests.post(f"{API_BASE_URL}/session-tag", json={"session_tag": None})
                if response.status_code == 200:
                    st.success("✅ Session cleared")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear session")
            except requests.exceptions.RequestException as e:
                st.error(f"🔌 API connection error: {e}")
    
    if available_sessions:
        st.subheader("Session Loading")
        
        selected_session = st.selectbox(
            "Select a session to view:",
            options=[""] + available_sessions,
            format_func=lambda x: "Choose a session..." if x == "" else x
        )
        
        if selected_session:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col2:
                if st.button(f"📂 Load {selected_session}", type="primary"):
                    try:
                        response = requests.post(f"{API_BASE_URL}/sessions/{selected_session}/load")
                        if response.status_code == 200:
                            st.success(f"✅ Session '{selected_session}' loaded into conversation!")
                            st.info("💡 You can now continue the conversation with this session's context")
                            st.rerun()
                        else:
                            st.error("❌ Failed to load session")
                    except requests.exceptions.RequestException as e:
                        st.error(f"🔌 API connection error: {e}")
            
            with col3:
                if st.button(f"🗑️ Delete {selected_session}", type="secondary"):
                    try:
                        response = requests.delete(f"{API_BASE_URL}/sessions/{selected_session}")
                        if response.status_code == 200:
                            st.success(f"✅ Session '{selected_session}' deleted")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete session")
                    except requests.exceptions.RequestException as e:
                        st.error(f"🔌 API connection error: {e}")
            
            try:
                response = requests.get(f"{API_BASE_URL}/sessions/{selected_session}")
                if response.status_code == 200:
                    history = response.json().get("history", [])
                    if history:
                        st.markdown(f"**Session: {selected_session}** ({len(history)} interactions)")
                        
                        with st.container(height=400):
                            for i, interaction in enumerate(history):
                                timestamp = interaction.get("timestamp", "Unknown time")
                                user_msg = interaction.get("user", {}).get("content", "")
                                assistant_msg = interaction.get("assistant", {}).get("content", "")
                                
                                st.markdown(f"**#{i+1} - {timestamp}**")
                                st.markdown(f"👤 **User:** {user_msg}")
                                st.markdown(f"🤖 **DeXteR:** {assistant_msg}")
                                st.divider()
                    else:
                        st.info("No interactions in this session yet")
                else:
                    st.error("Failed to load session history")
            except requests.exceptions.RequestException as e:
                st.error(f"🔌 API connection error: {e}")
    
    st.divider()
    
    st.subheader("Conversation Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("💡 Start a new conversation to clear current history and begin fresh")
    
    with col2:
        if st.button("🆕 Start New Conversation", type="secondary"):
            try:
                response = requests.post(f"{API_BASE_URL}/chat/new-conversation")
                if response.status_code == 200:
                    st.success("✅ New conversation started!")
                    st.balloons()
                else:
                    st.error("❌ Failed to start new conversation")
            except requests.exceptions.RequestException as e:
                st.error(f"🔌 API connection error: {e}")
    
    st.divider()
    
    try:
        response = requests.get(f"{API_BASE_URL}/system-prompt")
        if response.status_code == 200:
            current_prompt = response.json()["system_prompt"]
        else:
            st.error("Failed to fetch system prompt")
            return
    except requests.exceptions.RequestException as e:
        st.error(f"API connection error: {e}")
        return
    
    st.subheader("System Prompt")
    
    edited_prompt = st.text_area(
        "Edit the system prompt:",
        value=current_prompt,
        height=400,
        help="Modify the system prompt that defines DeXteR's behavior and context"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Update System Prompt", type="primary"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/system-prompt",
                    json={"system_prompt": edited_prompt}
                )
                if response.status_code == 200:
                    st.success("System prompt updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update system prompt")
            except requests.exceptions.RequestException as e:
                st.error(f"API connection error: {e}")
    
    with col2:
        if st.button("Reset to Current"):
            st.rerun()

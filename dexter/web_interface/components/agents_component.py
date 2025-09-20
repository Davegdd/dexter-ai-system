import streamlit as st
import requests
import time
from datetime import datetime

def agents_component():
    """Streamlit component for launching and managing agents via API"""
    
    st.header("🤖 Agent Launcher")
    st.markdown("Select an agent and provide a task description to execute.")
    
    try:
        response = requests.get("http://localhost:8080/agents", timeout=5)
        if response.status_code != 200:
            st.error("❌ Cannot connect to DeXteR server. Make sure the server is running on http://localhost:8080")
            return
        
        available_agents = response.json()["agents"]
    except requests.exceptions.RequestException:
        st.error("❌ Cannot connect to DeXteR server. Make sure the server is running on http://localhost:8080")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Available Agents")
        selected_agent = st.selectbox(
            "Choose an agent:",
            available_agents,
            help="Select which agent to use for your task"
        )
        
        agent_descriptions = {
            "test": "🧪 A mock agent for testing purposes.",
            "youtube": "📺 An agent for interacting with YouTube videos, including searching, watching, and extracting transcripts.", 
            "auchan": "🛒 An agent for interacting with Auchan's website for grocery shopping.",
            "report": "📊 An agent for generating reports and documents from web search data."
        }
        
        if selected_agent in agent_descriptions:
            st.info(agent_descriptions[selected_agent])
    
    with col2:
        st.subheader("Task Configuration")
        
        task_description = st.text_area(
            "Task Description:",
            height=150,
            placeholder="Describe what you want the agent to do...",
            help="Provide a clear description of the task you want the agent to perform"
        )
        
        st.markdown("**Additional Arguments (Optional)**")
        with st.expander("Advanced Configuration", expanded=False):
            st.markdown("Provide additional arguments as JSON format if needed by the agent.")
            additional_args_text = st.text_area(
                "Additional Arguments (JSON):",
                height=100,
                placeholder='{"key": "value", "param": 123}',
                help="Enter additional arguments in JSON format. Leave empty if not needed."
            )
            
            additional_args = None
            if additional_args_text.strip():
                try:
                    import json
                    additional_args = json.loads(additional_args_text)
                    st.success("✅ Valid JSON format")
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format: {e}")
                    additional_args = None
        
        col_execute, col_clear = st.columns([1, 1])
        
        with col_execute:
            execute_button = st.button(
                "🚀 Launch Agent",
                type="primary",
                disabled=not task_description.strip(),
                help="Execute the selected agent with the provided task"
            )
        
        with col_clear:
            if st.button("🗑️ Clear", help="Clear the task description and additional args"):
                st.rerun()
    
    if execute_button and task_description.strip():
        st.markdown("---")
        st.subheader("🔄 Agent Execution")
        
        with st.container():
            st.markdown(f"**Agent:** {selected_agent}")
            st.markdown(f"**Task:** {task_description}")
            if additional_args:
                st.markdown(f"**Additional Args:** `{additional_args}`")
            
            try:
                request_data = {
                    "agent_name": selected_agent,
                    "task": task_description
                }
                
                if additional_args:
                    request_data["additional_args"] = additional_args
                
                response = requests.post(
                    "http://localhost:8080/agents/execute",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    agent_data = response.json()
                    agent_id = agent_data["agent_id"]
                    
                    st.success(f"✅ Agent launched successfully! ID: {agent_id}")
                    
                    progress_container = st.container()
                    with progress_container:
                        st.info("⏳ Agent is running... Checking status...")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        max_checks = 60
                        check_count = 0
                        
                        while check_count < max_checks:
                            try:
                                status_response = requests.get(
                                    f"http://localhost:8080/agents/{agent_id}/status",
                                    timeout=10
                                )
                                
                                if status_response.status_code == 200:
                                    status_data = status_response.json()
                                    
                                    if status_data["status"] == "running":
                                        progress = min((check_count + 1) * 100 // max_checks, 95)
                                        progress_bar.progress(progress)
                                        status_text.text(f"Agent running... ({check_count + 1}/{max_checks})")
                                        time.sleep(5)
                                        check_count += 1
                                        
                                    elif status_data["status"] == "completed":
                                        progress_bar.progress(100)
                                        status_text.text("Completed!")
                                        
                                        progress_container.empty()
                                        
                                        st.success("✅ Agent completed successfully!")
                                        
                                        st.subheader("📋 Results")
                                        with st.expander("View Full Result", expanded=True):
                                            st.markdown(status_data["result"])
                                        
                                        if "agent_results_history" not in st.session_state:
                                            st.session_state.agent_results_history = []
                                        
                                        st.session_state.agent_results_history.append({
                                            "agent": selected_agent,
                                            "task": task_description,
                                            "result": status_data["result"],
                                            "success": True,
                                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        })
                                        
                                        requests.delete(f"http://localhost:8080/agents/{agent_id}")
                                        break
                                        
                                    elif status_data["status"] == "failed":
                                        progress_container.empty()
                                        
                                        st.error(f"❌ Agent failed: {status_data.get('error', 'Unknown error')}")
                                        
                                        if "agent_results_history" not in st.session_state:
                                            st.session_state.agent_results_history = []
                                        
                                        st.session_state.agent_results_history.append({
                                            "agent": selected_agent,
                                            "task": task_description,
                                            "error": status_data.get('error', 'Unknown error'),
                                            "success": False,
                                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        })
                                        
                                        requests.delete(f"http://localhost:8080/agents/{agent_id}")
                                        break
                                        
                                else:
                                    st.error(f"❌ Failed to check agent status: {status_response.status_code}")
                                    break
                                    
                            except requests.exceptions.RequestException as e:
                                st.error(f"❌ Connection error while checking status: {e}")
                                break
                        
                        else:
                            # Timeout reached
                            progress_container.empty()
                            st.warning("⚠️ Agent execution timed out after 5 minutes")
                            # Clean up on server
                            requests.delete(f"http://localhost:8080/agents/{agent_id}")
                
                else:
                    st.error(f"❌ Failed to launch agent: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection error: {e}")
    
    # Show recent results if any exist
    if "agent_results_history" in st.session_state and st.session_state.agent_results_history:
        st.markdown("---")
        st.subheader("📚 Recent Results")
        
        # Show last few results
        for i, result_item in enumerate(reversed(st.session_state.agent_results_history[-3:])):
            with st.expander(f"{result_item['agent']} - {result_item['timestamp']}", expanded=False):
                st.markdown(f"**Task:** {result_item['task'][:100]}...")
                if result_item['success']:
                    st.success("✅ Completed")
                    st.markdown(result_item['result'])
                else:
                    st.error("❌ Failed")
                    st.markdown(f"**Error:** {result_item['error']}")

import streamlit as st
import threading
import time
import queue
import requests
import base64
from RealtimeSTT import AudioToTextRecorder
from .vision_capture import init_vision_mode, render_vision_status, get_vision_frame_if_enabled

def realtime_stt_component():
    """Real-time Speech-to-Text component with start/stop button control and optional vision mode."""
    
    # Initialize session state
    if 'stt_recorder' not in st.session_state:
        st.session_state.stt_recorder = None
    if 'stt_is_recording' not in st.session_state:
        st.session_state.stt_is_recording = False
    if 'stt_text_output' not in st.session_state:
        st.session_state.stt_text_output = []
    if 'stt_current_text' not in st.session_state:
        st.session_state.stt_current_text = ""
    if 'stt_stop_event' not in st.session_state:
        st.session_state.stt_stop_event = None
    if 'stt_text_queue' not in st.session_state:
        st.session_state.stt_text_queue = None
    if 'stt_chat_history' not in st.session_state:
        st.session_state.stt_chat_history = []
    if 'stt_response_type' not in st.session_state:
        st.session_state.stt_response_type = "Written"
    if 'stt_latest_audio' not in st.session_state:
        st.session_state.stt_latest_audio = None
    if 'stt_current_audio_response' not in st.session_state:
        st.session_state.stt_current_audio_response = None
    if 'stt_vision_mode' not in st.session_state:
        st.session_state.stt_vision_mode = False

    def play_audio_automatically(audio_data):
        """Play audio automatically using JavaScript"""
        # Convert audio data to base64
        audio_b64 = base64.b64encode(audio_data).decode()
        
        # Create JavaScript to play audio automatically
        audio_html = f"""
        <script>
            const audioData = 'data:audio/wav;base64,{audio_b64}';
            const audio = new Audio(audioData);
            audio.play().catch(e => console.log('Error playing audio:', e));
        </script>
        """
        
        st.components.v1.html(audio_html, height=0)

    def send_to_chat(text, webrtc_ctx=None):
        """Send transcribed text to chat endpoint and get response, optionally with image."""
        try:
            # Prepare the request payload
            payload = {"message": text}
            
            # If vision mode is enabled, try to get frame data
            if st.session_state.stt_vision_mode:
                image_base64 = get_vision_frame_if_enabled(webrtc_ctx)
                if image_base64:
                    payload["base64_data"] = image_base64
                    payload["file_type"] = "image"
            
            # Always send text to chat endpoint
            response = requests.post(
                "http://localhost:8080/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text_response = data.get("response", "No response")
                
                # If spoken response is requested, convert text response to audio
                if st.session_state.stt_response_type == "Spoken":
                    try:
                        tts_response = requests.post(
                            "http://localhost:8080/tts",
                            json={"text": text_response},
                            timeout=30
                        )
                        
                        if tts_response.status_code == 200:
                            # Store audio data in session state for playback
                            st.session_state.stt_latest_audio = tts_response.content
                            return {"response": text_response, "audio_data": tts_response.content, "type": "audio"}
                        else:
                            print(f"TTS error: {tts_response.status_code}")
                            return {"response": text_response, "type": "text"}
                    except Exception as e:
                        print(f"Audio generation error: {e}")
                        return {"response": text_response, "type": "text"}
                else:
                    return {"response": text_response, "type": "text"}
            else:
                return {"response": f"Error: {response.status_code}", "type": "text"}
        except requests.RequestException as e:
            return {"response": f"Connection error: {str(e)}", "type": "text"}

    def start_recording():
        """Start the real-time recording."""
        if not st.session_state.stt_is_recording:
            recorder = AudioToTextRecorder()
            stop_event = threading.Event()
            text_queue = queue.Queue()
            
            st.session_state.stt_recorder = recorder
            st.session_state.stt_stop_event = stop_event
            st.session_state.stt_text_queue = text_queue
            st.session_state.stt_is_recording = True
            
            def process_text(text):
                """Process incoming text from the recorder - thread safe version."""
                text_queue.put(text)
            
            # Start recording in a separate thread
            def record_loop(recorder_instance, stop_event_instance):
                while not stop_event_instance.is_set():
                    try:
                        recorder_instance.text(process_text)
                    except Exception as e:
                        print(f"Recording error: {e}")
                        break
            
            recording_thread = threading.Thread(
                target=record_loop, 
                args=(recorder, stop_event), 
                daemon=True
            )
            recording_thread.start()

    def stop_recording():
        """Stop the real-time recording."""
        if st.session_state.stt_stop_event:
            st.session_state.stt_stop_event.set()
        st.session_state.stt_is_recording = False
        st.session_state.stt_recorder = None
        st.session_state.stt_stop_event = None
        st.session_state.stt_text_queue = None

    # Vision mode setup
    webrtc_ctx = init_vision_mode()

    # Process queued text from background thread
    if st.session_state.stt_text_queue and st.session_state.stt_is_recording:
        try:
            while True:
                text = st.session_state.stt_text_queue.get_nowait()
                st.session_state.stt_current_text = text
                if text.strip():  # Only process non-empty text
                    st.session_state.stt_text_output.append(text)
                    
                    # Send to chat endpoint and get response (with optional vision)
                    with st.spinner("Getting AI response..."):
                        result = send_to_chat(text, webrtc_ctx)
                    
                    # Store current audio response if available
                    if result["type"] == "audio" and "audio_data" in result:
                        st.session_state.stt_current_audio_response = {
                            "text": result["response"],
                            "audio_data": result["audio_data"],
                            "user_input": text,
                            "timestamp": time.strftime("%H:%M:%S")
                        }
                    else:
                        st.session_state.stt_current_audio_response = None
                    
                    # Add to chat history with audio info
                    chat_entry = {
                        "user": text,
                        "assistant": result["response"],
                        "timestamp": time.strftime("%H:%M:%S"),
                        "has_audio": result["type"] == "audio",
                        "vision_used": st.session_state.stt_vision_mode
                    }
                    
                    if result["type"] == "audio" and "audio_data" in result:
                        chat_entry["audio_data"] = result["audio_data"]
                    
                    st.session_state.stt_chat_history.append(chat_entry)
        except queue.Empty:
            pass

    # UI Layout
    st.subheader("🎤 Real-time Speech-to-Text with AI Chat")
    
    # Configuration options
    col1, col2 = st.columns(2)
    
    with col1:
        # Response type selection
        st.session_state.stt_response_type = st.radio(
            "Response Type:",
            ["Written", "Spoken"],
            horizontal=True,
            key="stt_response_type_radio",
            help="Choose whether DeXteR should respond with text or speech"
        )
    
    with col2:
        # Vision mode checkbox
        st.session_state.stt_vision_mode = st.checkbox(
            "👁️ Vision Mode",
            value=st.session_state.stt_vision_mode,
            help="Enable camera to include visual context with your speech"
        )

    # Show camera feed if vision mode is enabled
    render_vision_status(webrtc_ctx)

    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🎙️ Start Recording", disabled=st.session_state.stt_is_recording):
            start_recording()
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Recording", disabled=not st.session_state.stt_is_recording):
            stop_recording()
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear All"):
            st.session_state.stt_text_output = []
            st.session_state.stt_current_text = ""
            st.session_state.stt_chat_history = []
            st.rerun()

    # Status indicator
    if st.session_state.stt_is_recording:
        vision_status = " with vision 👁️" if st.session_state.stt_vision_mode else ""
        st.success(f"🔴 Recording{vision_status}... Speak now!")
    else:
        st.info("⚪ Ready to record")

    # Current text display (real-time)
    if st.session_state.stt_current_text:
        st.markdown("**Currently hearing:** " + st.session_state.stt_current_text)

    # Current audio response display (auto-plays only the latest)
    if st.session_state.stt_current_audio_response:
        st.markdown("---")
        st.markdown("**Latest Audio Response:**")
        with st.container():
            response_data = st.session_state.stt_current_audio_response
            st.markdown(f"**You said:** {response_data['user_input']}")
            st.markdown(f"**DeXteR responds:** {response_data['text']} 🔊")
            
            # Auto-play the current audio
            play_audio_automatically(response_data['audio_data'])
            
            # Also provide manual control
            st.audio(response_data['audio_data'], format="audio/wav")

    # Chat history display (updated to show vision usage)
    if st.session_state.stt_chat_history:
        st.markdown("---")
        st.markdown("**Conversation History:**")
        
        for i, chat in enumerate(reversed(st.session_state.stt_chat_history[-5:])):  # Show last 5 exchanges
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"**{chat['timestamp']}**")
                    if chat.get('vision_used', False):
                        st.markdown("👁️ Vision")
                with col2:
                    st.markdown(f"**You:** {chat['user']}")
                    if chat.get('has_audio', False):
                        st.markdown(f"**DeXteR:** {chat['assistant']} 🔊")
                    else:
                        st.markdown(f"**DeXteR:** {chat['assistant']}")
                st.markdown("---")
    else:
        st.markdown("*Start recording and speak to begin chatting with DeXteR!*")

    # Auto-refresh when recording
    if st.session_state.stt_is_recording:
        time.sleep(0.1)
        st.rerun()
        st.markdown(f"**DeXteR responds:** {response_data['text']} 🔊")
        
        # Auto-play the current audio
        play_audio_automatically(response_data['audio_data'])
        
        # Also provide manual control
        st.audio(response_data['audio_data'], format="audio/wav")

    # Chat history display (updated to show vision usage)
    if st.session_state.stt_chat_history:
        st.markdown("---")
        st.markdown("**Conversation History:**")
        
        for i, chat in enumerate(reversed(st.session_state.stt_chat_history[-5:])):  # Show last 5 exchanges
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"**{chat['timestamp']}**")
                    if chat.get('vision_used', False):
                        st.markdown("👁️ Vision")
                with col2:
                    st.markdown(f"**You:** {chat['user']}")
                    if chat.get('has_audio', False):
                        st.markdown(f"**DeXteR:** {chat['assistant']} 🔊")
                    else:
                        st.markdown(f"**DeXteR:** {chat['assistant']}")
                st.markdown("---")
    else:
        st.markdown("*Start recording and speak to begin chatting with DeXteR!*")

    # Auto-refresh when recording
    if st.session_state.stt_is_recording:
        time.sleep(0.1)
        st.rerun()

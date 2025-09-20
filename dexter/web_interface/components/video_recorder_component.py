import base64

import streamlit as st
import requests


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


def video_recorder_component():
    st.subheader("📹 Video Recorder")

    # Add tabs for record vs upload
    tab1, tab2 = st.tabs(["Record Video", "Upload Video"])

    with tab1:
        st.warning("Recording is disabled in this version.")
        # if "prefix" not in st.session_state:
        #     st.session_state["prefix"] = str(uuid.uuid4())
        # prefix = st.session_state["prefix"]
        # recorded_file = RECORD_DIR / f"{prefix}_recording.flv"

        # def recorder_factory() -> MediaRecorder:
        #     return MediaRecorder(
        #         str(recorded_file),
        #         format="flv",
        #         options={
        #             "fflags": "+genpts",
        #             "avoid_negative_ts": "make_zero",
        #             "max_delay": "5000000",
        #         },
        #     )

        # ctx = webrtc_streamer(
        #     key="record",
        #     mode=WebRtcMode.SENDRECV,
        #     media_stream_constraints={
        #         "video": True,
        #         "audio": True,
        #     },
        #     in_recorder_factory=recorder_factory,
        #     rtc_configuration={
        #         "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        #     },
        #     async_processing=True,
        # )

        # # Show recording status
        # if ctx.state.playing:
        #     st.success("🔴 Recording in progress...")

        # # Download button
        # if recorded_file.exists():
        #     with recorded_file.open("rb") as f:
        #         st.download_button("📥 Download Recording", f, "recording.flv")

    with tab2:
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'webm'],
            help="Upload a video file to send to AI"
        )

        if uploaded_file is not None:
            st.success(f"✅ Video loaded: {uploaded_file.name}")

            # Add message input and send to chat
            st.divider()
            st.subheader("💬 Send video with message to AI")
            
            # Response type selection
            response_type = st.radio(
                "Response Type:",
                ["Written", "Spoken"],
                horizontal=True,
                help="Choose text or audio response"
            )
            
            message = st.text_area(
                "Enter your message about the video:",
                placeholder="Describe what you want to know about this video...",
                height=100
            )
            
            if st.button("🚀 Send to AI", type="primary"):
                if message.strip():
                    try:
                        # Convert video to base64
                        video_base64 = base64.b64encode(uploaded_file.getbuffer()).decode('utf-8')
                        
                        # Send to chat endpoint
                        response = requests.post(
                            "http://localhost:8080/chat",
                            json={
                                "message": message,
                                "base64_data": video_base64,
                                "file_type": "video"
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ Message sent successfully!")
                            st.write("**AI Response:**")
                            text_response = result.get("response", "No response")
                            st.write(text_response)
                            
                            # If spoken response requested, generate and play audio
                            if response_type == "Spoken":
                                try:
                                    tts_response = requests.post(
                                        "http://localhost:8080/tts",
                                        json={"text": text_response}
                                    )
                                    
                                    if tts_response.status_code == 200:
                                        # Auto-play the audio
                                        play_audio_automatically(tts_response.content)
                                        # Also provide manual control
                                        st.audio(tts_response.content, format="audio/wav")
                                    else:
                                        st.error("Audio generation failed")
                                except Exception as e:
                                    st.error(f"Audio error: {str(e)}")
                        else:
                            st.error(f"❌ Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Error sending message: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a message before sending.")
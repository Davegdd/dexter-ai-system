import streamlit as st
import requests
import base64

def play_audio_automatically(audio_data):
    """Play audio automatically using JavaScript"""
    audio_b64 = base64.b64encode(audio_data).decode()
    
    # Create JavaScript to play audio automatically
    audio_html = f"""
    <script>
        const audioData = 'data:audio/wav;base64,{audio_b64}';
        const audio = new Audio(audioData);
        audio.volume = 0.8;
        audio.play().catch(e => console.log('Error playing audio:', e));
    </script>
    """
    
    st.components.v1.html(audio_html, height=0)

def text_chat_component():
    """Text chat component for DeXteR"""
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize session state for camera
    if "show_camera" not in st.session_state:
        st.session_state.show_camera = False
    if "captured_image" not in st.session_state:
        st.session_state.captured_image = None

    # Initialize session state for response type
    if "response_type" not in st.session_state:
        st.session_state.response_type = "text"  # Default to text response

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "image" in message and message["image"]:
                st.image(message["image"], caption="Sent image", width=300)
            st.markdown(message["content"])

    # Camera controls
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📷 Camera", key="camera_button"):
            st.session_state.show_camera = not st.session_state.show_camera
            if not st.session_state.show_camera:
                st.session_state.captured_image = None

    # Show camera if enabled
    if st.session_state.show_camera:
        st.write("📸 Take a picture:")
        camera_image = st.camera_input("Take a picture to send with your message")
        
        if camera_image is not None:
            st.session_state.captured_image = camera_image
            st.success("✅ Picture captured! It will be sent with your next message.")
            
            # Show preview
            st.image(camera_image, caption="Preview - This will be sent with your message", width=300)
            
            if st.button("Clear Picture", key="clear_picture"):
                st.session_state.captured_image = None
                st.rerun()

    # Response type selection
    response_type = st.radio(
        "Response Type:",
        ["Written", "Spoken"],
        horizontal=True,
        key="text_response_type",
        help="Choose whether DeXteR should respond with text or speech"
    )

    # Chat input
    if prompt := st.chat_input("What would you like to ask DeXteR?"):
        # Prepare image data if available
        image_base64 = None
        if st.session_state.captured_image is not None:
            # Convert image to base64
            image_base64 = base64.b64encode(st.session_state.captured_image.getvalue()).decode()

        # Add user message to chat history
        user_message = {
            "role": "user", 
            "content": prompt,
            "image": st.session_state.captured_image
        }
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user"):
            if st.session_state.captured_image is not None:
                st.image(st.session_state.captured_image, caption="Sent image", width=300)
            st.markdown(prompt)

        # Get response from DeXteR
        with st.chat_message("assistant"):
            with st.spinner("DeXteR is thinking..."):
                try:
                    # Prepare request data
                    request_data = {"message": prompt}
                    if image_base64:
                        request_data["base64_data"] = image_base64
                        request_data["file_type"] = "image"
                    
                    if response_type == "Spoken":
                        # First get text response to display
                        response = requests.post(
                            "http://localhost:8080/chat",
                            json=request_data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            dexter_response = result["response"]
                            st.markdown(dexter_response)
                            
                            # Generate and play audio for the response
                            tts_response = requests.post(
                                "http://localhost:8080/tts",
                                json={"text": dexter_response}
                            )
                            
                            if tts_response.status_code == 200:
                                st.write("🔊 Playing audio response...")
                                # Play audio immediately
                                play_audio_automatically(tts_response.content)
                            
                            # Add assistant response to chat history
                            st.session_state.messages.append({"role": "assistant", "content": dexter_response})
                        else:
                            error_msg = f"Server error: {response.status_code}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        # For written responses, use regular chat endpoint
                        response = requests.post(
                            "http://localhost:8080/chat",
                            json=request_data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            dexter_response = result["response"]
                            st.markdown(dexter_response)
                            
                            # Add assistant response to chat history
                            st.session_state.messages.append({"role": "assistant", "content": dexter_response})
                        else:
                            error_msg = f"Server error: {response.status_code}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        
                except requests.exceptions.ConnectionError:
                    error_msg = "Cannot connect to DeXteR server. Make sure the server is running on http://localhost:8080"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                except Exception as e:
                    error_msg = f"Unexpected error: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

        # Clear captured image after sending
        st.session_state.captured_image = None
        st.session_state.show_camera = False

    # Clear chat button
    if st.button("Clear Chat", key="clear_text_chat"):
        st.session_state.messages = []
        st.session_state.captured_image = None
        st.session_state.show_camera = False
        st.rerun()
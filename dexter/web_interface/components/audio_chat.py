import streamlit as st
import requests
import io
import logging
from audio_recorder_streamlit import audio_recorder
import urllib.parse
import base64
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def send_audio_to_server(audio_data: bytes, format: str = "wav", response_type: str = "text") -> Tuple[Optional[dict], Optional[str]]:
    """Helper function to send audio to server and get transcription"""
    try:
        files = {"audio_file": ("audio.wav", io.BytesIO(audio_data), "audio/wav")}
        data = {"response_type": response_type}
        response = requests.post("http://localhost:8080/transcribe", files=files, data=data)
        
        if response.status_code == 200:
            if response_type == "audio":
                # URL decode the transcription text
                encoded_transcription = response.headers.get("X-Transcription", "")
                decoded_transcription = urllib.parse.unquote(encoded_transcription) if encoded_transcription else ""
                return {"transcription": decoded_transcription, "audio_data": response.content}, None
            else:
                return response.json(), None
        else:
            return None, f"Server error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to DeXteR server"
    except Exception as e:
        return None, f"Unexpected error: {e}"

def play_audio_automatically(audio_data: bytes):
    """Play audio automatically using JavaScript"""
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

def manual_recording_mode():
    """Manual recording mode - user clicks to record"""
    st.subheader("Manual Recording")
    
    response_type = st.radio(
        "Response Type:",
        ["Written", "Spoken"],
        horizontal=True,
        key="manual_response_type",
        help="Choose whether DeXteR should respond with text or speech"
    )
    
    audio_bytes = audio_recorder(
        text="Click to record",
        energy_threshold=0.1,
        pause_threshold=5, 
        recording_color="#e8b62c", 
        neutral_color="#6aa36f",
        key="manual_audio_recorder"
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        if st.button("Send to DeXteR", key="send_manual_audio"):
            with st.spinner("Processing audio..."):
                response_mode = "audio" if response_type == "Spoken" else "text"
                result, error = send_audio_to_server(audio_bytes, response_type=response_mode)
                
                if result:
                    st.success("Audio processed successfully!")
                    with st.expander("Transcription", expanded=True):
                        st.write(result["transcription"])
                    
                    if response_type == "Spoken" and "audio_data" in result:
                        with st.expander("DeXteR Audio Response", expanded=True):
                            st.write("🔊 Playing audio response...")
                            play_audio_automatically(result["audio_data"])
                    else:
                        with st.expander("DeXteR Response", expanded=True):
                            st.write(result["response"])
                else:
                    st.error(error)

def audio_chat_component():
    """Audio chat component for DeXteR"""
    
    st.title("🎤 DeXteR Audio Chat")
    
    manual_recording_mode()
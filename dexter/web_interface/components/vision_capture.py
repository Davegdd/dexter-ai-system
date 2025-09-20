import streamlit as st
import queue
import base64
import cv2
from streamlit_webrtc import WebRtcMode, webrtc_streamer

def init_vision_mode():
    """Initialize WebRTC camera for vision mode if enabled."""
    if st.session_state.get('stt_vision_mode', False):
        webrtc_ctx = webrtc_streamer(
            key="stt-vision-camera",
            mode=WebRtcMode.SENDONLY,
            media_stream_constraints={"video": True},
        )
        return webrtc_ctx
    return None

def capture_frame_as_base64(webrtc_ctx):
    """Capture a frame from the WebRTC stream and convert to base64."""
    if webrtc_ctx and webrtc_ctx.video_receiver:
        try:
            video_frame = webrtc_ctx.video_receiver.get_frame(timeout=1)
            img_rgb = video_frame.to_ndarray(format="rgb24")
            
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            
            _, buffer = cv2.imencode('.jpg', img_bgr)
            
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            return img_base64
        except queue.Empty:
            st.warning("No frame available. Make sure the camera is active.")
            return None
    return None

def render_vision_status(webrtc_ctx):
    """Render the camera status for vision mode."""
    if st.session_state.get('stt_vision_mode', False) and webrtc_ctx:
        st.markdown("**Camera Feed:**")
        if webrtc_ctx.video_receiver:
            st.info("📹 Camera is active - visual context will be included with your speech")
        else:
            st.warning("📹 Camera not detected - please allow camera access")

def get_vision_frame_if_enabled(webrtc_ctx):
    """Get base64 frame data if vision mode is enabled and camera is available."""
    if st.session_state.get('stt_vision_mode', False) and webrtc_ctx:
        return capture_frame_as_base64(webrtc_ctx)
    return None

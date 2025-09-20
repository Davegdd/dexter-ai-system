import streamlit as st
from components.video_recorder_component import video_recorder_component
from components.audio_chat import audio_chat_component
from components.text_chat import text_chat_component
from components.realtime_stt_component import realtime_stt_component
from components.test_component import test_component
from components.context_memory_component import context_memory_component
from components.agents_component import agents_component

st.set_page_config(
    page_title="DeXteR Web Interface",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 DeXteR - AI Assistant")

st.sidebar.title("Chat Mode")
mode = st.sidebar.radio(
    "Choose your interaction mode:",
    ["Text Chat", "Audio Chat", "Real-time STT", "Video Recorder", "Context & Memory", "Agents"] # "Test Component"]
)

if mode == "Text Chat":
    text_chat_component()
elif mode == "Audio Chat":
    audio_chat_component()
elif mode == "Real-time STT":
    realtime_stt_component()
elif mode == "Video Recorder":
    video_recorder_component()
elif mode == "Context & Memory":
    context_memory_component()
elif mode == "Agents":
    agents_component()
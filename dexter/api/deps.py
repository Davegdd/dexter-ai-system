from dexter.core.llm import LLM
from dexter.core.stt import init_stt
from dexter.core.tts import TTSManager

llm = None
tts_manager = None

def init_components():
    global llm, tts_manager
    init_stt()
    llm = LLM()
    tts_manager = TTSManager()

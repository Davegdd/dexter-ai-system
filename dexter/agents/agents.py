from smolagents import CodeAgent, LiteLLMModel
from dexter.agents.agents_utils import save_screenshot
from dexter.agents.tools import *
from dexter.config.settings import settings

api_key = settings.GEMINI_API_KEY
model = LiteLLMModel(model_id="gemini/gemini-2.0-flash", api_key=api_key)
    
test_agent = CodeAgent(
    tools=[], 
    model=model, 
    add_base_tools=True, 
    max_steps=40,
    verbosity_level=0,
    managed_agents=[])
test_agent.name = "test_agent"
test_agent.description = "A mock agent for testing purposes."

youtube_agent = CodeAgent(
    tools=[search_youtube_videos, get_video_transcript, watch_youtube_video], 
    model=model, 
    add_base_tools=True, 
    additional_authorized_imports=[],
    step_callbacks=[],
    max_steps=40,
    verbosity_level=2,
    managed_agents=[])
youtube_agent.name = "youtube_agent"
youtube_agent.description = "An agent for interacting with YouTube videos, including searching, watching, and extracting transcripts."

auchan_agent = CodeAgent(
    tools=[search_products, go_back, close_popups, extract_text_from_pdf], 
    model=model, 
    add_base_tools=True, 
    additional_authorized_imports=["helium", "pypdf"],
    step_callbacks=[save_screenshot],
    max_steps=40,
    verbosity_level=2,
    managed_agents=[])
auchan_agent.name = "auchan_agent"
auchan_agent.description = "An agent for interacting with Auchan's website for grocery shopping."

report_agent = CodeAgent(
    tools=[download_image], 
    model=model, 
    add_base_tools=True, 
    additional_authorized_imports=["plotly.*", "reportlab.*", "matplotlib.*",
        "json",
        "pandas",
        "numpy"],
    step_callbacks=[],
    max_steps=40,
    verbosity_level=2,
    managed_agents=[])
report_agent.name = "report_agent"
report_agent.description = "An agent for generating reports and documents from web search data."
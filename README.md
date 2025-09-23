DeXteR is my take on trying to incorporate AI more naturally and with less friction into my life/home. It is a personal system and interface for multimodal interaction with LLMs/LVLM, motivated by the philosophy that such capable technology should not be confined behind a text box and should be as open-source and local as possible. It allows for multimodal interaction and incorporates modes for different degrees of autonomy in the scale of agency (from an LLM with tools to fully fledged Deep Research style agents).

## Examples of interaction:

- **Text-to-Text and Text-to-Speech**: every type of interaction includes the possibility of receiving a written or spoken response since the user's preference can change from conversation to conversation or even question to question. 

https://github.com/user-attachments/assets/3cffb30a-dbc3-43a6-9fe2-37e905fb8d97



-**Real Time Speech-to-Speech with Vision**: leverages the awesome library RealtimeSTT for VAD and transcription, combined with a custom implementation to allow visual input. If the Vision Mode checkbox is ticked, a frame will be grabbed from a camera for each user turn thus enabling speech-to-speech/text with visual clues.


https://github.com/user-attachments/assets/8d42e1ef-5a6a-4078-873d-743274978dc7


## Agents:

 The word agent has become a buzzword wrongly thought of in binary terms (it is or it is not an agent), when the reality is that there is a spectrum of autonomy going from deterministic workflows where an LLM is used at some point, to Deep Research style agents where the LLM chooses which actions to perform and in which order. 

I have found that the best approach is to have a general conversational LLM with tools (middle of the spectrum) and then separately implement the two extremes, with the possibility of sharing as needed tools from the Deep Research agents with the conversational LLM. 

<div align="center">
  <img width="536" height="324" src="https://github.com/user-attachments/assets/1e929afa-f1d7-4472-8388-d95d358a99f5" />
</div>


The agentic framework used is Smolagents by Huggingface, a wonderful framework that saves boilerplate code, allows for easy customization and avoids the overabstraction and harmful constraints of other bloated solutions.

Agents can be manually launched from the corresponding component of the UI or by asking DeXteR to launch them. If agents do not behave as expected, I recommend using reasoning models if possible, this is one of those use cases where it is not overkill.

I have implemented three for my most common use cases: 

-**Auchan Agent**: for interacting with Auchan's website for grocery shopping (uses vision and text for web browsing). Capable of searching for products and putting them in the cart. In the following example it can be seen browsing the website for requested products and recovering from errors and annoying pop-ups and banners, as well as realizing that it should search for the products in Spanish despite the task being in English.


https://github.com/user-attachments/assets/3b4814eb-b1c5-4a55-829f-cf1daf19bca0



-**Report Agent**: for generating reports and documents from web search data on arbitrary topics. In this example the model is tasked with finding information on recent incidents involving planes in Europe and creating an interactive map.


https://github.com/user-attachments/assets/3163b762-556d-4a1a-b466-a03f61ac7b83


-**YouTube Agent**: for interacting with YouTube videos, including searching, watching, and extracting transcripts. It allows to quickly locate media of interest, saving a lot of time of manual searches.


## Context & Memory:

This is probably the most important piece in any LLM system, impacting everything from latency to accuracy (I have found the latency of Gemini models to increase substantially at around 70k tokens despite having a 1M context window). It is likely that even if computing power and context window keep growing, context and memory management will remain essential for as long the best AI we have are LLMs, that is, stateless systems. 

A long-term memory system using Qdrant as vector db, and a ChatGPT-style bio tool to autonomously enrich the system prompt is a WIP. 

For now I have implemented what I have called “sessions”, which is simply the labelling of certain interactions as belonging to a specific topic, this allows to load all interactions about that topic together in memory in one go. The intended effect is to be able to continue that conversation about planning a trip or an electronics project with related relevant previous interactions, leaving out distracting or irrelevant ones. The method is solid but annoyingly manual, so I will probably move to an automated hot or cold tagging/clustering process mediated by an LLM soon.


https://github.com/user-attachments/assets/6f93f8da-a9d2-4b3e-84e7-2a458661dc13



## Features

- **Speech-to-Text**: Real-time speech recognition using Whisper models
- **Large Language Model Integration**: Support for multiple LLM providers via LiteLLM
- **Text-to-Speech**: Voice synthesis using Piper TTS
- **Agent System**: Modular agent architecture for specialized tasks
- **Web Interface**: Streamlit-based web interface for interaction
- **Memory Management**: Conversation history and session management

## Project Structure

```
dexter/                          # Main package directory
├── core/                        # Core business logic
│   ├── llm.py                   # Language model integration
│   ├── stt.py                   # Speech-to-text functionality
│   └── prompts.py               # System prompts and templates
├── agents/                      # Agent system
├── memory/                      # Memory and history management
├── service/                     # Service layer
├── web_interface/              # Web-based user interface
├── utils/                      # Utilities and helpers
└── config/                     # Configuration management

scripts/                         # Entry points and scripts
tests/                          # Test files
data/                           # Data files (audio, records, etc.)
logs/                           # Log files
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Configure your environment variables in `.env`

## Usage

### Start the Server
```bash
dexter-server
# or
python scripts/server.py
```

### Run the Web Interface
```bash
streamlit run web_interface/streamlit_app.py
```

## Development

The project is organized according to Python best practices with clear separation of concerns:

- Core functionality in `dexter/core/`
- Business logic separated from presentation
- Modular agent system
- Comprehensive test coverage (planned)
- Professional package structure

## License

MIT License

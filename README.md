[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B.svg)](https://streamlit.io/)
[![HuggingFace](https://img.shields.io/badge/Agents-Smolagents-yellow)](https://huggingface.co/docs/smolagents/index)

> ⚠️ **Note**  
> This project was developed and tested on **macOS** (MacBook Pro M3 Pro 18GB). It is not intended as a ready-to-run solution but rather as a personal experiment that I’m sharing so others can **reuse ideas, code, and inspiration**. Expect to adapt it to your own environment.

---

## Demo

<table>
   <tr>
    <td><b>Speech ↔ Speech + Vision</b></td>
  </tr>
  <tr>
    <td>
      <a href="https://github.com/user-attachments/assets/8d42e1ef-5a6a-4078-873d-743274978dc7">
        <img src="https://github.com/user-attachments/assets/8d42e1ef-5a6a-4078-873d-743274978dc7" width="350"/>
      </a>
    </td>
  </tr>
</table>

---

## Overview

DeXteR is my attempt to integrate AI into my daily life and home in a more natural, frictionless way.  
It is a **personal multimodal system and interface** for interacting with LLMs and LVLMs, driven by the philosophy that such powerful technology should not be locked behind a text box and should be as **open-source and local** as possible.  

It supports multiple modes of interaction and incorporates different levels of autonomy along the **agency spectrum**—from a simple LLM with tools to fully fledged *Deep Research* style agents.  

---

## Features

- **Speech-to-Speech (optional Vision)** – [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) (Parakeet or Whisper with ms local latency) + custom vision code
- **LLM Agnostic** – Multiple providers supported via LiteLLM, tools compatible between models  
- **Text-to-Speech** – Voice synthesis using Piper TTS (custom distortion for robotic/sci-fi touch) (ms local latency) 
- **Agent System** – Modular agent system for specialized tasks powered by Smolagents
- **Backend** – Built with FastAPI
- **Web Interface** – Built with Streamlit  
- **Memory Management** – Conversation history + session handling

---

## Examples of interaction:

- **Text-to-Text and Text-to-Speech**: every type of interaction includes the possibility of receiving a written or spoken response since the user's preference can change from conversation to conversation or even question to question. 

https://github.com/user-attachments/assets/3cffb30a-dbc3-43a6-9fe2-37e905fb8d97



- **Real Time Speech-to-Speech with Vision**: leverages the awesome library [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) for VAD and transcription, combined with a custom implementation to allow visual input. If the Vision Mode checkbox is ticked, a frame will be grabbed from a camera for each user turn thus enabling speech-to-speech/text with visual clues.


https://github.com/user-attachments/assets/8d42e1ef-5a6a-4078-873d-743274978dc7

---

## Agents

The word *agent* is often misunderstood as binary—it either is or isn’t an agent. In reality, autonomy exists on a **spectrum**:  
- At one end: deterministic workflows where an LLM is always used in the same manner in a specific step or steps.  
- At the other: *Deep Research* style agents, where the LLM decides which actions to perform and in what order.  

My approach is to keep a **conversational LLM with tools** at the core (middle ground) and separately implement the two extremes, with the possibility of sharing as needed tools from the Deep Research style agents with the conversational LLM.

<div align="center">
  <img width="536" height="324" src="https://github.com/user-attachments/assets/1e929afa-f1d7-4472-8388-d95d358a99f5" />
</div>  

The agentic framework used is Smolagents by Huggingface [Smolagents](https://huggingface.co/docs/smolagents/index), which saves boilerplate, is easily customizable, and avoids the over-abstraction and constraints of bulkier solutions.  

Agents can be launched manually from the UI or by asking DeXteR directly. If agents do not behave as expected, I recommend using reasoning models if possible, this is one of those use cases where it is not overkill.  

### Implemented Agents
I have implemented three for my most common use cases:

- **Auchan Agent** – Browses Auchan’s grocery site (using vision + text). Capable of searching for products and putting them in the cart. In the following example it can be seen browsing the website for requested products and recovering from errors and annoying pop-ups and banners, as well as realizing that it should search for the products in Spanish despite the task being in English.


https://github.com/user-attachments/assets/2972a231-e952-4460-975d-54f3fadd57c4


- **Report Agent** – For generating reports and documents (PDFs, PPTs, etc.) from web search data on arbitrary topics. In this example the model is tasked with finding information on recent incidents involving planes in Europe and creating an interactive map.  


https://github.com/user-attachments/assets/f680535a-dd6c-4b56-9a7d-8f6451d4a7ee


- **YouTube Agent** – For interacting with YouTube videos, including searching, watching, and extracting transcripts. It allows to quickly locate media of interest, saving a lot of time of manual searches.  

---

## Context & Memory

This is probably the most important piece in any LLM system, impacting everything from latency to accuracy. I have found the latency of Gemini models to increase substantially at around 70k tokens despite having a 1M context window. It is likely that even if computing power and context window keep growing, context and memory management will remain essential for as long the best AI we have are LLMs, that is, stateless systems. 

A long-term memory system using Qdrant as vector db, and a ChatGPT-style bio tool to autonomously enrich the system prompt is a WIP. 

For now I have implemented what I have called “sessions”, which is simply the labelling of certain interactions as belonging to a specific topic, this allows to load all interactions about that topic together in memory in one go. The intended effect is to be able to continue that conversation about planning a trip or an electronics project with related relevant previous interactions, leaving out distracting or irrelevant ones. The method is annoyingly manual, so I will probably move to an automated hot or cold tagging/clustering process mediated by an LLM soon.

  https://github.com/user-attachments/assets/6f93f8da-a9d2-4b3e-84e7-2a458661dc13  

---

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

## License

MIT License

## Developer Notes

### Full Project Structure

<details>
<summary>Click to expand</summary>

    DeXteR/
    ├── 📁 dexter/                          # Main package directory
    │   ├── __init__.py
    │   ├── 📁 agents/                      # Agent system for specialized tasks
    │   │   ├── __init__.py
    │   │   ├── agents.py                   # Agent definitions and configurations
    │   │   ├── agents_cli_interface.py     # CLI interface for agents
    │   │   ├── agents_executors.py         # Agent execution logic
    │   │   ├── agents_utils.py             # Agent utility functions
    │   │   └── tools.py                    # Tools available to agents
    │   ├── 📁 api/                         # FastAPI REST API
    │   │   ├── __init__.py
    │   │   ├── app.py                      # Main FastAPI application
    │   │   ├── deps.py                     # Dependency injection
    │   │   └── 📁 routes/                  # API route definitions
    │   │       ├── __init__.py
    │   │       ├── agents.py               # Agent management endpoints
    │   │       ├── chat.py                 # Chat/conversation endpoints
    │   │       ├── sessions.py             # Session management endpoints
    │   │       ├── system.py               # System configuration endpoints
    │   │       ├── transcribe.py           # Audio transcription endpoints
    │   │       └── tts.py                  # Text-to-speech endpoints
    │   ├── 📁 config/                      # Configuration management
    │   │   ├── __init__.py
    │   │   ├── logging_config.py           # Logging configuration
    │   │   └── settings.py                 # Application settings
    │   ├── 📁 core/                        # Core business logic
    │   │   ├── __init__.py
    │   │   ├── llm.py                      # Language model integration
    │   │   ├── prompts.py                  # System prompts and templates
    │   │   ├── stt.py                      # Speech-to-text functionality
    │   │   ├── tts.py                      # Text-to-speech functionality
    │   │   └── voice_distortion.py         # Audio processing utilities
    │   ├── 📁 memory/                      # Conversation history storage
    │   │   └── 📁 sessions/                # Session-specific conversations
    │   ├── 📁 models/                      # AI model files
    │   │   └── 📁 tts/                     # Text-to-speech model files
    │   │       └── en_US-hfc_male-medium.onnx.json
    │   ├── 📁 service/                     # Service layer
    │   │   ├── __init__.py
    │   │   └── history_manager.py          # Conversation history management
    │   ├── 📁 utils/                       # Utilities and helpers
    │   │   ├── __init__.py
    │   │   └── common.py                   # Common utility functions
    │   └── 📁 web_interface/               # Streamlit web interface
    │       ├── __init__.py
    │       ├── streamlit_app.py            # Main web application
    │       └── 📁 components/              # UI components
    │           ├── __init__.py
    │           ├── agents_component.py     # Agent management UI
    │           ├── audio_chat.py           # Audio chat interface
    │           ├── context_memory_component.py # Memory management UI
    │           ├── realtime_stt_component.py   # Real-time STT UI
    │           ├── test_component.py       # Testing/debugging UI
    │           ├── text_chat.py            # Text chat interface
    │           └── video_recorder_component.py # Video recording UI
    ├── 📁 scripts/                         # Entry points and utilities
    │   └── server.py                       # Server startup script
    ├── 📁 tests/                           # Test suite
    │   ├── __init__.py
    │   ├── conftest.py                     # Test configuration
    │   ├── 📁 agents/                      # Agent tests
    │   ├── 📁 core/                        # Core functionality tests
    │   ├── 📁 service/                     # Service layer tests
    │   └── 📁 utils/                       # Utility tests
    ├── 📁 data/                            # Data files and storage
    │   └── 📁 scratch_pads/                # Temporary data storage
    ├── 📁 logs/                            # Application logs
    │   └── dexter.log                      # Main log file
    ├── 📁 dxt/                             # Virtual environment (excluded from git)
    ├── .env                                # Environment variables (excluded from git)
    ├── .gitignore                          # Git ignore rules
    ├── conftest.py                         # Global test configuration
    ├── pyproject.toml                      # Modern Python project configuration
    ├── requirements.txt                    # Python dependencies
    ├── setup.py                            # Package setup (legacy)
    └── README.md                           # Project documentation

</details>


### Details for anyone diving into the internals. 

<details>
<summary>Click to expand</summary>

- **Agents**  
  - Defined in `agents.py` with `.name` and `.description` used for prompt building.  
  - Their tools come from `tools.py` (decorated with `@tool`, proper docstring + type hints).  
  - Execution logic lives in `agents_executors.py` (run in separate threads, assigned to `pending_tasks` in `LLM`). Executors prepend task-specific instructions and handle imports.  
  - Agents must also be imported into `custom_executor` in `utils.py` to run.  
  - Auxiliary agent functions (callbacks, etc.) live in `agent_utils.py`.  
  - To expose agents to the LLM, import from `agents.py` and register:  
    ```python
    cls._instance.agents = generate_agents_prompt([test_agent, youtube_agent, auchan_agent, report_agent])
    ```  
  - Agents can also run standalone via `agent_launcher.py`.  

- **LLM**  
  - Tools and agents are passed as arguments when building the prompt string.  
</details>

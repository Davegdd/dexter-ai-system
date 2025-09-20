# DeXteR - AI Assistant

A comprehensive AI assistant that combines speech-to-text, large language models.

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

import os
import json
from datetime import datetime
from typing import Dict, List
from ..config.settings import settings

class HistoryManager:
    """
    Manages conversation history and session data for the DeXteR application.
    
    This class handles the creation, loading, and saving of conversation histories
    and session-specific data. It maintains two types of storage:
    - Memory directory: For general conversation histories
    - Sessions directory: For tagged conversation sessions
    
    Attributes:
        memory_directory (str): Directory path for storing general conversation histories
        sessions_directory (str): Directory path for storing session-specific conversations
        history_file (str): Current history file path being used
    
    The class automatically creates necessary directories and manages file operations
    for persistent storage of conversation data in JSON format.
    """
    memory_directory = settings.MEMORY_DIRECTORY
    sessions_directory = settings.SESSIONS_DIRECTORY

    def __init__(self):
        self.history_file = None
        os.makedirs(self.sessions_directory, exist_ok=True)
        
    def get_history_file(self, new_history: bool = False) -> str:
        """Get the history file path - create new if requested, otherwise use most recent."""
        if new_history:
            current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.history_file = os.path.join(self.memory_directory, f"{current_datetime}.json")
            self.save_history([{}])
        else:
            if not self.history_file:
                self.history_file = self._get_most_recent_history_file()
        return self.history_file
    
    def _get_most_recent_history_file(self) -> str:
        """Find the most recent JSON file in the memory directory."""
        json_files = [f for f in os.listdir(self.memory_directory) if f.endswith('.json')]
        if not json_files:
            return self.get_history_file(new_history=True)
        
        json_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.memory_directory, x)), reverse=True)
        return os.path.join(self.memory_directory, json_files[0])
    
    def load_history(self) -> List[Dict]:
        """Load history from the current history file."""
        if not self.history_file:
            self.get_history_file()
            
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return [{}]
    
    def save_history(self, history: List[Dict]):
        """Save history to the current history file."""
        if not self.history_file:
            self.get_history_file()
            
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def save_to_session(self, session_tag: str, user_msg: Dict, assistant_msg: Dict, system_prompt: str = None):
        """Save user and assistant messages to a session-specific file."""
        session_file = os.path.join(self.sessions_directory, f"{session_tag}.json")
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Creating new session file: {session_tag}")
            session_data = []
        
        if session_data and session_data[0].get("role") == "system":
            session_data.pop(0)
        
        if system_prompt:
            session_data.insert(0, {
                "role": "system",
                "content": system_prompt
            })
        
        interaction = {
            "user": user_msg,
            "assistant": assistant_msg
        }
        
        session_data.append(interaction)
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def get_session_history(self, session_tag: str) -> List[Dict]:
        """Load history from a specific session file."""
        session_file = os.path.join(self.sessions_directory, f"{session_tag}.json")
        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def list_sessions(self) -> List[str]:
        """List all available session tags."""
        if not os.path.exists(self.sessions_directory):
            return []
        
        json_files = [f for f in os.listdir(self.sessions_directory) if f.endswith('.json')]
        return [f[:-5] for f in json_files]
    
    def delete_session(self, session_tag: str) -> bool:
        """Delete a session file."""
        session_file = os.path.join(self.sessions_directory, f"{session_tag}.json")
        try:
            if os.path.exists(session_file):
                os.remove(session_file)
                return True
            return False
        except Exception:
            return False
    
    def load_session_into_history(self, session_tag: str) -> tuple[str, List[Dict]]:
        """Load a session file and return system prompt and history separately."""
        session_file = os.path.join(self.sessions_directory, f"{session_tag}.json")
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            system_prompt = None
            history = []
            
            for item in session_data:
                if item.get("role") == "system":
                    system_prompt = item["content"]
                elif "user" in item and "assistant" in item:
                    history.append(item["user"])
                    history.append(item["assistant"])
            
            history.insert(0, {"role": "system", "content": system_prompt})
            
            return system_prompt, history
        except (FileNotFoundError, json.JSONDecodeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not load session '{session_tag}': {e}")
            return None, [{}]
import os
import json
import tempfile
import shutil
from unittest.mock import patch
from pathlib import Path

from dexter.service.history_manager import HistoryManager


class TestHistoryManager:
    """Test cases for HistoryManager class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_dir = os.path.join(self.temp_dir, "memory")
        self.sessions_dir = os.path.join(self.temp_dir, "sessions")
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('dexter.service.history_manager.settings')
    def test_init_creates_sessions_directory(self, mock_settings):
        """Test that initialization creates sessions directory if it doesn't exist."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.temp_dir) / "new_sessions"
        
        # Act
        history_manager = HistoryManager()
        
        # Assert
        assert os.path.exists(str(mock_settings.SESSIONS_DIRECTORY))
        assert history_manager.history_file is None


class TestGetHistoryFile:
    """Test cases for get_history_file method."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_dir = os.path.join(self.temp_dir, "memory")
        self.sessions_dir = os.path.join(self.temp_dir, "sessions")
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('dexter.service.history_manager.settings')
    @patch('dexter.service.history_manager.datetime')
    def test_get_history_file_new_history_true(self, mock_datetime, mock_settings):
        """Test creating new history file."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager.get_history_file(new_history=True)
        
        # Assert
        expected_path = os.path.join(self.memory_dir, "20240101_120000.json")
        assert result == expected_path
        assert history_manager.history_file == expected_path
        assert os.path.exists(expected_path)
    
    @patch('dexter.service.history_manager.settings')
    @patch('dexter.service.history_manager.datetime')
    def test_get_history_file_new_history_true(self, mock_datetime, mock_settings):
        """Test creating new history file."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager.get_history_file(new_history=True)
        
        # Assert
        expected_path = os.path.join(self.memory_dir, "20240101_120000.json")
        assert result == expected_path
        assert history_manager.history_file == expected_path
        assert os.path.exists(expected_path)
    
    @patch('dexter.service.history_manager.settings')
    def test_get_history_file_existing_file(self, mock_settings):
        """Test getting existing history file."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        # Create existing file
        existing_file = os.path.join(self.memory_dir, "20240101_100000.json")
        with open(existing_file, 'w') as f:
            json.dump([{}], f)
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager.get_history_file(new_history=False)
        
        # Assert
        assert result == existing_file
        assert history_manager.history_file == existing_file
    
    @patch('dexter.service.history_manager.settings')
    def test_get_most_recent_history_file_multiple_files(self, mock_settings):
        """Test getting most recent file when multiple exist."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        # Create multiple files with different timestamps
        older_file = os.path.join(self.memory_dir, "20240101_100000.json")
        newer_file = os.path.join(self.memory_dir, "20240101_200000.json")
        
        with open(older_file, 'w') as f:
            json.dump([{}], f)
        
        # Wait a bit to ensure different modification times
        import time
        time.sleep(0.01)
        
        with open(newer_file, 'w') as f:
            json.dump([{}], f)
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager._get_most_recent_history_file()
        
        # Assert
        assert result == newer_file


class TestLoadHistory:
    """Test cases for load_history method."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_dir = os.path.join(self.temp_dir, "memory")
        self.sessions_dir = os.path.join(self.temp_dir, "sessions")
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('dexter.service.history_manager.settings')
    def test_load_history_existing_file(self, mock_settings):
        """Test loading history from existing file."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        test_history = [{"role": "user", "content": "Hello"}]
        history_file = os.path.join(self.memory_dir, "test.json")
        
        with open(history_file, 'w') as f:
            json.dump(test_history, f)
        
        history_manager = HistoryManager()
        history_manager.history_file = history_file
        
        # Act
        result = history_manager.load_history()
        
        # Assert
        assert result == test_history
    
    @patch('dexter.service.history_manager.settings')
    def test_load_history_file_not_found(self, mock_settings):
        """Test loading history when file doesn't exist."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        history_manager = HistoryManager()
        history_manager.history_file = os.path.join(self.memory_dir, "nonexistent.json")
        
        # Act
        result = history_manager.load_history()
        
        # Assert
        assert result == [{}]
    
    @patch('dexter.service.history_manager.settings')
    def test_load_history_invalid_json(self, mock_settings):
        """Test loading history from file with invalid JSON."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        history_file = os.path.join(self.memory_dir, "invalid.json")
        with open(history_file, 'w') as f:
            f.write("invalid json content")
        
        history_manager = HistoryManager()
        history_manager.history_file = history_file
        
        # Act
        result = history_manager.load_history()
        
        # Assert
        assert result == [{}]


class TestSaveHistory:
    """Test cases for save_history method."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_dir = os.path.join(self.temp_dir, "memory")
        self.sessions_dir = os.path.join(self.temp_dir, "sessions")
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('dexter.service.history_manager.settings')
    def test_save_history(self, mock_settings):
        """Test saving history to file."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        test_history = [{"role": "user", "content": "Hello"}]
        history_file = os.path.join(self.memory_dir, "test.json")
        
        history_manager = HistoryManager()
        history_manager.history_file = history_file
        
        # Act
        history_manager.save_history(test_history)
        
        # Assert
        assert os.path.exists(history_file)
        with open(history_file, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == test_history


class TestSessionMethods:
    """Test cases for session-related methods."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_dir = os.path.join(self.temp_dir, "memory")
        self.sessions_dir = os.path.join(self.temp_dir, "sessions")
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('dexter.service.history_manager.settings')
    def test_save_to_session_new_file(self, mock_settings):
        """Test saving to a new session file."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        user_msg = {"role": "user", "content": "Hello"}
        assistant_msg = {"role": "assistant", "content": "Hi there!"}
        system_prompt = "You are a helpful assistant"
        
        history_manager = HistoryManager()
        
        # Act
        history_manager.save_to_session("test_session", user_msg, assistant_msg, system_prompt)
        
        # Assert
        session_file = os.path.join(self.sessions_dir, "test_session.json")
        assert os.path.exists(session_file)
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        assert len(session_data) == 2
        assert session_data[0]["role"] == "system"
        assert session_data[0]["content"] == system_prompt
        assert session_data[1]["user"] == user_msg
        assert session_data[1]["assistant"] == assistant_msg
    
    @patch('dexter.service.history_manager.settings')
    def test_save_to_session_existing_file(self, mock_settings):
        """Test saving to an existing session file."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        # Create existing session file
        session_file = os.path.join(self.sessions_dir, "existing_session.json")
        existing_data = [
            {"role": "system", "content": "Old system prompt"},
            {"user": {"role": "user", "content": "Previous message"}, 
             "assistant": {"role": "assistant", "content": "Previous response"}}
        ]
        
        with open(session_file, 'w') as f:
            json.dump(existing_data, f)
        
        user_msg = {"role": "user", "content": "New message"}
        assistant_msg = {"role": "assistant", "content": "New response"}
        system_prompt = "New system prompt"
        
        history_manager = HistoryManager()
        
        # Act
        history_manager.save_to_session("existing_session", user_msg, assistant_msg, system_prompt)
        
        # Assert
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        assert len(session_data) == 3  # New system prompt + old interaction + new interaction
        assert session_data[0]["role"] == "system"
        assert session_data[0]["content"] == system_prompt
        assert session_data[2]["user"] == user_msg
        assert session_data[2]["assistant"] == assistant_msg
    
    @patch('dexter.service.history_manager.settings')
    def test_get_session_history(self, mock_settings):
        """Test getting session history."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        session_data = [
            {"role": "system", "content": "System prompt"},
            {"user": {"role": "user", "content": "Hello"}, 
             "assistant": {"role": "assistant", "content": "Hi!"}}
        ]
        
        session_file = os.path.join(self.sessions_dir, "test_session.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager.get_session_history("test_session")
        
        # Assert
        assert result == session_data
    
    @patch('dexter.service.history_manager.settings')
    def test_get_session_history_nonexistent(self, mock_settings):
        """Test getting history for nonexistent session."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager.get_session_history("nonexistent_session")
        
        # Assert
        assert result == []
    
    @patch('dexter.service.history_manager.settings')
    def test_list_sessions(self, mock_settings):
        """Test listing all sessions."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        # Create some session files
        session_files = ["session1.json", "session2.json", "session3.json"]
        for filename in session_files:
            with open(os.path.join(self.sessions_dir, filename), 'w') as f:
                json.dump([], f)
        
        # Create non-json file that should be ignored
        with open(os.path.join(self.sessions_dir, "not_a_session.txt"), 'w') as f:
            f.write("ignored")
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager.list_sessions()
        
        # Assert
        expected = ["session1", "session2", "session3"]
        assert sorted(result) == sorted(expected)
    
    @patch('dexter.service.history_manager.settings')
    def test_delete_session_existing(self, mock_settings):
        """Test deleting an existing session."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        session_file = os.path.join(self.sessions_dir, "to_delete.json")
        with open(session_file, 'w') as f:
            json.dump([], f)
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager.delete_session("to_delete")
        
        # Assert
        assert result is True
        assert not os.path.exists(session_file)
    
    @patch('dexter.service.history_manager.settings')
    def test_delete_session_nonexistent(self, mock_settings):
        """Test deleting a nonexistent session."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        history_manager = HistoryManager()
        
        # Act
        result = history_manager.delete_session("nonexistent")
        
        # Assert
        assert result is False
    
    @patch('dexter.service.history_manager.settings')
    def test_load_session_into_history(self, mock_settings):
        """Test loading session into history format."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        session_data = [
            {"role": "system", "content": "You are helpful"},
            {"user": {"role": "user", "content": "Hello"}, 
             "assistant": {"role": "assistant", "content": "Hi!"}},
            {"user": {"role": "user", "content": "How are you?"}, 
             "assistant": {"role": "assistant", "content": "I'm good!"}}
        ]
        
        session_file = os.path.join(self.sessions_dir, "test_session.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        history_manager = HistoryManager()
        
        # Act
        system_prompt, history = history_manager.load_session_into_history("test_session")
        
        # Assert
        assert system_prompt == "You are helpful"
        assert len(history) == 5  # system + 4 messages (2 user + 2 assistant)
        assert history[0]["role"] == "system"
        assert history[0]["content"] == "You are helpful"
        assert history[1]["role"] == "user"
        assert history[1]["content"] == "Hello"
        assert history[2]["role"] == "assistant"
        assert history[2]["content"] == "Hi!"
    
    @patch('dexter.service.history_manager.settings')
    def test_load_session_into_history_nonexistent(self, mock_settings):
        """Test loading nonexistent session into history."""
        # Arrange
        mock_settings.MEMORY_DIRECTORY = Path(self.memory_dir)
        mock_settings.SESSIONS_DIRECTORY = Path(self.sessions_dir)
        
        history_manager = HistoryManager()
        
        # Act
        system_prompt, history = history_manager.load_session_into_history("nonexistent")
        
        # Assert
        assert system_prompt is None
        assert history == [{}]
from unittest.mock import Mock, patch
from concurrent.futures import Future

from dexter.agents.agents_executors import (
    youtube_agent,
    auchan_agent,
    report_agent,
    AGENTS
)

class TestAgentExecutors:
    """Test cases for agent executor functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_task = "Test task description"
        self.additional_args = {"key": "value", "number": 42}

    @patch('dexter.agents.agents_executors.executor.submit')
    @patch('dexter.agents.agents_executors._youtube_agent_obj')
    def test_youtube_agent_without_additional_args(self, mock_agent, mock_submit):
        # Arrange
        mock_future = Mock(spec=Future)
        mock_submit.return_value = mock_future
        
        # Act
        result = youtube_agent(self.test_task)
        
        # Assert
        assert result == mock_future
        # Verify that the task was prepended with YouTube instructions
        call_args = mock_submit.call_args[0]
        assert len(call_args) == 2
        assert call_args[0] == mock_agent.run
        assert "You have access to YouTube search tools" in call_args[1]
        assert self.test_task in call_args[1]
    
    @patch('dexter.agents.agents_executors.executor.submit')
    @patch('dexter.agents.agents_executors._youtube_agent_obj')
    def test_youtube_agent_with_additional_args(self, mock_agent, mock_submit):
        # Arrange
        mock_future = Mock(spec=Future)
        mock_submit.return_value = mock_future
        
        # Act
        result = youtube_agent(self.test_task, self.additional_args)
        
        # Assert
        assert result == mock_future
        call_args = mock_submit.call_args[0]
        assert len(call_args) == 3
        assert call_args[2] == self.additional_args

    @patch('dexter.agents.agents_executors.executor.submit')
    @patch('dexter.agents.agents_executors._auchan_agent_obj')
    @patch('helium.start_chrome')
    @patch('dexter.agents.agents_executors.webdriver')
    def test_auchan_agent_without_additional_args(self, mock_webdriver, mock_start_chrome, mock_agent, mock_submit):
        # Arrange
        mock_future = Mock(spec=Future)
        mock_submit.return_value = mock_future
        mock_driver = Mock()
        mock_start_chrome.return_value = mock_driver
        
        # Act
        result = auchan_agent(self.test_task)
        
        # Assert
        assert result == mock_future
        mock_start_chrome.assert_called_once()
        mock_agent.python_executor.assert_any_call("from helium import *")
        mock_agent.python_executor.assert_any_call("from pypdf import *")
        
        # Verify that the task was prepended with helium instructions
        call_args = mock_submit.call_args[0]
        assert "You can use helium to interact with websites" in call_args[1]

    @patch('dexter.agents.agents_executors.executor.submit')
    @patch('dexter.agents.agents_executors._report_agent_obj')
    def test_report_agent_without_additional_args(self, mock_agent, mock_submit):
        # Arrange
        mock_future = Mock(spec=Future)
        mock_submit.return_value = mock_future
        mock_agent.additional_authorized_imports = ["pandas", "matplotlib"]
        
        # Act
        result = report_agent(self.test_task)
        
        # Assert
        assert result == mock_future
        call_args = mock_submit.call_args[0]
        assert "You can import the following packages" in call_args[1]
        assert "pandas" in call_args[1]
        assert "matplotlib" in call_args[1]

    def test_agents_mapping(self):
        # Arrange & Act
        agents = AGENTS
        
        # Assert
        assert "youtube" in agents
        assert "auchan" in agents
        assert "report" in agents
        assert agents["youtube"] == youtube_agent
        assert agents["auchan"] == auchan_agent
        assert agents["report"] == report_agent

class TestThreadPoolExecutor:
    """Test cases for ThreadPoolExecutor configuration."""
    
    def test_executor_configuration(self):
        # Arrange & Act
        from dexter.agents.agents_executors import executor
        
        # Assert
        assert executor._max_workers == 4
        assert hasattr(executor, 'submit')
        assert hasattr(executor, 'shutdown')


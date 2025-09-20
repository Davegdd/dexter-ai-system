from unittest.mock import Mock, patch
from concurrent.futures import Future
from dexter.core.llm import LLM
from dexter.service.history_manager import HistoryManager

class TestLLM:
    
    def setup_method(self):
        """Reset singleton instance before each test."""
        LLM._instance = None
    
    def test_singleton_pattern(self):
        """Test that LLM follows singleton pattern."""
        # Arrange & Act
        instance1 = LLM()
        instance2 = LLM()
        
        # Assert
        assert instance1 is instance2
        assert LLM._instance is not None
    
    @patch('dexter.core.llm.settings')
    @patch('dexter.core.llm.generate_tools_prompt')
    @patch('dexter.core.llm.generate_agents_prompt')
    @patch('dexter.core.llm.build_system_prompt')
    def test_initialization(self, mock_build_system, mock_gen_agents, mock_gen_tools, mock_settings):
        """Test LLM initialization with proper default values."""
        # Arrange
        mock_settings.DEFAULT_MODEL = "test-model"
        mock_gen_tools.return_value = "test-tools"
        mock_gen_agents.return_value = "test-agents"
        mock_build_system.return_value = "test-system-prompt"
        
        # Act
        llm = LLM()
        
        # Assert
        assert llm.model == "test-model"
        assert llm.tools == "test-tools"
        assert llm.agents == "test-agents"
        assert llm.system_prompt == "test-system-prompt"
        assert llm.complete_response is None
        assert llm.speech_text is None
        assert llm.new_history is False
        assert llm.timestamp_mode is True
        assert llm.pending_tasks == []
        assert llm.session_tag is None
        assert isinstance(llm.history_manager, HistoryManager)
    
    def test_prepare_input_file_content_video(self):
        """Test file content preparation for video files."""
        # Arrange
        llm = LLM()
        base64_data = "test_video_data"
        file_type = "video"
        
        # Act
        result = llm._prepare_input_file_content(base64_data, file_type)
        
        # Assert
        expected = {
            "type": "file",
            "file": {
                "file_data": "data:video/mp4;base64,test_video_data"
            },
        }
        assert result == expected
    
    def test_prepare_input_file_content_image(self):
        """Test file content preparation for image files."""
        # Arrange
        llm = LLM()
        base64_data = "test_image_data"
        file_type = "image"
        
        # Act
        result = llm._prepare_input_file_content(base64_data, file_type)
        
        # Assert
        expected = {
            "type": "file",
            "file": {
                "file_data": "data:image/jpeg;base64,test_image_data"
            },
        }
        assert result == expected
    
    def test_prepare_input_file_content_fallback(self):
        """Test file content preparation with unknown file type falls back to image."""
        # Arrange
        llm = LLM()
        base64_data = "test_data"
        file_type = "unknown"
        
        # Act
        result = llm._prepare_input_file_content(base64_data, file_type)
        
        # Assert
        expected = {
            "type": "file",
            "file": {
                "file_data": "data:image/jpeg;base64,test_data"
            },
        }
        assert result == expected
    
    def test_prepare_user_message_text_only(self):
        """Test user message preparation with text only."""
        # Arrange
        llm = LLM()
        user_text = "Hello, world!"
        
        # Act
        result = llm._prepare_user_message(user_text)
        
        # Assert
        expected = {"role": "user", "content": "Hello, world!"}
        assert result == expected
    
    def test_prepare_user_message_with_file(self):
        """Test user message preparation with file content."""
        # Arrange
        llm = LLM()
        user_text = "Analyze this image"
        base64_data = "test_image_data"
        file_type = "image"
        
        # Act
        result = llm._prepare_user_message(user_text, base64_data, file_type)
        
        # Assert
        expected = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image"},
                {
                    "type": "file",
                    "file": {
                        "file_data": "data:image/jpeg;base64,test_image_data"
                    },
                }
            ],
        }
        assert result == expected
    
    @patch('dexter.core.llm.datetime')
    def test_add_timestamp_if_enabled_true(self, mock_datetime):
        """Test timestamp addition when timestamp_mode is enabled."""
        # Arrange
        llm = LLM()
        llm.timestamp_mode = True
        mock_datetime.now.return_value.strftime.return_value = "01/01/2024 12:00:00"
        text = "Test message"
        
        # Act
        result = llm._add_timestamp_if_enabled(text)
        
        # Assert
        assert result == "[01/01/2024 12:00:00] Test message"
    
    def test_add_timestamp_if_enabled_false(self):
        """Test timestamp not added when timestamp_mode is disabled."""
        # Arrange
        llm = LLM()
        llm.timestamp_mode = False
        text = "Test message"
        
        # Act
        result = llm._add_timestamp_if_enabled(text)
        
        # Assert
        assert result == "Test message"
    
    def test_extract_speech_text(self):
        """Test speech text extraction by removing code blocks."""
        # Arrange
        llm = LLM()
        response_text = "Here's the solution:\n```py\nprint('hello')\n```\nThat should work!"
        extracted_code = "print('hello')"
        
        # Act
        result = llm._extract_speech_text(response_text, extracted_code)
        
        # Assert
        expected = "Here's the solution:\n\nThat should work!"
        assert result == expected
    
    def test_check_completed_tasks_with_successful_task(self):
        """Test checking completed tasks with successful result."""
        # Arrange
        llm = LLM()
        mock_future = Mock(spec=Future)
        mock_future.done.return_value = True
        mock_future.result.return_value = "Task completed successfully"
        llm.pending_tasks = [mock_future]
        
        with patch.object(llm, 'llm_input') as mock_llm_input:
            # Act
            llm._check_completed_tasks()
            
            # Assert
            assert len(llm.pending_tasks) == 0
            mock_llm_input.assert_called_once()
            call_args = mock_llm_input.call_args[0][0]
            assert "Task completed successfully" in call_args[0]['text']
    
    def test_check_completed_tasks_with_failed_task(self):
        """Test checking completed tasks with failed result."""
        # Arrange
        llm = LLM()
        mock_future = Mock(spec=Future)
        mock_future.done.return_value = True
        mock_future.result.side_effect = Exception("Task failed")
        llm.pending_tasks = [mock_future]
        
        with patch.object(llm, 'llm_input') as mock_llm_input:
            # Act
            llm._check_completed_tasks()
            
            # Assert
            assert len(llm.pending_tasks) == 0
            mock_llm_input.assert_called_once()
            call_args = mock_llm_input.call_args[0][0]
            assert "Task error: Task failed" in call_args[0]['text']

    def test_check_completed_tasks_with_pending_task(self):
        """Test checking completed tasks when task is still pending."""
        # Arrange
        llm = LLM()
        mock_future = Mock(spec=Future)
        mock_future.done.return_value = False
        llm.pending_tasks = [mock_future]
        
        with patch.object(llm, 'llm_input') as mock_llm_input:
            # Act
            llm._check_completed_tasks()
            
            # Assert
            assert len(llm.pending_tasks) == 1
            mock_llm_input.assert_not_called()
    
    @patch('dexter.core.llm.completion')
    @patch('dexter.core.llm.settings')
    def test_send_message_with_retry_success(self, mock_settings, mock_completion):
        """Test successful API call without retries."""
        # Arrange
        llm = LLM()
        mock_settings.TEMPERATURE = 0.7
        mock_settings.MAX_TOKENS = 1000
        mock_settings.TOP_P = 0.9
        mock_response = Mock()
        mock_completion.return_value = mock_response
        messages = [{"role": "user", "content": "test"}]
        
        # Act
        result = llm._send_message_with_retry(messages)
        
        # Assert
        assert result == mock_response
        mock_completion.assert_called_once_with(
            model=llm.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
            tools=[],
            tool_choice="auto"
        )
    
    @patch('dexter.core.llm.extract_code_from_text')
    @patch('dexter.core.llm.run_extracted_code')
    @patch('dexter.core.llm.format_content')
    @patch.object(LLM, '_send_message_with_retry')
    def test_llm_input_with_extracted_code_future(self, mock_send, mock_format, mock_run_code, mock_extract):
        """Test llm_input when extracted code returns a Future."""
        # Arrange
        llm = LLM()
        llm.history = [{"role": "system", "content": "system"}]
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response with code"
        mock_send.return_value = mock_response
        mock_extract.return_value = "print('hello')"
        mock_future = Mock(spec=Future)
        mock_run_code.return_value = mock_future
        
        question_dict = [{"text": "Execute some code"}]
        
        with patch.object(llm.history_manager, 'save_history'), \
             patch.object(llm.history_manager, 'save_to_session'):
            
            # Act
            llm.llm_input(question_dict)
            
            # Assert
            assert mock_future in llm.pending_tasks
            assert llm.complete_response == "Response with code"
            assert llm.speech_text is not None  # Should be set for code responses
    
    @patch('dexter.core.llm.extract_code_from_text')
    @patch.object(LLM, '_send_message_with_retry')
    def test_llm_input_without_code(self, mock_send, mock_extract):
        """Test llm_input when no code is extracted."""
        # Arrange
        llm = LLM()
        llm.history = [{"role": "system", "content": "system"}]
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Simple response"
        mock_send.return_value = mock_response
        mock_extract.return_value = None
        
        question_dict = [{"text": "Just a question"}]
        
        with patch.object(llm.history_manager, 'save_history'), \
             patch.object(llm.history_manager, 'save_to_session'), \
             patch.object(llm, '_check_completed_tasks') as mock_check:
            
            # Act
            llm.llm_input(question_dict)
            
            # Assert
            assert llm.complete_response == "Simple response"
            assert llm.speech_text is None
            mock_check.assert_called_once()
    
    def test_llm_input_new_history(self):
        """Test llm_input starts new history when new_history is True."""
        # Arrange
        llm = LLM()
        llm.new_history = True
        question_dict = [{"text": "New conversation"}]
        
        with patch.object(llm.history_manager, 'get_history_file') as mock_get_history, \
             patch.object(llm.history_manager, 'save_history') as mock_save_history, \
             patch.object(llm.history_manager, 'save_to_session'), \
             patch.object(llm, '_send_message_with_retry') as mock_send, \
             patch.object(llm, '_check_completed_tasks') as mock_check, \
             patch('dexter.core.llm.extract_code_from_text', return_value=None), \
             patch('dexter.core.llm.datetime') as mock_datetime:
            
            mock_datetime.now.return_value.strftime.return_value = "16/09/2025 10:59:22"
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Response"
            mock_send.return_value = mock_response
            
            # Act
            llm.llm_input(question_dict)
            
            # Assert
            mock_get_history.assert_called_with(new_history=True)
            assert llm.new_history is False
            assert llm.history == [{'role': 'system', 'content': llm.system_prompt}, 
                                   {'role': 'user', 'content': '[16/09/2025 10:59:22] New conversation'}, 
                                   {'role': 'assistant', 'content': 'Response'}]
            mock_save_history.assert_called_once()
            mock_check.assert_called_once()
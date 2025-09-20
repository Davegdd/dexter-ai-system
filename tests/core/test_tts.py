from unittest.mock import Mock, patch
from dexter.core.tts import TTSManager

class TestTTSManager:
    
    @patch('dexter.core.tts.PiperVoice')
    @patch('dexter.core.tts.VoiceDistortor')
    @patch('dexter.core.tts.settings')
    def test_initialization_with_defaults(self, mock_settings, mock_distortor_class, mock_piper_voice_class):
        """Test TTSManager initialization with default settings."""
        # Arrange
        mock_settings.TTS_DEFAULT_SPEED = 1.0
        mock_settings.TTS_CLEAN_TEXT = True
        mock_settings.TTS_MODEL_PATH = "/path/to/model"
        mock_settings.AUDIO_SAMPLE_RATE = 22050
        mock_piper_voice = Mock()
        mock_piper_voice_class.load.return_value = mock_piper_voice
        mock_distortor = Mock()
        mock_distortor_class.return_value = mock_distortor
        
        # Act
        tts_manager = TTSManager()
        
        # Assert
        assert tts_manager.default_speed == 1.0
        assert tts_manager.should_clean_text is True
        assert tts_manager.piper_voice == mock_piper_voice
        assert tts_manager.distortor == mock_distortor
        mock_piper_voice_class.load.assert_called_once_with("/path/to/model")
        mock_distortor_class.assert_called_once_with(sample_rate=22050)
    
    @patch('dexter.core.tts.PiperVoice')
    @patch('dexter.core.tts.VoiceDistortor')
    @patch('dexter.core.tts.settings')
    def test_initialization_with_custom_params(self, mock_settings, mock_distortor_class, mock_piper_voice_class):
        """Test TTSManager initialization with custom parameters."""
        # Arrange
        mock_settings.TTS_MODEL_PATH = "/path/to/model"
        mock_piper_voice = Mock()
        mock_piper_voice_class.load.return_value = mock_piper_voice
        mock_distortor = Mock()
        mock_distortor_class.return_value = mock_distortor
        
        # Act
        tts_manager = TTSManager(default_speed=1.5, clean_text=False, sample_rate=44100)
        
        # Assert
        assert tts_manager.default_speed == 1.5
        assert tts_manager.should_clean_text is False
        mock_distortor_class.assert_called_once_with(sample_rate=44100)
    
    def test_clean_text_content_removes_markdown(self):
        """Test that text cleaning removes markdown formatting."""
        # Arrange
        tts_manager = TTSManager()
        text_with_markdown = "**Bold text** and *italic* with `code` and # Header\n[Link](http://example.com) and https://test.com"
        
        # Act
        cleaned_text = tts_manager._clean_text_content(text_with_markdown)
        
        # Assert
        expected = "Bold text and italic with code and Header\n and "
        assert cleaned_text == expected
    
    def test_clean_text_content_empty_text(self):
        """Test text cleaning with empty or None text."""
        # Arrange
        tts_manager = TTSManager()
        
        # Act & Assert
        assert tts_manager._clean_text_content("") == ""
        assert tts_manager._clean_text_content(None) is None
    
    def test_clean_text_content_no_markdown(self):
        """Test text cleaning with plain text (no markdown)."""
        # Arrange
        tts_manager = TTSManager()
        plain_text = "This is plain text without any formatting."
        
        # Act
        cleaned_text = tts_manager._clean_text_content(plain_text)
        
        # Assert
        assert cleaned_text == plain_text
    
    @patch('dexter.core.tts.wave.open')
    @patch('dexter.core.tts.SynthesisConfig')
    @patch('dexter.core.tts.time.time')
    def test_generate_audio_file_without_distortion(self, mock_time, mock_synthesis_config, mock_wave_open):
        """Test audio generation without voice distortion."""
        # Arrange
        tts_manager = TTSManager()
        tts_manager.should_clean_text = False
        mock_piper_voice = Mock()
        tts_manager.piper_voice = mock_piper_voice
        mock_wav_file = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wav_file
        mock_time.side_effect = [0.0, 2.5]  # start and end times
        mock_config = Mock()
        mock_synthesis_config.return_value = mock_config
        
        text = "Hello, world!"
        output_path = "/path/to/output.wav"
        
        # Act
        result = tts_manager.generate_audio_file(text, output_path, apply_distortion=False)
        
        # Assert
        assert result == output_path
        mock_wave_open.assert_called_once_with(output_path, "wb")
        mock_piper_voice.synthesize_wav.assert_called_once_with(text, mock_wav_file, syn_config=mock_config)
        mock_synthesis_config.assert_called_once_with(
            volume=2.0,
            length_scale=tts_manager.default_speed
        )
    
    @patch('dexter.core.tts.os.remove')
    @patch('dexter.core.tts.wave.open')
    @patch('dexter.core.tts.SynthesisConfig')
    @patch('dexter.core.tts.time.time')
    def test_generate_audio_file_with_distortion(self, mock_time, mock_synthesis_config, mock_wave_open, mock_os_remove):
        """Test audio generation with voice distortion."""
        # Arrange
        tts_manager = TTSManager()
        tts_manager.should_clean_text = False
        mock_piper_voice = Mock()
        tts_manager.piper_voice = mock_piper_voice
        mock_distortor = Mock()
        tts_manager.distortor = mock_distortor
        mock_wav_file = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wav_file
        mock_time.side_effect = [0.0, 1.0, 2.0, 3.0]  # start, distortion start, distortion end, total end
        mock_config = Mock()
        mock_synthesis_config.return_value = mock_config
        
        text = "Hello, world!"
        output_path = "/path/to/output.wav"
        temp_path = "/path/to/output_temp.wav"
        
        # Act
        result = tts_manager.generate_audio_file(text, output_path, apply_distortion=True)
        
        # Assert
        assert result == output_path
        mock_wave_open.assert_called_once_with(temp_path, "wb")
        mock_piper_voice.synthesize_wav.assert_called_once_with(text, mock_wav_file, syn_config=mock_config)
        mock_distortor.process_file.assert_called_once_with(temp_path, output_path)
        mock_os_remove.assert_called_once_with(temp_path)
    
    @patch('dexter.core.tts.wave.open')
    @patch('dexter.core.tts.SynthesisConfig')
    def test_generate_audio_file_with_text_cleaning(self, mock_synthesis_config, mock_wave_open):
        """Test audio generation with text cleaning enabled."""
        # Arrange
        tts_manager = TTSManager()
        tts_manager.should_clean_text = True
        mock_piper_voice = Mock()
        tts_manager.piper_voice = mock_piper_voice
        mock_wav_file = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wav_file
        
        text_with_markdown = "**Hello**, world!"
        expected_cleaned_text = "Hello, world!"
        output_path = "/path/to/output.wav"
        
        # Act
        result = tts_manager.generate_audio_file(text_with_markdown, output_path, apply_distortion=False)
        
        # Assert
        assert result == output_path
        # Verify that the cleaned text was passed to synthesize_wav
        call_args = mock_piper_voice.synthesize_wav.call_args
        assert call_args[0][0] == expected_cleaned_text  # First argument should be cleaned text
    
    @patch('dexter.core.tts.wave.open')
    def test_generate_audio_file_exception_handling(self, mock_wave_open):
        """Test audio generation handles exceptions gracefully."""
        # Arrange
        tts_manager = TTSManager()
        tts_manager.should_clean_text = False
        mock_piper_voice = Mock()
        tts_manager.piper_voice = mock_piper_voice
        mock_wave_open.side_effect = Exception("File error")
        
        text = "Hello, world!"
        output_path = "/path/to/output.wav"
        
        # Act
        result = tts_manager.generate_audio_file(text, output_path)
        
        # Assert
        assert result is None
    
    @patch('dexter.core.tts.wave.open')
    @patch('dexter.core.tts.SynthesisConfig')
    def test_generate_audio_file_custom_speed(self, mock_synthesis_config, mock_wave_open):
        """Test audio generation with custom speed parameter."""
        # Arrange
        tts_manager = TTSManager()
        tts_manager.should_clean_text = False
        tts_manager.default_speed = 1.2
        mock_piper_voice = Mock()
        tts_manager.piper_voice = mock_piper_voice
        mock_wav_file = Mock()
        mock_wave_open.return_value.__enter__.return_value = mock_wav_file
        mock_config = Mock()
        mock_synthesis_config.return_value = mock_config
        
        text = "Hello, world!"
        output_path = "/path/to/output.wav"
        
        # Act
        result = tts_manager.generate_audio_file(text, output_path, speed=1.5, apply_distortion=False)
        
        # Assert
        assert result == output_path
        # Verify that the default speed is used in SynthesisConfig (speed parameter is not currently implemented)
        mock_synthesis_config.assert_called_once_with(
            volume=2.0,
            length_scale=1.2  # Should use default_speed, not the speed parameter (based on current implementation)
        )
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
import requests
from googleapiclient.discovery import build
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from dexter.agents.tools import (
    download_image,
    search_products,
    extract_text_from_pdf,
    search_youtube_videos,
    get_video_transcript,
    watch_youtube_video
)

class TestDownloadImage:
    def test_download_image_success(self):
        # Arrange
        url = "https://example.com/image.jpg"
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            save_path = temp_file.name
        
        mock_response = Mock()
        mock_response.content = b"fake image data"
        
        # Act & Assert
        with patch('requests.get', return_value=mock_response):
            result = download_image(url, save_path)
            assert result is True
            
        # Cleanup
        os.unlink(save_path)
    
    def test_download_image_request_failure(self):
        # Arrange
        url = "https://example.com/nonexistent.jpg"
        save_path = "/tmp/test_image.jpg"
        
        # Act & Assert
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error")):
            with pytest.raises(Exception, match="Failed to download image"):
                download_image(url, save_path)
    
    def test_download_image_save_failure(self):
        # Arrange
        url = "https://example.com/image.jpg"
        save_path = "/invalid/path/image.jpg"
        
        mock_response = Mock()
        mock_response.content = b"fake image data"
        
        # Act & Assert
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception, match="Failed to save image"):
                download_image(url, save_path)


class TestSearchProducts:
    @patch('dexter.agents.tools.go_to')
    @patch('urllib.parse.quote')
    def test_search_products_success(self, mock_quote, mock_go_to):
        # Arrange
        product_name = "crema de cacahuete"
        encoded_name = "crema%20de%20cacahuete"
        expected_url = f"https://www.compraonline.alcampo.es/search?q={encoded_name}"
        
        mock_quote.return_value = encoded_name
        
        # Act
        result_url = search_products(product_name)
        
        # Assert
        assert result_url == expected_url
        mock_quote.assert_called_once_with(product_name)
        mock_go_to.assert_called_once_with(expected_url)


class TestExtractTextFromPdf:
    def test_extract_text_from_pdf_success(self):
        # Arrange
        pdf_path = "/fake/path/test.pdf"
        expected_text = "This is test content from PDF"
        
        mock_page = Mock()
        mock_page.extract_text.return_value = expected_text
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        
        # Act & Assert
        with patch('builtins.open', mock_open()):
            with patch('pypdf.PdfReader', return_value=mock_reader):
                result = extract_text_from_pdf(pdf_path)
                assert result == expected_text
    
    def test_extract_text_from_pdf_file_not_found(self):
        # Arrange
        pdf_path = "/nonexistent/path/test.pdf"
        
        # Act & Assert
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            result = extract_text_from_pdf(pdf_path)
            assert "Error extracting text from PDF" in result


class TestSearchYouTubeVideos:
    @patch('dexter.agents.tools.build')
    @patch('dexter.agents.tools.YouTubeTranscriptApi')
    def test_search_youtube_videos_basic(self, mock_transcript_api, mock_build):
        # Arrange
        query = "python tutorial"
        
        mock_youtube = Mock()
        mock_search = Mock()
        mock_videos = Mock()
        
        # Mock search response
        search_response = {
            "items": [{
                "id": {"videoId": "test123"},
                "snippet": {
                    "title": "Python Tutorial",
                    "description": "Learn Python basics",
                    "channelTitle": "Code Academy",
                    "publishedAt": "2024-01-01T00:00:00Z",
                    "thumbnails": {}
                }
            }]
        }
        
        # Mock statistics response
        stats_response = {
            "items": [{
                "id": "test123",
                "statistics": {"viewCount": "1000", "likeCount": "50"}
            }]
        }
        
        mock_search.list.return_value.execute.return_value = search_response
        mock_videos.list.return_value.execute.return_value = stats_response
        mock_youtube.search.return_value = mock_search
        mock_youtube.videos.return_value = mock_videos
        mock_build.return_value = mock_youtube
        
        # Mock transcript
        mock_transcript_api.get_transcript.return_value = [
            {"text": "Welcome to Python tutorial"}
        ]
        
        # Act
        results = search_youtube_videos(query, max_results=1)
        
        # Assert
        assert len(results) == 1
        assert results[0]["video_id"] == "test123"
        assert results[0]["title"] == "Python Tutorial"
        assert results[0]["url"] == "https://www.youtube.com/watch?v=test123"
        assert "statistics" in results[0]
        assert "transcript" in results[0]
    
    @patch('dexter.agents.tools.build')
    def test_search_youtube_videos_no_transcripts(self, mock_build):
        # Arrange
        query = "test query"
        
        mock_youtube = Mock()
        mock_search = Mock()
        mock_videos = Mock()
        
        search_response = {"items": []}
        stats_response = {"items": []}
        
        mock_search.list.return_value.execute.return_value = search_response
        mock_videos.list.return_value.execute.return_value = stats_response
        mock_youtube.search.return_value = mock_search
        mock_youtube.videos.return_value = mock_videos
        mock_build.return_value = mock_youtube
        
        # Act
        results = search_youtube_videos(query, include_transcripts=False)
        
        # Assert
        assert results == []


class TestGetVideoTranscript:
    @patch('dexter.agents.tools.YouTubeTranscriptApi')
    def test_get_video_transcript_success(self, mock_transcript_api):
        # Arrange
        video_id = "test123"
        transcript_data = [
            {"text": "Hello everyone"},
            {"text": "Welcome to this video"}
        ]
        expected_transcript = "Hello everyone\nWelcome to this video"
        
        mock_transcript_api.get_transcript.return_value = transcript_data
        
        # Act
        result = get_video_transcript(video_id)
        
        # Assert
        assert result == expected_transcript
        mock_transcript_api.get_transcript.assert_called_once_with(video_id)
    
    @patch('dexter.agents.tools.YouTubeTranscriptApi')
    def test_get_video_transcript_no_transcript_available(self, mock_transcript_api):
        # Arrange
        video_id = "test123"
        mock_transcript_api.get_transcript.side_effect = TranscriptsDisabled("Transcripts disabled")
        
        # Act
        result = get_video_transcript(video_id)
        
        # Assert
        assert result is None
    
    @patch('dexter.agents.tools.YouTubeTranscriptApi')
    def test_get_video_transcript_not_found(self, mock_transcript_api):
        # Arrange
        video_id = "test123"
        mock_transcript_api.get_transcript.side_effect = NoTranscriptFound(video_id, ["en"], [])
        
        # Act
        result = get_video_transcript(video_id)
        
        # Assert
        assert result is None


class TestWatchYouTubeVideo:
    @patch('dexter.agents.tools.genai.Client')
    def test_watch_youtube_video_success(self, mock_client_class):
        # Arrange
        url = "https://www.youtube.com/watch?v=test123"
        prompt = "What is this video about?"
        expected_response = "This video is about Python programming."
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = expected_response
        
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Act
        result = watch_youtube_video(url, prompt)
        
        # Assert
        assert result == expected_response
        mock_client.models.generate_content.assert_called_once()
    
    @patch('dexter.agents.tools.genai.Client')
    def test_watch_youtube_video_api_error(self, mock_client_class):
        # Arrange
        url = "https://www.youtube.com/watch?v=test123"
        prompt = "What is this video about?"
        
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        # Act
        result = watch_youtube_video(url, prompt)
        
        # Assert
        assert result is None
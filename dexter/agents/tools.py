import logging
from typing import Dict, List
import requests
from smolagents import WebSearchTool, VisitWebpageTool, tool
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from google import genai
from google.genai import types
from typing import Optional
from helium import *
from dexter.config.settings import settings

logger = logging.getLogger(__name__)

web_search = WebSearchTool()
visit_webpage = VisitWebpageTool()

@tool
def download_image(url: str, save_path: str) -> Optional[bool]:
    """Downloads an image from the provided URL and saves it to the specified path.
    
    Args:
        url (str): The URL of the image to download
        save_path (str): The local file path where the image should be saved
        
    Returns:
        Optional[bool]: True if download and save are successful, None otherwise
        
    Raises:
        requests.exceptions.RequestException: If the download fails
        IOError: If saving the file fails
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download image from {url}: {str(e)}")
    except IOError as e:
        raise Exception(f"Failed to save image to {save_path}: {str(e)}")
    
@tool
def search_products(product_name: str) -> str:
    """
    Search for products on Alcampo's website.

    Args:
        product_name: Name of the product to search for in Spanish (e.g., "crema de cacahuete") as a string.

    Returns:
        The URL that was accessed as a string and navigates to the search results page.
    """
    from urllib.parse import quote
    
    encoded_name = quote(product_name)
    url = f"https://www.compraonline.alcampo.es/search?q={encoded_name}"
    go_to(url)
    
    return url

@tool
def go_back() -> None:
    """Goes back to previous page."""
    driver.back()

@tool
def close_popups() -> str:
    """
    Closes any visible modal or pop-up on the page. Use this to dismiss pop-up windows!
    This does not work on cookie consent banners.
    """
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

@tool
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from any PDF file.

    Args:
        pdf_path: Path to the PDF file to extract text from

    Returns:
        The extracted text content from the PDF as a string
    """
    import pypdf
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        return f"Error extracting text from PDF: {e}"
    return text

@tool
def search_youtube_videos(
    query: str,
    max_results: int = 10,
    video_duration: Optional[str] = None,
    order: Optional[str] = None,
    published_after: Optional[str] = None,
    safe_search: str = "none",
    language: Optional[str] = None,
    include_transcripts: bool = True, 
) -> List[Dict]:
    """
    Search YouTube for videos with optional filters, statistics, and transcripts.

    Args:
        query (str): Search query string.
        max_results (int): Maximum number of results to return (default 10).
        video_duration (Optional[str]): Filter by video duration; one of 'short', 'medium', 'long'.
        order (Optional[str]): Sort order; one of 'date', 'rating', 'relevance', 'title', 'viewCount'.
        published_after (Optional[str]): Restrict to videos published after this ISO 8601 timestamp (e.g., '2024-01-01T00:00:00Z').
        safe_search (str): Safe search setting; 'moderate', 'strict', or 'none' (default 'none').
        language (Optional[str]): Relevance language.
        include_transcripts (bool): Whether to fetch video transcripts using unofficial API.

    Returns:
        List[Dict]: A list of enriched video metadata dictionaries.
    """
    youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

    # Step 1: Search videos
    search_response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results,
        videoDuration=video_duration,
        order=order,
        publishedAfter=published_after,
        safeSearch=safe_search,
        relevanceLanguage=language
    ).execute()

    items = search_response.get("items", [])
    video_ids = [item["id"]["videoId"] for item in items]

    # Step 2: Fetch statistics
    stats_map = {}
    if video_ids:
        stats_response = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()
        for stat_item in stats_response.get("items", []):
            stats_map[stat_item["id"]] = stat_item.get("statistics", {})

    # Step 3: Fetch transcripts (optional)
    transcript_map = {}
    if include_transcripts:
        for vid in video_ids:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(vid)
                transcript_map[vid] = "\n".join([entry["text"] for entry in transcript])
            except (TranscriptsDisabled, NoTranscriptFound):
                transcript_map[vid] = None

    # Step 4: Merge data
    results = []
    for item in items:
        vid = item["id"]["videoId"]
        snippet = item["snippet"]
        result = {
            "video_id": vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "title": snippet["title"],
            "description": snippet["description"],
            "channel_title": snippet["channelTitle"],
            "published_at": snippet["publishedAt"],
            "thumbnails": snippet["thumbnails"],
            "statistics": stats_map.get(vid, {}),
        }
        if include_transcripts:
            result["transcript"] = transcript_map.get(vid)
        results.append(result)

    return results

@tool
def get_video_transcript(video_id: str) -> Optional[str]:
    """
    Get transcript text for a given YouTube video ID using youtube-transcript-api.

    Args:
        video_id (str): The unique video identifier on YouTube.

    Returns:
        Optional[str]: Full transcript text if available, or None.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([entry["text"] for entry in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

@tool
def watch_youtube_video(url: str, prompt: str) -> Optional[str]:
    """
    Watch a YouTube video and answer questions or analyze content based on the prompt.
    
    Args:
        url (str): The YouTube video URL to analyze
        prompt (str): Question or description of what to look for in the video
        
    Returns:
        Optional[str]: response about the video content, or None if analysis fails
    """
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        response = client.models.generate_content(
            model='models/gemini-2.0-flash',
            contents=types.Content(
                parts=[
                    types.Part(
                        file_data=types.FileData(file_uri=url),
                        video_metadata=types.VideoMetadata(fps=0.5),
                    ),
                    types.Part(text=prompt)
                ]
            )
        )
        
        return response.text
    except Exception as e:
        print(f"Error analyzing video: {str(e)}")
        return None
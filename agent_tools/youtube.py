import logging
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build as build_docs
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import os
from .config import Config

logger = logging.getLogger(__name__)

class YouTubeFetcher:
    """Handles YouTube playlist video retrieval and transcript fetching."""
    
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)
        logger.info("YouTubeFetcher initialized with YouTube Data API")
    
    def get_playlist_video_ids(self, playlist_id: str) -> List[str]:
        """
        Fetch all video IDs from a YouTube playlist.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            List of video IDs from the playlist
        """
        video_ids = []
        next_page_token = None
        
        try:
            while True:
                # Request playlist items
                request = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,  # Maximum allowed by API
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                # Extract video IDs from response
                for item in response['items']:
                    video_id = item['contentDetails']['videoId']
                    video_ids.append(video_id)
                
                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
                logger.info(f"Fetched {len(video_ids)} videos so far from playlist {playlist_id}")
            
            logger.info(f"Successfully fetched {len(video_ids)} total videos from playlist {playlist_id}")
            return video_ids
            
        except HttpError as e:
            logger.error(f"YouTube API error fetching playlist {playlist_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching playlist {playlist_id}: {e}")
            raise
    
    def fetch_transcript(self, video_id: str) -> Dict[str, any]:
        """
        Fetch transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with transcript data:
            - text: Full transcript text
            - language: Language code of transcript
            - status: 'available', 'unavailable', or 'error'
        """
        try:
            # Get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript first, then any available
            transcript = None
            language = None
            
            try:
                # Prefer English transcript
                transcript = transcript_list.find_transcript(['en'])
                language = 'en'
            except NoTranscriptFound:
                # Fall back to any available transcript
                try:
                    available_transcripts = list(transcript_list)
                    if available_transcripts:
                        transcript = available_transcripts[0]
                        language = transcript.language_code
                except Exception:
                    pass
            
            if transcript is None:
                logger.warning(f"No transcript found for video {video_id}")
                return {
                    'text': '',
                    'language': None,
                    'status': 'unavailable'
                }
            
            # Fetch the actual transcript
            transcript_data = transcript.fetch()
            
            # Combine all transcript segments into full text
            full_text = ' '.join([entry['text'] for entry in transcript_data])
            
            logger.info(f"Successfully fetched transcript for video {video_id} in language {language}")
            return {
                'text': full_text,
                'language': language,
                'status': 'available'
            }
            
        except TranscriptsDisabled:
            logger.warning(f"Transcripts disabled for video {video_id}")
            return {
                'text': '',
                'language': None,
                'status': 'unavailable'
            }
        except NoTranscriptFound:
            logger.warning(f"No transcript found for video {video_id}")
            return {
                'text': '',
                'language': None,
                'status': 'unavailable'
            }
        except VideoUnavailable:
            logger.warning(f"Video {video_id} is unavailable")
            return {
                'text': '',
                'language': None,
                'status': 'error'
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching transcript for video {video_id}: {e}")
            return {
                'text': '',
                'language': None,
                'status': 'error'
            }
    
    def store_raw_transcript_in_google_docs(self, video_id: str, transcript_text: str) -> Optional[str]:
        """
        Store raw transcript in Google Docs and return the document URL.
        
        Args:
            video_id: YouTube video ID
            transcript_text: Full transcript text
            
        Returns:
            Google Docs URL or None if failed
        """
        try:
            # Initialize Google Docs API
            # Note: This requires Google service account credentials
            # For now, we'll return a placeholder and log the action
            logger.info(f"Storing transcript for video {video_id} in Google Docs")
            logger.info(f"Transcript length: {len(transcript_text)} characters")
            
            # TODO: Implement actual Google Docs API integration
            # This would require:
            # 1. Service account credentials setup
            # 2. Google Docs API client initialization
            # 3. Document creation with transcript content
            # 4. Setting appropriate permissions
            
            # For now, return a placeholder URL
            placeholder_url = f"https://docs.google.com/document/d/placeholder_{video_id}"
            logger.info(f"Placeholder Google Docs URL created: {placeholder_url}")
            
            return placeholder_url
            
        except Exception as e:
            logger.error(f"Failed to store transcript in Google Docs for video {video_id}: {e}")
            return None

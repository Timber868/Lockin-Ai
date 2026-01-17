"""Text-to-Speech module using ElevenLabs API.

This module handles converting text input to audio output using ElevenLabs
text-to-speech service for the FocusAI system.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables from .env file
load_dotenv()

# Initialize ElevenLabs client
_api_key = os.getenv("ELEVENLABS_API_KEY")
if not _api_key:
    raise ValueError("ELEVENLABS_API_KEY not found in environment variables. Please check your .env file.")

_client = ElevenLabs(api_key=_api_key)

# Default voice ID (can be customized)
DEFAULT_VOICE_ID = "KD9g1wXK6axrG4J0LGFn"


def text_to_audio(
    text: str,
    output_path: Optional[str] = None,
    voice_id: str = DEFAULT_VOICE_ID
) -> str:
    """Convert text input to audio output using ElevenLabs.
    
    Args:
        text: Input text to convert to speech
        output_path: Optional path to save the audio file or directory.
                     If None, saves to 'audio' folder in project root.
                     If a directory, generates a filename with timestamp.
    
    Returns:
        Full file path where the audio was saved
    
    Raises:
        Exception: If text-to-speech conversion fails
    """
    # Determine output file path
    if output_path is None:
        # Default to 'audio' folder in project root
        output_dir = Path(__file__).parent.parent.parent / "audio"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"audio_{timestamp}.mp3"
    else:
        output_path = Path(output_path)
        # If output_path is a directory, generate filename
        if output_path.is_dir() or not output_path.suffix:
            output_path.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_path / f"audio_{timestamp}.mp3"
        else:
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert text to speech using ElevenLabs
    with _client.text_to_speech.with_raw_response.convert(
        text=text,
        voice_id=voice_id
    ) as response:
        # Get audio data from generator
        audio_data_generator = response.data
        audio_data = b"".join(audio_data_generator) if audio_data_generator else b""
    
    # Save audio file
    with open(output_path, "wb") as f:
        f.write(audio_data)
    
    # Return the full file path as string
    return str(output_path.resolve())


if __name__ == "__main__":
    # Example usage
    sample_text = "Hi!"
    audio_path = text_to_audio(sample_text, voice_id="Xb7hH8MSUJpSbSDYk0k2")
    print(f"Audio conversion completed. Saved to: {audio_path}")

"""Text-to-Speech module using ElevenLabs API.

This module handles converting text input to audio output using ElevenLabs
text-to-speech service for the FocusAI system.
"""

import os
from pathlib import Path
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
    file_name: str,
    directory: str = "default",
    voice_id: str = DEFAULT_VOICE_ID
) -> str:
    """Convert text input to audio output using ElevenLabs.
    
    Args:
        text: Input text to convert to speech
        file_name: Name of the audio file (without extension, will be saved as .mp3)
        directory: Subdirectory within reaction/audio/ to save the file.
                   Creates directory if it doesn't exist.
        voice_id: ElevenLabs voice ID to use for speech synthesis
    
    Returns:
        Full file path where the audio was saved (with version number if file exists)
    
    Raises:
        Exception: If text-to-speech conversion fails
    """
    # Base audio directory: reaction/audio/
    base_audio_dir = Path(__file__).parent / "audio"
    
    # Create directory structure: reaction/audio/{directory}/
    output_dir = base_audio_dir / directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure file_name has .mp3 extension (remove if already present, then add)
    file_name = file_name.replace(".mp3", "")
    base_file_path = output_dir / f"{file_name}.mp3"
    
    # Check if file exists and increment version if needed
    output_path = base_file_path
    version = 1
    while output_path.exists():
        version += 1
        output_path = output_dir / f"{file_name}_v{version}.mp3"
    
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
    sample_text = "Hello, this is the diddy boy test of the text-to-speech system."
    audio_path = text_to_audio(
        text=sample_text,
        file_name="test_audio",
        directory="flash mcqueen speech",
        voice_id=DEFAULT_VOICE_ID
    )
    print(f"Audio conversion completed. Saved to: {audio_path}")

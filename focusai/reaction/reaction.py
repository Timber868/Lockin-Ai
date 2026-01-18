"""Reaction module for generating character audio responses based on states.

This module handles creating audio files for different character reactions
based on user states (looking, up, down, at_your_phone).
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Handle imports for both module and direct execution
try:
    from .tts import text_to_audio
except ImportError:
    # If relative import fails, try absolute import (when run directly)
    import sys
    from pathlib import Path as PathLib
    # Add parent directories to path so we can import from focusai.reaction
    current_dir = PathLib(__file__).parent
    project_root = current_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    # Now try absolute import
    try:
        from focusai.reaction.tts import text_to_audio
    except ImportError:
        # Fallback: direct import from same directory
        from tts import text_to_audio

# Load environment variables
load_dotenv()

# Initialize ElevenLabs client for voice listing
_api_key = os.getenv("ELEVENLABS_API_KEY")
if not _api_key:
    raise ValueError("ELEVENLABS_API_KEY not found in environment variables. Please check your .env file.")

_client = ElevenLabs(api_key=_api_key)


class UserState(Enum):
    """Enumeration of possible user states that trigger character reactions."""
    LOOKING = "looking"
    UP = "up"
    DOWN = "down"
    AT_YOUR_PHONE = "at_your_phone"

def list_voices() -> List[Dict[str, Any]]:
    """List all available voices (including created ones).
    
    Returns:
        List of dictionaries containing voice information (voice_id, name, etc.)
    
    Example:
        >>> voices = list_voices()
        >>> for voice in voices:
        ...     print(f"{voice['name']}: {voice['voice_id']}")
    """
    try:
        response = _client.voices.get_all()
        
        voices = []
        if hasattr(response, 'voices'):
            for voice in response.voices:
                voices.append({
                    'voice_id': voice.voice_id if hasattr(voice, 'voice_id') else None,
                    'name': voice.name if hasattr(voice, 'name') else None,
                    'category': voice.category if hasattr(voice, 'category') else None,
                    'description': voice.description if hasattr(voice, 'description') else None,
                })
        
        return voices
    
    except Exception as e:
        raise Exception(f"Error listing voices: {str(e)}")

def get_voice_id_for_character_name(character_name: str) -> str:
    """Get the voice ID associated with a character name.
    
    Searches through available voices to find a match based on the character name.
    Matches are case-insensitive and allow partial matches.
    
    Args:
        character_name: Name of the character to search for
    
    Returns:
        ElevenLabs voice_id string for the character
    
    Raises:
        ValueError: If no voice is found matching the character name
    """
    # Get all available voices
    voices = list_voices()
    
    # Normalize character name for comparison (lowercase, remove spaces/underscores)
    normalized_character = character_name.lower().replace(" ", "").replace("_", "")
    
    # Search for matching voice
    for voice in voices:
        if voice.get('name'):
            # Normalize voice name for comparison
            normalized_voice_name = voice['name'].lower().replace(" ", "").replace("_", "")
            
            # Check for exact match or if character name is contained in voice name
            if (normalized_character == normalized_voice_name or 
                normalized_character in normalized_voice_name or
                normalized_voice_name in normalized_character):
                voice_id = voice.get('voice_id')
                if voice_id:
                    return voice_id
    
    # If no match found, raise an error
    available_names = [v.get('name', 'Unknown') for v in voices if v.get('name')]
    raise ValueError(
        f"No voice found matching character name '{character_name}'. "
        f"Available voices: {', '.join(available_names) if available_names else 'None'}"
    )

def get_voice_id_for_character(character_name: str) -> str:
    """Get the voice ID associated with a character name.
    
    TODO: Implement character to voice_id mapping.
    This function should return the ElevenLabs voice_id for the given character.
    
    Args:
        character_name: Name of the character
    
    Returns:
        ElevenLabs voice_id string for the character
    
    Raises:
        ValueError: If character_name is not found in the mapping
    """
    # TODO: Implement your character to voice_id mapping here
    # Example:
    # character_voices = {
    #     "flash_mcqueen": "Xb7hH8MSUJpSbSDYk0k2",
    #     "tarzan": "KD9g1wXK6axrG4J0LGFn",
    #     ...
    # }
    # return character_voices.get(character_name.lower())
    
    # Placeholder - replace with your implementation
    raise NotImplementedError("get_voice_id_for_character not yet implemented")


def generate_reactions(
    character_name: str,
    state_texts: Dict[UserState, str]
) -> Dict[UserState, str]:
    """Generate audio files for character reactions based on user states.
    
    This function takes a character name and a dictionary mapping states to
    text lines, generates audio for each state, and returns a dictionary
    mapping states to the generated audio file paths.
    
    Args:
        character_name: Name of the character (used for folder and voice selection)
        state_texts: Dictionary mapping UserState enum values to text lines
                    that the character should say for each state
    
    Returns:
        Dictionary mapping UserState to generated audio file paths
        (relative paths from project root or absolute paths)
    
    Raises:
        ValueError: If character_name doesn't have an associated voice_id
        Exception: If text-to-speech conversion fails for any state
    
    Example:
        >>> state_texts = {
        ...     UserState.LOOKING: "I see you're paying attention!",
        ...     UserState.UP: "Looking up at the ceiling?",
        ...     UserState.DOWN: "What's down there?",
        ...     UserState.AT_YOUR_PHONE: "Put that phone away!"
        ... }
        >>> audio_paths = generate_reactions("Flash McQueen", state_texts)
        >>> print(audio_paths[UserState.LOOKING])
        # "C:\\Users\\...\\focusai\\reaction\\audio\\flash mcqueen\\flash_mcqueen_looking.mp3"
    """
    # Get voice_id for the character
    try:
        voice_id = get_voice_id_for_character_name(character_name)
    except ValueError as e:
        raise ValueError(f"Failed to get voice_id for character '{character_name}': {e}")
    
    # Normalize character name for directory (lowercase, replace spaces)
    directory_name = character_name.lower().replace(" ", "_")
    
    # Dictionary to store state -> audio file path mappings
    state_audio_paths: Dict[UserState, str] = {}
    
    # Generate audio for each state
    for state, text in state_texts.items():
        # Create file name: {character}_{state}.mp3
        # Example: "flash_mcqueen_looking.mp3"
        file_name = f"{directory_name}_{state.value}"
        
        # Generate audio file using text_to_audio
        # Directory will be the character name (as provided)
        audio_path = text_to_audio(
            text=text,
            file_name=file_name,
            directory=character_name,
            voice_id=voice_id
        )
        
        # Store the path in the result dictionary
        state_audio_paths[state] = audio_path
    
    return state_audio_paths


if __name__ == "__main__":
    # Example usage
    state_texts = {
        UserState.LOOKING: "I see you're focused and paying attention!",
        UserState.UP: "What are you looking at up there? Is there a big penis dangling.",
        UserState.DOWN: "Is there something interesting down there? Is Jacob naked or something?",
        UserState.AT_YOUR_PHONE: "Hey! Put that phone away and focus! Gooning is bad for your health."
    }
    
    # Note: This will fail until get_voice_id_for_character is implemented
    try:
        audio_paths = generate_reactions("Shrek", state_texts)
        print("Generated audio files:")
        for state, path in audio_paths.items():
            print(f"  {state.value}: {path}")
    except NotImplementedError as e:
        print(f"Error: {e}")

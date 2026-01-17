"""Voice management module for creating and managing ElevenLabs voices."""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

# Initialize ElevenLabs client
_api_key = os.getenv("ELEVENLABS_API_KEY")
if not _api_key:
    raise ValueError("ELEVENLABS_API_KEY not found in environment variables. Please check your .env file.")

_client = ElevenLabs(api_key=_api_key)


def design_voice(
    voice_description: str,
    text: str,
    model_id: Optional[str] = "eleven_multilingual_ttv_v2"
) -> Dict[str, Any]:
    """Design a voice by describing it in text.
    
    This creates voice previews based on a text description. You get back
    one or more previews with generated_voice_id that you can then create.
    
    Args:
        voice_description: Text description of the voice (20-1000 characters).
                          Example: "A friendly narrator with a deep voice and slight echo"
        model_id: Optional model to use for voice design
    
    Returns:
        Dictionary with previews containing generated_voice_id and audio samples
    
    Example:
        >>> result = design_voice("A warm, friendly female voice with British accent")
        >>> preview_id = result['previews'][0]['generated_voice_id']
    """
    try:
        # Design voice using text-to-voice design endpoint
        response = _client.text_to_voice.design(
            voice_description=voice_description,
            text=text,
            model_id=model_id
        )
        
        # Convert response to dictionary format
        previews = []
        if hasattr(response, 'previews') and response.previews:
            for preview in response.previews:
                previews.append({
                    'generated_voice_id': preview.generated_voice_id if hasattr(preview, 'generated_voice_id') else None,
                    'audio': preview.audio if hasattr(preview, 'audio') else None,
                })
        
        return {
            'previews': previews,
            'model_id': model_id
        }
    
    except Exception as e:
        raise Exception(f"Error designing voice: {str(e)}")


def create_voice(
    voice_name: str,
    voice_description: str,
    generated_voice_id: str
) -> str:
    """Create a permanent voice from a generated preview.
    
    This converts a generated_voice_id (from design_voice) into a permanent
    voice_id that you can use for text-to-speech.
    
    Args:
        voice_name: Name for your voice (e.g., "MyCustomVoice")
        voice_description: Description of the voice
        generated_voice_id: The generated_voice_id from design_voice preview
    
    Returns:
        The permanent voice_id that can be used for text-to-speech
    
    Example:
        >>> voice_id = create_voice(
        ...     "MyFriendlyNarrator",
        ...     "A warm, friendly female voice",
        ...     preview_id
        ... )
    """
    try:
        response = _client.text_to_voice.create(
            voice_name=voice_name,
            voice_description=voice_description,
            generated_voice_id=generated_voice_id
        )
        
        # Extract voice_id from response
        if hasattr(response, 'voice_id'):
            return response.voice_id
        elif hasattr(response, 'voice') and hasattr(response.voice, 'voice_id'):
            return response.voice.voice_id
        else:
            # Try to get it from response data
            if isinstance(response, dict):
                return response.get('voice_id')
            raise ValueError("Could not extract voice_id from response")
    
    except Exception as e:
        raise Exception(f"Error creating voice: {str(e)}")


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


def get_voice_details(voice_id: str) -> Dict[str, Any]:
    """Get details about a specific voice.
    
    Args:
        voice_id: The voice ID to look up
    
    Returns:
        Dictionary with voice details (name, description, settings, etc.)
    """
    try:
        response = _client.voices.get(voice_id=voice_id)
        
        return {
            'voice_id': response.voice_id if hasattr(response, 'voice_id') else voice_id,
            'name': response.name if hasattr(response, 'name') else None,
            'category': response.category if hasattr(response, 'category') else None,
            'description': response.description if hasattr(response, 'description') else None,
            'settings': response.settings if hasattr(response, 'settings') else None,
        }
    
    except Exception as e:
        raise Exception(f"Error getting voice details: {str(e)}")


def create_voice_from_description(
    voice_name: str,
    voice_description: str,
    preview_index: int = 0
) -> str:
    """Complete workflow: design and create a voice in one step.
    
    This is a convenience function that combines design_voice and create_voice.
    
    Args:
        voice_name: Name for your voice
        voice_description: Text description of the voice (20-1000 characters)
        preview_index: Which preview to use if multiple are returned (default: 0)
    
    Returns:
        The permanent voice_id ready to use for text-to-speech
    
    Example:
        >>> voice_id = create_voice_from_description(
        ...     "FriendlyAssistant",
        ...     "A warm, cheerful female voice with American accent"
        ... )
        >>> # Now use voice_id in text_to_audio()
    """
    # Step 1: Design voice (get previews)
    design_result = design_voice(voice_description)
    
    if not design_result['previews']:
        raise ValueError("No voice previews generated. Try a different description.")
    
    if preview_index >= len(design_result['previews']):
        raise ValueError(f"Preview index {preview_index} out of range. Available: {len(design_result['previews'])}")
    
    # Get the generated_voice_id from selected preview
    generated_voice_id = design_result['previews'][preview_index]['generated_voice_id']
    
    if not generated_voice_id:
        raise ValueError("No generated_voice_id found in preview")
    
    # Step 2: Create permanent voice
    voice_id = create_voice(voice_name, voice_description, generated_voice_id)
    
    return voice_id


if __name__ == "__main__":
    # Example usage
    print("=== Creating a custom voice ===")
    
    text = "Mario the lovely plumber. Hes very italian. Whenever he speaks, he says 'Waluigi! first! If he ever mentions Waluigi, he says 'Waluigi! first! '"
    voice_description = "Mario the lovely plumber"
    design_voice_result, model_id = design_voice(text=text, voice_description=voice_description)
    print(f"Model ID: {model_id}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(__file__).parent.parent.parent / "audio" / f"audio_{timestamp}.mp3"
    with open(output_path, "wb") as f:
        f.write(design_voice_result)

    # Method 1: Complete workflow (design + create)
    # voice_id = create_voice_from_description(
    #     voice_name="TestVoice",
    #     voice_description="A friendly, energetic male voice with a slight accent"
    # )
    # print(f"Created voice with ID: {voice_id}")
    
    # # Method 2: Step by step (design first, then create)
    # # design_result = design_voice("A calm, soothing female voice")
    # # preview_id = design_result['previews'][0]['generated_voice_id']
    # # voice_id = create_voice("MyCalmVoice", "A calm, soothing female voice", preview_id)
    
    # # List all voices to see your new one
    # print("\n=== All available voices ===")
    # voices = list_voices()
    # for voice in voices:
    #     print(f"{voice['name']}: {voice['voice_id']}")

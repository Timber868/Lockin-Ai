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
        text: Text sample to use for voice generation
        model_id: Optional model to use for voice design
    
    Returns:
        Dictionary with previews containing generated_voice_id and audio samples
    
    Example:
        >>> result = design_voice(
        ...     "A warm, friendly female voice with British accent",
        ...     "Hello, this is a test of the voice"
        ... )
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
                # Try multiple ways to access audio data
                audio_data = None
                # Check for audio_base_64 (with underscore - as seen in debug output)
                if hasattr(preview, 'audio_base_64'):
                    audio_data = preview.audio_base_64
                elif hasattr(preview, 'audio_base64'):
                    audio_data = preview.audio_base64
                elif hasattr(preview, 'audio'):
                    audio_data = preview.audio
                elif hasattr(preview, 'audio_data'):
                    audio_data = preview.audio_data
                elif hasattr(preview, 'sample_audio'):
                    audio_data = preview.sample_audio
                # Check if it's a dict/object with audio field
                elif isinstance(preview, dict):
                    audio_data = preview.get('audio_base_64') or preview.get('audio_base64') or preview.get('audio') or preview.get('audio_data')
                
                previews.append({
                    'generated_voice_id': preview.generated_voice_id if hasattr(preview, 'generated_voice_id') else None,
                    'audio': audio_data,
                    '_preview_obj': preview,  # Keep original for debugging
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
        voice_name: Name for your voice (e.g., "Flash McQueen", "Tarzan")
        voice_description: Description of the voice
        generated_voice_id: The generated_voice_id from design_voice preview
    
    Returns:
        The permanent voice_id that can be used for text-to-speech
    
    Example:
        >>> voice_id = create_voice(
        ...     "FlashMcQueen",
        ...     "A fast-talking, energetic race car character",
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
    text: str,
    preview_index: int = 0,
    model_id: Optional[str] = "eleven_multilingual_ttv_v2"
) -> str:
    """Complete workflow: design and create a voice in one step.
    
    This is a convenience function that combines design_voice and create_voice.
    Use this to create a new character voice quickly.
    
    Args:
        voice_name: Name for your character voice (e.g., "Flash McQueen", "Tarzan")
        voice_description: Text description of the voice (20-1000 characters)
        text: Sample text to use for voice generation
        preview_index: Which preview to use if multiple are returned (default: 0)
        model_id: Optional model to use for voice design
    
    Returns:
        The permanent voice_id ready to use for text-to-speech
    
    Example:
        >>> voice_id = create_voice_from_description(
        ...     "FlashMcQueen",
        ...     "A fast-talking, energetic race car character with Italian accent",
        ...     "Ka-chow! I am speed! Lightning McQueen here!"
        ... )
        >>> # Now use voice_id in text_to_audio() or it will be found by get_voice_id_for_character_name()
    """
    # Step 1: Design voice (get previews)
    design_result = design_voice(voice_description, text, model_id)
    
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


def create_character_voice(
    character_name: str,
    character_description: str,
    sample_text: Optional[str] = None,
    preview_index: int = 0
) -> str:
    """Create a new character voice - simplified interface for character creation.
    
    This is a high-level function specifically for creating character voices.
    It provides default sample text if none is provided.
    
    Args:
        character_name: Name of the character (e.g., "Flash McQueen")
        character_description: Description of how the character should sound
                              (20-1000 characters)
        sample_text: Optional text sample. If None, uses a default based on character name
        preview_index: Which preview to use if multiple are returned (default: 0)
    
    Returns:
        The permanent voice_id for the created character
    
    Example:
        >>> voice_id = create_character_voice(
        ...     "Flash McQueen",
        ...     "A fast-talking, energetic race car character with Italian accent who says 'Ka-chow!'"
        ... )
        >>> print(f"Created character voice with ID: {voice_id}")
    """
    # Generate default sample text if none provided
    if sample_text is None:
        sample_text = f"Hello! I am {character_name}. This is what I sound like."
    
    # Create the voice
    voice_id = create_voice_from_description(
        voice_name=character_name,
        voice_description=character_description,
        text=sample_text,
        preview_index=preview_index
    )
    
    return voice_id


if __name__ == "__main__":
    # Example usage - Create a new character voice
    print("=== Creating a new character voice ===")
    
    # Example 1: Create character voice (simple method)
    # try:
    #     voice_id = create_character_voice(
    #         character_name="Flash McQueen",
    #         character_description="A fast-talking, energetic race car character with Italian accent",
    #         sample_text="Ka-chow! I am speed! Lightning McQueen here, ready to race!"
    #     )
    #     print(f"✓ Created character voice with ID: {voice_id}")
    # except Exception as e:
    #     print(f"✗ Error creating character voice: {e}")
    
    # # Example 2: List all available voices
    # print("\n=== All available voices ===")
    # try:
    #     voices = list_voices()
    #     for voice in voices:
    #         print(f"  {voice['name']}: {voice['voice_id']}")
    # except Exception as e:
    #     print(f"✗ Error listing voices: {e}")
    
    # Example 3: Step-by-step voice creation (more control)
    print("\n=== Step-by-step voice creation ===")
    try:
        # Step 1: Design voice (get previews)
        design_result = design_voice(
            voice_description="Scottish Mark.An unfriendly character with a deep Scottish accent. When he speaks hes basically screaming.",
            text="Hello! This is what I sound like. I have a Scottish accent and hate adventures! I live in a swamp and have a deep voice."
        )
        print(f"Generated {len(design_result['previews'])} preview(s)")
        
        # Save preview audio files so you can listen to them
        previews_dir = Path(__file__).parent / "audio" / "previews"
        previews_dir.mkdir(parents=True, exist_ok=True)
        
        saved_preview_files = []
        for i, preview in enumerate(design_result['previews']):
            audio_data = preview.get('audio')
            generated_voice_id = preview.get('generated_voice_id', 'unknown')
            preview_obj = preview.get('_preview_obj')
            
            # Debug: Print what we got
            print(f"\n  Preview {i} debug:")
            print(f"    generated_voice_id: {generated_voice_id}")
            print(f"    audio_data type: {type(audio_data)}")
            if preview_obj:
                print(f"    preview_obj attributes: {dir(preview_obj)}")
                # Try accessing audio directly from object
                if hasattr(preview_obj, 'audio'):
                    try:
                        audio_attr = getattr(preview_obj, 'audio')
                        print(f"    audio attribute type: {type(audio_attr)}")
                        if audio_attr and not audio_data:
                            audio_data = audio_attr
                    except Exception as e:
                        print(f"    Error accessing audio: {e}")
            
            if audio_data:
                # Handle different audio formats
                audio_bytes = None
                try:
                    if isinstance(audio_data, bytes):
                        # Direct bytes
                        audio_bytes = audio_data
                    elif isinstance(audio_data, str):
                        # Could be base64 or a path - try base64 first
                        import base64
                        try:
                            audio_bytes = base64.b64decode(audio_data)
                        except Exception:
                            # Maybe it's a URL or path?
                            print(f"    Audio is string but not base64: {audio_data[:50]}...")
                    elif hasattr(audio_data, 'read'):
                        # File-like object
                        audio_bytes = audio_data.read()
                    elif hasattr(audio_data, '__iter__') and not isinstance(audio_data, (str, bytes)):
                        # Generator or iterable - convert to bytes
                        audio_bytes = b"".join(audio_data)
                    else:
                        print(f"    Warning: Unknown audio format: {type(audio_data)}")
                except Exception as e:
                    print(f"    Error processing audio: {e}")
                
                if audio_bytes:
                    # Save preview file
                    preview_filename = f"preview_{i}_{generated_voice_id[:8] if generated_voice_id else 'unknown'}.mp3"
                    preview_path = previews_dir / preview_filename
                    
                    with open(preview_path, "wb") as f:
                        f.write(audio_bytes)
                    
                    saved_preview_files.append(str(preview_path))
                    print(f"  ✓ Saved preview {i} to: {preview_path}")
                else:
                    print(f"  ✗ Could not convert audio data to bytes for preview {i}")
            else:
                print(f"  ✗ No audio data found for preview {i}")
                # Try to get audio from preview object directly using text_to_speech with generated_voice_id
                if generated_voice_id:
                    print(f"    Attempting to generate audio sample using generated_voice_id...")
                    try:
                        # Use the local _client instead of importing from tts
                        # Try to generate a sample with the generated_voice_id
                        with _client.text_to_speech.with_raw_response.convert(
                            text="This is a preview of the generated voice.",
                            voice_id=generated_voice_id
                        ) as sample_response:
                            audio_generator = sample_response.data
                            audio_bytes = b"".join(audio_generator) if audio_generator else None
                            
                            if audio_bytes:
                                preview_filename = f"preview_{i}_{generated_voice_id[:8]}.mp3"
                                preview_path = previews_dir / preview_filename
                                
                                with open(preview_path, "wb") as f:
                                    f.write(audio_bytes)
                                
                                saved_preview_files.append(str(preview_path))
                                print(f"  ✓ Generated and saved preview {i} to: {preview_path}")
                    except Exception as e:
                        print(f"    Could not generate sample: {e}")
        
        if saved_preview_files:
            print(f"\nYou can now listen to {len(saved_preview_files)} preview file(s) at:")
            for path in saved_preview_files:
                print(f"  - {path}")
        
        # Step 2: Create voice from first preview (commented out - uncomment when ready to create)
        # if design_result['previews']:
        #     preview_id = design_result['previews'][0]['generated_voice_id']
        #     voice_id = create_voice(
        #         voice_name="ScottishAdventurer",
        #         voice_description="A friendly, energetic character with a Scottish accent",
        #         generated_voice_id=preview_id
        #     )
        #     print(f"\nCreated voice with ID: {voice_id}")
        
    except Exception as e:
        print(f"Error: {e}")

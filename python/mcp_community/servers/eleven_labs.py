"""An ElevenLabs MCP server for text-to-speech conversion."""

import base64
import io
import logging
import os
from typing import ClassVar

from mcp.server import FastMCP
from mcp.types import ImageContent, TextContent

try:
    # Import the ElevenLabs client
    from elevenlabs import VoiceSettings  # Ensure VoiceSettings is available
    from elevenlabs.client import ElevenLabs

    HAS_ELEVENLABS = True
except ImportError:
    HAS_ELEVENLABS = False
    from typing import Any

    ElevenLabs: Any = None  # Provide a dummy type for ElevenLabs
    VoiceSettings = None  # Ensure VoiceSettings is always bound

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ElevenLabs")


class ElevenLabsMCPFactory:
    """Factory for creating ElevenLabs MCP servers with configurable options."""

    # Default settings
    DEFAULT_API_KEY: ClassVar[str | None] = None
    DEFAULT_VOICE: ClassVar[str] = "Adam"
    DEFAULT_MODEL: ClassVar[str] = "eleven_multilingual_v2"
    DEFAULT_FORMAT: ClassVar[str] = "mp3_44100_128"  # Updated format specification
    DEFAULT_RETURN_AUDIO: ClassVar[bool] = True

    @classmethod
    def create(
        cls,
        api_key: str | None = DEFAULT_API_KEY,
        default_voice: str = DEFAULT_VOICE,
        default_model: str = DEFAULT_MODEL,
        output_format: str = DEFAULT_FORMAT,
        return_audio: bool = DEFAULT_RETURN_AUDIO,
        log_level: str = "INFO",
    ) -> FastMCP:
        """Create an ElevenLabs MCP server with configurable options."""
        if not HAS_ELEVENLABS:
            raise ImportError(
                "ElevenLabs package is not installed. "
                "Please install it with `pip install elevenlabs`."
            )

        # Configure logging
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Create a new MCP server
        mcp = FastMCP("ElevenLabs")

        # Check if API key is set
        if api_key:
            logger.info("ElevenLabs API key set")
        else:
            # Check environment variable
            api_key = os.environ.get("ELEVENLABS_API_KEY")
            if api_key:
                logger.info("ElevenLabs API key found in environment variables")
            else:
                logger.warning(
                    "No ElevenLabs API key provided. Using limited free tier."
                )

        @mcp.tool()
        def text_to_speech(
            text: str,
            voice: str = default_voice,
            model: str = default_model,
            output_format: str = output_format,
            stability: float = 0.5,
            similarity_boost: float = 0.75,
            style: float = 0.0,
            use_speaker_boost: bool = True,
        ) -> list[TextContent | ImageContent]:
            """Convert text to speech using ElevenLabs API.

            Executes text-to-speech conversion and returns generated audio data.
            """
            try:
                logger.info(f"Generating speech for text: {text[:50]}...")

                # Validate output format
                valid_formats = [
                    "mp3_22050_32",
                    "mp3_44100_32",
                    "mp3_44100_64",
                    "mp3_44100_96",
                    "mp3_44100_128",
                    "mp3_44100_192",
                    "pcm_8000",
                    "pcm_16000",
                    "pcm_22050",
                    "pcm_24000",
                    "pcm_44100",
                    "ulaw_8000",
                ]
                if output_format not in valid_formats:
                    logger.warning(
                        f"Invalid output format: {output_format}. Using default mp3_44100_128."
                    )
                    output_format = "mp3_44100_128"

                # Create ElevenLabs client (assumes proper API key)
                client = ElevenLabs(api_key=api_key)

                # Setup voice settings in the correct format for the SDK.
                # Always convert settings to a VoiceSettings instance.
                settings_dict = {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost,
                }
                if VoiceSettings is None:
                    raise RuntimeError("VoiceSettings is not available.")
                voice_settings = VoiceSettings(**settings_dict)

                # Generate audio using the convert method which returns a generator.
                audio_generator = client.text_to_speech.convert(
                    text=text,
                    voice_id=voice,
                    model_id=model,
                    voice_settings=voice_settings,
                    output_format=output_format,
                )

                # Collect audio data from the generator
                audio_data = b""
                try:
                    for chunk in audio_generator:
                        audio_data += chunk
                except Exception as e:
                    logger.error(f"Error collecting audio data: {e}")
                    return [
                        TextContent(
                            type="text", text=f"Error collecting audio data: {e}"
                        )
                    ]

                # Save audio data to an in-memory buffer
                buffer = io.BytesIO(audio_data)
                buffer.seek(0)

                # Prepare response result
                result: list[TextContent | ImageContent] = [
                    TextContent(
                        type="text",
                        text=f"Successfully generated audio from text ({len(buffer.getvalue())} bytes)",
                    )
                ]
                if return_audio:
                    # Determine MIME type based on output format
                    mime_type = f"audio/{output_format}"
                    audio_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    result.append(
                        ImageContent(
                            type="image", data=audio_base64, mimeType=mime_type
                        )
                    )
                return result

            except Exception as e:
                logger.error(f"Error generating speech: {str(e)}")
                return [
                    TextContent(type="text", text=f"Error generating speech: {str(e)}")
                ]

        @mcp.tool()
        def list_voices() -> str:
            """List all available voices from ElevenLabs."""
            try:
                logger.info("Fetching available voices")
                client = ElevenLabs(api_key=api_key)
                voice_response = client.voices.get_all()
                voices_list = voice_response.voices  # List of Voice objects

                result = "Available Voices:\n\n"
                for voice in voices_list:
                    result += f"Name: {getattr(voice, 'name', 'Unknown')}\n"
                    result += f"Voice ID: {getattr(voice, 'voice_id', 'Unknown')}\n"
                    if getattr(voice, "description", None):
                        result += f"Description: {voice.description}\n"
                    if getattr(voice, "preview_url", None):
                        result += f"Preview URL: {voice.preview_url}\n"
                    if hasattr(voice, "category"):
                        result += f"Category: {voice.category}\n"
                    if getattr(voice, "labels", None):
                        labels = voice.labels
                        if isinstance(labels, dict):
                            result += f"Labels: {', '.join(f'{k}: {v}' for k, v in labels.items())}\n"
                        else:
                            result += f"Labels: {labels}\n"
                    result += "\n"
                return result

            except Exception as e:
                logger.error(f"Error listing voices: {str(e)}")
                return f"Error listing voices: {str(e)}"

        @mcp.tool()
        def get_models() -> str:
            """List all available text-to-speech models."""
            try:
                logger.info("Fetching available models")
                client = ElevenLabs(api_key=api_key)
                models_list = client.models.get_all()

                result = "Available Models:\n\n"
                for model in models_list:
                    result += f"Model ID: {model.model_id}\n"
                    result += f"Name: {model.name}\n"
                    if getattr(model, "description", None):
                        result += f"Description: {model.description}\n"
                    if model.token_cost_factor is not None:
                        if isinstance(model.token_cost_factor, dict):
                            result += f"  - Input: {model.token_cost_factor.get('input', 'N/A')}\n"
                            result += f"  - Output: {model.token_cost_factor.get('output', 'N/A')}\n"
                        else:
                            result += f"Token Cost Factor: {model.token_cost_factor}\n"
                    result += "\n"
                return result

            except Exception as e:
                logger.error(f"Error listing models: {str(e)}")
                return f"Error listing models: {str(e)}"

        @mcp.tool()
        def get_user_info() -> str:
            """Get user subscription information."""
            try:
                logger.info("Fetching user subscription info")
                client = ElevenLabs(api_key=api_key)
                user = client.user.get()
                subscription = client.user.get_subscription()

                result = "User Information:\n\n"
                result += f"User ID: {user.user_id}\n"
                result += f"First Name: {getattr(user, 'first_name', 'N/A')}\n"
                result += f"Last Name: {getattr(user, 'last_name', 'N/A')}\n"
                result += f"Email: {getattr(user, 'email', 'N/A')}\n\n"
                result += "Subscription:\n"
                if hasattr(subscription, "tier"):
                    result += f"Tier: {subscription.tier}\n"
                if hasattr(subscription, "character_limit"):
                    result += f"Character limit: {subscription.character_limit}\n"
                if hasattr(subscription, "character_count"):
                    result += f"Character count: {subscription.character_count}\n"
                if hasattr(subscription, "next_character_count_reset_unix"):
                    result += (
                        f"Reset at: {subscription.next_character_count_reset_unix}\n"
                    )
                return result

            except Exception as e:
                logger.error(f"Error getting user info: {str(e)}")
                return f"Error getting user info: {str(e)}"

        @mcp.tool()
        def get_voice_info(voice_name_or_id: str) -> str:
            """Get detailed information about a specific voice."""
            try:
                logger.info(f"Fetching info for voice: {voice_name_or_id}")
                client = ElevenLabs(api_key=api_key)
                try:
                    specific_voice = client.voices.get(voice_id=voice_name_or_id)
                    if specific_voice:
                        selected_voice = specific_voice
                    else:
                        raise Exception("Voice not found via direct lookup")
                except Exception:
                    voice_response = client.voices.get_all()
                    voices_list = getattr(voice_response, "voices", [])
                    selected_voice = None
                    for voice in voices_list:
                        if (voice_name_or_id == voice.name) or (
                            voice_name_or_id == voice.voice_id
                        ):
                            selected_voice = voice
                            break
                    if not selected_voice and voices_list:
                        for voice in voices_list:
                            if (
                                getattr(voice, "name", "")
                                .lower()
                                .find(voice_name_or_id.lower())
                                != -1
                            ):
                                selected_voice = voice
                                break

                if not selected_voice:
                    return f"Voice '{voice_name_or_id}' not found. Use list_voices to see available voices."

                result = (
                    f"Voice Details for {getattr(selected_voice, 'name', 'Unknown')} "
                    f"({getattr(selected_voice, 'voice_id', 'Unknown')}):\n\n"
                )
                if getattr(selected_voice, "description", None):
                    result += f"Description: {selected_voice.description}\n"
                if hasattr(selected_voice, "category"):
                    result += f"Category: {selected_voice.category}\n"
                if getattr(selected_voice, "preview_url", None):
                    result += f"Preview URL: {selected_voice.preview_url}\n"
                if selected_voice.fine_tuning is not None:
                    allowed = getattr(selected_voice.fine_tuning, "allowed", None)
                    if allowed is not None:
                        result += f"Fine-tuning allowed: {allowed}\n"
                if getattr(selected_voice, "labels", None):
                    result += "Labels:\n"
                    try:
                        for key, value in selected_voice.labels.items():
                            result += f"  - {key}: {value}\n"
                    except Exception:
                        result += f"  {selected_voice.labels}\n"
                if hasattr(selected_voice, "samples"):
                    try:
                        num_samples = (
                            len(selected_voice.samples) if selected_voice.samples else 0
                        )
                        result += f"Voice samples: {num_samples} available\n"
                    except Exception:
                        result += "Voice samples: Information unavailable\n"
                return result

            except Exception as e:
                logger.error(f"Error getting voice info: {str(e)}")
                return f"Error getting voice info: {str(e)}"

        logger.info("ElevenLabs MCP server created successfully")
        return mcp

    # End of create()


# Create default instance with standard configuration
if HAS_ELEVENLABS:
    mcp = ElevenLabsMCPFactory.create()
    ElevenLabsMCP = mcp
else:
    # Create a dummy MCP that raises an error when used
    ElevenLabsMCP = FastMCP("ElevenLabs")

    @ElevenLabsMCP.tool()
    def elevenlabs_not_installed() -> str:
        """Inform the user that the ElevenLabs package is not installed."""
        return "The ElevenLabs package is not installed. Please install it with `pip install elevenlabs`."


__all__ = ["ElevenLabsMCP", "ElevenLabsMCPFactory"]

if __name__ == "__main__":
    from mcp_community import run_mcp

    run_mcp(ElevenLabsMCP)

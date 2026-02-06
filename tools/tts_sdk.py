"""TTS tool for converting text to speech.

Demonstrates a simple, single-file tool implementation.

Authors:
    GDP Labs
"""

from typing import Any, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from gl_speech_sdk import SpeechClient

import os

class TTSConfig(BaseModel):
    """Config schema for the TTS tool."""

    tts_base_url: str = Field(default="", description="The base URL for the TTS API")
    tts_api_key: str = Field(default="", description="The API key for the TTS API")
    model: str = Field(default="tts-dimas-formal", description="The model to use for the TTS API")
    wait: bool = Field(default=True, description="Whether to wait for the TTS API to complete")

class TTSInput(BaseModel):
    """Input schema for the TTS tool."""

    text: str = Field(description="The text to convert to speech")


class TTSTool(BaseTool):
    """Tool for converting text to speech."""

    name: str = "tts-test"
    description: str = "Converts text to speech."
    args_schema: type[BaseModel] = TTSInput
    tool_config_schema: type[BaseModel] = TTSConfig
    tool_config: TTSConfig = Field(default_factory=TTSConfig)

    def __init__(self, config: Optional[TTSConfig] = None, **kwargs: Any):
        super().__init__(**kwargs)
        if config:
            self.tool_config = config
        else:
            # Provide fallbacks to prevent NoneType errors during server-side validation
            self.tool_config = TTSConfig(
                tts_base_url=os.getenv("TTS_BASE_URL", ""),
                tts_api_key=os.getenv("TTS_API_KEY", ""),
                model=os.getenv("TTS_MODEL", "tts-dimas-formal"),
                # Convert string env var to actual boolean
                wait=str(os.getenv("TTS_WAIT", "True")).lower() == "true",
            )

    def _run(self, text: str, **kwargs: Any) -> str:
        """Convert speech to text.

        Args:
            audio_file: The audio file to convert to text.
            **kwargs: Additional execution arguments.

        Returns:
            Text string.
        """

        try:
            tts_client = SpeechClient(api_key=self.tool_config.tts_api_key,
                base_url=self.tool_config.tts_base_url
            )
            response_result = tts_client.tts.synthesize(
                text=text,
                model=self.tool_config.model,
                wait=self.tool_config.wait
            )
            return response_result.result
        except Exception as e:
            return f"Error processing audio: {str(e)}"


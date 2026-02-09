"""TTS tool for converting text to speech.

Demonstrates a simple, single-file tool implementation.

Authors:
    GDP Labs
"""

from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
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

    def _run(self, text: str, config: RunnableConfig = None, **kwargs: Any) -> str:
        """Convert speech to text.

        Args:
            audio_file: The audio file to convert to text.
            **kwargs: Additional execution arguments.

        Returns:
            Text string.
        """

        try:
            tool_config = self.get_tool_config(config)
            if (tool_config.tts_base_url == "" or tool_config.tts_api_key == ""):
                return "Error: TTS base URL or API key is not set"
            else:
                tts_client = SpeechClient(api_key=tool_config.tts_api_key,
                    base_url=tool_config.tts_base_url
                )
                response_result = tts_client.tts.synthesize(
                    text=text,
                    model=tool_config.model,
                    wait=tool_config.wait,
                    as_signed_url=True
                )
                return response_result.result
        except Exception as e:
            return f"Error processing audio: {str(e)}"


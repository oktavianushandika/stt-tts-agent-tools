"""STT tool for converting speech to text.

Demonstrates a simple, single-file tool implementation.

Authors:
    GDP Labs
"""

from typing import Any

from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from gl_speech_sdk import SpeechClient

import base64

class STTConfig(BaseModel):
    """Config schema for the STT tool."""

    stt_base_url: str = Field(default="", description="The base URL for the STT API")
    stt_api_key: str = Field(default="", description="The API key for the STT API")
    model: str = Field(default="stt-general", description="The model to use for the STT API")
    wait: bool = Field(default=True, description="Whether to wait for the STT API to complete")

class STTInput(BaseModel):
    """Input schema for the STT tool."""

    audio_file: bytes = Field(description="The audio file to convert to text")


class STTTool(BaseTool):
    """Tool for converting speech to text."""

    name: str = "stt-test"
    description: str = "Converts speech to text."
    args_schema: type[BaseModel] = STTInput
    tool_config_schema: type[BaseModel] = STTConfig


    def convert_to_base64(self, audio_file: bytes) -> str:
        """Convert audio to base64 format."""
        return base64.b64encode(open(audio_file, "rb").read()).decode("utf-8")

    def _run(self, audio_file: bytes, config: RunnableConfig = None, **kwargs: Any) -> str:
        """Convert speech to text.

        Args:
            audio_file: The audio file to convert to text.
            **kwargs: Additional execution arguments.

        Returns:
            Text string.
        """

        try:
            tool_config = self.get_tool_config(config)
            if (tool_config.stt_base_url == "" or tool_config.stt_api_key == ""):
                return "Error: STT base URL or API key is not set"
            else:
                base64_audio = self.convert_to_base64(audio_file)

                stt_client = SpeechClient(api_key=tool_config.stt_api_key,
                    base_url=tool_config.stt_base_url
                )
                response_result = stt_client.stt.transcribe(
                    data=base64_audio,
                    model=tool_config.model,
                    wait=tool_config.wait
                )
                
                return response_result.result
        except Exception as e:
            return f"Error processing audio: {str(e)}"


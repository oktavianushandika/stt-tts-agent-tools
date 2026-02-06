"""STT tool for converting speech to text.

Demonstrates a simple, single-file tool implementation.

Authors:
    GDP Labs
"""

from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

import os
import base64
import requests

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
    args_schema: Type[BaseModel] = STTInput
    tool_config_schema: Type[BaseModel] = STTConfig
    tool_config: STTConfig = Field(default_factory=STTConfig)

    def __init__(self, config: Optional[STTConfig] = None, **kwargs: Any):
        super().__init__(**kwargs)
        if config:
            self.tool_config = config
        else:
            # Provide fallbacks to prevent NoneType errors during server-side validation
            self.tool_config = STTConfig(
                stt_base_url=os.getenv("STT_BASE_URL", ""),
                stt_api_key=os.getenv("STT_API_KEY", ""),
                model=os.getenv("STT_MODEL", "stt-general"),
                # Convert string env var to actual boolean
                wait=str(os.getenv("STT_WAIT", "True")).lower() == "true",
            )

    def convert_to_base64(self, audio_file: bytes) -> str:
        """Convert audio to base64 format."""
        return base64.b64encode(audio_file).decode("utf-8")

    def _run(self, audio_file: bytes, **kwargs: Any) -> str:
        """Convert speech to text.

        Args:
            audio_file: The audio file to convert to text.
            **kwargs: Additional execution arguments.

        Returns:
            Text string.
        """

        try:
            base64_audio = self.convert_to_base64(audio_file)

            payload = {
                "config": {
                    "engine": self.tool_config.model or "stt-general", 
                    "wait": str(self.tool_config.wait).lower() == "true",
                    "speaker_count": 1,
                    "include_filler": "false",
                    "include_partial_results": "false",
                    "auto_punctuation": "false",
                    "enable_spoken_numerals": "false",
                    "enable_speech_insights": "false",
                    "enable_voice_insights": "false"
                },
                "request": {
                    "label": "stt-test-job",
                    "data": base64_audio
                }
            }

            response = requests.post(
                self.tool_config.stt_base_url, 
                json=payload, 
                headers={"x-api-key": self.tool_config.stt_api_key},
                timeout=30 # Good practice to add a timeout
            )
            
            response.raise_for_status() # Raise error for bad status codes
            return response.json().get("result", "No result found")
            
        except Exception as e:
            return f"Error processing audio: {str(e)}"


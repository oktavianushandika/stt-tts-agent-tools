"""TTS tool for converting text to speech.

Demonstrates a simple, single-file tool implementation.

Authors:
    GDP Labs
"""

from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

import os
import requests

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
    args_schema: Type[BaseModel] = TTSInput
    tool_config_schema: Type[BaseModel] = TTSConfig
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
        """Convert text to speech.

        Args:
            text: The text to convert to speech.
            **kwargs: Additional execution arguments.

        Returns:
            Speech audio URL string.
        """

        try:
            url = f"{self.tool_config.tts_base_url}?as_signed_url=true"
            api_key = self.tool_config.tts_api_key

            payload = {
                "config": {
                    "model": self.tool_config.model,
                    "wait": self.tool_config.wait,
                    "pitch": 0,
                    "tempo": 1,
                    "audio_format": "opus",
                    "sample_rate": 16000
                },
                "request": {
                    "label": "tts-test-job",
                    "text": text
                }
            }

            response = requests.post(url, json=payload, headers={"x-api-key": api_key})
            job = response.json()

            if job["status"] == "complete":
                return job["result"]["path"]
            else:
                return f"Error processing audio: {job['error']}"
        except Exception as e:
            return f"Error processing audio: {str(e)}"


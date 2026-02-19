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
from aip_agents.utils import LoggerManager

import time

logger = LoggerManager.get_logger(__name__)

class TTSConfig(BaseModel):
    """Config schema for the TTS tool."""

    tts_base_url: str = Field(default="", description="The base URL for the TTS API")
    tts_api_key: str = Field(default="", description="The API key for the TTS API")
    model: str = Field(default="tts-dimas-formal", description="The model to use for the TTS API")
    wait: bool = Field(default=True, description="Whether to wait for the TTS API to complete")

class TTSInput(BaseModel):
    """Input schema for the TTS tool."""

    text: str = Field(description="The text to convert to speech")
    model: Optional[str] = Field(
        default=None,
        description="The TTS model to use. Options: 'tts-dimas-formal' (male voice) or 'tts-ocha-gentle' (female voice). If not specified, uses the default model from config."
    )


class TTSTool(BaseTool):
    """Tool for converting text to speech."""

    name: str = "tts-test"
    description: str = """Converts text to speech. 
    Supports both male voice (tts-dimas-formal) and female voice (tts-ocha-gentle).
    You can specify the model parameter to choose the voice type."""
    args_schema: type[BaseModel] = TTSInput
    tool_config_schema: type[BaseModel] = TTSConfig

    def _run(self, text: str, config: RunnableConfig = None, **kwargs: Any) -> str:
        """Convert text to speech.

        Args:
            text: The text to convert to speech.
            model: Optional model to use. If not specified, uses config default.
            config: Runtime configuration.
            **kwargs: Additional execution arguments.

        Returns:
            S3 URL to the generated audio file.
        """

        try:
            tool_config = self.get_tool_config(config)
            if (tool_config.tts_base_url == "" or tool_config.tts_api_key == ""):
                return "Error: TTS base URL or API key is not set"
            
            # Use the model parameter if provided, otherwise use config default
            selected_model = kwargs.get("model") if kwargs.get("model") is not None else tool_config.model
            
            tts_client = SpeechClient(
                api_key=tool_config.tts_api_key,
                base_url=tool_config.tts_base_url
            )
            result = tts_client.tts.synthesize(
                text=text,
                model=selected_model,
                wait=False,
                audio_format="mp3"
            )

            job_id = result.job_id

            while True:
                status = tts_client.tts.get_job(job_id)

                if status.status.lower() == "complete" or status.status.lower() == "failed":
                    break

                time.sleep(5)

            job_response = tts_client.tts.get_job(job_id=job_id, as_signed_url=True)

            return job_response.result.path
        except Exception as e:
            logger.error(f"Error in TTS tool: {str(e)}")
            return f"Error processing audio: {str(e)}"


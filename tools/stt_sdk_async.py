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

import time

class STTConfig(BaseModel):
    """Config schema for the STT tool."""

    stt_base_url: str = Field(default="", description="The base URL for the STT API")
    stt_api_key: str = Field(default="", description="The API key for the STT API")
    model: str = Field(default="stt-general", description="The model to use for the STT API")
    wait: bool = Field(default=True, description="Whether to wait for the STT API to complete")

class STTInput(BaseModel):
    """Input schema for the STT tool."""

    uri: str = Field(description="The URI of the audio file")


class STTTool(BaseTool):
    """Tool for converting speech to text."""

    name: str = "stt-test"
    description: str = "Converts speech to text."
    args_schema: type[BaseModel] = STTInput
    tool_config_schema: type[BaseModel] = STTConfig

    def _run(self, uri: str, config: RunnableConfig = None, **kwargs: Any) -> str:
        """Convert speech to text.

        Args:
            uri: The URI of the audio file.
            **kwargs: Additional execution arguments.

        Returns:
            Text string.
        """

        try:
            tool_config = self.get_tool_config(config)
            if (tool_config.stt_base_url == "" or tool_config.stt_api_key == ""):
                return "Error: STT base URL or API key is not set"
            else:
                stt_client = SpeechClient(api_key=tool_config.stt_api_key,
                    base_url=tool_config.stt_base_url
                )
                result = stt_client.stt.transcribe(
                    model=tool_config.model,
                    wait=False,
                    uri=uri,
                    include_filler=True,
                    include_partial_results=True,
                    auto_punctuation=True
                )
                job_id = result.job_id

                while True:
                    status = stt_client.stt.get_job(job_id)

                    if status.status.lower() == "complete" or status.status.lower() == "failed":
                        break;
                    time.sleep(5)

                job_response = stt_client.stt.get_job(job_id)

                if hasattr(job_response, 'result') and hasattr(job_response.result, 'data'):
                    all_segments = job_response.result.data
                    
                    clean_transcripts = [
                        segment.transcript 
                        for segment in all_segments 
                        if segment.channel == 0
                    ]
                    
                    full_transcript = " ".join(clean_transcripts)
                    
                    return full_transcript
                else:
                    return "No transcript data found in the result."
        except Exception as e:
            return f"Error processing audio: {str(e)}"


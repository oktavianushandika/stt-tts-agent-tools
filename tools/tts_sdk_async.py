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
from aip_agents.utils.artifact_helpers import create_artifact_response

import os
import time
import base64
import uuid

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
    _output_dir: str = "/tmp/tts_output"

    def _get_latest_file_in_directory(self) -> Optional[str]:
        """Get the most recently modified file in the output directory.

        Returns:
            Optional[str]: Path to the latest file, or None if no files exist
        """
        try:
            if not os.path.exists(self._output_dir):
                logger.debug(f"Output directory does not exist: {self._output_dir}")
                return None
                
            current_files = os.listdir(self._output_dir)
            
            # Get full paths for files only (not directories)
            files = [
                os.path.join(self._output_dir, f)
                for f in current_files
                if os.path.isfile(os.path.join(self._output_dir, f))
            ]
            
            if not files:
                logger.debug("No files found in output directory")
                return None
            
            # Return the most recently MODIFIED file (not created)
            latest_file = max(files, key=os.path.getmtime)
            logger.debug(f"Found latest file: {latest_file}")
            return latest_file
        except Exception as e:
            logger.warning(f"Failed to get latest file: {e}")
            return None

    def _handle_file_artifact(self, execution_result: str) -> Optional[dict[str, Any]]:
        """Create artifact response from generated file if one exists.

        Args:
            execution_result: The result from code execution

        Returns:
            A dictionary from create_artifact_response or None
        """
        latest_file = self._get_latest_file_in_directory()
        
        if not latest_file:
            logger.debug("No files found in output directory")
            return None

        try:
            # Read the file as binary
            with open(latest_file, "rb") as f:
                file_bytes = f.read()
            
            if not file_bytes:
                logger.warning(f"File {latest_file} is empty")
                return None
            
            filename = os.path.basename(latest_file)
            logger.debug(f"Creating artifact from file: {filename} ({len(file_bytes)} bytes)")
            
            # Create artifact response
            result = create_artifact_response(
                result=execution_result or f"File generated successfully: {filename}",
                artifact_data=file_bytes,
                artifact_name=filename,
                artifact_description=f"Generated file: {filename}",
            )
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to create artifact from file {latest_file}: {e}")
            return None
        finally:
            # Clean up the file after creating the artifact
            try:
                if os.path.exists(latest_file):
                    os.remove(latest_file)
                    logger.debug(f"Cleaned up file: {latest_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up file {latest_file}: {e}")

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
            
            # Ensure output directory exists
            os.makedirs(self._output_dir, exist_ok=True)
            
            # Use the model parameter if provided, otherwise use config default
            selected_model = kwargs.get("model") if kwargs.get("model") is not None else tool_config.model
            
            tts_client = SpeechClient(
                api_key=tool_config.tts_api_key,
                base_url=tool_config.tts_base_url
            )
            result = tts_client.tts.synthesize(
                text=text,
                model=selected_model,
                wait=False
            )

            job_id = result.job_id

            while True:
                status = tts_client.tts.get_job(job_id)

                if status.status.lower() == "complete" or status.status.lower() == "failed":
                    break

                time.sleep(5)

            job_response = tts_client.tts.get_job(job_id)
            
            if job_response.status.lower() == "failed":
                return f"Error: TTS job failed with status: {job_response.status}"

            base64_audio = job_response.result.data

            audio_bytes = base64.b64decode(base64_audio)
            
            # Generate unique filename
            unique_filename = f"output_audio_{uuid.uuid1()}.mp3"
            local_file_path = os.path.join(self._output_dir, unique_filename)
            
            # Write audio to file
            with open(local_file_path, "wb") as audio_file:
                audio_file.write(audio_bytes)

            # Create artifact from the local file we just created
            file_artifact = self._handle_file_artifact(f"Audio generated successfully using {selected_model}")
            
            if file_artifact:
                return file_artifact
            else:
                return f"Audio generated but failed to create artifact. Local file: {local_file_path}"
                
        except Exception as e:
            logger.error(f"Error in TTS tool: {str(e)}")
            return f"Error processing audio: {str(e)}"


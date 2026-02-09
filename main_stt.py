"""Speech to Text Assistant - Modular Tool Integration.

Authors:
    GDP Labs
"""
import os
from glaip_sdk import Agent
from tools.stt_sdk import STTTool
from dotenv import load_dotenv

load_dotenv(override=True)


def main():
    """Run speech to text assistant with modular tools."""
    
    agent = Agent(
        name="stt-test-agent",
        instruction="""You are a speech to text assistant.
        Use the available tools to help users with speech to text conversion.
        When the user provides an audio file, use the stt tool to convert it directly to base64 format first,
        then use the stt tool to convert the base64 format to text.
        If you have trouble accessing the audio file, immediately use local path provided or try fetch it from the provided s3 URL if there is any.
        The audio file is provided in the files parameter.
        Use the direct local path of the audio file in /tmp/agent_files_<random_string>/<random_string>/<audio_file> for the audio file.
        If the audio is uploaded to s3 bucket, use the s3 path for the audio file.
        Example:
        /tmp/agent_files_<random_string>/<random_string>/<audio_file>
        s3://<bucket_name>/<audio_file>
        The audio file is provided in the files parameter.
        
        If there is any error, show the error message to the user.""",
        tools=[STTTool],
        tool_configs={
            STTTool: {
                "stt_base_url": os.getenv("STT_BASE_URL", ""),
                "stt_api_key": os.getenv("STT_API_KEY", ""),
                "model": "stt-general",
                "wait": "True",
            }
        },
        model="google/gemini-2.5-flash",
    )

    agent.deploy()

    response = agent.run("""
    Help me convert the attached audio file to text.
    """, files=["audio/audio.webm"])
    print(response)


if __name__ == "__main__":
    main()

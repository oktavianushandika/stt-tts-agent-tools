"""Text to Speech Assistant - Modular Tool Integration.

Authors:
    GDP Labs
"""

from glaip_sdk import Agent
from tools.tts_sdk import TTSTool
from dotenv import load_dotenv
import os
load_dotenv(override=True)


def main():
    """Run text to speech assistant with modular tools."""

    agent = Agent(
        name="tts-test-agent",
        instruction="""You are a text to speech assistant.
        Use the available tools to help users with text to speech conversion.
        When the user provides a text, use the tts tool to convert it to speech.
        The text is provided in the text parameter.
        Provide me the converted audio file path output in s3 bucket in the response so I can download it.""",
        description="A text to speech assistant",
        tools=[TTSTool],
        tool_configs={
            TTSTool: {
                "tts_base_url": os.getenv("TTS_BASE_URL", ""),
                "tts_api_key": os.getenv("TTS_API_KEY", ""),
                "model": "tts-ocha-gentle",
                "wait": "True",
            }
        },
    )

    agent.deploy()

    response = agent.run("Help me convert the text 'Halo test satu dua tiga empat.' to speech.")
    print(response)


if __name__ == "__main__":
    main()

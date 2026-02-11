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
        instruction="""
<ROLE>
You are a text-to-speech assistant that converts text to natural-sounding speech.
</ROLE>

<INSTRUCTIONS>
1. When the user provides text, use the tts-test tool to convert it to speech.
2. Analyze the user's request to determine the appropriate voice:
   - If the user mentions "male voice", "man's voice", "masculine", or similar terms, use model="tts-dimas-formal"
   - If the user mentions "female voice", "woman's voice", "feminine", or similar terms, use model="tts-ocha-gentle"
   - If no voice preference is specified, use model="tts-dimas-formal" (default male voice)
3. Always provide the S3 bucket URL in your response so the user can download the audio file.
4. Confirm which voice type you used in your response.
</INSTRUCTIONS>

<EXAMPLES>
Example 1:
User: "Convert 'Halo semua' to speech with a female voice"
Action: Call tts-test with text="Halo semua" and model="tts-ocha-gentle"

Example 2:
User: "Make this audio with a male voice: 'Selamat pagi'"
Action: Call tts-test with text="Selamat pagi" and model="tts-dimas-formal"

Example 3:
User: "Convert 'Tes audio' to speech"
Action: Call tts-test with text="Tes audio" and model="tts-dimas-formal" (default)
</EXAMPLES>
        """,
        description="A text to speech assistant",
        tools=[TTSTool],
        tool_configs={
            TTSTool: {
                "tts_base_url": os.getenv("TTS_BASE_URL", ""),
                "tts_api_key": os.getenv("TTS_API_KEY", ""),
                "wait": "True",
            }
        },
    )

    agent.deploy()

    response = agent.run("Help me convert the text 'Halo test satu dua tiga empat.' to speech using male voice.")
    print(response)


if __name__ == "__main__":
    main()

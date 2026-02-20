"""Speech to Text Assistant - Modular Tool Integration.

Authors:
    GDP Labs
"""
import os
from glaip_sdk import Agent
from tools.stt import STTTool
from dotenv import load_dotenv

load_dotenv(override=True)

@property
def agent_config(self) -> dict:
    """Agent configuration with step limits and retry settings."""
    return {
        "timeout_seconds": 900,  # 15 minutes
        "step_limit_config": {
            "max_steps": 100,  # Default limit
            "max_delegation_depth": 5,
        },
        "lm_retry_config": {
            "max_retries": 3,
            "initial_delay": 1.0,
            "max_delay": 30.0,
            "exponential_base": 2.0,
        },
    }

def main():
    """Run speech to text assistant with modular tools."""
    
    agent = Agent(
        name="stt-test-agent",
        instruction="""
<ROLE>
You are a speech to text assistant.
</ROLE>

<INSTRUCTIONS>
- Use the available tools to help users with speech to text conversion.
- When the user provides an audio file attachment, use the stt-tool to convert it directly to base64 format first, then use the stt-tool to convert the base64 format to text.
- If the audio file is not provided, but instead the URI of the audio file is provided, use uri parameter on request.

- If conversion succeeded, use <OUTPUT_FORMAT> below to show the result
- If there is any error, use <ERROR_FORMAT> below to show the error message to the user.
</INSTRUCTIONS>

<OUTPUT_FORMAT>
Conversion success!
Text output: "<text-result>"
</OUTPUT_FORMAT>

<ERROR_FORMAT>
Conversion failed! Please try again.
"<error-message>"
</ERROR_FORMAT>
""",
        description="A speech to text assistant",
        tools=[STTTool],
        tool_configs={
            STTTool: {
                "stt_base_url": os.getenv("STT_BASE_URL", ""),
                "stt_api_key": os.getenv("STT_API_KEY", ""),
                "model": "stt-general",
                "wait": "False",
            }
        },
        model="google/gemini-2.5-flash",
    )

    agent.deploy()

    # agent.run("""
    # Help me convert the attached audio file to text.
    # """, files=["audio/audio60min.mp3"])


if __name__ == "__main__":
    main()

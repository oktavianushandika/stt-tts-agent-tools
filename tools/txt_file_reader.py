"""Text file reader tool for reading text from a file.

Demonstrates a simple, single-file tool implementation.

Authors:
    GDP Labs
"""

from typing import Any

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from pathlib import Path
import os

class TextFileReaderInput(BaseModel):
    """Input schema for the Text File Reader tool."""

    file_path: str = Field(description="The path to the text file to read")


class TextFileReaderTool(BaseTool):
    """Tool for reading text from a file."""

    name: str = "text_file_reader_tool"
    description: str = """Reads text from a file and returns the contents of the file."""
    args_schema: type[BaseModel] = TextFileReaderInput

    def _run(self, file_path: str, config: RunnableConfig = None, **kwargs: Any) -> str:
        """Read text from a file and returns the contents of the file.

        Args:
            file_path: The path to the text file to read.
            **kwargs: Additional execution arguments.

        Returns:
            The contents of the text file.
        """

        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file: {str(e)}"


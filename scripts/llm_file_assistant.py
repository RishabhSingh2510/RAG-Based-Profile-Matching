import os
import sys
import json
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Ensure src directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fs_tools
from logger import SessionLogger

load_dotenv()



class LLMFileAssistant:
    """
    OOP Agent orchestrating Google Gemini API function calling, local tools, and session logging.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Gemini API client, model settings, tools engine, and session logger.

        Args:
            model_name (Optional[str]): Gemini model ID (defaults to GEMINI_MODEL env or 'gemini-2.5-flash').
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.logger = SessionLogger(log_dir="logs")
        self.fs_tools = fs_tools.FileSystemTools()
        self.client = genai.Client(api_key=self.api_key) if self.api_key and self.api_key != "your_gemini_api_key_here" else None

    def execute_tool_call(self, tool_name: str, arguments: dict) -> Any:
        """
        Execute requested tool function and record real-time logs.

        Args:
            tool_name (str): Name of tool function.
            arguments (dict): Keyword arguments for the tool.

        Returns:
            Any: Tool execution output dict or list.
        """
        self.logger.log("TOOL EXECUTION", f"Tool: {tool_name} | Arguments: {json.dumps(arguments)}")
        print(f"\n[TOOL EXECUTION] Tool: {tool_name} | Arguments: {json.dumps(arguments)}")

        func = getattr(self.fs_tools, tool_name, None)
        if not func:
            err_msg = f"Tool '{tool_name}' not recognized."
            print(f"[TOOL ERROR] {err_msg}")
            self.logger.log("TOOL ERROR", err_msg)
            return {"status": "error", "error": err_msg}

        try:
            result = func(**arguments)
            summary = f"Returned {len(result)} items." if isinstance(result, list) else f"Status: {result.get('status', 'unknown')}"
            print(f"[TOOL RESPONSE] {summary}")

            log_detail = f"Status: {result.get('status')} | Details: {json.dumps(result)}" if isinstance(result, dict) else f"Returned {len(result)} items."
            self.logger.log("TOOL RESPONSE", f"Tool '{tool_name}' -> {log_detail}")
            return result

        except Exception as e:
            err_msg = f"Exception executing '{tool_name}': {str(e)}"
            print(f"[TOOL ERROR] {err_msg}")
            self.logger.log("TOOL ERROR", err_msg)
            return {"status": "error", "error": err_msg}

    def run_query(self, user_query: str) -> str:
        """
        Send user query to Gemini API and handle tool execution loops.

        Args:
            user_query (str): User natural language query string.

        Returns:
            str: Synthesized text response from Gemini.
        """
        self.logger.log("USER QUERY", user_query)

        if not self.client:
            err = "[API KEY MISSING] GEMINI_API_KEY is not set in '.env'."
            self.logger.log("ASSISTANT RESPONSE", err)
            return err

        try:
            # Bind tool wrappers to instance method execute_tool_call
            def read_file(filepath: str) -> dict:
                """Read content from resume files (PDF, TXT, DOCX) and extract plain text and metadata."""
                return self.execute_tool_call("read_file", {"filepath": filepath})

            def list_files(directory: str, extension: str = None) -> list:
                """List all files in a directory with optional extension filtering."""
                args = {"directory": directory}
                if extension:
                    args["extension"] = extension
                return self.execute_tool_call("list_files", args)

            def write_file(filepath: str, content: str) -> dict:
                """Write text content to a target file. Automatically creates parent directories if needed."""
                return self.execute_tool_call("write_file", {"filepath": filepath, "content": content})

            def search_in_file(filepath: str, keyword: str) -> dict:
                """Search for keywords inside a specific file (case-insensitive) and return context snippets."""
                return self.execute_tool_call("search_in_file", {"filepath": filepath, "keyword": keyword})

            tools_list = [read_file, list_files, write_file, search_in_file]

            chat = self.client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    tools=tools_list,
                    temperature=0.2,
                    system_instruction="You are an intelligent File System Assistant. Always use your tools to inspect resume documents before answering queries."
                )
            )

            response = chat.send_message(user_query)

            while response.function_calls:
                for call in response.function_calls:
                    tool_output = self.execute_tool_call(call.name, dict(call.args))
                    response = chat.send_message(types.Part.from_function_response(name=call.name, response={"result": tool_output}))

            final_text = response.text
            if not final_text and hasattr(response, 'candidates') and response.candidates:
                parts_text = [p.text for p in response.candidates[0].content.parts if getattr(p, 'text', None)]
                if parts_text:
                    final_text = "\n".join(parts_text)
            if not final_text:
                final_text = "Completed query using tools."

            self.logger.log("ASSISTANT RESPONSE", final_text)
            return final_text

        except Exception as e:
            err_msg = f"[ERROR] Execution failed: {str(e)}"
            self.logger.log("ASSISTANT RESPONSE", err_msg)
            return err_msg

    def start_cli(self):
        """
        Start interactive command line interface (CLI) prompt loop.
        """
        print("=" * 65)
        print(" LLM-POWERED FILE SYSTEM ASSISTANT (Gemini Tool Calling)")
        print(f" Session Log: '{self.logger.log_filepath}'")
        print("=" * 65)

        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            print(f"\nUser Query: {query}")
            result = self.run_query(query)
            print(f"\n[ASSISTANT RESPONSE]\n{result}")
            self.logger.log("SESSION END", "Single query completed.")
            return

        print("\nSample Queries to Try:")
        print("  1. 'Read all resumes in the resumes folder'")
        print("  2. 'Find resumes mentioning Python experience'")
        print("  3. 'Create a summary file for resume_john_doe.pdf in summaries folder'")
        print("  4. Type 'exit' or 'quit' to end session.\n")

        while True:
            try:
                user_input = input("\nEnter your query > ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    print(f"Goodbye! Session log saved to '{self.logger.log_filepath}'")
                    self.logger.log("SESSION END", "User exited.")
                    break

                response = self.run_query(user_input)
                print(f"\n[ASSISTANT RESPONSE]\n{response}")
                print("-" * 65)

            except (KeyboardInterrupt, EOFError):
                print(f"\nExiting session. Log saved to '{self.logger.log_filepath}'")
                self.logger.log("SESSION END", "Interrupted by user (Ctrl+C).")
                break


def main():
    assistant = LLMFileAssistant()
    assistant.start_cli()


if __name__ == "__main__":
    main()

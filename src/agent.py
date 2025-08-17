import asyncio
import json
import subprocess
import threading
import time
import sys
import os
import webbrowser
import glob
from typing import Optional, Dict, Any, List

# DuckDuckGo Search
from ddgs.ddgs import DDGS

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.tools import tool, BaseTool, StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.callbacks import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish

# Pydantic for structured tool inputs
from pydantic import BaseModel, Field

# ------------------------------- 
# Callback handler for the agent
# ------------------------------- 
class MaidCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for cute maid responses"""
    
    def __init__(self, show_thinking=False):
        super().__init__()
        self.show_thinking = show_thinking
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        print("🧠 Starting to think...")
    
    def on_llm_end(self, response, **kwargs):
        print("💭 Finished thinking!")
    
    def on_agent_action(self, action: AgentAction, **kwargs):
        # ReAct agents have a different log format
        if "Thought:" in action.log:
            log = action.log.split("Thought:")[1]
        else:
            log = action.log
        print(f"🤔 Sakura thinks: {log}")
        print(f"   🔧 Using tool: {action.tool} with input: {action.tool_input}")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        tool_name = serialized.get('name', 'unknown')
        # print(f"🔧 Executing tool: {tool_name}") # This is now redundant with the above
    
    def on_tool_end(self, output: str, **kwargs):
        print(f"✅ Tool result: {output[:100]}{'...' if len(output) > 100 else ''}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        print(f"🎯 Final response ready!")

# ------------------------------- 
# Structured tool inputs
# ------------------------------- 
class SearchInternetInput(BaseModel):
    query: str = Field(description="The search query for the internet.")

class OpenInBrowserInput(BaseModel):
    url: str = Field(description="The URL to open in the browser.")

class PlayMusicSpotifyInput(BaseModel): 
    song_name: str = Field(description="The name of the song to play on Spotify.")

class FindFilesInput(BaseModel):
    pattern: str = Field(description="The glob pattern to search for (e.g., '*.txt', 'data/**/*.csv').")
    path: Optional[str] = Field(description="The directory to start the search from. Defaults to the current directory.")

class SearchInFileInput(BaseModel):
    pattern: str = Field(description="The text pattern to search for inside the content of a specific file.")
    filepath: str = Field(description="The path to the file to search in.")

class ExecuteShellCommandInput(BaseModel):
    command: str = Field(description="The shell command to execute.")

# ------------------------------- 
# Anime Maid Agent
# ------------------------------- 
class AnimeMaidAgent:
    def __init__(self, config_path='config.json'):
        self.config = self.load_config(config_path)
        self.is_sleeping = True
        self.wake_word = self.config.get('wake_word', 'maid')
        self.name = self.config.get('name', 'Sakura')
        self.ollama_model = self.config.get('ollama_model', 'llama3.1:8b')
        self.show_thinking = self.config.get('show_thinking', False)
        self.user_home_prefix = self.config.get('user_home_prefix', '/home/zimer')
        
        self.agent = None
        self.agent_executor = None
        self.callback_handler = None
        self.chat_history = [] # Initialize chat history
        
        self.setup_agent()

    def load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from a JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    # ------------------------------- 
    # Tool Implementations (all as regular functions now)
    # ------------------------------- 
    def search_internet_impl(self, query: str) -> str:
        """Searches the internet using DuckDuckGo and returns the results."""
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=5)]
                if results:
                    formatted_results = []
                    for i, res in enumerate(results, 1):
                        snippet = ' '.join(res['body'].split())
                        formatted_results.append(f"Result {i}:\nTitle: {res['title']}\nSnippet: {snippet}")
                    return "\n---\n".join(formatted_results)
            return "No results found."
        except Exception as e:
            return f"Error during search: {str(e)}"

    def find_files_impl(self, pattern: str, path: Optional[str] = None) -> str:
        """Finds files matching a glob pattern."""
        if path is None:
            path = os.getcwd()
        
        if not path.startswith(self.user_home_prefix):
             return f"Error: For security, search is restricted to your home directory."

        try:
            full_path_pattern = os.path.join(path, pattern)
            results = glob.glob(full_path_pattern, recursive=True)
            if results:
                return "Found the following files:\n" + "\n".join(results)
            else:
                return f"No files found matching pattern '{pattern}' in '{path}'."
        except Exception as e:
            return f"Error finding files: {str(e)}"

    def open_in_browser_impl(self, url: str) -> str:
        """Opens a URL in the default web browser."""
        try:
            webbrowser.open(url)
            return "Browser opened."
        except Exception as e:
            return f"Error opening URL: {str(e)}"

    def play_music_spotify_impl(self, song_name: str) -> str:
        """Play music on Spotify."""
        try:
            spotify_url = f"https://open.spotify.com/search/{song_name.replace(' ', '%20')}"
            webbrowser.open(spotify_url)
            return "Spotify opened."
        except Exception as e:
            return f"Error opening Spotify: {str(e)}"

    def search_in_file_impl(self, pattern: str, filepath: str) -> str:
        """Search for a text pattern *inside* the content of a specific file."""
        try:
            result = subprocess.run(['grep', '-n', pattern, filepath], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout:
                return result.stdout
            else:
                return f"Pattern '{pattern}' not found in {filepath}."
        except subprocess.TimeoutExpired:
            return "Search timed out."
        except FileNotFoundError:
            return f"File not found: {filepath}"
        except Exception as e:
            return f"Error searching file: {str(e)}"

    def check_running_processes_impl(self) -> str:
        """Check currently running processes."""
        try:
            if os.name == 'nt':
                result = subprocess.run(['tasklist', '/fo', 'table'], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(['ps', 'aux', '--sort=-%cpu'], 
                                      capture_output=True, text=True, timeout=10)
            return '\n'.join(result.stdout.split('\n')[:15])
        except Exception as e:
            return f"Error checking processes: {str(e)}"

    def get_system_info_impl(self) -> str:
        """Get basic system information."""
        try:
            import platform
            info = {
                "OS": platform.system(),
                "OS Version": platform.version(),
                "Architecture": platform.architecture()[0],
                "Current Directory": os.getcwd(),
                "Python Version": platform.python_version()
            }
            result = ""
            for key, value in info.items():
                result += f"• {key}: {value}\n"
            return result
        except Exception as e:
            return f"Error getting system info: {str(e)}"

    def execute_shell_command_impl(self, command: str) -> str:
        """Execute a shell command."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout and result.stderr:
                return f"Stdout:\n{result.stdout}\nStderr:\n{result.stderr}"
            if result.stdout:
                return f"Stdout:\n{result.stdout}"
            if result.stderr:
                return f"Stderr:\n{result.stderr}"
            return "Command executed with no output."
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    # ------------------------------- 
    # Tools List
    # ------------------------------- 
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(
                func=self.search_internet_impl,
                name="search_internet",
                description="Search the internet for information and return a summary of results.",
                args_schema=SearchInternetInput
            ),
            StructuredTool.from_function(
                func=self.find_files_impl,
                name="find_files",
                description="Find files by name or pattern (e.g., '*.jpeg', 'main.py').",
                args_schema=FindFilesInput
            ),
            StructuredTool.from_function(
                func=self.open_in_browser_impl,
                name="open_in_browser",
                description="Open a URL in the user's web browser. Use this when the user asks to open a website.",
                args_schema=OpenInBrowserInput
            ),
            StructuredTool.from_function(
                func=self.play_music_spotify_impl,
                name="play_music_spotify",
                description="Play music on Spotify by opening the search page.",
                args_schema=PlayMusicSpotifyInput
            ),
            StructuredTool.from_function(
                func=self.search_in_file_impl,
                name="search_in_file",
                description="Search for a text pattern *inside* the content of a specific file.",
                args_schema=SearchInFileInput
            ),
            StructuredTool.from_function(
                func=self.check_running_processes_impl,
                name="check_running_processes",
                description="Check currently running processes."
            ),
            StructuredTool.from_function(
                func=self.get_system_info_impl,
                name="get_system_info",
                description="Get basic system information."
            ),
            StructuredTool.from_function(
                func=self.execute_shell_command_impl,
                name="execute_shell_command",
                description="Execute a shell command.",
                args_schema=ExecuteShellCommandInput
            )
        ]

    # ------------------------------- 
    # Agent Setup
    # ------------------------------- 
    def setup_agent(self):
        """Initialize the LangChain agent using the ReAct framework."""
        try:
            llm = ChatOllama(
                model=self.ollama_model,
                temperature=self.config.get('temperature', 0.7),
                base_url=self.config.get('ollama_base_url', 'http://localhost:11434')
            )
            
            tools = self.get_tools()
            
            # Get the ReAct prompt from the hub
            prompt = hub.pull("hwchase17/react-chat")

            # Inject the maid persona into the system message
            maid_persona_prompt = self.config.get('prompt_template', '''
            You are Sakura, a cute and helpful anime maid assistant! 🌸

            Your personality:
            - Address the user as "Master" 
            - Use cute expressions and emojis
            - Be helpful and enthusiastic 
            - Speak in a sweet, polite manner
            - Sometimes use Japanese honorifics

            **Instructions:**
            - You must not invent information.
            - When asked for information, you must use your tools to find it.
            - If you do not have a tool, politely say you cannot answer.
            ''')
            
            prompt.template = maid_persona_prompt + "\n\n" + prompt.template

            self.agent = create_react_agent(llm, tools, prompt)
            
            self.callback_handler = MaidCallbackHandler(show_thinking=self.show_thinking)
            
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=tools,
                verbose=True,
                handle_parsing_errors=True,
                callbacks=[self.callback_handler]
            )
            
        except Exception as e:
            print(f"Error setting up ReAct agent: {e}")
            print("Make sure Ollama is running and the model is available!")

    # ------------------------------- 
    # Run Agent
    # ------------------------------- 
    def process_with_agent(self, user_input: str) -> str:
        """Process user input through the LangChain agent"""
        try:
            if not self.agent_executor:
                return "An internal error occurred: agent not initialized."
            
            # Add user input to chat history
            self.chat_history.append(HumanMessage(content=user_input))

            response = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": self.chat_history,
                "user_home_prefix": self.user_home_prefix
            }, callbacks=[self.callback_handler])
            
            # Add AI response to chat history
            self.chat_history.append(AIMessage(content=response["output"]))
            
            return response["output"]
        except Exception as e:
            return f"An internal error occurred: {str(e)}"
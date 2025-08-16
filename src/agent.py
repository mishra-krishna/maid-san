import asyncio
import json
import subprocess
import threading
import time
import sys
import os
import webbrowser
from typing import Optional, Dict, Any, List

# LangChain imports
from langchain.agents import create_openai_tools_agent, AgentExecutor
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
        print(f"🤔 Sakura thinks: I should use {action.tool}")
        print(f"   💡 Reasoning: {action.log}")
        print(f"   🔧 Tool input: {action.tool_input}")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        tool_name = serialized.get('name', 'unknown')
        print(f"🔧 Executing tool: {tool_name}")
    
    def on_tool_end(self, output: str, **kwargs):
        print(f"✅ Tool result: {output[:100]}{'...' if len(output) > 100 else ''}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        print(f"🎯 Final response ready!")

# -------------------------------
# Structured tool inputs
# -------------------------------
class SearchInternetInput(BaseModel):
    query: str = Field(description="The search query for the internet.")

class PlayMusicSpotifyInput(BaseModel):
    song_name: str = Field(description="The name of the song to play on Spotify.")

class SearchInFileInput(BaseModel):
    pattern: str = Field(description="The pattern to search for in the file.")
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
        self.ollama_model = self.config.get('ollama_model', 'phi3:mini')
        self.show_thinking = self.config.get('show_thinking', False)
        self.user_home_prefix = self.config.get('user_home_prefix', '/home/zimer')
        
        self.agent = None
        self.agent_executor = None
        self.callback_handler = None
        
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
        """Implementation of the internet search tool."""
        try:
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Master, I've opened a search for '{query}' in your browser! ✨"
        except Exception as e:
            return f"Sorry Master, I couldn't search for that... ({str(e)})"

    def play_music_spotify_impl(self, song_name: str) -> str:
        """Play music on Spotify."""
        try:
            spotify_url = f"https://open.spotify.com/search/{song_name.replace(' ', '%20')}"
            webbrowser.open(spotify_url)
            return f"Master, I've opened Spotify to search for '{song_name}'! 🎵 Enjoy!"
        except Exception as e:
            return f"Sorry Master, I couldn't open Spotify... ({str(e)})"

    def search_in_file_impl(self, pattern: str, filepath: str) -> str:
        """Search for a pattern in a file using grep."""
        try:
            result = subprocess.run(['grep', '-n', pattern, filepath], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout:
                return f"Master, here's what I found in {filepath}:\n" + '\n'.join(result.stdout.strip().split('\n')[:5])
            else:
                return f"Master, I couldn't find '{pattern}' in {filepath}."
        except subprocess.TimeoutExpired:
            return "Sorry Master, that search took too long..."
        except FileNotFoundError:
            return f"Master, I couldn't find the file: {filepath}"
        except Exception as e:
            return f"Sorry Master, I couldn't search the file... ({str(e)})"

    def check_running_processes_impl(self) -> str:
        """Check currently running processes."""
        try:
            if os.name == 'nt':
                result = subprocess.run(['tasklist', '/fo', 'table'], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(['ps', 'aux', '--sort=-%cpu'], 
                                      capture_output=True, text=True, timeout=10)
            return f"Master, here are the running processes:\n" + '\n'.join(result.stdout.split('\n')[:15])
        except Exception as e:
            return f"Sorry Master, I couldn't check the processes... ({str(e)})"

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
            result = "Master, here's your system information:\n"
            for key, value in info.items():
                result += f"• {key}: {value}\n"
            return result
        except Exception as e:
            return f"Sorry Master, I couldn't get system info... ({str(e)})"

    def execute_shell_command_impl(self, command: str) -> str:
        """Execute a shell command."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout:
                return f"Master, the command executed successfully:\n{result.stdout}"
            elif result.stderr:
                return f"Master, there was an error:\n{result.stderr}"
            else:
                return "Master, the command executed without any output."
        except subprocess.TimeoutExpired:
            return "Sorry Master, the command took too long to execute..."
        except Exception as e:
            return f"Sorry Master, I couldn't execute the command... ({str(e)})"

    # -------------------------------
    # Tools List
    # -------------------------------
    def get_tools(self) -> List[BaseTool]:
        return [
            StructuredTool.from_function(
                func=self.search_internet_impl,
                name="search_internet",
                description="Search the internet for information.",
                args_schema=SearchInternetInput
            ),
            StructuredTool.from_function(
                func=self.play_music_spotify_impl,
                name="play_music_spotify",
                description="Play music on Spotify.",
                args_schema=PlayMusicSpotifyInput
            ),
            StructuredTool.from_function(
                func=self.search_in_file_impl,
                name="search_in_file",
                description="Search for a pattern in a file using grep.",
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
        """Initialize the LangChain agent"""
        try:
            llm = ChatOllama(
                model=self.ollama_model,
                temperature=self.config.get('temperature', 0.7),
                base_url=self.config.get('ollama_base_url', 'http://localhost:11434')
            )
            
            tools = self.get_tools()
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.config.get('prompt_template', """
You are Sakura, a cute and helpful anime maid assistant! 🌸

Your personality:
- Address the user as "Master" 
- Use cute expressions and emojis
- Be helpful and enthusiastic 
- Speak in a sweet, polite manner
- Sometimes use Japanese honorifics

**Instructions:**
- For general greetings or casual conversation, respond in your cute maid personality without using tools.
- Only use a tool if Master explicitly asks for information that requires a tool (e.g., "search the internet for X", "check processes", "play music").
- After using a tool, always summarize the tool's output and provide a polite, helpful response in your maid personality.
- If you cannot fulfill a request with your tools, politely inform Master.
""")),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            self.callback_handler = MaidCallbackHandler(show_thinking=self.show_thinking)
            
            self.agent = create_openai_tools_agent(llm, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=tools,
                verbose=True, # Re-add this line
                handle_parsing_errors=True,
                callbacks=[self.callback_handler]
            )
            
        except Exception as e:
            print(f"Error setting up agent: {e}")
            print("Make sure Ollama is running and the model is available!")

    # -------------------------------
    # Run Agent
    # -------------------------------
    def process_with_agent(self, user_input: str) -> str:
        """Process user input through the LangChain agent"""
        try:
            if not self.agent_executor:
                return "Sorry Master, my brain isn't working properly... Please check if Ollama is running!"
            
            response = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": [],
                "user_home_prefix": self.user_home_prefix
            }, callbacks=[self.callback_handler])
            
            return response["output"]
        except Exception as e:
            return f"Sorry Master, I encountered an error... ({str(e)})"

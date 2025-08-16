#!/usr/bin/env python3
"""
Anime Maid CLI Assistant Agent with LangChain
A cute command line assistant that uses LangChain for proper tool calling
"""

import os
import requests
import sys
from src.agent import AnimeMaidAgent
from src.cli import MaidCLI

def check_dependencies():
    """Check for required dependencies."""
    try:
        import langchain
        from langchain_community.llms import Ollama
        from langchain_community.chat_models import ChatOllama
    except ImportError:
        print("❌ LangChain not found! Please install:")
        print("   pip install langchain langchain-community")
        return False
    return True

def check_ollama_connection(url='http://localhost:11434'):
    """Check if Ollama is running."""
    try:
        response = requests.get(f'{url}/api/version', timeout=5)
        if response.status_code != 200:
            print(f"⚠️  Warning: Ollama doesn't seem to be running on {url}")
            print("   Please start Ollama: ollama serve")
            return False
    except requests.exceptions.RequestException:
        print(f"⚠️  Warning: Cannot connect to Ollama at {url}!")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Start it: ollama serve")
        return False
    return True

def main():
    """Main entry point"""
    print("Setting up Sakura...")
    
    if not check_dependencies():
        return
        
    # Construct the path to the config.json file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.json')

    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found at '{config_path}'")
        return

    agent = AnimeMaidAgent(config_path=config_path)
    
    if not check_ollama_connection(agent.config.get('ollama_base_url')):
        print(f"   3. Pull model: ollama pull {agent.ollama_model}")
        return

    cli = MaidCLI(agent)
    cli.run()

if __name__ == "__main__":
    main()

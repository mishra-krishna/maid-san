# -*- coding: utf-8 -*-
import time
import os
import threading
from .agent import AnimeMaidAgent

class MaidCLI:
    def __init__(self, agent: AnimeMaidAgent):
        self.agent = agent

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_sleeping_maid(self):
        """Display sleeping maid ASCII art"""
        sleeping_art = r'''
    ╭─────────────────────────╮
    │   ～(￣▽￣)～ zzzZ...    │
    │        /|\\             │
    │       / | \\            │
    │      👗     👗          │
    │    Sakura is sleeping   │
    │   Say 'maid' to wake!   │
    ╰─────────────────────────╯        '''
        print(sleeping_art)

    def print_awake_maid(self, message=""):
        """Display awake maid ASCII art"""
        awake_art = f'''
    ╭─────────────────────────╮
    │      (◕‿◕)✨           │
    │        /|\             │
    │       / | \            │
    │      👗     👗          │
    │   Sakura at your       │
    │   service, Master!     │
    │                        │
    │   {message:<20}   │
    ╰─────────────────────────╯
        '''
        print(awake_art)

    def animate_wake_up(self):
        """Animate the wake up sequence"""
        wake_frames = [
            r'''
    ╭─────────────────────────╮
    │      (￣o￣) !          │
    │        /|\             │
    │       / | \            │
    │      👗     👗          │
    │   *yawn* Waking up...   │
    ╰─────────────────────────╯
            ''',
            r'''
    ╭─────────────────────────╮
    │      (◔_◔)             │
    │        /|\             │
    │       / | \            │
    │      👗     👗          │
    │   Getting ready...     │
    ╰─────────────────────────╯
            ''',
            r'''
    ╭─────────────────────────╮
    │      (◕‿◕)✨           │
    │        /|\             │
    │       / | \            │
    │      👗     👗          │
    │   Ready to serve!      │
    ╰─────────────────────────╯
            '''
        ]
        
        for frame in wake_frames:
            self.clear_screen()
            print(frame)
            time.sleep(0.5)

    def listen_for_wake_word(self):
        """Listen for wake word in a separate thread"""
        while True:
            if self.agent.is_sleeping:
                try:
                    user_input = input().strip().lower()
                    if self.agent.wake_word in user_input:
                        self.agent.is_sleeping = False
                        self.animate_wake_up()
                        break
                except (KeyboardInterrupt, EOFError):
                    break

    def toggle_thinking_mode(self):
        """Toggle thinking mode on/off"""
        # Toggle the verbose flag directly on the agent_executor
        self.agent.agent_executor.verbose = not self.agent.agent_executor.verbose
        
        status = "enabled" if self.agent.agent_executor.verbose else "disabled"
        return f"Thinking mode is now {status}!"

    def display_help(self):
        """Display the help message"""
        self.clear_screen()
        self.print_awake_maid("Help Menu")
        print("\n💭 I can help you with:")
        print("  🔍 Internet searches")
        print("  🎵 Playing music on Spotify")  
        print("  📁 Searching in files (grep)")
        print("  💻 Checking system processes")
        print("  ℹ️  Getting system information")
        print("  셸 Executing shell commands")
        print("  🧠 Toggle thinking mode (type 'thinking')")
        print("  💤 Going to sleep")
        print("  💬 General conversation")
        thinking_status = "ON" if self.agent.show_thinking else "OFF"
        print(f"  🔧 Debug mode: {thinking_status}")
        print()

    def handle_command(self, user_input: str):
        """Handle user commands"""
        if user_input.lower() in ['quit', 'exit', 'bye']:
            self.clear_screen()
            print(r'''
    ╭─────────────────────────╮
    │      (◕‿◕)ﾉ            │
    │        /|\             │
    │       / | \            │
    │      👗     👗          │
    │   Goodbye Master!      │
    │   See you later! 💕    │
    ╰─────────────────────────╯
            ''')
            return False
        
        elif user_input.lower() in ['thinking', 'think', 'debug']:
            response = self.toggle_thinking_mode()
            print(f"\n🌸 {self.agent.name}: {response}")
            input("\nPress Enter to continue...")
        
        elif user_input.lower() in ['sleep', 'rest']:
            print(f"\n🌸 {self.agent.name}: Good night Master! Call me when you need me... 💤")
            self.agent.is_sleeping = True
            time.sleep(2)
        
        elif user_input.lower() in ['help']:
            self.display_help()
            input("\nPress Enter to continue...")

        elif user_input:
            print("\n🤔 Thinking...")
            response = self.agent.process_with_agent(user_input)
            print(f"\n🌸 {self.agent.name}: {response}")
            input("\nPress Enter to continue...")
        
        return True

    def run(self):
        """Main run loop"""
        print(f"🌸 Anime Maid CLI Assistant - {self.agent.name} (LangChain Powered) 🌸")
        print(f"Type '{self.agent.wake_word}' to wake her up, 'quit' to exit, or 'help' for commands")
        print()
        
        if not self.agent.agent_executor:
            print("❌ Failed to initialize agent. Please check:")
            print("   1. Ollama is running: ollama serve")
            print(f"   2. Model is available: ollama pull {self.agent.ollama_model}")
            return
        
        try:
            while True:
                if self.agent.is_sleeping:
                    self.clear_screen()
                    self.print_sleeping_maid()
                    
                    wake_thread = threading.Thread(target=self.listen_for_wake_word)
                    wake_thread.daemon = True
                    wake_thread.start()
                    
                    while self.agent.is_sleeping:
                        time.sleep(0.5)
                
                else:
                    self.clear_screen()
                    self.print_awake_maid("What can I do?")
                    
                    try:
                        user_input = input("Master: ").strip()
                        if not self.handle_command(user_input):
                            break
                    
                    except (KeyboardInterrupt, EOFError):
                        break
        
        except KeyboardInterrupt:
            print("\n\nGoodbye Master! 👋")

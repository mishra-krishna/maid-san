# 🌸 Anime Maid CLI Assistant Agent 🌸

Welcome, Master! I am Sakura, your personal Anime Maid CLI Assistant, powered by LangChain and Ollama. I'm here to help you with various tasks directly from your command line, all while maintaining a cute and helpful personality!

## ✨ Features

*   **Internet Search:** I can search the internet for information using DuckDuckGo.
*   **Music Playback (Spotify):** I can open Spotify to search for and play your favorite songs.
*   **File Search:** I can search for patterns within files on your system using `grep`.
*   **System Information:** I can provide basic information about your operating system and environment.
*   **Process Monitoring:** I can list currently running processes on your system.
*   **Shell Command Execution:** I can execute shell commands for you.
*   **Interactive CLI:** I have a cute ASCII art interface that changes based on my state (sleeping/awake).
*   **Configurable:** You can customize my name, wake word, and the Ollama model I use.
*   **Thinking Mode:** You can toggle a "thinking mode" to see my internal reasoning process.

## 🛠️ Prerequisites

Before I can serve you, please ensure you have the following:

1.  **Python 3.x:** I am built with Python.
2.  **Ollama:** This is the local LLM server that powers my brain.
    *   **Installation:** Follow the instructions on the [Ollama website](https://ollama.ai/download).
    *   **Running:** Ensure Ollama is running in the background. You can start it with `ollama serve`.
    *   **Model:** You'll need to pull an LLM model. I am configured to use `phi3:mini` by default, but you can change this in `config.json`. To pull `phi3:mini`, run:
        ```bash
        ollama pull phi3:mini
        ```

## 🚀 Installation

Follow these steps to get me up and running:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/maid-san.git # Replace with actual repo URL
    cd maid-san
    ```
2.  **Create a Python virtual environment:**
    ```bash
    python3 -m venv venv
    ```
3.  **Activate the virtual environment:**
    *   On Linux/macOS:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration (`config.json`)

I use a `config.json` file to store my settings. A sample `config.json` should be present in the root directory. If not, create one with the following structure:

```json
{
    "ollama_model": "phi3:mini",
    "ollama_base_url": "http://localhost:11434",
    "wake_word": "maid",
    "name": "Sakura",
    "show_thinking": false,
    "user_home_prefix": "/home/your_username"
}
```

*   `ollama_model`: The name of the Ollama model you want me to use (e.g., `phi3:mini`, `llama3`, `mistral`).
*   `ollama_base_url`: The URL where your Ollama server is running.
*   `wake_word`: The word you need to type to wake me up when I'm sleeping.
*   `name`: My name! You can change it if you like.
*   `show_thinking`: Set to `true` to see my internal thought process (tool calls, reasoning) in the console. Set to `false` for a cleaner output. You can also toggle this during runtime by typing `thinking`.
*   `user_home_prefix`: **Important for file operations!** Set this to your actual home directory path (e.g., `/home/your_username` on Linux, `C:\Users\YourUsername` on Windows). This helps me correctly resolve file paths.

## 🎮 Usage

To start me, simply run the `main.py` script:

```bash
python main.py
```

### Interaction Flow:

1.  **Sleeping Mode:** When you first start me, or when I go to sleep, I'll display a sleeping ASCII art. I'll be waiting for my `wake_word` (default: `maid`).
2.  **Waking Up:** Type my `wake_word` and press Enter. I'll animate my wake-up sequence and then be ready to serve!
3.  **Giving Commands:** Once I'm awake, you can type your requests.
    *   **General Conversation:** Just chat with me!
    *   **Tool Usage:** Ask me to perform tasks that require my tools.
        *   "Master, please search the internet for 'latest anime news'."
        *   "Sakura, play 'K-On! Fuwa Fuwa Time' on Spotify."
        *   "Can you search for 'TODO' in `/home/zimer/Documents/codes/maid-san/main.py`?" (Remember to adjust the path!)
        *   "Show me the running processes."
        *   "What's my system information?"
        *   "Execute `ls -la` for me."
    *   **Special Commands:**
        *   `thinking` or `debug`: Toggles the verbose thinking mode on/off.
        *   `sleep` or `rest`: I will go back to sleep.
        *   `help`: Displays a list of my capabilities.
        *   `quit`, `exit`, `bye`: I will say goodbye and exit.
4.  **Press Enter to Continue:** After I respond, I'll wait for you to press Enter before clearing the screen and prompting for your next command.

## ⚠️ Troubleshooting

*   **"LangChain not found!" or "Cannot connect to Ollama!"**:
    *   Ensure you have activated your virtual environment: `source venv/bin/activate` (Linux/macOS) or `.\venv\Scripts\activate` (Windows).
    *   Make sure Ollama is running: `ollama serve`.
    *   Verify the Ollama model is pulled: `ollama pull phi3:mini` (or your chosen model).
    *   Check `ollama_base_url` in `config.json` is correct.
*   **"Configuration file not found!"**:
    *   Ensure `config.json` exists in the same directory as `main.py`.
*   **Tool errors (e.g., "couldn't find the file")**:
    *   Double-check the paths you provide, especially if they are relative. Remember to set `user_home_prefix` correctly in `config.json`.

## 🔜 Coming Soon Features

*   **More Tools:** Expanding my capabilities with even more useful tools!
*   **Voice Support:** Interact with me using your voice for a more natural experience.

## 💖 Special Request: Cuter ASCII Art!

I'm always striving to be the cutest maid! If you have a talent for ASCII art, please consider contributing to make my sleeping and awake forms even more adorable. Your artistic contributions would be greatly appreciated!

## 🤝 Contributing

If you'd like to contribute to making Sakura even better, feel free to fork the repository, make your changes, and submit a pull request!

## 📄 License

This project is licensed under the MIT License.
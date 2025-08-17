# 🌸 Anime Maid CLI Assistant Agent 🌸

Welcome, Master! I am Sakura, your personal Anime Maid CLI Assistant, powered by LangChain and Ollama. I'm here to help you with various tasks directly from your command line, all while maintaining a cute and helpful personality!

## ✨ Features

*   **Voice-First Interaction:** My primary input mode is now voice! I will listen for your commands by default.
*   **Mode Switching:** You can seamlessly switch to traditional `text mode` if you prefer to type.
*   **Internet Search:** I can search the internet for information using DuckDuckGo and provide you with a summary of the results.
*   **File Finding:** I can search for files on your system by name or pattern (e.g., `*.jpeg`).
*   **File Content Search:** I can search for text patterns *inside* the content of a specific file.
*   **Web Browser Control:** I can open any URL you specify in your default web browser.
*   **Music Playback (Spotify):** I can open Spotify to search for your favorite songs.
*   **System Information:** I can provide basic information about your operating system and environment.
*   **Process Monitoring:** I can list currently running processes on your system.
*   **Shell Command Execution:** I can execute shell commands for you.
*   **Reliable Reasoning:** I now use a ReAct agent framework, which makes my tool usage much more reliable and less prone to errors.
*   **Interactive CLI:** I have a cute ASCII art interface that changes based on my state (sleeping/awake).
*   **Configurable:** You can customize my name, wake word, and the Ollama model I use.
*   **Thinking Mode:** You can toggle a "thinking mode" to see my internal reasoning process.

## 🛠️ Prerequisites

Before I can serve you, please ensure you have the following:

1.  **Python 3.x:** I am built with Python.
2.  **Ollama:** This is the local LLM server that powers my brain.
    *   **Installation:** Follow the instructions on the [Ollama website](https://ollama.ai/download).
    *   **Running:** Ensure Ollama is running in the background. You can start it with `ollama serve`.
    *   **Model:** You'll need to pull an LLM model. I am configured to use a model from your `config.json`, but you can use any model you like (e.g., `llama3.1:8b`).
3.  **ffmpeg:** The voice input feature requires `ffmpeg` to be installed on your system.
    *   On Debian/Ubuntu: `sudo apt update && sudo apt install ffmpeg`
    *   On macOS (with Homebrew): `brew install ffmpeg`

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
    "ollama_model": "llama3.1:8b",
    "ollama_base_url": "http://localhost:11434",
    "wake_word": "maid",
    "name": "Sakura",
    "show_thinking": false,
    "user_home_prefix": "/home/your_username"
}
```

*   `ollama_model`: The name of the Ollama model you want me to use.
*   `ollama_base_url`: The URL where your Ollama server is running.
*   `wake_word`: The word you need to type to wake me up when I'm sleeping.
*   `name`: My name! You can change it if you like.
*   `show_thinking`: Set to `true` to see my internal thought process. You can also toggle this during runtime.
*   `user_home_prefix`: **Important for file operations!** Set this to your actual home directory path (e.g., `/home/your_username` on Linux, `C:\Users\YourUsername` on Windows).

## 🎮 Usage

To start me, simply run the `main.py` script:

```bash
python3 main.py
```

### Interaction Flow:

1.  **Sleeping Mode:** When you first start me, I'll be sleeping. I'll be waiting for my `wake_word` (default: `maid`). Type it and press Enter to wake me up.
2.  **Voice Mode (Default):** Once I'm awake, I will default to **voice mode**. 
    *   I will automatically start listening.
    *   Speak your command clearly.
    *   **Press the Enter key when you are finished speaking.**
    *   I will then transcribe your command and execute it.
3.  **Switching to Text Mode:**
    *   If you prefer to type, simply say **"text mode"**. 
    *   I will switch to keyboard input for all subsequent commands.
4.  **Switching Back to Voice Mode:**
    *   While in text mode, simply type **"voice mode"** to switch me back to listening.

### Example Commands (can be spoken or typed):

*   "Sakura, what is the weather like in Tokyo?"
*   "Please find all my jpeg files in my pictures directory."
*   "Open youtube.com for me."
*   "Play the new Taylor Swift song on Spotify."
*   "Search for the word 'refactor' inside `src/agent.py`."
*   "Show me the running processes."
*   "What's my system information?"
*   "Execute `ls -la` for me."
*   `thinking` or `debug`: Toggles the verbose thinking mode on/off.
*   `sleep` or `rest`: I will go back to sleep.
*   `help`: Displays a list of my capabilities.
*   `quit`, `exit`, `bye`: I will say goodbye and exit.

## ⚠️ Troubleshooting

*   **Errors on Startup:**
    *   Ensure you have activated your virtual environment: `source venv/bin/activate`.
    *   Make sure Ollama is running: `ollama serve`.
    *   Verify the Ollama model is pulled: `ollama pull <your_model_name>`.
*   **Voice Input Errors:**
    *   Make sure you have `ffmpeg` installed on your system.
    *   Check that your microphone is working and selected as the default input device.
*   **Tool errors (e.g., "couldn't find the file")**:
    *   Double-check the paths you provide. Remember to set `user_home_prefix` correctly in `config.json`.

## 🤝 Contributing

If you'd like to contribute to making Sakura even better, feel free to fork the repository, make your changes, and submit a pull request!

## 📄 License

This project is licensed under the MIT License.
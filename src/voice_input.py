# src/voice_input.py
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import whisper
import os
import tempfile
import queue
import threading
import sys

class VoiceInput:
    def __init__(self, model_size="base"):
        print("🎙️ Loading speech-to-text model...")
        try:
            self.model = whisper.load_model(model_size)
            print("✅ Speech-to-text model loaded.")
        except Exception as e:
            print(f"❌ Error loading whisper model: {e}")
            print("   Please make sure you have ffmpeg installed (`sudo apt-get install ffmpeg`).")
            self.model = None

    def record_audio_continuous(self, sample_rate=16000):
        q = queue.Queue()

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        stop_event = threading.Event()
        def wait_for_enter():
            input("\n🎤 I am listening, Master... Press Enter when you are finished speaking.\n")
            stop_event.set()

        input_thread = threading.Thread(target=wait_for_enter)
        input_thread.start()

        with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback, dtype='int16'):
            recorded_frames = []
            while not stop_event.is_set():
                recorded_frames.append(q.get())
        
        print("✅ Recording finished.")
        audio_data = np.concatenate(recorded_frames, axis=0)
        return audio_data, sample_rate

    def save_wav(self, audio_data, sample_rate):
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, "maid_san_input.wav")
        wav.write(temp_filename, sample_rate, audio_data)
        return temp_filename

    def transcribe_audio(self, filename):
        if not self.model:
            return "Error: Whisper model not loaded."
        print("🧠 Transcribing audio...")
        try:
            result = self.model.transcribe(filename, fp16=False)
            print("✅ Transcription finished.")
            return result['text']
        except Exception as e:
            return f"Error during transcription: {str(e)}"

    def listen(self):
        audio_data, sample_rate = self.record_audio_continuous()
        filename = self.save_wav(audio_data, sample_rate)
        text = self.transcribe_audio(filename)
        try:
            os.remove(filename) # Clean up the temp file
        except OSError as e:
            print(f"Error removing temp file: {e}")
        return text
import os
import sys
import threading

from dotenv import load_dotenv

from db import init_db, save_transcription
from recorder import Recorder
from transcriber import init_client, transcribe
from hotkeys import HotkeyManager
from ui import FlowUI
from setup_mic import pick_device, save_device_to_env


def paste_text(text):
    """Copy text to clipboard via clip.exe and simulate Ctrl+V."""
    import subprocess
    import keyboard
    import time

    process = subprocess.Popen("clip", stdin=subprocess.PIPE, shell=True)
    process.communicate(text.encode("utf-16-le"))

    time.sleep(0.05)
    keyboard.send("ctrl+v")


def main():
    # Load config
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(env_path)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-key-here":
        print("ERROR: Set your OPENAI_API_KEY in .env")
        sys.exit(1)

    # Mic setup
    mic_index = os.getenv("MIC_DEVICE_INDEX")
    if not mic_index:
        print("No microphone configured. Let's pick one.\n")
        device = pick_device()
        if device is None:
            sys.exit(1)
        save_device_to_env(device)
        mic_index = device
    else:
        mic_index = int(mic_index)

    # Init
    init_client(api_key)
    init_db()
    recorder = Recorder(mic_index)
    ui = FlowUI()

    def on_state_change(state):
        ui.set_state(state)

    def on_result(text, duration_ms):
        if text and text.strip():
            save_transcription(text.strip(), duration_ms)
            paste_text(text.strip())
            print(f"[{duration_ms}ms] {text.strip()}")

    def on_quit():
        print("Quitting Flow...")
        ui.quit()

    hotkeys = HotkeyManager(recorder, transcribe, on_state_change, on_result, on_quit)

    # Wire up X button to cancel
    def on_cancel():
        hotkeys._on_escape(None)

    ui.set_cancel_callback(on_cancel)

    # Start hotkey listener in background thread
    threading.Thread(target=hotkeys.start, daemon=True).start()

    print("Flow is running. Hold Left Ctrl + Left Alt to record.")
    print("Press Ctrl+C in this terminal to quit.\n")

    # Tkinter main loop (must be main thread)
    try:
        ui.run()
    except KeyboardInterrupt:
        ui.quit()


if __name__ == "__main__":
    main()

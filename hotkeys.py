import keyboard
import time
import threading


class HotkeyManager:
    IDLE = "idle"
    RECORDING = "recording"
    LOCKED = "locked"
    TRANSCRIBING = "transcribing"

    def __init__(self, recorder, transcriber_fn, on_state_change, on_result, on_quit=None):
        self.recorder = recorder
        self.transcriber_fn = transcriber_fn
        self.on_state_change = on_state_change  # callback(state)
        self.on_result = on_result  # callback(text)
        self.on_quit = on_quit
        self.state = self.IDLE
        self._record_start_time = None
        self._ctrl_held = False
        self._alt_held = False

    def start(self):
        keyboard.on_press_key("left ctrl", self._on_ctrl_press, suppress=False)
        keyboard.on_release_key("left ctrl", self._on_ctrl_release, suppress=False)
        keyboard.on_press_key("left alt", self._on_alt_press, suppress=False)
        keyboard.on_release_key("left alt", self._on_alt_release, suppress=False)
        keyboard.on_press_key("space", self._on_space, suppress=False)
        keyboard.add_hotkey("ctrl+alt+q", self._on_quit, suppress=False)

    def _both_held(self):
        return self._ctrl_held and self._alt_held

    def _on_ctrl_press(self, event):
        self._ctrl_held = True
        if self._both_held():
            if self.state == self.IDLE:
                self._start_recording()
            elif self.state == self.LOCKED:
                self._finish_recording()

    def _on_alt_press(self, event):
        self._alt_held = True
        if self._both_held():
            if self.state == self.IDLE:
                self._start_recording()
            elif self.state == self.LOCKED:
                self._finish_recording()

    def _on_ctrl_release(self, event):
        self._ctrl_held = False
        if self.state == self.RECORDING:
            self._finish_recording()

    def _on_alt_release(self, event):
        self._alt_held = False
        if self.state == self.RECORDING:
            self._finish_recording()

    def _on_space(self, event):
        if self.state == self.RECORDING:
            self.state = self.LOCKED
            self.on_state_change(self.LOCKED)
        elif self.state == self.LOCKED:
            self._finish_recording()

    def _on_quit(self):
        if self.on_quit:
            self.on_quit()

    def _on_escape(self, event):
        if self.state in (self.RECORDING, self.LOCKED):
            self.recorder.cancel()
            self.state = self.IDLE
            self.on_state_change(self.IDLE)

    def _start_recording(self):
        self.state = self.RECORDING
        self._record_start_time = time.time()
        self.recorder.start()
        self.on_state_change(self.RECORDING)

    def _finish_recording(self):
        self.state = self.TRANSCRIBING
        self.on_state_change(self.TRANSCRIBING)
        duration_ms = int((time.time() - self._record_start_time) * 1000)
        wav_data = self.recorder.stop()

        if wav_data is None:
            self.state = self.IDLE
            self.on_state_change(self.IDLE)
            return

        # Transcribe in background thread so we don't block the keyboard hook
        def do_transcribe():
            try:
                text = self.transcriber_fn(wav_data)
                self.on_result(text, duration_ms)
            except Exception as e:
                print(f"Transcription error: {e}")
            finally:
                self.state = self.IDLE
                self.on_state_change(self.IDLE)

        threading.Thread(target=do_transcribe, daemon=True).start()

import io
import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000  # Whisper expects 16kHz
CHANNELS = 1


class Recorder:
    def __init__(self, device_index):
        self.device_index = device_index
        self._buffer = []
        self._recording = False
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            device=device_index,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def _callback(self, indata, frames, time_info, status):
        if self._recording:
            self._buffer.append(indata.copy())

    def start(self):
        self._buffer = []
        self._recording = True

    def stop(self):
        self._recording = False

        if not self._buffer:
            return None

        audio = np.concatenate(self._buffer, axis=0)

        # Minimum length check (0.75 seconds)
        duration_secs = len(audio) / SAMPLE_RATE
        if duration_secs < 0.75:
            print(f"[audio] Too short ({duration_secs:.2f}s), skipping")
            return None

        # RMS per half-second chunk
        chunk_size = SAMPLE_RATE // 2
        chunk_rms = []
        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            chunk_rms.append(rms)

        peak_rms = max(chunk_rms)
        chunks_str = " | ".join(f"{r:.4f}" for r in chunk_rms)
        print(f"[audio] Chunk RMS: {chunks_str}")
        print(f"[audio] Peak RMS: {peak_rms:.6f}")

        if peak_rms < 0.0018:
            print("[audio] Below silence threshold, skipping transcription")
            return None

        buf = io.BytesIO()
        sf.write(buf, audio, SAMPLE_RATE, format="WAV")
        buf.seek(0)
        return buf

    def cancel(self):
        self._recording = False
        self._buffer = []

from openai import OpenAI


client = None


def init_client(api_key):
    global client
    client = OpenAI(api_key=api_key)


def transcribe(wav_bytes_io):
    wav_bytes_io.name = "audio.wav"
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=wav_bytes_io,
    )
    return response.text

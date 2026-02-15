# Flow (Speech to text) Windows
(created because didn't want to pay for wisperflow)
Voice-to-text that pastes anywhere. Hold a hotkey, speak, release — your words get transcribed and pasted wherever your cursor is.

Built on OpenAI's Whisper API with a minimal floating pill UI.

## How it works

1. Hold **Left Ctrl + Left Alt** to start recording
2. Release to stop and transcribe
3. Text gets pasted at your cursor automatically

You can also press **Space** while recording to lock it on (hands-free), then press **Space** again or **Ctrl+Alt** to finish. Press **Ctrl+Alt+Q** to quit.

## Setup

```bash
git clone https://github.com/CaelanL/flow.git
cd flow
python -m venv venv
source venv/bin/activate        # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
```

Add your OpenAI API key to `.env`, then run:

```bash
python flow.py
```

On first run it'll ask you to pick a microphone.

## Requirements

- Python 3.10+
- OpenAI API key
- Windows

## License

MIT

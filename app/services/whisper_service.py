import openai
import requests
import tempfile

openai.api_key = "YOUR_OPENAI_KEY"

async def transcribe_audio(audio_url: str) -> str:
    audio = requests.get(audio_url).content

    with tempfile.NamedTemporaryFile(suffix=".ogg") as f:
        f.write(audio)
        f.flush()
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=open(f.name, "rb")
        )
    return transcript["text"]

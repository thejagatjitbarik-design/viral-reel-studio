import asyncio
import edge_tts
from pathlib import Path

DEFAULT_VOICE = "en-US-ChristopherNeural"

async def generate_speech(text: str, output_path: Path, voice: str = DEFAULT_VOICE):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return output_path

def create_voiceover(text: str, output_path: Path, voice: str = DEFAULT_VOICE):
    return asyncio.run(generate_speech(text, output_path, voice))

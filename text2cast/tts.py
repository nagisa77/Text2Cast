import os
from .config import Config, OPENAI_API_KEY
import openai


def script_to_audio(cfg: Config) -> list:
    import json
    with open(cfg.script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)
    os.makedirs(cfg.audio_dir, exist_ok=True)
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    audio_files = []
    for idx, item in enumerate(script):
        speaker = item.get('speaker', '0')
        text = item['text']
        voice = cfg.speaker_voice.get(str(speaker), 'alloy')
        out_path = os.path.join(cfg.audio_dir, f'{idx}_{speaker}.mp3')
        response = client.audio.speech.create(
            model=cfg.tts_model,
            voice=voice,
            input=text,
        )
        with open(out_path, 'wb') as af:
            af.write(response.content)
        audio_files.append(out_path)
    return audio_files

import os
from .config import Config, OPENAI_API_KEY
import openai
import logging

logger = logging.getLogger(__name__)


def script_to_audio(cfg: Config) -> list:
    import json
    logger.debug("Reading script JSON from %s", cfg.script_path)
    with open(cfg.script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)

    logger.debug("Ensuring audio directory %s exists", cfg.audio_dir)
    os.makedirs(cfg.audio_dir, exist_ok=True)
    logger.debug("Creating OpenAI client for TTS")
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    audio_files = []

    for idx, item in enumerate(script):
        speaker = item.get('speaker', '0')
        text = item['text']
        voice = cfg.speaker_voice.get(str(speaker), 'alloy')
        out_path = os.path.join(cfg.audio_dir, f'{idx}_{speaker}.mp3')

        logger.debug("Generating audio for item %d with voice %s", idx, voice)
        response = client.audio.speech.create(
            model=cfg.tts_model,
            voice=voice,
            input=text,
        )

        logger.debug("Writing audio file to %s", out_path)
        with open(out_path, 'wb') as af:
            af.write(response.content)
        audio_files.append(out_path)
    return audio_files

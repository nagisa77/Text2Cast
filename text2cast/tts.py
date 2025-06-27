import os
import uuid
import base64
import requests
from .config import (
    Config,
    OPENAI_API_KEY,
    VOLCENGINE_TOKEN,
    VOLCENGINE_APP_ID,
)
import openai
import logging
import time

logger = logging.getLogger(__name__)


def script_to_audio(cfg: Config) -> list:
    import json
    logger.debug("Reading script JSON from %s", cfg.script_path)
    with open(cfg.script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)

    logger.debug("Ensuring audio directory %s exists", cfg.audio_dir)
    os.makedirs(cfg.audio_dir, exist_ok=True)

    audio_files = []

    if cfg.tts_engine == "openai":
        logger.debug("Creating OpenAI client for TTS")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
    elif cfg.tts_engine == "volcengine":
        logger.debug("Using Volcengine HTTP API for TTS")
        client = None
        if not VOLCENGINE_TOKEN or not VOLCENGINE_APP_ID:
            raise ValueError("VOLCENGINE_TOKEN or VOLCENGINE_APP_ID not set")
    else:
        raise ValueError(f"Unknown tts_engine: {cfg.tts_engine}")

    logger.debug("speaker_voice: %s", cfg.speaker_voice)

    for idx, item in enumerate(script):
        speaker = item.get('speaker', '0')
        text = item['text']
        voice = cfg.speaker_voice.get(str(speaker), 'alloy')
        logger.debug("speaker: %s, voice: %s", speaker, voice)
        out_path = os.path.join(cfg.audio_dir, f'{idx}_{voice}.mp3')

        logger.debug("Generating audio for item %d with voice %s", idx, voice)
        delay = 1
        while True:
            try:
                if cfg.tts_engine == "openai":
                    response = client.audio.speech.create(
                        model=cfg.tts_model,
                        voice=voice,
                        input=text,
                    )
                    audio_data = response.content
                else:
                    logger.debug("VOLCENGINE_APP_ID: %s", VOLCENGINE_APP_ID)
                    logger.debug("VOLCENGINE_TOKEN: %s", VOLCENGINE_TOKEN)
                    logger.debug("tts_model: %s", cfg.tts_model)

                    payload = {
                        "app": {
                            "appid": VOLCENGINE_APP_ID,
                            "token": VOLCENGINE_TOKEN,
                            "cluster": cfg.tts_model,
                        },
                        "user": {"uid": "text2cast"},
                        "audio": {
                            "voice_type": voice,
                            "encoding": "mp3",
                            "rate": 24000,
                        },
                        # "resource_id": "volc.tts_async.emotion",
                        "request": {
                            "reqid": str(uuid.uuid4()),
                            "text": text,
                            "text_type": "plain",
                            "operation": "query",
                            "sequence": 1
                        }
                    }
                    headers = {"Authorization": f"Bearer;{VOLCENGINE_TOKEN}"}
                    resp = requests.post(
                        "https://openspeech.bytedance.com/api/v1/tts",
                        json=payload,
                        headers=headers,
                        timeout=30,
                    )

                    resp.raise_for_status()
                    data = resp.json()

                    logger.debug("data.get('code'): %s", data.get("code"))

                    # if data.get("code") != 0:
                    #     raise RuntimeError(data)
                    audio_data = base64.b64decode(data["data"])
                break
            except Exception as e:
                msg = str(e).lower()
                if (
                    "rate limit" in msg
                    or "status_code" in msg and "1002" in msg
                    or "429" in msg
                ):
                    logger.warning(
                        "Rate limit encountered, sleeping %.1f seconds", delay
                    )
                    time.sleep(delay)
                    delay = min(delay * 2, 60)
                    continue
                raise

        logger.debug("Writing audio file to %s", out_path)
        with open(out_path, 'wb') as af:
            af.write(audio_data)
        audio_files.append(out_path)

    # Concatenate individual audio files into one
    combined_path = os.path.join(cfg.audio_dir, 'combined.mp3')
    logger.debug("Concatenating %d audio files into %s", len(audio_files), combined_path)
    with open(combined_path, 'wb') as outfile:
        for path in audio_files:
            with open(path, 'rb') as infile:
                outfile.write(infile.read())

    audio_files.append(combined_path)
    return audio_files

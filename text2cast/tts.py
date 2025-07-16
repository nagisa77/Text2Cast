import os
import uuid
import base64
import requests
import time
import subprocess
from .config import Config
from . import config as cfg_module
import openai
import logging
import shutil

logger = logging.getLogger(__name__)

TARGET_RATE = 44100  # output sample-rate (Hz)
TARGET_CH = 2        # channels (1 = mono, 2 = stereo)
BITRATE = 192        # average bitrate (kbps)


def convert_audio(input_path: str, output_path: str) -> None:
    """Convert audio file to the target format using ffmpeg."""
    tmp_path = output_path + ".tmp"
    if input_path != tmp_path:
        os.rename(input_path, tmp_path)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        tmp_path,
        "-ar",
        str(TARGET_RATE),
        "-ac",
        str(TARGET_CH),
        "-b:a",
        f"{BITRATE}k",
        output_path,
    ]
    subprocess.run(cmd, check=True)
    os.remove(tmp_path)


def generate_silence(output_path: str, duration: float) -> None:
    """Generate a silent MP3 file of the given duration."""
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"anullsrc=r={TARGET_RATE}:cl=stereo",
        "-t",
        str(duration),
        "-ac",
        str(TARGET_CH),
        "-b:a",
        f"{BITRATE}k",
        output_path,
    ]
    subprocess.run(cmd, check=True)


def script_to_audio(cfg: Config) -> list:
    import json

    logger.debug("Reading script JSON from %s", cfg.script_path)
    with open(cfg.script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    logger.debug("Ensuring audio directory %s exists", cfg.audio_dir)
    os.makedirs(cfg.audio_dir, exist_ok=True)

    audio_files = []

    if cfg.tts_engine == "openai":
        logger.debug("Creating OpenAI client for TTS")
        client = openai.OpenAI(api_key=cfg_module.OPENAI_API_KEY)
    elif cfg.tts_engine == "volcengine":
        logger.debug("Using Volcengine HTTP API for TTS")
        client = None
        if not cfg_module.VOLCENGINE_TOKEN or not cfg_module.VOLCENGINE_APP_ID:
            raise ValueError("VOLCENGINE_TOKEN or VOLCENGINE_APP_ID not set")
    elif cfg.tts_engine == "minimax":
        logger.debug("Using Minimax HTTP API for TTS")
        client = None
        if not cfg_module.MINIMAX_API_KEY or not cfg_module.MINIMAX_GROUP_ID:
            raise ValueError("MINIMAX_API_KEY or MINIMAX_GROUP_ID not set")
    else:
        raise ValueError(f"Unknown tts_engine: {cfg.tts_engine}")

    logger.debug("speaker_voice: %s", cfg.speaker_voice)

    for idx, item in enumerate(script):
        if item.get("type") == "sound_effect":
            se_path = item.get("path")
            if not os.path.isabs(se_path):
                se_path = os.path.join(cfg.audio_dir, se_path)
            if not os.path.exists(se_path):
                logger.warning("Sound effect %s does not exist", se_path)
            ext = os.path.splitext(se_path)[1]
            out_path = os.path.join(cfg.audio_dir, f"{idx}_sound_effect{ext}")
            try:
                shutil.copy2(se_path, out_path)
            except Exception as e:  # pragma: no cover - just log
                logger.warning("Failed to copy %s to %s: %s", se_path, out_path, e)
                out_path = se_path
            convert_audio(out_path, out_path)
            audio_files.append(out_path)
            continue
        if item.get("type") == "silent":
            duration = float(item.get("duration", 1))
            out_path = os.path.join(cfg.audio_dir, f"{idx}_silent.mp3")
            generate_silence(out_path, duration)
            audio_files.append(out_path)
            continue

        speaker = item.get("speaker", "0")
        text = item["text"]
        if str(speaker) not in cfg.speaker_voice:
            continue
        voice = cfg.speaker_voice.get(str(speaker), "alloy")
        logger.debug("speaker: %s, voice: %s", speaker, voice)
        out_path = os.path.join(cfg.audio_dir, f"{idx}_{voice}.mp3")

        logger.debug("Generating audio for item %d with voice %s", idx, voice)

        if cfg.tts_engine == "openai":
            response = client.audio.speech.create(
                model=cfg.tts_model,
                voice=voice,
                input=text,
            )
            audio_data = response.content
        elif cfg.tts_engine == "volcengine":
            logger.debug("VOLCENGINE_APP_ID: %s", cfg_module.VOLCENGINE_APP_ID)
            logger.debug("VOLCENGINE_TOKEN: %s", cfg_module.VOLCENGINE_TOKEN)
            logger.debug("tts_model: %s", cfg.tts_model)

            payload = {
                "app": {
                    "appid": cfg_module.VOLCENGINE_APP_ID,
                    "token": cfg_module.VOLCENGINE_TOKEN,
                    "cluster": cfg.tts_model,
                },
                "user": {"uid": "text2cast"},
                "audio": {
                    "voice_type": voice,
                    "encoding": "mp3",
                    "rate": 24000,
                    "speed_ratio": 1.0,
                },
                # "resource_id": "volc.tts_async.emotion",
                "request": {
                    "reqid": str(uuid.uuid4()),
                    "text": text,
                    "text_type": "plain",
                    "operation": "query",
                    "sequence": 1,
                },
            }
            headers = {"Authorization": f"Bearer;{cfg_module.VOLCENGINE_TOKEN}"}
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
            payload_data = data.get("data")
            if isinstance(payload_data, dict):
                payload_data = payload_data.get("audio")
            audio_data = base64.b64decode(payload_data)
        else:
            logger.debug("MINIMAX_GROUP_ID: %s", cfg_module.MINIMAX_GROUP_ID)
            logger.debug("tts_model: %s", cfg.tts_model)

            payload = {
                "model": cfg.tts_model,
                "text": text,
                "timber_weights": [{"voice_id": voice, "weight": 1}],
                "voice_setting": {
                    "voice_id": voice,
                    "speed": 1.2,
                    "pitch": 0,
                    "vol": 1,
                    "latex_read": False,
                },
                "audio_setting": {
                    "sample_rate": 32000,
                    "bitrate": 128000,
                    "format": "mp3",
                },
                "language_boost": "auto",
            }
            url = (
                f"https://api.minimax.chat/v1/t2a_v2?GroupId="
                f"{cfg_module.MINIMAX_GROUP_ID}"
            )
            headers = {"Authorization": f"Bearer {cfg_module.MINIMAX_API_KEY}"}

            delay = 1
            for _ in range(5):
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                if data.get("base_resp", {}).get("status_code") == 1002:
                    logger.warning(
                        "Rate limit encountered, sleeping for %s seconds", delay
                    )
                    time.sleep(delay)
                    delay = min(delay * 2, 60)
                    continue
                break
            if data.get("base_resp", {}).get("status_code") != 0:
                raise RuntimeError(data)
            audio_data = bytes.fromhex(data["data"]["audio"])

        logger.debug("Writing audio file to %s", out_path)
        tmp = out_path + ".raw"
        with open(tmp, "wb") as af:
            af.write(audio_data)
        convert_audio(tmp, out_path)
        audio_files.append(out_path)

    # Concatenate individual audio files into one
    combined_path = os.path.join(cfg.audio_dir, "combined.mp3")
    logger.debug(
        "Concatenating %d audio files into %s", len(audio_files), combined_path
    )
    with open(combined_path, "wb") as outfile:
        for path in audio_files:
            with open(path, "rb") as infile:
                outfile.write(infile.read())

    audio_files.append(combined_path)
    return audio_files

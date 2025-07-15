import base64
import os
import requests
import logging
import json
from typing import List, Dict

from . import config as cfg_module
from .config import load_env_vars

logger = logging.getLogger(__name__)


def _encode_audio_file(path: str) -> Dict[str, str]:
    """Return base64 encoded audio and format for a given file."""
    with open(path, "rb") as af:
        data = base64.b64encode(af.read()).decode("utf-8")
    fmt = os.path.splitext(path)[1].lstrip(".")
    return {"audio_bytes": data, "audio_format": fmt}


def clone_voice(samples: List[str], voice_name: str) -> str:
    """Create a custom voice with Volcengine's voice cloning service.

    Parameters
    ----------
    samples : list of str
        Paths to audio sample files used for cloning.
    voice_name : str
        Name for the new cloned voice.

    Returns
    -------
    str
        The voice_id returned by the service.
    """
    load_env_vars()
    token = cfg_module.VOLCENGINE_TOKEN
    appid = cfg_module.VOLCENGINE_APP_ID

    logger.info("VOLCENGINE_TOKEN: %s", token)
    logger.info("VOLCENGINE_APP_ID: %s", appid) 

    if not token or not appid:
        raise ValueError("VOLCENGINE_TOKEN or VOLCENGINE_APP_ID not set")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer;{token}",
        "Resource-Id": "volc.megatts.voiceclone",
    }

    audios = [_encode_audio_file(p) for p in samples]
    payload = {
        "appid": appid,
        "speaker_id": voice_name,
        "audios": audios,
        "source": 2,
        "language": 0,
        "model_type": 1,
    }

    logger.debug("Uploading %d samples for voice %s", len(samples), voice_name)
    resp = requests.post(
        "https://openspeech.bytedance.com/api/v1/mega_tts/audio/upload",
        json=payload,
        headers=headers,
        timeout=60,
    )
    resp.raise_for_status()
    logger.debug("Clone response: %s", resp.json())
    return voice_name


def get_clone_status(voice_name: str) -> dict:
    """Fetch cloning status for a voice."""
    load_env_vars()
    token = cfg_module.VOLCENGINE_TOKEN
    appid = cfg_module.VOLCENGINE_APP_ID
    if not token or not appid:
        raise ValueError("VOLCENGINE_TOKEN or VOLCENGINE_APP_ID not set")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer;{token}",
        "Resource-Id": "volc.megatts.voiceclone",
    }
    body = {"appid": appid, "speaker_id": voice_name}
    resp = requests.post(
        "https://openspeech.bytedance.com/api/v1/mega_tts/status",
        headers=headers,
        json=body,
        timeout=60,
    )
    logger.debug("resp: %s", resp.text)
    resp.raise_for_status()
    return resp.json()

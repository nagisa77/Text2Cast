import uuid
import requests
import logging
import json
from typing import List

from . import config as cfg_module
from .config import load_env_vars

logger = logging.getLogger(__name__)


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
    if not token or not appid:
        raise ValueError("VOLCENGINE_TOKEN or VOLCENGINE_APP_ID not set")

    files = [("sample", open(p, "rb")) for p in samples]

    payload = {
        "app": {
            "appid": appid,
            "token": token,
        },
        "voice_name": voice_name,
        "request": {
            "reqid": str(uuid.uuid4()),
        },
    }
    headers = {"Authorization": f"Bearer;{token}"}

    logger.debug("Sending voice clone request with %d samples", len(samples))
    resp = requests.post(
        "https://openspeech.bytedance.com/api/v1/mega_tts/audio/upload",
        headers=headers,
        files=files,
        data={"payload": json.dumps(payload)},
        timeout=60,
    )
    logger.debug("resp: %s", resp.text)
    resp.raise_for_status()
    data = resp.json()
    voice_id = data.get("data", {}).get("voice_id") or data.get("voice_id")
    logger.debug("Received voice_id: %s", voice_id)
    return voice_id

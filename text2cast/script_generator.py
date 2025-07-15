from .prompts import BRIEF2SCRIPT
from .config import Config, OPENAI_API_KEY, DEEPSEEK_API_KEY
from .utils import wash_json
import openai
import json
import logging

logger = logging.getLogger(__name__)


def brief_to_script(cfg: Config) -> list:
    logger.debug("Reading brief from %s", cfg.brief_path)
    with open(cfg.brief_path, "r", encoding="utf-8") as f:
        text = f.read()

    logger.debug("Creating OpenAI client for script generation")
    if cfg.chat_engine == "deepseek":
        client = openai.OpenAI(
            api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"
        )
    else:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

    logger.debug("Sending script generation request")
    resp = client.chat.completions.create(
        model=cfg.model_script,
        messages=[
            {"role": "system", "content": BRIEF2SCRIPT},
            {"role": "user", "content": text},
        ],
    )
    script_text = resp.choices[0].message.content.strip()
    logger.debug("Received script text: %s", script_text)

    logger.debug("Is script_text a string? %s", isinstance(script_text, str))

    script = json.loads(wash_json(script_text))

    # Ensure every entry has a type field for downstream processing
    for item in script:
        item.setdefault("type", "tts")

    with open(cfg.script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    return script

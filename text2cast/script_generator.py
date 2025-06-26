from .prompts import BRIEF2SCRIPT
from .config import Config, OPENAI_API_KEY
from .utils import wash_json
import openai
import json


def brief_to_script(cfg: Config) -> list:
    with open(cfg.brief_path, 'r', encoding='utf-8') as f:
        text = f.read()
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=cfg.model_script,
        messages=[{"role": "system", "content": BRIEF2SCRIPT}, {"role": "user", "content": text}],
    )
    script_text = resp.choices[0].message.content.strip()
    script = json.loads(wash_json(script_text))
    with open(cfg.script_path, 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    return script

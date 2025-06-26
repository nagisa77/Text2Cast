from .prompts import INPUT2BRIEF
from .config import Config, OPENAI_API_KEY
import openai


def input_to_brief(cfg: Config) -> str:
    with open(cfg.input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=cfg.model_summary,
        messages=[{"role": "system", "content": INPUT2BRIEF}, {"role": "user", "content": text}],
    )
    brief = resp.choices[0].message.content.strip()
    with open(cfg.brief_path, 'w', encoding='utf-8') as f:
        f.write(brief)
    return brief

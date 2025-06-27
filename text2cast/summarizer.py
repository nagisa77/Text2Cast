from .prompts import INPUT2BRIEF
from .config import Config, OPENAI_API_KEY, DEEPSEEK_API_KEY
import openai
import logging

logger = logging.getLogger(__name__)


def input_to_brief(cfg: Config) -> str:
    logger.debug("Reading input text from %s", cfg.input_path)
    with open(cfg.input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    logger.debug("Creating OpenAI client for summarization")
    if cfg.chat_engine == "deepseek":
        client = openai.OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
    else:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

    logger.debug("Sending summarization request")
    resp = client.chat.completions.create(
        model=cfg.model_summary,
        messages=[{"role": "system", "content": INPUT2BRIEF}, {"role": "user", "content": text}],
    )
    brief = resp.choices[0].message.content.strip()
    logger.debug("Received summary with %d characters", len(brief))

    logger.debug("Writing summary to %s", cfg.brief_path)
    with open(cfg.brief_path, 'w', encoding='utf-8') as f:
        f.write(brief)
    return brief

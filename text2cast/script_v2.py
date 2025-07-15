import json
import logging
from typing import List, Dict

import openai
from firecrawl import FirecrawlApp

from .config import Config, OPENAI_API_KEY, DEEPSEEK_API_KEY

logger = logging.getLogger(__name__)


def urls_to_script(cfg: Config) -> List[Dict[str, str]]:
    """Generate script entries from article URLs.

    The input file specified by ``cfg.input_path`` must be a JSON file with
    ``global`` and ``local`` lists, each containing objects with ``title`` and
    ``url`` fields.
    """
    logger.debug("Reading articles from %s", cfg.input_path)
    with open(cfg.input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("global", []) + data.get("local", [])

    if not articles:
        raise ValueError("No articles found in input file")

    logger.debug("Creating Firecrawl client")
    fc = FirecrawlApp()

    logger.debug("Creating OpenAI client for summarization")
    if cfg.chat_engine == "deepseek":
        client = openai.OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    else:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

    script: List[Dict[str, str]] = []
    speaker = 1

    for article in articles:
        title = article.get("title", "")
        url = article.get("url")
        logger.info("Processing %s", url)

        content = ""
        try:
            result = fc.scrape_url(url, formats=["markdown"])
            content = result.markdown or ""
        except Exception as e:
            logger.warning("Failed to scrape %s: %s", url, e)

        summary = ""
        if content:
            try:
                prompt = f"请用中文用1-2句话总结这篇文章的主要内容：{content}. 不要超过100字。 不要以‘这片文章讲了...’开头，直接简练总结。"
                resp = client.chat.completions.create(
                    model=cfg.model_script,
                    messages=[{"role": "user", "content": prompt}],
                )
                summary = resp.choices[0].message.content.strip()
            except Exception as e:
                logger.warning("Failed to summarize %s: %s", url, e)

        text = f"{title} {summary}".strip()
        script.append({"speaker": str(speaker), "text": text})
        speaker = 1 if speaker == 2 else 2

    logger.debug("Writing script to %s", cfg.script_path)
    with open(cfg.script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    return script

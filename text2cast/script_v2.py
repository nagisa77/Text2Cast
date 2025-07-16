import json
import logging
from typing import List, Dict
from datetime import date

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

    global_articles = data.get("global", [])
    local_articles = data.get("local", [])

    if not global_articles and not local_articles:
        raise ValueError("No articles found in input file")

    logger.debug("Creating Firecrawl client")
    fc = FirecrawlApp()

    logger.debug("Creating OpenAI client for summarization")
    if cfg.chat_engine == "deepseek":
        client = openai.OpenAI(
            api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"
        )
    else:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

    script: List[Dict[str, str]] = []

    # Opening lines with current date
    today = date.today()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_str = f"{today.year}年{today.month}月{today.day}号{weekdays[today.weekday()]}"

    script.append(
        {"speaker": "1", "text": "全球视野，本土洞察！各位早上好,", "type": "tts"}
    )
    script.append(
        {
            "speaker": "2",
            "text": f"早上好，今天是{date_str}，这里是UU早报，数据说话，观点交锋，现在开始——",
            "type": "tts",
        }
    )
    intro_path = cfg.sound_effects.get("intro", "intro.mp3")
    script.append({"type": "sound_effect", "path": intro_path})

    speaker = 1

    for article in global_articles:
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
                prompt = f"""
#目标
你是一名资深的日报编辑，尤其擅长将不论长短的资讯事件提炼要点，总结精准，帮助读者快速了解文章的内容，以确定是否需要继续阅读文章。

#背景
现在我们总结每件热门新闻，制作成日晚报播报给用户

#限制
  1. 字数要求：总结的长度根据原文长度而灵活调整，原文长则总结可长，原文短则总结可短，字符数（不计空格）最多不超过150字。
  2. 语言要求：中文，书面语。允许少部分实体名词、专有名词、缩写等使用英文。
  3. 专有名词：不要修改原文的任何实体名词、专有名词、缩写等。除非有常见译名，否则不要翻译实体名词。不要试图修改实体名词意思。
  4. 内容要求：完整且准确地提炼事件概要，不压缩不省略不灌水，也不要包含任何额外信息。
  5. 输出要求：输出新闻总结本身即可，不要备注、说明等信息

#原文
{content}
"""
                resp = client.chat.completions.create(
                    model=cfg.model_script,
                    messages=[{"role": "user", "content": prompt}],
                )
                summary = resp.choices[0].message.content.strip()
            except Exception as e:
                logger.warning("Failed to summarize %s: %s", url, e)

        if title:
            script.append({"speaker": str(speaker), "text": title, "type": "tts"})
            script.append({"type": "silent", "duration": 0.5, "direction": "after_title"})
        if summary:
            script.append({"speaker": str(speaker), "text": summary, "type": "tts"})
        article_end = cfg.sound_effects.get("article_end", "article_end.mp3")
        script.append({"type": "sound_effect", "path": article_end})
        speaker = 1 if speaker == 2 else 2

    if local_articles:
        transition = cfg.sound_effects.get("transition", "transition.mp3")
        script.append({"type": "sound_effect", "path": transition})

    for article in local_articles:
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
                prompt = f"请用中文用1-2句话总结这篇文章的主要内容：{content}"
                resp = client.chat.completions.create(
                    model=cfg.model_script,
                    messages=[{"role": "user", "content": prompt}],
                )
                summary = resp.choices[0].message.content.strip()
            except Exception as e:
                logger.warning("Failed to summarize %s: %s", url, e)

        if title:
            script.append({"speaker": str(speaker), "text": title, "type": "tts"})
            script.append({"type": "silent", "duration": 0.5, "direction": "after_title"})
        if summary:
            script.append({"speaker": str(speaker), "text": summary, "type": "tts"})
        article_end = cfg.sound_effects.get("article_end", "article_end.mp3")
        script.append({"type": "sound_effect", "path": article_end})
        speaker = 1 if speaker == 2 else 2

    script.append(
        {
            "speaker": str(speaker),
            "text": "感谢您的收听，以上就是UU早报的全部内容，欢迎搜索订阅UU早晚报，晚上见。",
            "type": "tts",
        }
    )
    speaker = 1 if speaker == 2 else 2
    script.append(
        {
            "speaker": str(speaker),
            "text": "别走开，马上和你一起来了解不断飙升的日本大米价格……",
            "type": "tts",
        }
    )
    outro_path = cfg.sound_effects.get("outro", "outro.mp3")
    script.append({"type": "sound_effect", "path": outro_path})

    logger.debug("Writing script to %s", cfg.script_path)
    with open(cfg.script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    return script

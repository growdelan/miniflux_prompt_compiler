import logging
import time
from collections.abc import Callable

import requests

from miniflux_prompt_compiler.types import ContentFetchError


def fetch_article_markdown(url: str, timeout: int = 15, retries: int = 3) -> str:
    logging.info("Jina: start")
    request_url = f"https://r.jina.ai/{url}"
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(request_url, timeout=timeout)
            response.raise_for_status()
            content = response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1)
                continue
            raise ContentFetchError(
                f"Nie udalo sie pobrac tresci artykulu: {exc}"
            ) from exc

        # Decyzja: pusta tresc traktujemy jako porazke, bo nie ma czego uzyc dalej.
        if content.strip():
            return content
        last_error = ContentFetchError("Pusta tresc z jina.ai")
        if attempt < retries:
            time.sleep(1)
            continue
        break

    raise ContentFetchError(f"Nie udalo sie pobrac tresci artykulu: {last_error}")


def fetch_article_with_fallback(
    url: str,
    use_playwright: bool,
    fallback_fetcher: Callable[[str], str] | None = None,
) -> str:
    try:
        content = fetch_article_markdown(url)
        logging.info("Content source selected: jina")
        return content
    except ContentFetchError as exc:
        logging.info("Jina: error (%s)", exc)
        if not use_playwright or fallback_fetcher is None:
            raise
        content = fallback_fetcher(url)
        logging.info("Content source selected: playwright")
        return content

import logging
import time
import urllib.error
import urllib.request


def fetch_article_markdown(url: str, timeout: int = 15, retries: int = 3) -> str:
    logging.info("Jina: start")
    request_url = f"https://r.jina.ai/{url}"
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request_url, timeout=timeout) as response:
                content = response.read().decode("utf-8", errors="replace")
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1)
                continue
            raise RuntimeError(f"Nie udalo sie pobrac tresci artykulu: {exc}") from exc

        # Decyzja: pusta tresc traktujemy jako porazke, bo nie ma czego uzyc dalej.
        if content.strip():
            return content
        last_error = RuntimeError("Pusta tresc z jina.ai")
        if attempt < retries:
            time.sleep(1)
            continue
        break

    raise RuntimeError(f"Nie udalo sie pobrac tresci artykulu: {last_error}")

import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"").strip("'")
    return values


def fetch_unread_entries(
    base_url: str, token: str, timeout: int = 10
) -> list[dict[str, object]]:
    # Miniflux API endpoint przyjmujemy w najprostszym wariancie: /v1/entries?status=unread.
    url = f"{base_url.rstrip('/')}/v1/entries?status=unread"
    request = urllib.request.Request(url, headers={"X-Auth-Token": token})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Nie udalo sie pobrac wpisow: {exc}") from exc

    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise RuntimeError("Nieprawidlowy format odpowiedzi Miniflux (brak listy entries).")
    return entries


def is_youtube_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    return host in {"youtube.com", "www.youtube.com", "youtu.be"}


def is_youtube_shorts(url: str) -> bool:
    parsed = urlparse(url)
    return "/shorts/" in parsed.path


def extract_youtube_id(url: str) -> str | None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host in {"youtube.com", "www.youtube.com"}:
        if parsed.path != "/watch":
            return None
        query = parse_qs(parsed.query)
        video_ids = query.get("v", [])
        return video_ids[0] if video_ids else None
    if host == "youtu.be":
        return parsed.path.lstrip("/") or None
    return None


def fetch_article_markdown(url: str, timeout: int = 15, retries: int = 3) -> str:
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


def fetch_youtube_transcript(video_id: str, preferred_language: str = "en") -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise RuntimeError("Brak zaleznosci youtube_transcript_api w srodowisku.") from exc

    try:
        # Decyzja: obslugujemy oba API (stare get_transcript i nowe fetch),
        # bo biblioteka zmieniala sposob wywolania miedzy wersjami.
        get_transcript = getattr(YouTubeTranscriptApi, "get_transcript", None)
        fetch = getattr(YouTubeTranscriptApi, "fetch", None)
        if callable(get_transcript):
            transcript = get_transcript(video_id, languages=[preferred_language])
        elif callable(fetch):
            transcript = YouTubeTranscriptApi().fetch(
                video_id, languages=[preferred_language]
            )
        else:
            raise RuntimeError("Nieznany interfejs youtube_transcript_api.")
    except Exception as exc:  # youtube_transcript_api rzuca kilka typow wyjatkow
        raise RuntimeError(f"Brak transkrypcji YouTube: {exc}") from exc

    if hasattr(transcript, "snippets"):
        lines = [snippet.text for snippet in transcript]
    else:
        lines = [item.get("text", "") for item in transcript]
    content = " ".join(line for line in lines if line)
    if not content.strip():
        raise RuntimeError("Pusta transkrypcja YouTube.")
    return content


def process_entry(
    entry: dict[str, object],
    article_fetcher: Callable[[str], str],
    youtube_fetcher: Callable[[str], str],
) -> tuple[bool, str | None]:
    title = str(entry.get("title", "")).strip()
    url = str(entry.get("url", "")).strip()
    if not url:
        return False, None

    logging.info("Start: %s", title or url)
    if is_youtube_url(url):
        if is_youtube_shorts(url):
            logging.info("Pomijam: YouTube Shorts")
            return False, None
        video_id = extract_youtube_id(url)
        if not video_id:
            logging.info("Niepoprawny link YouTube")
            return False, None
        logging.info("Typ: YouTube")
        content = youtube_fetcher(video_id)
        return True, content

    logging.info("Typ: artykul")
    content = article_fetcher(url)
    return True, content


def run(
    env_path: Path = Path(".env"),
    environ: dict[str, str] | None = None,
    fetcher: Callable[[str, str], list[dict[str, object]]] | None = None,
    article_fetcher: Callable[[str], str] | None = None,
    youtube_fetcher: Callable[[str], str] | None = None,
) -> str:
    env = environ or os.environ
    file_env = load_env(env_path)
    token = env.get("MINIFLUX_API_TOKEN") or file_env.get("MINIFLUX_API_TOKEN")
    if not token:
        raise RuntimeError(
            "Brak MINIFLUX_API_TOKEN w srodowisku lub w pliku .env w katalogu projektu."
        )

    base_url = "http://192.168.0.209:8111"
    fetcher = fetcher or fetch_unread_entries
    entries = fetcher(base_url, token)
    logging.info("Pobrano %d wpisow unread.", len(entries))
    article_fetcher = article_fetcher or fetch_article_markdown
    youtube_fetcher = youtube_fetcher or fetch_youtube_transcript

    success = 0
    failed = 0
    skipped = 0
    for entry in entries:
        try:
            processed, _content = process_entry(
                entry, article_fetcher=article_fetcher, youtube_fetcher=youtube_fetcher
            )
        except RuntimeError as exc:
            logging.info("Blad: %s", exc)
            failed += 1
            continue

        if processed:
            logging.info("Sukces")
            success += 1
        else:
            skipped += 1

    # Decyzja: na tym etapie zwracamy tylko podsumowanie, bez budowania promptu.
    return f"Unread entries: {len(entries)}; Success: {success}; Failed: {failed}; Skipped: {skipped}"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        message = run()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import logging
import os
from collections.abc import Callable
from pathlib import Path

from miniflux_prompt_compiler.adapters.clipboard import copy_to_clipboard
from miniflux_prompt_compiler.adapters.jina import fetch_article_with_fallback
from miniflux_prompt_compiler.adapters.miniflux_http import (
    fetch_unread_entries,
    mark_entry_read,
)
from miniflux_prompt_compiler.adapters.playwright_fetch import (
    fetch_article_with_playwright,
)
from miniflux_prompt_compiler.adapters.youtube import fetch_youtube_transcript
from miniflux_prompt_compiler.config import load_env
from miniflux_prompt_compiler.core.chunking import build_prompts_with_chunking
from miniflux_prompt_compiler.core.prompting import build_prompt
from miniflux_prompt_compiler.core.tokenization import (
    MAX_PROMPT_TOKENS,
    count_tokens,
    label_for_tokens,
)
from miniflux_prompt_compiler.core.url_classify import (
    extract_youtube_id,
    is_youtube_shorts,
    is_youtube_url,
)
from miniflux_prompt_compiler.types import MinifluxEntry, ProcessedItem


def process_entry(
    entry: MinifluxEntry,
    article_fetcher: Callable[[str], str],
    youtube_fetcher: Callable[[str], str],
) -> tuple[bool, ProcessedItem | None]:
    title = (entry.get("title") or "").strip()
    url = (entry.get("url") or "").strip()
    if not url:
        logging.info("Brak URL, pomijam wpis.")
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
        return True, ProcessedItem(title=title, content=content)

    logging.info("Typ: artykul")
    content = article_fetcher(url)
    return True, ProcessedItem(title=title, content=content)


def run(
    env_path: Path = Path(".env"),
    environ: dict[str, str] | None = None,
    fetcher: Callable[[str, str], list[MinifluxEntry]] | None = None,
    article_fetcher: Callable[[str], str] | None = None,
    youtube_fetcher: Callable[[str], str] | None = None,
    marker: Callable[[str, str, int], None] | None = None,
    clipboard: Callable[[str], None] | None = None,
    use_playwright: bool = False,
    interactive: bool = True,
    input_reader: Callable[[], str] | None = None,
    max_tokens: int = MAX_PROMPT_TOKENS,
    tokenizer: str = "auto",
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
    if article_fetcher is None:
        if use_playwright:
            article_fetcher = lambda url: fetch_article_with_fallback(
                url,
                use_playwright=True,
                fallback_fetcher=fetch_article_with_playwright,
            )
        else:
            article_fetcher = lambda url: fetch_article_with_fallback(
                url, use_playwright=False
            )
    youtube_fetcher = youtube_fetcher or fetch_youtube_transcript
    marker = marker or mark_entry_read
    clipboard = clipboard or copy_to_clipboard

    success = 0
    failed = 0
    skipped = 0
    processed_items: list[ProcessedItem] = []
    for entry in entries:
        try:
            processed, item = process_entry(
                entry, article_fetcher=article_fetcher, youtube_fetcher=youtube_fetcher
            )
        except RuntimeError as exc:
            logging.info("Blad: %s", exc)
            failed += 1
            continue

        if processed:
            entry_id_raw = entry.get("id")
            try:
                entry_id = int(entry_id_raw) if entry_id_raw is not None else 0
            except (TypeError, ValueError):
                entry_id = 0
            if not entry_id:
                logging.info("Brak ID wpisu, pomijam oznaczanie jako read.")
            else:
                try:
                    marker(base_url, token, entry_id)
                    logging.info("Oznaczono jako read: %s", entry_id)
                except RuntimeError as exc:
                    logging.info("Blad oznaczania read: %s", exc)
            logging.info("Sukces")
            success += 1
            if item is not None:
                processed_items.append(item)
        else:
            skipped += 1

    full_prompt = build_prompt(processed_items)
    prompts = build_prompts_with_chunking(
        processed_items, max_tokens=max_tokens, tokenizer=tokenizer
    )
    summary = (
        f"Unread entries: {len(entries)}; Success: {success}; "
        f"Failed: {failed}; Skipped: {skipped}"
    )
    if not full_prompt or not prompts:
        logging.info("Brak przetworzonych wpisow, schowek nie jest nadpisywany.")
        return summary

    total_tokens = count_tokens(full_prompt, tokenizer=tokenizer)
    total_label = label_for_tokens(total_tokens)

    if len(prompts) == 1:
        if interactive:
            clipboard(prompts[0])
        else:
            token_count = count_tokens(prompts[0], tokenizer=tokenizer)
            label = label_for_tokens(token_count)
            print(f"Prompt 1/1 ({token_count} tokenow - {label})")
            print(prompts[0])
        return f"{summary}; Tokens: {total_tokens}; Label: {total_label}"

    print(f"Total tokens: {total_tokens} -> {total_label}")
    print(f"Generated prompts: {len(prompts)}")
    if interactive:
        input_reader = input_reader or (lambda: input())
        for index, prompt in enumerate(prompts, start=1):
            print(f"Press [Enter] to copy prompt {index}/{len(prompts)}")
            input_reader()
            clipboard(prompt)
            token_count = count_tokens(prompt, tokenizer=tokenizer)
            label = label_for_tokens(token_count)
            print(
                f"Copied prompt {index}/{len(prompts)} "
                f"({token_count} tokenow - {label})"
            )
    else:
        for index, prompt in enumerate(prompts, start=1):
            token_count = count_tokens(prompt, tokenizer=tokenizer)
            label = label_for_tokens(token_count)
            print(f"Prompt {index}/{len(prompts)} ({token_count} tokenow - {label})")
            print(prompt)

    return (
        f"{summary}; Prompts: {len(prompts)}; "
        f"Tokens: {total_tokens}; Label: {total_label}"
    )

import argparse
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from subprocess import CalledProcessError, run as run_process
from urllib.parse import parse_qs, urlparse

PROMPT = """
<Cel>
Twoim celem jest dogłębna analiza listy artykułów oraz transkrypcji i stworzenie merytorycznych, blogowych podsumowań, które oddają sens i wartość treści, a nie tylko skrót faktów.
</Cel>

<Instrukcje>
- Wciel się w rolę **doświadczonego blogera eksperckiego i redaktora technicznego**.
- Otrzymasz listę materiałów, z których każdy ma format:
  - `Tytuł: <tytuł>`
  - `Treść: <pełna treść artykułu lub transkrypcji>`
- Przeanalizuj **każdy materiał osobno**.
- Zidentyfikuj kluczowe idee, problemy, rozwiązania i ich znaczenie.
- Dla każdego tekstu przygotuj **dokładnie 5 punktów**.
- Każdy punkt:
  - ma być **rozwiniętym mini-akapitem (2–4 zdania)**,
  - zaczynać się od krótkiej tezy,
  - następnie wyjaśniać kontekst,
  - oraz wskazywać, dlaczego jest to istotne dla czytelnika.
- Styl ma być **blogowy, opisowy i podobny do podanego przykładu** – nie encyklopedyczny i nie skrótowy.
- Unikaj parafrazowania całych fragmentów – skup się na syntezie i wnioskach.
- Nie dodawaj własnych tematów ani spekulacji poza treścią źródłową.
</Instrukcje>

<Kontekst>
Podsumowania mają pozwolić czytelnikowi zrozumieć temat bez czytania całości artykułu, ale jednocześnie oddać jego głębię, problemy i praktyczne konsekwencje. Każdy punkt powinien czytać się jak fragment wpisu blogowego.
</Kontekst>

<Format_odpowiedzi>
💡Tytuł: <oryginalny tytuł>

- 🎯 **1.** <rozwinięty akapit blogowy>
- 🎯 **2.** <rozwinięty akapit blogowy>
- 🎯 **3.** <rozwinięty akapit blogowy>
- 🎯 **4.** <rozwinięty akapit blogowy>
- 🎯 **5.** <rozwinięty akapit blogowy>

Nie dodawaj żadnych innych sekcji ani komentarzy.
</Format_odpowiedzi>
"""

TOKEN_LABELS = (
    (32000, "GPT-Instant"),
    (50000, "GPT-Thinking"),
)
MAX_PROMPT_TOKENS = 50_000
TOKENIZER_OPTIONS = {"auto", "tiktoken", "approx"}


def count_tokens(text: str, tokenizer: str = "auto") -> int:
    if tokenizer not in TOKENIZER_OPTIONS:
        raise ValueError(f"Nieznany tokenizer: {tokenizer}")

    if tokenizer in {"auto", "tiktoken"}:
        try:
            import tiktoken
        except ImportError as exc:
            if tokenizer == "tiktoken":
                raise RuntimeError(
                    "Tokenizer tiktoken nie jest dostepny w srodowisku."
                ) from exc
            logging.info("Tokenizer: approx (fallback, wynik szacunkowy)")
            return max(1, len(text) // 4)
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    logging.info("Tokenizer: approx (wynik szacunkowy)")
    return max(1, len(text) // 4)


def label_for_tokens(count: int) -> str:
    for limit, label in TOKEN_LABELS:
        if count < limit:
            return label
    return "CHUNKING"


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
        values[key.strip()] = value.strip().strip('"').strip("'")
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
        raise RuntimeError(
            "Nieprawidlowy format odpowiedzi Miniflux (brak listy entries)."
        )
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


def fetch_article_with_fallback(
    url: str,
    use_playwright: bool,
    fallback_fetcher: Callable[[str], str] | None = None,
) -> str:
    try:
        content = fetch_article_markdown(url)
        logging.info("Content source selected: jina")
        return content
    except RuntimeError as exc:
        logging.info("Jina: error (%s)", exc)
        if not use_playwright or fallback_fetcher is None:
            raise
        content = fallback_fetcher(url)
        logging.info("Content source selected: playwright")
        return content


def fetch_article_with_playwright(url: str, timeout: int = 20) -> str:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Brak zaleznosci playwright w srodowisku.") from exc

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                logging.info("Playwright: start %s", url)
                page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
            except PlaywrightTimeoutError as exc:
                logging.info("Playwright: failed (timeout)")
                raise RuntimeError(f"Playwright timeout: {exc}") from exc

            consent_pattern = re.compile(
                r"^(accept|agree|accept all|i agree|zgadzam sie|akceptuj)$",
                re.IGNORECASE,
            )
            try:
                consent_button = page.get_by_role("button", name=consent_pattern)
                if consent_button.count() > 0:
                    consent_button.first.click(timeout=2000)
                    logging.info("Playwright: cookie-consent clicked")
            except Exception:
                pass

            content = page.evaluate(
                "() => (document.body && document.body.innerText) || ''"
            )
            if not isinstance(content, str) or not content.strip():
                logging.info("Playwright: failed (empty content)")
                raise RuntimeError("Pusta tresc z Playwrighta.")
            logging.info("Playwright: success (%d)", len(content))
            return content
    except RuntimeError:
        raise
    except Exception as exc:
        logging.info("Playwright: failed (%s)", exc)
        raise RuntimeError(f"Nie udalo sie pobrac tresci Playwright: {exc}") from exc


def fetch_youtube_transcript(video_id: str, preferred_language: str = "en") -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise RuntimeError(
            "Brak zaleznosci youtube_transcript_api w srodowisku."
        ) from exc

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


def mark_entry_read(
    base_url: str, token: str, entry_id: int, timeout: int = 10
) -> None:
    # Decyzja: probujemy kilka wariantow API (PUT/POST i inny endpoint),
    # bo instalacje Miniflux moga roznic sie obsluga tej operacji.
    attempts = [
        (
            "PUT",
            f"{base_url.rstrip('/')}/v1/entries?status=read",
            {"entry_ids": [entry_id]},
        ),
        (
            "PUT",
            f"{base_url.rstrip('/')}/v1/entries",
            {"entry_ids": [entry_id], "status": "read"},
        ),
        (
            "POST",
            f"{base_url.rstrip('/')}/v1/entries?status=read",
            {"entry_ids": [entry_id]},
        ),
        (
            "PUT",
            f"{base_url.rstrip('/')}/v1/entries/{entry_id}",
            {"status": "read"},
        ),
    ]
    for index, (method, url, payload_dict) in enumerate(attempts):
        payload = json.dumps(payload_dict).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            method=method,
            headers={"X-Auth-Token": token, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout):
                return
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 404} and index < len(attempts) - 1:
                continue
            raise RuntimeError(
                f"Nie udalo sie oznaczyc wpisu {entry_id} jako read: {exc}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Nie udalo sie oznaczyc wpisu {entry_id} jako read: {exc}"
            ) from exc


def copy_to_clipboard(text: str) -> None:
    try:
        run_process(["pbcopy"], input=text, text=True, check=True)
    except (CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError(f"Nie udalo sie skopiowac do schowka: {exc}") from exc


def build_prompt(items: list[dict[str, str]]) -> str:
    if not items:
        return ""

    sections: list[str] = []
    for item in items:
        title = item.get("title", "")
        content = item.get("content", "")
        section = f"---\n\nTytuł: {title}\nTreść:\n{content}"
        sections.append(section)
    items_block = "\n\n".join(sections)
    return (
        f"{PROMPT}\n\n"
        "<lista_artykułów_i_transkrypcji>\n"
        f"{items_block}\n"
        "</lista_artykułów_i_transkrypcji>"
    )


def build_prompts_with_chunking(
    items: list[dict[str, str]], max_tokens: int, tokenizer: str = "auto"
) -> list[str]:
    prompts: list[str] = []
    current: list[dict[str, str]] = []

    for item in items:
        current.append(item)
        prompt = build_prompt(current)
        if not prompt:
            current.pop()
            continue
        if count_tokens(prompt, tokenizer=tokenizer) <= max_tokens:
            continue

        current.pop()
        if current:
            prompts.append(build_prompt(current))
            current = [item]
            prompt = build_prompt(current)
            if prompt and count_tokens(prompt, tokenizer=tokenizer) <= max_tokens:
                continue

        logging.info("Item exceeds max token limit and was skipped")
        current = []

    if current:
        prompts.append(build_prompt(current))

    return prompts


def process_entry(
    entry: dict[str, object],
    article_fetcher: Callable[[str], str],
    youtube_fetcher: Callable[[str], str],
) -> tuple[bool, str | None, str | None]:
    title = str(entry.get("title", "")).strip()
    url = str(entry.get("url", "")).strip()
    if not url:
        logging.info("Brak URL, pomijam wpis.")
        return False, None, None

    logging.info("Start: %s", title or url)
    if is_youtube_url(url):
        if is_youtube_shorts(url):
            logging.info("Pomijam: YouTube Shorts")
            return False, None, None
        video_id = extract_youtube_id(url)
        if not video_id:
            logging.info("Niepoprawny link YouTube")
            return False, None, None
        logging.info("Typ: YouTube")
        content = youtube_fetcher(video_id)
        return True, title, content

    logging.info("Typ: artykul")
    content = article_fetcher(url)
    return True, title, content


def run(
    env_path: Path = Path(".env"),
    environ: dict[str, str] | None = None,
    fetcher: Callable[[str, str], list[dict[str, object]]] | None = None,
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
    processed_items: list[dict[str, str]] = []
    for entry in entries:
        try:
            processed, title, content = process_entry(
                entry, article_fetcher=article_fetcher, youtube_fetcher=youtube_fetcher
            )
        except RuntimeError as exc:
            logging.info("Blad: %s", exc)
            failed += 1
            continue

        if processed:
            entry_id = int(entry.get("id", 0))
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
            if title is not None and content is not None:
                processed_items.append({"title": title, "content": content})
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Miniflux Prompt Compiler")
    parser.add_argument(
        "--playwright",
        action="store_true",
        help="Wlacz fallback Playwright po bledzie Jiny.",
    )
    interactive_group = parser.add_mutually_exclusive_group()
    interactive_group.add_argument(
        "--interactive",
        action="store_true",
        dest="interactive",
        help="Wlacz tryb interaktywny kopiowania promptow.",
    )
    interactive_group.add_argument(
        "--no-interactive",
        action="store_false",
        dest="interactive",
        help="Wylacz tryb interaktywny (wypisz prompty do stdout).",
    )
    parser.set_defaults(interactive=True)
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=MAX_PROMPT_TOKENS,
        help="Maksymalna liczba tokenow na prompt (domyslnie 50000).",
    )
    parser.add_argument(
        "--tokenizer",
        choices=sorted(TOKENIZER_OPTIONS),
        default="auto",
        help="Wybor tokenizera: auto, tiktoken, approx.",
    )
    return parser.parse_args(argv)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        args = parse_args(sys.argv[1:])
        message = run(
            use_playwright=args.playwright,
            interactive=args.interactive,
            max_tokens=args.max_tokens,
            tokenizer=args.tokenizer,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

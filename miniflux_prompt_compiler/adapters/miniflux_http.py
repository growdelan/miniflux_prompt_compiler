import json
import socket
import urllib.error
import urllib.parse
import urllib.request

from miniflux_prompt_compiler.types import ContentFetchError, MinifluxEntry, MinifluxError


def fetch_unread_entries(
    base_url: str, token: str, timeout: int = 10
) -> list[MinifluxEntry]:
    # Miniflux API endpoint przyjmujemy w najprostszym wariancie: /v1/entries?status=unread.
    url = f"{base_url.rstrip('/')}/v1/entries?status=unread"
    request = urllib.request.Request(url, headers={"X-Auth-Token": token})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise MinifluxError(f"Nie udalo sie pobrac wpisow: {exc}") from exc

    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise MinifluxError(
            "Nieprawidlowy format odpowiedzi Miniflux (brak listy entries)."
        )
    return entries


def mark_entry_read(
    base_url: str, token: str, entry_id: int, timeout: int = 10
) -> None:
    url = f"{base_url.rstrip('/')}/v1/entries"
    payload = json.dumps({"entry_ids": [entry_id], "status": "read"}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        method="PUT",
        headers={"X-Auth-Token": token, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout):
            return
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise MinifluxError(
            f"Nie udalo sie oznaczyc wpisu {entry_id} jako read: {exc}"
        ) from exc


def fetch_entry_content(
    base_url: str, token: str, entry_id: int, timeout: int = 10
) -> str:
    query = urllib.parse.urlencode({"update_content": "true"})
    url = (
        f"{base_url.rstrip('/')}/v1/entries/{entry_id}/fetch-content?{query}"
    )
    request = urllib.request.Request(url, headers={"X-Auth-Token": token})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (
        urllib.error.URLError,
        TimeoutError,
        socket.timeout,
        json.JSONDecodeError,
    ) as exc:
        raise ContentFetchError(
            f"Nie udalo sie pobrac tresci z Miniflux fetch-content: {exc}"
        ) from exc

    content = payload.get("content")
    if not isinstance(content, str):
        raise ContentFetchError(
            "Nieprawidlowy format odpowiedzi Miniflux fetch-content (brak content)."
        )
    if not content.strip():
        raise ContentFetchError("Pusta tresc z Miniflux fetch-content.")
    return content

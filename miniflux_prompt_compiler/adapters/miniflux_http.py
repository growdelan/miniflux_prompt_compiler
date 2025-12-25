import json
import urllib.error
import urllib.request

from miniflux_prompt_compiler.types import MinifluxEntry, MinifluxError


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
            raise MinifluxError(
                f"Nie udalo sie oznaczyc wpisu {entry_id} jako read: {exc}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MinifluxError(
                f"Nie udalo sie oznaczyc wpisu {entry_id} jako read: {exc}"
            ) from exc

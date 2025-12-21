import json
import logging
import os
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path


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


def run(
    env_path: Path = Path(".env"),
    environ: dict[str, str] | None = None,
    fetcher: Callable[[str, str], list[dict[str, object]]] | None = None,
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
    return f"Unread entries: {len(entries)}"


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

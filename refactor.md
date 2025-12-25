# Instrukcja refactoru (AI‑friendly) – plan zmian

Cel: uporządkować projekt tak, aby był łatwiejszy do utrzymania i refaktoryzowania przez inne AI/agentów oraz stabilniejszy w przyszłych zmianach. Priorytet: minimalna zmiana logiki, maksymalna poprawa struktury i kontraktów danych.

## Zasady refactoru

* **Nie zmieniaj zachowania funkcjonalnego** (poza naprawą oczywistych kruchych miejsc). Po każdej większej zmianie uruchom testy.
* **Oddziel warstwy**:

  * `core/` – czysta logika (bez sieci, bez systemu, bez schowka),
  * `adapters/` – I/O (Miniflux HTTP, Jina, Playwright, clipboard),
  * `cli.py` – argumenty i uruchomienie.
* **Wprowadź kontrakty danych** (TypedDict lub dataclass) dla:

  * wpisu Miniflux (`MinifluxEntry`),
  * przetworzonego elementu do promptu (`ProcessedItem`).
* **Ujednolić sposób logowania**: preferuj `logging` jako single source of truth; `print()` tylko do wypisywania promptów w trybie `--no-interactive`.

---

## Etap 1 — Porządek w testach i zależnościach

### 1.1 Standard testów: unittest

Ustalamy, że testy uruchamiamy **wyłącznie przez `unittest`**.

Do zrobienia:

* Usuń `pytest` z `pyproject.toml` (żeby dependencies nie sugerowały innego runnera).
* Zaktualizuj `AGENTS.md`, aby podawał tylko jedną komendę testów:

  * `python -m unittest discover -s tests`
* Upewnij się, że wszystkie nowe testy są zgodne z `unittest` (bez fixture’ów pytest).

Efekt: brak sprzecznych sygnałów dla AI i deterministyczny sposób uruchamiania testów.

---

## Etap 2 — Kontrakty danych (TypedDict / dataclass)

### 2.1 Dodaj typy domenowe

Utwórz plik `miniflux_prompt_compiler/types.py` i dodaj:

* `MinifluxEntry` (TypedDict)

  * `id: int | str | None` (realnie bywa różnie)
  * `title: str | None`
  * `url: str | None`
  * (opcjonalnie inne pola, ale tylko jeśli używane)

* `ProcessedItem` (dataclass lub TypedDict)

  * `title: str`
  * `content: str`

### 2.2 Zastosuj typy w kodzie

* `fetch_unread_entries()` zwraca `list[MinifluxEntry]`.
* `process_entry()` przyjmuje `MinifluxEntry` i zwraca np. `tuple[bool, ProcessedItem | None]` (lub `(processed, title, content)` jeśli chcesz minimalnie).
* `build_prompt()` i `build_prompts_with_chunking()` pracują na `list[ProcessedItem]`.

Efekt: AI ma mniej stanów do rozważania i mniej “zgadywania” kontraktów.

---

## Etap 3 — Rozbicie `main.py` na moduły

### 3.1 Docelowa struktura

```
.
├── miniflux_prompt_compiler/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── types.py
│   ├── core/
│   │   ├── prompting.py
│   │   ├── tokenization.py
│   │   ├── url_classify.py
│   │   └── chunking.py
│   └── adapters/
│       ├── miniflux_http.py
│       ├── jina.py
│       ├── playwright_fetch.py
│       ├── youtube.py
│       └── clipboard.py
├── tests/
└── pyproject.toml
```

### 3.2 Mapowanie funkcji z `main.py`

#### `core/tokenization.py`

* `count_tokens()`
* `label_for_tokens()`
* stałe: `TOKEN_LABELS`, `TOKENIZER_OPTIONS`

#### `core/prompting.py`

* `PROMPT`
* `build_prompt()`

#### `core/chunking.py`

* `build_prompts_with_chunking()`

#### `core/url_classify.py`

* `is_youtube_url()`
* `is_youtube_shorts()`
* `extract_youtube_id()`

#### `adapters/jina.py`

* `fetch_article_markdown()`
* ewentualnie: wspólny helper retry/timeout

#### `adapters/playwright_fetch.py`

* `fetch_article_with_playwright()`

#### `adapters/youtube.py`

* `fetch_youtube_transcript()`

#### `adapters/miniflux_http.py`

* `fetch_unread_entries()`
* `mark_entry_read()`

#### `adapters/clipboard.py`

* `copy_to_clipboard()`

#### `config.py`

* `load_env()`
* pobieranie konfiguracji: `MINIFLUX_API_TOKEN`, `MINIFLUX_BASE_URL`

#### `cli.py`

* `parse_args()`
* `main()`
* wywołanie nowej funkcji orkiestrującej (np. `app.run(...)`)

#### `app.py` (opcjonalnie)

* `run()` i `process_entry()` jako orkiestracja + glue

> Minimalistycznie możesz zostawić `run()` w `cli.py`, ale lepiej dać `run()` do `app.py`, a `cli.py` tylko parsuje args i odpala.

---

## Etap 4 — Konfiguracja `base_url`

### 4.1 Usuń hardcode

Zastąp:

* `base_url = "http://192.168.0.209:8111"`

Konfiguracją:

* env: `MINIFLUX_BASE_URL` (domyślnie np. `http://localhost:8080` lub brak domyślnej i wymagane)
* opcja CLI: `--base-url`

### 4.2 Zasada rozstrzygania

1. CLI (`--base-url`)
2. env (`MINIFLUX_BASE_URL`)
3. `.env`
4. fallback (jeśli naprawdę chcesz), ale wtedy jawnie zaloguj, że użyto domyślnej.

---

## Etap 5 — Uporządkowanie błędów i “kruchych miejsc”

### 5.1 Własne wyjątki (opcjonalnie, ale AI‑friendly)

Utwórz np. w `types.py`:

* `class ContentFetchError(RuntimeError): ...`
* `class MinifluxError(RuntimeError): ...`

Rzucaj je w adapterach, a w `run()` łap i raportuj spójnie.

### 5.2 Popraw `entry_id`

Zmień parsowanie `id` na bezpieczne:

* jeśli `id` nie da się skonwertować do `int`, nie crashuj całego przebiegu; zaloguj i pomiń oznaczanie `read`.

### 5.3 Ustabilizuj `fetch_youtube_transcript()`

Obecny fragment jest kruchy:

* jeśli obiekt ma `snippets`, zwykle treść jest w `transcript.snippets`.

Refactor:

* rozpoznaj 2–3 warianty struktury i wyciągnij tekst deterministycznie:

  * lista dictów `[{"text": ...}, ...]`
  * obiekt z `.snippets` (iteruj po `snippets`)
  * fallback: iteracja po `transcript` tylko jeśli to jest iterable z elementami mającymi `.text` lub `['text']`.

---

## Etap 6 — Spójność logowania i interakcji

* Wszystkie komunikaty operacyjne → `logging.info`.
* `print()` tylko w trybie `--no-interactive` (wypisanie promptu) i ewentualnie nagłówków promptów.
* Rozważ flagę `--quiet` / `--verbose` (opcjonalnie).

---

## Etap 7 — Zachowanie testowalności (wstrzykiwanie zależności)

Utrzymaj wzorzec:

* `run(..., fetcher=..., article_fetcher=..., youtube_fetcher=..., marker=..., clipboard=..., input_reader=...)`

Po rozbiciu na moduły:

* w `app.run()` ustaw domyślne adaptery, ale dalej pozwól je nadpisać w testach.

---

## Checklista końcowa

* [ ] `pytest -q` (lub `python -m unittest ...`) przechodzi lokalnie.
* [ ] Brak hardcode `base_url` w kodzie.
* [ ] `main.py` zastąpione pakietem `miniflux_prompt_compiler/`.
* [ ] `build_prompt()` i chunking są w `core/` i nie robią I/O.
* [ ] Typy `MinifluxEntry` i `ProcessedItem` użyte w całym kodzie.
* [ ] Fallback Jina → Playwright działa jak wcześniej.

---

## Minimalny zakres zmian (jeśli chcesz “mały refactor”)

Jeżeli chcesz zrobić tylko to, co daje największy efekt przy najmniejszym koszcie:

1. typy (`types.py`) + podmiana sygnatur,
2. wyniesienie `core/` (tokeny/prompt/chunking/url),
3. `base_url` do env/CLI,
4. ujednolicenie test runnera.

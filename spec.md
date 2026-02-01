# Specyfikacja techniczna

## Cel
Aplikacja CLI w Pythonie pobiera wszystkie nieprzeczytane wpisy z Miniflux, ekstraktuje treść artykułów lub transkrypcje YouTube, składa prompt (lub wiele promptow przy przekroczeniu limitu tokenow), kopiuje je do schowka macOS w trybie interaktywnym i oznacza jako przeczytane tylko wpisy przetworzone z sukcesem. Dodatkowo wspiera opcjonalny fallback Playwright dla artykułów, uruchamiany tylko po błędzie Jiny i po włączeniu flagi CLI.

## Architektura i przepływ danych
1. Wczytanie konfiguracji: `MINIFLUX_API_TOKEN` z `.env`/ENV; `base_url` rozstrzygany w kolejnosci: CLI `--base-url` → env `MINIFLUX_BASE_URL` → `.env` → domyslny fallback (logowany).
2. Pobranie listy `unread` wpisów z Miniflux, zachowanie kolejności.
3. Klasyfikacja linków: YouTube (youtube.com, youtu.be) z pominięciem `/shorts/`; pozostałe to artykuły.
4. Ekstrakcja treści:
   - Artykuły: `https://r.jina.ai/<URL>` z maks. 3 retry i timeoutem 10–15 s.
   - Fallback (opcjonalnie): Playwright uruchamiany tylko dla artykułów, gdy Jina rzuci wyjątek lub zwróci pustą treść, i tylko przy fladze `--playwright` (1 próba, timeout 20 s, headless).
   - YouTube: `youtube_transcript_api` z preferencją `en`, bez timestampów; brak transkrypcji to porażka.
5. Sukcesy trafiają do promptu, porażki są logowane i pozostają jako `unread`.
6. Po każdym sukcesie wpis jest oznaczany jako `read` (pojedyncze ID).
7. Prompt jest liczony tokenowo, etykietowany i w razie potrzeby dzielony na chunki na granicy calych artykulow.
8. Finalne prompty sa kopiowane do schowka macOS w trybie interaktywnym dopiero po Enter (rowniez gdy jest tylko jeden prompt); w trybie nieinteraktywnym trafiaja do stdout.
9. Etykiety na podstawie liczby tokenow:
   - < 32 000: `GPT-Instant`
   - 32 000 – 49 999: `GPT-Thinking`
   - >= 50 000: `CHUNKING`

## Komponenty techniczne
- Warstwa CLI: `miniflux_prompt_compiler/cli.py` (parsowanie argumentow, `main()`).
- Orkiestracja: `miniflux_prompt_compiler/app.py` (przeplyw, `run()`, `process_entry()`).
- Core (bez I/O): `miniflux_prompt_compiler/core/` (prompt, tokeny, chunking, klasyfikacja URL).
- Adapters (I/O): `miniflux_prompt_compiler/adapters/` (Miniflux HTTP, Jina, Playwright, YouTube, clipboard).
- Kontrakty danych: `miniflux_prompt_compiler/types.py` (`MinifluxEntry`, `ProcessedItem`).
- Konfiguracja: `miniflux_prompt_compiler/config.py` (wczytywanie `.env`).

## Uwagi implementacyjne
- Brak async; przetwarzanie sekwencyjne.
- Bledy pojedynczego wpisu nie przerywaja calego procesu.
- Playwright nie wpływa na zachowanie bez flagi `--playwright`.
- Chunkowanie uruchamia sie tylko po przekroczeniu limitu tokenow.

## Roadmapa
- Szczegoly milestone'ow i statusy znajduja sie w `ROADMAP.md`.

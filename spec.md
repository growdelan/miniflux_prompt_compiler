# Specyfikacja techniczna

## Cel
Aplikacja CLI w Pythonie pobiera wszystkie nieprzeczytane wpisy z Miniflux, ekstraktuje treść artykułów lub transkrypcje YouTube, składa prompt (lub wiele promptow przy przekroczeniu limitu tokenow), kopiuje je do schowka macOS w trybie interaktywnym i oznacza jako przeczytane tylko wpisy przetworzone z sukcesem. Dla artykułów pobranych z Miniflux `fetch-content` aplikacja normalizuje HTML do markdown przez `trafilatura` i czyści wynik z portalowego noise. Dodatkowo wspiera opcjonalny fallback Playwright dla artykułów, uruchamiany tylko po błędzie Jiny i po włączeniu flagi CLI. Osobny tryb `--links` zwraca wyłącznie URL-e wpisów artykułowych (nie-YouTube), bez próby pozyskiwania treści.

## Architektura i przepływ danych
1. Wczytanie konfiguracji: `MINIFLUX_API_TOKEN` z `.env`/ENV; `base_url` rozstrzygany w kolejnosci: CLI `--base-url` → env `MINIFLUX_BASE_URL` → `.env` → domyslny fallback (logowany).
2. Pobranie listy `unread` wpisów z Miniflux, zachowanie kolejności.
3. Klasyfikacja linków: YouTube (youtube.com, youtu.be) z pominięciem `/shorts/`; pozostałe to artykuły.
4. Tryb `--links`: po klasyfikacji aplikacja filtruje wpisy do artykułów, buduje wynik zawierający same URL-e (po jednym na linię), pomija ekstrakcję treści, liczenie tokenów i chunkowanie, a wpisy uwzględnione w wyniku są traktowane jako sukces.
5. Domyślny tryb ekstrakcji treści (bez `--links`):
   - Artykuły: najpierw `GET /v1/entries/{entryID}/fetch-content?update_content=true` (Miniflux); przy sukcesie odpowiedź HTML jest konwertowana przez `trafilatura` do markdown i czyszczona z powtarzalnego noise, a wynik ma format `# {title}` + treść. Przy błędzie lub pustej treści fallback do `https://r.jina.ai/<URL>` (maks. 3 retry, timeout 10–15 s).
   - Fallback (opcjonalnie): Playwright uruchamiany tylko dla artykułów, gdy Jina rzuci wyjątek lub zwróci pustą treść, i tylko przy fladze `--playwright` (1 próba, timeout 20 s, headless).
   - YouTube: `youtube_transcript_api` z preferencją `en`, bez timestampów; brak transkrypcji to porażka.
6. Sukcesy trafiają do promptu, porażki są logowane i pozostają jako `unread`.
7. Po każdym sukcesie wpis jest oznaczany jako `read` (pojedyncze ID).
8. Prompt jest liczony tokenowo, etykietowany i w razie potrzeby dzielony na chunki na granicy calych artykulow.
9. Finalne prompty sa kopiowane do schowka macOS w trybie interaktywnym dopiero po Enter (rowniez gdy jest tylko jeden prompt); w trybie nieinteraktywnym trafiaja do stdout. W trybie `--links` ta sama logika dostarczenia wyniku dotyczy jednego bloku tekstu zawierającego same URL-e.
10. Etykiety na podstawie liczby tokenow:
   - < 32 000: `GPT-Instant`
   - 32 000 – 49 999: `GPT-Thinking`
   - >= 50 000: `CHUNKING`

## Komponenty techniczne
- Warstwa CLI: `miniflux_prompt_compiler/cli.py` (parsowanie argumentow, `main()`, w tym flaga `--links`).
- Orkiestracja: `miniflux_prompt_compiler/app.py` (przeplyw, `run()`, `process_entry()`, oraz sciezka links-only).
- Core (bez I/O): `miniflux_prompt_compiler/core/` (prompt, tokeny, chunking, klasyfikacja URL, ewentualne filtrowanie i skladanie listy URL-i).
- Adapters (I/O): `miniflux_prompt_compiler/adapters/` (Miniflux HTTP, Jina, Playwright, YouTube, clipboard oraz ekstrakcja markdown z HTML przez `trafilatura`).
- Kontrakty danych: `miniflux_prompt_compiler/types.py` (`MinifluxEntry`, `ProcessedItem`).
- Konfiguracja: `miniflux_prompt_compiler/config.py` (wczytywanie `.env`).

## Uwagi implementacyjne
- Brak async; przetwarzanie sekwencyjne.
- Bledy pojedynczego wpisu nie przerywaja calego procesu.
- Playwright nie wpływa na zachowanie bez flagi `--playwright`.
- Chunkowanie uruchamia sie tylko po przekroczeniu limitu tokenow.
- Tryb `--links` omija ekstrakcję treści, tokenizację i chunkowanie; wykorzystuje istniejącą klasyfikację URL do pominięcia wpisów YouTube.
- Konwersja `trafilatura` + cleanup dotyczy tylko ścieżki sukcesu Miniflux `fetch-content`; fallbacki Jina/Playwright pozostają bez zmian.

## Decyzje techniczne
- Priorytetem dla artykulow jest Miniflux `fetch-content`; dopiero przy bledzie lub pustej tresci uruchamiany jest fallback Jina, a nastepnie (opcjonalnie) Playwright.
- Tryb `--links` zwraca wyłącznie URL-e wpisów sklasyfikowanych jako artykuły (nie-YouTube) i nie uruchamia żadnego mechanizmu pozyskiwania treści ani transkrypcji (dotyczy PRD: `001-links-only-mode-prd.md`).
- Dla sukcesu Miniflux `fetch-content` odpowiedź HTML jest normalizowana do markdown przez `trafilatura` i czyszczona z portalowego noise; fallbacki Jina/Playwright pozostają bez tej normalizacji (dotyczy PRD: `002-trafilatura-miniflux-markdown-cleanup-prd.md`).

## Roadmapa
- Szczegoly milestone'ow i statusy znajduja sie w `ROADMAP.md`.

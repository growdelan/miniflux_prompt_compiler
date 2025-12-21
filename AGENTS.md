# Repository Guidelines

## Project Structure & Module Organization
- `main.py` zawiera punkt wejścia oraz minimalny klient Miniflux do pobierania `unread`.
- `pyproject.toml` definiuje metadane projektu i wymagania Pythona (`>=3.13`).
- `README.md` opisuje cel narzędzia w jednym zdaniu.
- `tests/test_smoke.py` zawiera prosty smoke test dla minimalnego przebiegu.

## Build, Test, and Development Commands
- `MINIFLUX_API_TOKEN=... python main.py` uruchamia aplikację i pobiera liczbę `unread`.
- `python -m unittest discover -s tests` uruchamia smoke test.
- Brak zdefiniowanych komend budowania lub uruchamiania środowiska wirtualnego; jeśli dodasz skrypty, opisz je tutaj.

## Coding Style & Naming Conventions
- Projekt jest w Pythonie; trzymaj się stylu PEP 8.
- Wcięcia: 4 spacje; brak tabulatorów.
- Nazwy funkcji i zmiennych: `snake_case`; klasy: `CamelCase`.
- Brak skonfigurowanych narzędzi formatowania/lintowania — jeśli je dodasz (np. `ruff`, `black`), zaktualizuj tę sekcję.

## Testing Guidelines
- Testy używają `unittest` i są trzymane w `tests/` z nazwami `test_*.py`.
- Smoke test nie wykonuje realnych wywołań HTTP; używa prostego `fetcher` stub.

## Commit & Pull Request Guidelines
- Repozytorium nie ma jeszcze historii commitów, więc nie ma ustalonej konwencji wiadomości.
- Proponowany standard: krótki, opisowy tytuł i kontekst w treści (np. „Add Miniflux client stub”).
- W PR uwzględnij: cel zmiany, zakres, kroki testów (lub informację o braku), oraz linki do powiązanych zadań/issue.

## Co dodano na tym etapie
- Minimalny klient Miniflux pobierający `unread` i logujący liczbę wpisów.
- Klasyfikacja linków (YouTube vs artykuł) z pominięciem `/shorts/`.
- Ekstrakcja treści artykułów przez `https://r.jina.ai/<URL>` z retry i timeoutem.
- Pobieranie transkrypcji YouTube z obsługą różnych wersji API biblioteki.
- Oznaczanie wpisów jako `read` po sukcesie, z fallbackiem na różne warianty API.
- Budowa promptu z tagami `<lista_artykułów_i_transkrypcji>...</lista_artykułów_i_transkrypcji>` i kopiowanie do schowka macOS.
- Wstrzykiwalne fetchery w `run()` oraz `process_entry()` dla testowalności.
- Smoke test potwierdzający przebieg bez połączeń sieciowych.

## Decyzje architektoniczne
- Brak zewnetrznych zaleznosci HTTP: uzywamy `urllib.request`, zeby utrzymac minimalizm.
- Konfiguracja tokenu tylko przez `MINIFLUX_API_TOKEN` z `.env` lub srodowiska.
- Endpoint przyjety w najprostszym wariancie: `/v1/entries?status=unread`.
- YouTube: obsluga `get_transcript` (stare API) i `fetch` (nowe API) w `youtube_transcript_api`.
- Jina: pusta odpowiedz traktowana jako porazka, pelna jako sukces niezaleznie od dlugosci.
- Oznaczanie `read`: probujemy kilka wariantow endpointu/metody, bo instalacje Miniflux moga sie roznic.
- Clipboard: uzywamy `pbcopy` jako najprostszej integracji z macOS.
- Prompt: lista wpisow zawsze zamknieta w dedykowanych tagach, by latwo ja wyodrebniac.

## Czego nie robimy na tym etapie
- Brak asynchronicznosci, retry i rozbudowanej obslugi bledow sieciowych.

## Configuration & Secrets
- Nie przechowuj sekretów w repozytorium. Jeśli aplikacja będzie wymagać kluczy/API, trzymaj je w zmiennych środowiskowych i udokumentuj w README.

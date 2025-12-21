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
- Wstrzykiwalny `fetcher` w `run()` dla testowalnosci.
- Smoke test potwierdzajacy prosty przebieg end-to-end bez sieci.

## Decyzje architektoniczne
- Brak zewnetrznych zaleznosci HTTP: uzywamy `urllib.request`, zeby utrzymac minimalizm.
- Konfiguracja tokenu tylko przez `MINIFLUX_API_TOKEN` z `.env` lub srodowiska.
- Endpoint przyjety w najprostszym wariancie: `/v1/entries?status=unread`.

## Czego nie robimy na tym etapie
- Brak ekstrakcji tresci (Jina/YouTube), budowy promptu i schowka macOS.
- Brak oznaczania wpisow jako `read`.
- Brak asynchronicznosci, retry i rozbudowanej obslugi bledow sieciowych.

## Configuration & Secrets
- Nie przechowuj sekretów w repozytorium. Jeśli aplikacja będzie wymagać kluczy/API, trzymaj je w zmiennych środowiskowych i udokumentuj w README.

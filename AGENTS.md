# Repository Guidelines

## Project Structure & Module Organization
- `main.py` jest cienkim wrapperem kompatybilnym z dotychczasowym uruchomieniem i re-eksportami.
- `miniflux_prompt_compiler/cli.py` zawiera parsowanie argumentów i `main()`.
- `miniflux_prompt_compiler/app.py` zawiera `run()` i orkiestrację przepływu.
- `miniflux_prompt_compiler/core/` to czysta logika (prompt, tokeny, chunking, klasyfikacja URL).
- `miniflux_prompt_compiler/adapters/` to integracje I/O (Miniflux HTTP, Jina, Playwright, YouTube, clipboard).
- `miniflux_prompt_compiler/config.py` wczytuje `.env`.
- `miniflux_prompt_compiler/types.py` zawiera kontrakty danych.
- `pyproject.toml` definiuje metadane projektu i wymagania Pythona (`>=3.13`).
- `README.md` opisuje cel narzędzia w jednym zdaniu.
- `tests/test_smoke.py` zawiera prosty smoke test dla minimalnego przebiegu.

## Build, Test, and Development Commands
- `python -m unittest discover -s tests` uruchamia smoke test.

## Coding Style & Naming Conventions
- Projekt jest w Pythonie; trzymaj się stylu PEP 8.
- Wcięcia: 4 spacje; brak tabulatorów.
- Nazwy funkcji i zmiennych: `snake_case`; klasy: `CamelCase`.
- Brak skonfigurowanych narzędzi formatowania/lintowania — jeśli je dodasz (np. `ruff`, `black`), zaktualizuj tę sekcję.

## Testing Guidelines
- Testy używają `unittest` i są trzymane w `tests/` z nazwami `test_*.py`.
- Smoke test nie wykonuje realnych wywołań HTTP; używa prostego `fetcher` stub.
- Dla każdego milestone dodaj testy i uruchom `python -m unittest discover -s tests`.

## Commit & Pull Request Guidelines
- Repozytorium nie ma jeszcze historii commitów, więc nie ma ustalonej konwencji wiadomości.
- Proponowany standard: krótki, opisowy tytuł i kontekst w treści (np. „Add Miniflux client stub”).
- W PR uwzględnij: cel zmiany, zakres, kroki testów (lub informację o braku), oraz linki do powiązanych zadań/issue.

## Configuration & Secrets
- Nie przechowuj sekretów w repozytorium. Jeśli aplikacja będzie wymagać kluczy/API, trzymaj je w zmiennych środowiskowych i udokumentuj w README.

## Source of Truth
- Szczegoly funkcji, decyzji i milestone'ow: `spec.md`.

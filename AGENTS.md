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

## Commit & Pull Request Guidelines
- Repozytorium nie ma jeszcze historii commitów, więc nie ma ustalonej konwencji wiadomości.
- Proponowany standard: krótki, opisowy tytuł i kontekst w treści (np. „Add Miniflux client stub”).
- W PR uwzględnij: cel zmiany, zakres, kroki testów (lub informację o braku), oraz linki do powiązanych zadań/issue.

## Co dodano na tym etapie
- Minimalny klient Miniflux pobierający `unread` i logujący liczbę wpisów.
- Typy danych: `MinifluxEntry` (`TypedDict`) oraz `ProcessedItem` (`dataclass`) w `miniflux_prompt_compiler/types.py`.
- Klasyfikacja linków (YouTube vs artykuł) z pominięciem `/shorts/`.
- Ekstrakcja treści artykułów przez `https://r.jina.ai/<URL>` z retry i timeoutem.
- Pobieranie transkrypcji YouTube z obsługą różnych wersji API biblioteki.
- Oznaczanie wpisów jako `read` po sukcesie, z fallbackiem na różne warianty API.
- Budowa promptu z tagami `<lista_artykułów_i_transkrypcji>...</lista_artykułów_i_transkrypcji>` i kopiowanie do schowka macOS.
- Liczenie tokenów promptu oraz etykiety `GPT-Instant`, `GPT-Thinking`, `CHUNKING` w stdout.
- Fallback do przybliżonego liczenia tokenów przy braku `tiktoken` z logiem ostrzegawczym.
- Testy progów etykiet tokenów.
- Wstrzykiwalne fetchery w `run()` oraz `process_entry()` dla testowalności.
- Smoke test potwierdzający przebieg bez połączeń sieciowych.
- Testy jednostkowe dla klasyfikacji URL i budowy promptu.
- Instrukcja uruchamiania i testów w `README.md`.
- Flaga CLI `--playwright` sterujaca trybem fallback oraz test potwierdzajacy jej przekazanie do `run()`.
- Implementacja Playwright fallback dla artykulow (headless, 1 proba, 20 s timeout) oraz test uzycia fallbacku.
- Logi dla Jina i Playwright (start/blad/sukces), wskazanie zrodla tresci oraz instrukcje uruchomienia fallbacku w README.
- Chunkowanie promptow po granicy wpisow z pomijaniem wpisow przekraczajacych limit tokenow.
- Logi podsumowujace liczbe promptow po chunkowaniu i tokeny dla kazdego z nich.
- Testy logiki chunkowania (dzielenie i pomijanie zbyt duzego wpisu).
- Tryb interaktywny kopiowania promptow po Enter z komunikatami o tokenach i etykietach.
- Tryb nieinteraktywny (`--no-interactive`) wypisujacy prompty do stdout.
- Flagi CLI `--interactive` i `--no-interactive` oraz test trybu nieinteraktywnego.
- Flagi CLI `--max-tokens` i `--tokenizer` z przekazaniem do logiki tokenow i chunkowania.
- Obsluga tokenizerow `auto`, `tiktoken`, `approx` i testy liczenia przyblizonego.
- Aktualizacja README o nowe flagi uruchomieniowe.
- Rozbicie kodu na modul `core/`, `adapters/`, `app.py`, `cli.py`, `config.py` z zachowaniem logiki.
- Cienki `main.py` jako wrapper i re-eksport funkcji dla kompatybilnosci testow i uruchomienia.
- Konfiguracja `MINIFLUX_BASE_URL` z rozstrzyganiem CLI/env/.env i domyslnym fallbackiem.
- Flaga CLI `--base-url` do nadpisania adresu Miniflux oraz testy przekazania/odczytu.
- Aktualizacja README o `MINIFLUX_BASE_URL` i uzycie `--base-url`.
- Wyjatki domenowe `ContentFetchError` i `MinifluxError` dla stabilniejszych komunikatow I/O.
- Stabilniejsza ekstrakcja transkrypcji YouTube (snippets/listy/obiekty).
- Bezpieczne parsowanie `entry_id` z logiem i pominieciem oznaczania `read` przy blednym ID.
- Ujednolicenie logowania operacyjnego: `logging.info` zamiast `print()` poza trybem `--no-interactive`.
- Dostosowanie testu trybu nieinteraktywnego do logowania INFO.
- Kolorowanie etykiet `GPT-Instant` (zielony) i `GPT-Thinking` (zolty) w logach i stdout.
- Czerwony komunikat o pominieciu wpisu przekraczajacego limit tokenow.
- Aktualizacja testow pod kolory ANSI (strip kodow w asercjach).

## Decyzje architektoniczne
- Brak zewnetrznych zaleznosci HTTP: uzywamy `urllib.request`, zeby utrzymac minimalizm.
- Typy `MinifluxEntry` i `ProcessedItem` centralizujemy w osobnym module, by ujednolicic sygnatury funkcji i uproscic testy.
- Konfiguracja tokenu tylko przez `MINIFLUX_API_TOKEN` z `.env` lub srodowiska.
- Endpoint przyjety w najprostszym wariancie: `/v1/entries?status=unread`.
- YouTube: obsluga `get_transcript` (stare API) i `fetch` (nowe API) w `youtube_transcript_api`.
- Jina: pusta odpowiedz traktowana jako porazka, pelna jako sukces niezaleznie od dlugosci.
- Oznaczanie `read`: probujemy kilka wariantow endpointu/metody, bo instalacje Miniflux moga sie roznic.
- Clipboard: uzywamy `pbcopy` jako najprostszej integracji z macOS.
- Prompt: lista wpisow zawsze zamknieta w dedykowanych tagach, by latwo ja wyodrebniac.
- Tokenizer: `tiktoken` jest opcjonalny, a przy jego braku stosujemy przyblizone liczenie z logiem.
- Progi etykiet tokenow sa zgodne z PRD (<32k, 32k–49,999, >=50k).
- Chunkowanie jest deterministyczne, zachowuje kolejnosc wpisow i nie tnie tresci w srodku.
- Wpis przekraczajacy limit tokenow jest pomijany z ostrzezeniem w logach.
- Tryb interaktywny jest domyslny, a `--no-interactive` przechodzi na stdout bez kopiowania do schowka.
- `--tokenizer tiktoken` wymaga obecnosci `tiktoken`; `auto` przechodzi na przyblizenie, `approx` wymusza szacunek.
- Limit tokenow jest konfigurowalny przez `--max-tokens` i przekazywany do chunkowania.
- Testy: zostajemy przy `unittest`, bez dodatkowych frameworkow.
- Tryb fallback jest kontrolowany flaga `--playwright` i nie zmienia domyslnego zachowania bez tej flagi.
- Playwright dziala synchronicznie i tylko jako fallback po bledzie Jiny.
- Logowanie operacyjne oparte o `logging.info`, bez dodatkowych narzedzi obserwowalnosci.
- Struktura kodu jest rozdzielona na warstwy `core/` (czysta logika) i `adapters/` (I/O), z `app.py` jako orkiestracja.
- `main.py` pozostaje kompatybilnym punktem wejscia i re-eksportem API dla testow.
- `base_url` jest rozstrzygany w kolejnosci: CLI -> env -> .env -> domyslny fallback z logiem.
- Adaptery I/O rzucaja wyjatki domenowe zamiast ogolnych `RuntimeError`, bez zmiany zachowania funkcjonalnego.
- `entry_id` nie blokuje przebiegu; przy blednym ID wpis nie jest oznaczany jako `read`.
- Komunikaty operacyjne sa logowane przez `logging`, a `print()` pozostaje tylko do wypisywania promptow w trybie `--no-interactive`.
- Kolorowanie informacji realizowane przez kody ANSI bez dodatkowych zaleznosci.
- Testy ignoruja kody ANSI, sprawdzajac tresc komunikatow.

## Czego nie robimy na tym etapie
- Brak asynchronicznosci, retry i rozbudowanej obslugi bledow sieciowych.
- Brak pelnego modelowania wszystkich pol odpowiedzi Miniflux (korzystamy tylko z wymaganych pol).
- Brak detekcji paywalla i rozbudowanego czyszczenia tresci.
- Brak automatycznej instalacji przegladarek Playwright.
- Brak zmian w zachowaniu funkcjonalnym i logice biznesowej; refactor jest strukturalny.
- Brak walidacji ani normalizacji `MINIFLUX_BASE_URL` poza prostym `strip()`.
- Brak wprowadzenia flag `--quiet` / `--verbose` (pozostawione na przyszlosc).
- Brak przelacznika do wylaczenia kolorow w logach i stdout.

## Aktualny stan
- co dziala: pobieranie `unread` z Miniflux, ekstrakcja Jina/YouTube, prompty z chunkowaniem po tokenach, etykiety tokenow, kolorowe etykiety i ostrzezenia ANSI, tryb interaktywny i `--no-interactive`, fallback Playwright (flaga `--playwright`) z logami, konfiguracja `MINIFLUX_BASE_URL` (CLI/env/.env), wyjatki domenowe dla I/O, stabilne oznaczanie `read`, logowanie operacyjne przez `logging`.
- co jest skonczone: milestone’y 0.5–16 z `spec.md` oznaczone jako zrealizowane.
- co jest nastepne: brak kolejnego milestone’u; kolejne kroki po nowym PRD/ustaleniach.

## Configuration & Secrets
- Nie przechowuj sekretów w repozytorium. Jeśli aplikacja będzie wymagać kluczy/API, trzymaj je w zmiennych środowiskowych i udokumentuj w README.

# Repository Guidelines

## Project Structure & Module Organization
- `main.py` zawiera punkt wejścia oraz minimalny klient Miniflux do pobierania `unread`.
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

## Decyzje architektoniczne
- Brak zewnetrznych zaleznosci HTTP: uzywamy `urllib.request`, zeby utrzymac minimalizm.
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

## Czego nie robimy na tym etapie
- Brak asynchronicznosci, retry i rozbudowanej obslugi bledow sieciowych.
- Brak detekcji paywalla i rozbudowanego czyszczenia tresci.
- Brak automatycznej instalacji przegladarek Playwright.

## Aktualny stan
- co dziala: pobieranie `unread` z Miniflux, ekstrakcja Jina/YouTube, prompty z chunkowaniem po tokenach, etykiety tokenow, tryb interaktywny i `--no-interactive`, fallback Playwright (flaga `--playwright`) z logami.
- co jest skonczone: milestone’y 0.5–11 z `spec.md` oznaczone jako zrealizowane.
- co jest nastepne: brak kolejnego milestone’u; kolejne kroki po nowym PRD/ustaleniach.

## Configuration & Secrets
- Nie przechowuj sekretów w repozytorium. Jeśli aplikacja będzie wymagać kluczy/API, trzymaj je w zmiennych środowiskowych i udokumentuj w README.

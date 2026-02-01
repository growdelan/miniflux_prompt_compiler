# Roadmapa (milestones)

## Milestone 0.5: Minimal end-to-end slice (zrealizowany)
Cel: aplikacja uruchamia sie, wykonuje jedno bardzo proste zadanie i zwraca poprawny wynik.
Definition of Done: da sie uruchomic jednym poleceniem; istnieje jeden prosty test / smoke check; brak placeholderow.
Zakres: minimalny przebieg od wejscia do wyjscia (np. pobranie jednej prostej wartosci i jej wypisanie).

## Milestone 1: Podstawa integracji z Miniflux (zrealizowany)
Cel: pobranie i uporzadkowanie listy `unread` wpisow.
Definition of Done: konfiguracja `.env` dziala; lista wpisow jest pobrana i zachowuje kolejnosc; loguje liczbe wpisow.
Zakres: klient HTTP, autoryzacja tokenem, model danych wpisu (id, tytul, url).

## Milestone 2: Ekstrakcja tresci (zrealizowany)
Cel: uzyskanie tresci artykulow i transkrypcji YouTube.
Definition of Done: dziala klasyfikacja linkow; Jina z retry i timeoutem; YouTube z preferencja `en`; porazki sa logowane.
Zakres: parser URL, integracje z Jina i `youtube_transcript_api`.

## Milestone 3: Prompt i oznaczanie `read` (zrealizowany)
Cel: generowanie promptu i aktualizacja statusu wpisow.
Definition of Done: poprawny format promptu; sukcesy trafiaja do promptu; wpisy sukcesu oznaczane jako `read`; schowek nadpisywany tylko przy co najmniej jednym sukcesie.
Zakres: builder promptu, clipboard macOS, endpoint aktualizacji statusu.

## Milestone 4: Stabilnosc i jakosc (zrealizowany)
Cel: poprawa niezawodnosci i podstawowe testy.
Definition of Done: obsluga bledow sieciowych i pustych odpowiedzi; testy jednostkowe logiki klasyfikacji i budowania promptu; instrukcja uruchamiania.
Zakres: testy (unittest), doprecyzowanie logow i dokumentacji.

## Milestone 5: Flaga Playwright i kontrola uruchomienia (zrealizowany)
Cel: dodanie opcjonalnego trybu fallback bez zmiany domyslnego zachowania.
Definition of Done: flaga `--playwright` jest parsowana i przekazywana do logiki ekstrakcji; bez flagi aplikacja dziala identycznie jak dotychczas.
Zakres: parsing argumentow CLI, przekazanie konfiguracji do `run()` i ekstraktora artykulow.

## Milestone 6: Playwright fallback MVP (zrealizowany)
Cel: pobranie plain text przez Playwright po bledzie Jiny.
Definition of Done: Playwright uruchamia sie headless, 1 proba, timeout 20 s; sukces to niepusta tresc; porazka pozostawia wpis jako `unread`.
Zakres: uruchomienie przegladarki, `document.body.innerText`, best-effort klikniecie cookie consent.

## Milestone 7: Logowanie i dokumentacja Playwright (zrealizowany)
Cel: jasne logi i instrukcje uruchomienia nowej funkcji.
Definition of Done: logi INFO zawieraja start i blad Jiny, start Playwrighta, sukces/porazke oraz zrodlo tresci; README opisuje zaleznosc `playwright` i `playwright install`.
Zakres: komunikaty logow, aktualizacja README i opis wymagan.

## Milestone 8: Liczenie tokenow i etykiety promptu (zrealizowany)
Cel: wiarygodne liczenie tokenow i widoczna klasyfikacja promptu.
Definition of Done: aplikacja liczy tokeny pojedynczego promptu; etykiety `GPT-Instant`, `GPT-Thinking`, `CHUNKING` sa wypisywane w stdout; fallback przyblizony jest logowany jako szacunek.
Zakres: `count_tokens`, `label_for_tokens`, integracja z logami i stdout.

## Milestone 9: Chunkowanie promptow po granicy wpisow (zrealizowany)
Cel: automatyczne dzielenie promptu na wiele promptow bez ciecia tresci artykulow.
Definition of Done: chunkowanie uruchamia sie po przekroczeniu `--max-tokens`; kazdy chunk miesci sie w limicie; pojedynczy wpis przekraczajacy limit jest pominiety z ostrzezeniem.
Zakres: `build_prompts_with_chunking`, logika cofania ostatniego wpisu, zachowanie kolejnosci.

## Milestone 10: Tryb interaktywny i nieinteraktywny kopiowania (zrealizowany)
Cel: wygodne kopiowanie wielu promptow do schowka oraz opcja bez interakcji.
Definition of Done: przy wielu promptach aplikacja informuje o liczbie i zakresach tokenow; w trybie interaktywnym kopiuje kolejno po Enter z komunikatem o etykiecie; `--no-interactive` wypisuje prompty do stdout bez oczekiwania.
Zakres: obsluga wejscia uzytkownika, integracja z `pbcopy`, obsluga flag `--interactive/--no-interactive`.

## Milestone 11: Rozszerzenie CLI dla kontroli tokenow (zrealizowany)
Cel: pelna kontrola limitu i wyboru tokenizerow przez CLI.
Definition of Done: `--max-tokens` ustawia limit; `--tokenizer` wspiera `auto`, `tiktoken`, `approx`; parametry sa przekazywane do logiki tokenow i chunkowania.
Zakres: parsing argumentow CLI, walidacja parametrow, dokumentacja w README.

## Milestone 12: Refactor - rozbicie na moduly (zrealizowany)
Cel: uporzadkowanie struktury kodu bez zmiany zachowania funkcjonalnego.
Definition of Done: logika podzielona na `core/`, `adapters/`, `app.py`, `cli.py`, `config.py`; `main.py` pozostaje kompatybilnym wrapperem; testy przechodza bez zmian funkcjonalnych.
Zakres: przeniesienie funkcji z `main.py` do modulow oraz aktualizacja importow w testach.

## Milestone 13: Konfiguracja base_url (zrealizowany)
Cel: usuniecie hardcode adresu Miniflux i wprowadzenie konfiguracji z CLI i env.
Definition of Done: `--base-url` nadpisuje adres; `MINIFLUX_BASE_URL` jest wspierany z `.env`; fallback jest jawnie logowany.
Zakres: rozstrzyganie base_url w `run()`, flaga CLI oraz aktualizacja testow i README.

## Milestone 14: Uporzadkowanie bledow i kruchych miejsc (zrealizowany)
Cel: ujednolicenie bledow I/O i poprawa stabilnosci przetwarzania wpisow.
Definition of Done: adaptery I/O korzystaja z wyjatkow domenowych; parsowanie `entry_id` nie przerywa przebiegu; transkrypcja YouTube jest stabilnie ekstraktowana.
Zakres: `ContentFetchError` i `MinifluxError`, stabilizacja ekstrakcji YouTube oraz bezpieczne ID w `run()`.

## Milestone 15: Spojnosc logowania i interakcji (zrealizowany)
Cel: uporzadkowanie komunikatow operacyjnych i wyjsciowych.
Definition of Done: komunikaty operacyjne ida przez `logging.info`; `print()` pozostaje tylko do wypisywania promptow w trybie `--no-interactive`.
Zakres: przeniesienie komunikatow o tokenach/promptach do logow oraz aktualizacja testow.

## Milestone 16: Kolory w komunikatach tokenow i ostrzezeniach (zrealizowany)
Cel: szybkie rozroznienie etykiet tokenow oraz ostrzezen o pominietych wpisach.
Definition of Done: `GPT-Instant` jest zielony, `GPT-Thinking` zolty, a komunikat o pominieciu wpisu przekraczajacego limit tokenow jest czerwony; testy pozostaja stabilne.
Zakres: kolorowanie ANSI w logach/wyjsciu oraz dostosowanie testow do kodow ANSI.

## Milestone 17: Timeouty Jina jako bledy domenowe (zrealizowany)
Cel: stabilne przetwarzanie timeoutow z `urllib` bez przerywania calego przebiegu.
Definition of Done: `TimeoutError` i `socket.timeout` sa mapowane na `ContentFetchError`, co pozwala na retry i uruchomienie fallbacku Playwright; jest test jednostkowy.
Zakres: obsluga timeoutow w adapterze Jina i test potwierdzajacy opakowanie wyjatku.

## Milestone 18: Enter przed kopiowaniem pojedynczego promptu (zrealizowany)
Cel: ujednolicenie trybu interaktywnego niezaleznie od liczby promptow.
Definition of Done: w trybie interaktywnym kopiowanie nawet jednego promptu następuje dopiero po Enter; logi potwierdzaja kopiowanie; test to weryfikuje.
Zakres: logika kopiowania w trybie interaktywnym oraz test smoke.

## Milestone 19: Miniflux fetch-content jako pierwszy wybor (done)
Cel: najpierw probowac pobrac tresc artykulu przez Miniflux `fetch-content`, a dopiero potem fallback Jina -> Playwright.
Definition of Done: dla artykulow pierwsza proba to `GET /v1/entries/{entryID}/fetch-content?update_content=true`; przy bledzie lub pustej tresci nastepuje fallback do Jina, a po jej porazce (i tylko z flaga) do Playwright; logi wskazuja zrodlo tresci i powod fallbacku; testy pokrywaja sukces Miniflux oraz fallbacki.
Zakres: nowy endpoint w adapterze Miniflux, zmiana kolejnosci ekstrakcji artykulow, logowanie zrodla tresci, testy i aktualizacja dokumentacji.

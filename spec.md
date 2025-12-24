# Specyfikacja techniczna

## Cel
Aplikacja CLI w Pythonie (pojedynczy plik) pobiera wszystkie nieprzeczytane wpisy z Miniflux, ekstraktuje treść artykułów lub transkrypcje YouTube, składa prompt (lub wiele promptow przy przekroczeniu limitu tokenow), kopiuje je do schowka macOS w trybie interaktywnym i oznacza jako przeczytane tylko wpisy przetworzone z sukcesem. Dodatkowo wspiera opcjonalny fallback Playwright dla artykułów, uruchamiany tylko po błędzie Jiny i po włączeniu flagi CLI.

## Architektura i przepływ danych
1. Wczytanie konfiguracji z `.env` (token API), stałe w kodzie: URL Miniflux i placeholder promptu.
2. Pobranie listy `unread` wpisów z Miniflux, zachowanie kolejności.
3. Klasyfikacja linków: YouTube (youtube.com, youtu.be) z pominięciem `/shorts/`; pozostałe to artykuły.
4. Ekstrakcja treści:
   - Artykuły: `https://r.jina.ai/<URL>` z maks. 3 retry i timeoutem 10–15 s.
   - Fallback (opcjonalnie): Playwright uruchamiany tylko dla artykułów, gdy Jina rzuci wyjątek lub zwróci pustą treść, i tylko przy fladze `--playwright` (1 próba, timeout 20 s, headless).
   - YouTube: `youtube_transcript_api` z preferencją `en`, bez timestampów; brak transkrypcji to porażka.
5. Sukcesy trafiają do promptu, porażki są logowane i pozostają jako `unread`.
6. Po każdym sukcesie wpis jest oznaczany jako `read` (pojedyncze ID).
7. Prompt jest liczony tokenowo, etykietowany i w razie potrzeby dzielony na chunki na granicy calych artykulow.
8. Finalne prompty sa kopiowane do schowka macOS w trybie interaktywnym (po Enter); w trybie nieinteraktywnym trafiaja do stdout.
9. Etykiety na podstawie liczby tokenow:
   - < 32 000: `GPT-Instant`
   - 32 000 – 49 999: `GPT-Thinking`
   - >= 50 000: `CHUNKING`

## Komponenty techniczne
- Miniflux client: pobieranie wpisów i oznaczanie `read`.
- Ekstraktor treści: obsługa Jina i YouTube, retry, timeouty; opcjonalny fallback Playwright dla artykułów.
- Budowniczy promptu: placeholder + sekcje `Tytul:` i `Tresc:` z separatorem `---`.
- Licznik tokenow: `tiktoken` gdy dostepny, z fallbackiem na przyblizenie.
- Chunker promptow: dzieli tylko na granicy calych wpisow, z limitem `--max-tokens`.
- Tryb interaktywny: sekwencyjne kopiowanie promptow do schowka po Enter.
- Clipboard: kopiowanie do schowka macOS.
- Logowanie: start/typ/sukces/blad/oznaczenie.

## Uwagi implementacyjne
- Brak async; przetwarzanie sekwencyjne.
- Bledy pojedynczego wpisu nie przerywaja calego procesu.
- Playwright nie wpływa na zachowanie bez flagi `--playwright`.
- Chunkowanie uruchamia sie tylko po przekroczeniu limitu tokenow.

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
Cel: generowanie promptu i aktualizacja statusu wpisów.
Definition of Done: poprawny format promptu; sukcesy trafiaja do promptu; wpisy sukcesu oznaczane jako `read`; schowek nadpisywany tylko przy co najmniej jednym sukcesie.
Zakres: builder promptu, clipboard macOS, endpoint aktualizacji statusu.

## Milestone 4: Stabilnosc i jakosc (zrealizowany)
Cel: poprawa niezawodnosci i podstawowe testy.
Definition of Done: obsluga bledow sieciowych i pustych odpowiedzi; testy jednostkowe logiki klasyfikacji i budowania promptu; instrukcja uruchamiania.
Zakres: testy (np. pytest), doprecyzowanie logow i dokumentacji.

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

## Milestone 9: Chunkowanie promptow po granicy wpisow
Cel: automatyczne dzielenie promptu na wiele promptow bez ciecia tresci artykulow.
Definition of Done: chunkowanie uruchamia sie po przekroczeniu `--max-tokens`; kazdy chunk miesci sie w limicie; pojedynczy wpis przekraczajacy limit jest pominiety z ostrzezeniem.
Zakres: `build_prompts_with_chunking`, logika cofania ostatniego wpisu, zachowanie kolejnosci.

## Milestone 10: Tryb interaktywny i nieinteraktywny kopiowania
Cel: wygodne kopiowanie wielu promptow do schowka oraz opcja bez interakcji.
Definition of Done: przy wielu promptach aplikacja informuje o liczbie i zakresach tokenow; w trybie interaktywnym kopiuje kolejno po Enter z komunikatem o etykiecie; `--no-interactive` wypisuje prompty do stdout bez oczekiwania.
Zakres: obsluga wejscia uzytkownika, integracja z `pbcopy`, obsluga flag `--interactive/--no-interactive`.

## Milestone 11: Rozszerzenie CLI dla kontroli tokenow
Cel: pelna kontrola limitu i wyboru tokenizerow przez CLI.
Definition of Done: `--max-tokens` ustawia limit; `--tokenizer` wspiera `auto`, `tiktoken`, `approx`; parametry sa przekazywane do logiki tokenow i chunkowania.
Zakres: parsing argumentow CLI, walidacja parametrow, dokumentacja w README.

# Specyfikacja techniczna

## Cel
Aplikacja CLI w Pythonie (pojedynczy plik) pobiera wszystkie nieprzeczytane wpisy z Miniflux, ekstraktuje treść artykułów lub transkrypcje YouTube, składa jeden prompt, kopiuje go do schowka macOS i oznacza jako przeczytane tylko wpisy przetworzone z sukcesem.

## Architektura i przepływ danych
1. Wczytanie konfiguracji z `.env` (token API), stałe w kodzie: URL Miniflux i placeholder promptu.
2. Pobranie listy `unread` wpisów z Miniflux, zachowanie kolejności.
3. Klasyfikacja linków: YouTube (youtube.com, youtu.be) z pominięciem `/shorts/`; pozostałe to artykuły.
4. Ekstrakcja treści:
   - Artykuły: `https://r.jina.ai/<URL>` z maks. 3 retry i timeoutem 10–15 s.
   - YouTube: `youtube_transcript_api` z preferencją `en`, bez timestampów; brak transkrypcji to porażka.
5. Sukcesy trafiają do promptu, porażki są logowane i pozostają jako `unread`.
6. Po każdym sukcesie wpis jest oznaczany jako `read` (pojedyncze ID).
7. Finalny prompt kopiowany do schowka macOS tylko jeśli zawiera co najmniej jeden wpis.

## Komponenty techniczne
- Miniflux client: pobieranie wpisów i oznaczanie `read`.
- Ekstraktor treści: obsługa Jina i YouTube, retry, timeouty.
- Budowniczy promptu: placeholder + sekcje `Tytul:` i `Tresc:` z separatorem `---`.
- Clipboard: kopiowanie do schowka macOS.
- Logowanie: start/typ/sukces/blad/oznaczenie.

## Uwagi implementacyjne
- Brak async; przetwarzanie sekwencyjne.
- Bledy pojedynczego wpisu nie przerywaja calego procesu.

# Roadmapa (milestones)

## Milestone 0.5: Minimal end-to-end slice
Cel: aplikacja uruchamia sie, wykonuje jedno bardzo proste zadanie i zwraca poprawny wynik.
Definition of Done: da sie uruchomic jednym poleceniem; istnieje jeden prosty test / smoke check; brak placeholderow.
Zakres: minimalny przebieg od wejscia do wyjscia (np. pobranie jednej prostej wartosci i jej wypisanie).

## Milestone 1: Podstawa integracji z Miniflux
Cel: pobranie i uporzadkowanie listy `unread` wpisow.
Definition of Done: konfiguracja `.env` dziala; lista wpisow jest pobrana i zachowuje kolejnosc; loguje liczbe wpisow.
Zakres: klient HTTP, autoryzacja tokenem, model danych wpisu (id, tytul, url).

## Milestone 2: Ekstrakcja tresci
Cel: uzyskanie tresci artykulow i transkrypcji YouTube.
Definition of Done: dziala klasyfikacja linkow; Jina z retry i timeoutem; YouTube z preferencja `en`; porazki sa logowane.
Zakres: parser URL, integracje z Jina i `youtube_transcript_api`.

## Milestone 3: Prompt i oznaczanie `read`
Cel: generowanie promptu i aktualizacja statusu wpisow.
Definition of Done: poprawny format promptu; sukcesy trafiaja do promptu; wpisy sukcesu oznaczane jako `read`; schowek nadpisywany tylko przy co najmniej jednym sukcesie.
Zakres: builder promptu, clipboard macOS, endpoint aktualizacji statusu.

## Milestone 4: Stabilnosc i jakosc
Cel: poprawa niezawodnosci i podstawowe testy.
Definition of Done: obsluga bledow sieciowych i pustych odpowiedzi; testy jednostkowe logiki klasyfikacji i budowania promptu; instrukcja uruchamiania.
Zakres: testy (np. pytest), doprecyzowanie logow i dokumentacji.

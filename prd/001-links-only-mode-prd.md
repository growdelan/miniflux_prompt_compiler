# PRD – Tryb `--links` dla samych linków newsów

## 1. Cel produktu

Celem jest rozszerzenie **Miniflux Prompt Compiler** o prosty tryb CLI, w ktorym narzedzie **nie pobiera tresci artykulow ani transkrypcji**, tylko zwraca **same linki do newsow** z nieprzeczytanych wpisow Miniflux.

Nowa funkcja ma sluzyc sytuacjom, w ktorych uzytkownik chce szybko zebrac liste zrodel do dalszej obrobki recznej lub przekazac same URL-e do innego workflow, bez kosztu i ryzyka zwiazanego z ekstrakcja tresci.

## 2. Problem do rozwiazania

Obecne dzialanie aplikacji zawsze probuje pobrac i przetworzyc tresc wpisu:

* artykuly przez Miniflux `fetch-content`, Jina i opcjonalnie Playwright,
* materialy YouTube przez transkrypcje.

To zachowanie jest poprawne dla glównego workflow, ale jest zbyt ciezkie dla prostego przypadku uzycia:

* "daj mi tylko liste linkow do newsow",
* bez fetchowania stron,
* bez transkrypcji,
* bez fallbackow,
* bez opoznien wynikajacych z I/O dla tresci.

## 3. Zakres funkcjonalny (In-Scope)

### 3.1 Nowy argument CLI

Dodany zostaje nowy argument:

* `--links`

Po jego uzyciu aplikacja przechodzi w specjalny tryb "links only".

### 3.2 Zachowanie trybu `--links`

W trybie `--links` aplikacja:

* pobiera liste `unread` wpisow z Miniflux, zachowujac kolejnosc,
* filtruje wpisy do linkow newsowych / artykulowych,
* buduje wynik zawierajacy **wylacznie URL-e**,
* nie probuje pobierac tresci artykulow,
* nie wywoluje Jiny,
* nie uruchamia Playwrighta,
* nie probuje pobierac transkrypcji YouTube.

Przez "linki newsow" w MVP rozumiemy wpisy artykulowe, czyli wszystkie wpisy, ktore **nie sa klasyfikowane jako YouTube**.

### 3.3 Format wyjscia

Wynik w trybie `--links` zawiera same linki, po jednym na linie, w kolejnosci zgodnej z lista `unread`.

Przyklad:

```text
https://example.com/news-1
https://example.com/news-2
https://example.com/news-3
```

Bez dodatkowych blokow tresci, streszczen, tytulow artykulow i bez ekstrakcji body.

### 3.4 Oznaczanie wpisow jako `read`

W trybie `--links` wpis jest traktowany jako sukces, jezeli:

* zostal zakwalifikowany jako artykul / news,
* ma poprawny URL,
* jego link zostal uwzgledniony w wyniku.

Takie wpisy moga zostac oznaczone jako `read`, zgodnie z obecnym modelem "oznacz jako przeczytane po sukcesie".

## 4. Poza zakresem (Out-of-Scope)

Poza zakresem tej zmiany pozostaje:

* pobieranie tresci artykulow w trybie `--links`,
* pobieranie transkrypcji YouTube w trybie `--links`,
* mieszanie linkow z pelna trescia w jednym wyniku,
* nowy format eksportu do pliku,
* dodatkowa klasyfikacja semantyczna typu "czy to na pewno news".

MVP opiera sie na istniejacej klasyfikacji: "YouTube" vs "nie-YouTube".

## 5. Interfejs CLI

### 5.1 Nowa flaga

| Flaga | Opis |
| --- | --- |
| `--links` | Tryb, w ktorym aplikacja zwraca tylko linki do wpisow artykulowych i pomija cala ekstrakcje tresci |

### 5.2 Relacja do istniejacych flag

W trybie `--links`:

* `--playwright` nie ma znaczenia funkcjonalnego, bo nie dochodzi do ekstrakcji tresci,
* logika chunkowania i liczenia tokenow nie jest wymagana dla samych URL-i w MVP,
* `--interactive` / `--no-interactive` pozostaja zgodne z obecnym mechanizmem dostarczenia wyniku.

## 6. Integracja z obecna architektura

### 6.1 Oczekiwane zmiany logiczne

Nowa flaga powinna zostac obsluzona w warstwie:

* `cli.py` – parsowanie argumentu `--links`,
* `app.py` – osobna sciezka wykonania dla trybu links-only,
* `core/` – ewentualna pomocnicza logika filtrowania / budowy listy URL-i.

### 6.2 Niezmienione elementy

Bez zmian pozostaja:

* integracja z Miniflux dla pobrania listy `unread`,
* dotychczasowy domyslny workflow pobierania tresci bez flagi `--links`,
* obecna architektura modulowa projektu.

## 7. Kryteria akceptacji

* [ ] Po uruchomieniu z `--links` aplikacja nie probuje pobierac tresci artykulow.
* [ ] Po uruchomieniu z `--links` aplikacja nie probuje pobierac transkrypcji YouTube.
* [ ] Wynik zawiera tylko URL-e wpisow artykulowych, po jednym na linie.
* [ ] Kolejnosc linkow odpowiada kolejnosci wpisow `unread` z Miniflux.
* [ ] Domyslne zachowanie aplikacji bez `--links` pozostaje bez zmian.
* [ ] Wpisy YouTube nie sa uwzgledniane w wyniku trybu `--links`.

## 8. Wartosc biznesowa

* Szybsze zebranie listy zrodel bez kosztu ekstrakcji tresci.
* Prostszy workflow dla uzytkownika, ktory potrzebuje tylko URL-i.
* Mniejsze ryzyko bledow I/O w scenariuszu "lista linkow".
* Zachowanie zgodnosci z obecnym CLI bez naruszania domyslnego przeplywu.

# PRD – Oczyszczanie treści Miniflux przez trafilatura (markdown + noise cleanup)

## 1. Cel produktu

Celem jest poprawa jakosci tresci artykulow pobieranych z Miniflux w domyslnym workflow **Miniflux Prompt Compiler**. Obecnie tresc z `fetch-content` bywa zaszumiona i zawiera znaczniki HTML lub portalowe wstawki nieprzydatne w promptach.

Nowa funkcja ma:

* zamienic HTML z Miniflux na czysty markdown przez `trafilatura`,
* odfiltrowac powtarzalny noise (social media, CTA, techniczne smieci),
* zachowac prosty finalny format: `# {title}` + oczyszczona tresc.

## 2. Problem do rozwiazania

Aktualny przeplyw preferuje Miniflux `fetch-content`, co jest poprawne integracyjnie, ale czesto daje tresc:

* zanieczyszczona elementami nawigacyjnymi,
* z fragmentami social media,
* z nadmiarem nieistotnych linii,
* o nierownej jakosci wzgledem dalszego uzycia w promptach GPT.

Skutkiem sa mniej czytelne prompty i gorszy sygnal tresci merytorycznej.

## 3. Zakres funkcjonalny (In-Scope)

### 3.1 Konwersja HTML -> markdown dla Miniflux

Dla artykulow, gdy `fetch-content` z Miniflux zwroci tresc, aplikacja uruchamia:

* `trafilatura.extract(...)` z ustawieniami:
  * `output_format="markdown"`
  * `include_links=False`
  * `include_images=False`
  * `include_tables=False`
  * `favor_precision=True`
  * `with_metadata=False`

Wynik ekstrakcji jest traktowany jako surowy markdown do dalszego cleanupu.

### 3.2 Cleanup markdown po trafilatura

Na wyniku z `trafilatura` wykonywany jest prosty filtr tekstowy, ktory:

* usuwa linie pasujace do znanych wzorcow noise (regex),
* usuwa linie zawierajace znane portalowe/socjalowe wstawki (`contains`),
* redukuje nadmiar pustych linii (np. 3+ -> 2).

### 3.3 Finalny format tresci artykulu

Po cleanupie finalna tresc artykulu ma format:

* naglowek markdown: `# {title}`
* pusta linia
* oczyszczony markdown tresci

Jesli po ekstrakcji i cleanupie tresc jest pusta, nalezy zwrocic placeholder:

* `_Nie udalo sie wyciagnac tresci artykulu_`

## 4. Zakres zrodel i fallbacki

Konwersja `trafilatura` + cleanup obejmuje **wylacznie** sciezke, w ktorej sukces pochodzi z Miniflux `fetch-content`.

Dla fallbackow:

* Jina,
* Playwright,

zachowanie pozostaje bez zmian w ramach tego PRD.

## 5. Poza zakresem (Out-of-Scope)

Poza zakresem tej zmiany pozostaje:

* zmiana trybu `--links`,
* zmiana klasyfikacji YouTube i obslugi transkrypcji,
* przebudowa architektury ekstrakcji tresci,
* wprowadzanie nowych flag CLI,
* normalizacja outputu fallbackow Jina/Playwright.

## 6. Wplyw na interfejsy i kontrakty

### 6.1 CLI

Bez zmian:

* brak nowych flag,
* brak zmiany semantyki istniejacych flag.

### 6.2 Dane wewnetrzne

Semantyczna zmiana dla artykulow z Miniflux:

* `ProcessedItem.content` przechodzi z surowego HTML na markdown po cleanupie.

## 7. Zaleznosci i wymagania techniczne

Dodana zostaje nowa zaleznosc:

* `trafilatura`

W momencie implementacji zaleznosc musi zostac:

* dodana przez `uv add trafilatura`,
* uzasadniona w `spec.md` w sekcji „Decyzje techniczne”.

## 8. Kryteria akceptacji

* [ ] Dla sukcesu Miniflux (`fetch-content`) i poprawnego HTML wynik zawiera `# {tytul}` oraz markdown bez surowych znacznikow HTML.
* [ ] Linie zdefiniowane jako noise sa usuwane przez cleanup (regex + contains).
* [ ] Nadmiar pustych linii jest redukowany.
* [ ] Gdy `trafilatura` zwroci pusto (lub cleanup wyczyści tresc), zwracany jest placeholder `_Nie udalo sie wyciagnac tresci artykulu_`.
* [ ] Przy bledzie/pustej tresci z Miniflux nadal dziala obecny fallback Jina -> opcjonalnie Playwright.
* [ ] Tryb `--links` pozostaje bez zmian.
* [ ] Sciezka YouTube pozostaje bez zmian.

## 9. Testy i scenariusze walidacji

Minimalny zestaw scenariuszy do implementacji:

1. Miniflux zwraca HTML artykulu -> wynik jest markdown z naglowkiem tytulu.
2. Tresc zawiera znane social/noise linie -> cleanup usuwa je i zostawia tresc merytoryczna.
3. `trafilatura.extract` zwraca `None` lub pusty tekst -> zwracany placeholder.
4. Miniflux `fetch-content` fail/pusto -> uruchamiany niezmieniony fallback Jina/Playwright.
5. Uruchomienie z `--links` oraz przetwarzanie YouTube zachowuje dotychczasowe zachowanie.

## 10. Wartosc biznesowa

* Wyzsza jakosc promptow bez recznego czyszczenia tresci.
* Mniej smieci portalowych i social mediowych w danych wejsciowych dla GPT.
* Lepsza czytelnosc i wieksza powtarzalnosc outputu artykulowego.
* Zachowanie kompatybilnosci z obecnym CLI i fallbackami.

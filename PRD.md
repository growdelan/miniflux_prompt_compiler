# PRD — Fallback Playwright dla ekstrakcji treści artykułów

## 1. Cel dokumentu

Celem niniejszego PRD jest opisanie nowej funkcjonalności w narzędziu **Miniflux Prompt Compiler**, polegającej na **opcjonalnym użyciu Playwright jako mechanizmu fallback**, gdy ekstrakcja treści artykułu przez `jina.ai` zakończy się niepowodzeniem.

Dokument definiuje **zakres MVP**, zachowanie systemu, wymagania niefunkcjonalne oraz kryteria akceptacji, bez naruszania istniejącej, stabilnej architektury aplikacji.

---

## 2. Problem / Problem Statement

Aktualna wersja narzędzia polega na usłudze `r.jina.ai` do ekstrakcji treści artykułów. W praktyce użytkownik regularnie trafia na strony, które:

* aktywnie **blokują boty i scrapery**,
* zwracają błędy HTTP, w szczególności:

  * `HTTP 451: Unavailable For Legal Reasons`,
* są oparte o ciężki JavaScript lub mechanizmy anty-automatyzacyjne.

W takich przypadkach:

* artykuł pozostaje `unread`,
* treść nie trafia do promptu,
* użytkownik traci możliwość przetworzenia wartościowego materiału.

---

## 3. Cel produktu (Product Goal)

Zapewnienie **wysokiej skuteczności ekstrakcji treści artykułów**, nawet w przypadku stron blokujących boty, poprzez:

* użycie **prawdziwej, headless przeglądarki** (Playwright),
* zachowanie prostoty CLI,
* brak wpływu na YouTube i istniejące ścieżki sukcesu.

> Filozofia:
> **„Jeśli wygląda jak sensowny artykuł do czytania, to wystarczy.”**

---

## 4. Zakres funkcjonalny (In Scope)

### 4.1 Aktywacja funkcji

* Fallback Playwright **nie jest domyślnie aktywny**.
* Aktywowany wyłącznie przez flagę CLI:

```bash
uv run main.py --playwright
```

Bez flagi:

* zachowanie aplikacji pozostaje **100% niezmienione**.

---

### 4.2 Warunek uruchomienia Playwrighta

Playwright uruchamia się **wyłącznie dla artykułów (nie YouTube)**, gdy:

* `fetch_article_markdown()`:

  * rzuci wyjątek,
  * zwróci pustą treść,
  * zwróci dowolny błąd HTTP (np. 451).

Tryb działania:

* **lenient** — każdy błąd Jiny → Playwright (jeśli flaga aktywna).

---

### 4.3 Zachowanie Playwrighta (MVP)

#### Przeglądarka

* Playwright uruchamiany:

  * **headless**
  * lokalnie na macOS
* Instalacja:

  * `playwright` jako zależność Pythona
  * wymagane `playwright install`

#### Timeout i próby

* Maksymalny czas na stronę: **20 sekund**
* Liczba prób: **1**
* Brak limitu liczby fallbacków w jednym uruchomieniu

---

### 4.4 Ekstrakcja treści

#### Strategia

* Po załadowaniu strony:

  * próba kliknięcia cookie consent (`Accept`, `Agree`, best-effort),
  * pobranie **plain text** z dokumentu (np. `document.body.innerText`).

#### Reader mode

* Nie jest wymagany w MVP,
* ale architektura powinna umożliwiać jego dodanie w przyszłości.

#### Kryterium sukcesu

* **Dowolny niepusty tekst** uznawany jest za sukces.

---

### 4.5 Obsługa przeszkód

| Sytuacja           | Zachowanie       |
| ------------------ | ---------------- |
| Cookie banner      | Próba kliknięcia |
| Paywall / overlay  | Porażka          |
| Login required     | Porażka          |
| JS error / timeout | Porażka          |

W przypadku porażki:

* wpis pozostaje `unread`,
* aplikacja przechodzi do kolejnego wpisu.

---

## 5. Logowanie i obserwowalność

Wymagane logi (INFO):

* `Jina: start`
* `Jina: error (<reason>)`
* `Playwright: start <URL>`
* `Playwright: cookie-consent clicked`
* `Playwright: success (<chars_count>)`
* `Playwright: failed (paywall detected)`
* `Content source selected: jina | playwright`

Na MVP:

* detekcja paywalla logowana jako **`paywall detected`** (bez szczegółów).

---

## 6. Integracja z istniejącą architekturą

### Zasady

* Brak asynchroniczności
* Brak zmian w:

  * logice YouTube,
  * budowie promptu,
  * oznaczaniu `read`,
  * testach smoke (bez Playwrighta).

### Proponowane rozszerzenia

* Nowy `article_fetcher_with_fallback`:

  * najpierw Jina,
  * potem Playwright (warunkowo).
* Flaga CLI parsowana w `main()` i przekazywana do `run()`.

---

## 7. Out of Scope (na ten etap)

* Reader mode (Safari / Firefox-like)
* Heurystyki czyszczenia treści
* Usuwanie menu / footerów
* Retry Playwrighta
* Asynchroniczność
* Screenshoty / debug artifacts
* Obsługa captcha

---

## 8. Kryteria akceptacji (Acceptance Criteria)

* [ ] Gdy `--playwright` **nie jest użyte**, zachowanie aplikacji jest identyczne jak obecnie
* [ ] Gdy `jina.ai` zwróci błąd (np. 451) i flaga jest aktywna → Playwright próbuje pobrać treść
* [ ] YouTube nigdy nie używa Playwrighta
* [ ] Sukces Playwrighta oznacza:

  * dodanie treści do promptu,
  * oznaczenie wpisu jako `read`
* [ ] Porażka Playwrighta:

  * wpis pozostaje `unread`,
  * proces trwa dalej
* [ ] Logi jasno pokazują:

  * źródło treści,
  * przyczynę porażki (min. `paywall detected`)

---

## 9. Metryka sukcesu (Product Success Metric)

* Spadek liczby artykułów pozostających `unread` z powodu 451 / blokad botów
* Wzrost liczby materiałów trafiających do promptu bez ręcznej interwencji


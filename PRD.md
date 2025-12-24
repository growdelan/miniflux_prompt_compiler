# PRD – Auto‑chunkowanie promptów GPT

## 1. Cel produktu

Celem jest rozszerzenie **Miniflux Prompt Compiler** o inteligentne liczenie tokenów oraz automatyczne dzielenie (chunkowanie) generowanego promptu na wiele promptów, tak aby były one **bezpieczne do wklejenia do modeli GPT** oraz wygodne w codziennym workflow użytkownika.

Funkcja ma zachować podstawowe założenie aplikacji:

* jeden prompt = kompletne artykuły / transkrypcje,
* **bez cięcia treści w środku artykułu**,
* narzędzie pozostaje CLI‑first i bezstanowe (poza lokalnym cache opcjonalnym w przyszłości).

---

## 2. Zakres funkcjonalny (In‑Scope)

### 2.1 Liczenie tokenów

* Aplikacja liczy liczbę tokenów dla:

  * pojedynczego promptu,
  * każdego promptu w trybie chunkowania.
* Domyślny tokenizer:

  * `tiktoken` (jeśli dostępny w środowisku).
* Fallback:

  * przybliżone liczenie tokenów (np. `len(text) / 4`),
  * wyraźna informacja w logach, że wynik jest szacunkowy.

### 2.2 Klasyfikacja promptu

Na podstawie liczby tokenów aplikacja wyświetla etykietę:

| Liczba tokenów  | Etykieta       |
| --------------- | -------------- |
| < 32 000        | `GPT-Instant`  |
| 32 000 – 49 999 | `GPT-Thinking` |
| ≥ 50 000        | `CHUNKING`     |

Etykieta jest wyświetlana:

* w stdout po zakończeniu przetwarzania,
* osobno dla każdego promptu w trybie chunkowania.

---

## 3. Chunkowanie promptów

### 3.1 Zasady ogólne

* Chunkowanie uruchamia się automatycznie, gdy **łączna liczba tokenów przekracza limit** (`--max-tokens`, domyślnie `50_000`).
* Chunkowanie odbywa się **wyłącznie na granicy całych artykułów/transkrypcji**.
* Treść pojedynczego artykułu **nigdy nie jest dzielona** (MVP).

### 3.2 Algorytm

1. Zachowana zostaje kolejność wpisów z Miniflux.
2. Artykuły są dokładane do aktualnego chunku jeden po drugim.
3. Po każdym dodaniu:

   * budowany jest tymczasowy prompt,
   * liczona jest liczba tokenów.
4. Jeśli przekroczony zostanie limit:

   * ostatni artykuł jest cofany,
   * aktualny chunk zostaje zamknięty,
   * rozpoczynany jest nowy chunk od cofniętego artykułu.

### 3.3 Edge case – pojedynczy artykuł > limit

Domyślne zachowanie:

* artykuł jest pomijany,
* w logach pojawia się ostrzeżenie:

  * `Item exceeds max token limit and was skipped`.

(Obsługa dzielenia pojedynczego artykułu poza zakresem MVP).

---

## 4. Tryb interaktywny (kopiowanie promptów)

### 4.1 Zachowanie aplikacji

Jeśli powstał więcej niż jeden prompt:

* aplikacja informuje:

  * ile promptów zostanie wygenerowanych,
  * jaki jest ich zakres tokenów.

Przykład:

```
Total tokens: 73 120 → CHUNKING
Generated prompts: 2
Press [Enter] to copy prompt 1/2
```

### 4.2 Przebieg interakcji

* Po naciśnięciu `Enter`:

  * aktualny prompt zostaje skopiowany do schowka,
  * wyświetlany jest komunikat:

    * `Copied prompt 1/2 (31 842 tokens – GPT-Instant)`.
* Proces powtarza się aż do ostatniego promptu.

### 4.3 Tryb nieinteraktywny

* Flaga `--no-interactive`:

  * brak oczekiwania na `Enter`,
  * prompty są wypisywane kolejno do stdout **lub** zapisywane do plików (przyszłe rozszerzenie).

---

## 5. Interfejs CLI

### 5.1 Nowe flagi

| Flaga                              | Opis                                                  |         |                                |
| ---------------------------------- | ----------------------------------------------------- | ------- | ------------------------------ |
| `--max-tokens <int>`               | Maksymalna liczba tokenów na prompt (domyślnie 50000) |         |                                |
| `--interactive / --no-interactive` | Włącza/wyłącza tryb kopiowania po Enter               |         |                                |
| `--tokenizer auto                  | tiktoken                                              | approx` | Wybór sposobu liczenia tokenów |

---

## 6. Integracja z obecną architekturą

### 6.1 Nowe funkcje

* `count_tokens(text: str) -> int`
* `label_for_tokens(count: int) -> str`
* `build_prompts_with_chunking(items: list[dict[str,str]], max_tokens: int) -> list[str]`

### 6.2 Niezmienione elementy

* `process_entry()` – bez zmian
* `build_prompt()` – używana do generowania pojedynczego promptu
* logika pobierania treści (Jina / Playwright / YouTube) – bez zmian

---

## 7. Kryteria akceptacji

* [ ] Prompt < 32k tokenów → brak chunkowania, etykieta `GPT-Instant`
* [ ] Prompt 32k–49k → brak chunkowania, etykieta `GPT-Thinking`
* [ ] Prompt ≥ 50k → poprawne chunkowanie po artykułach
* [ ] Każdy chunk mieści się w limicie tokenów
* [ ] Użytkownik może sekwencyjnie kopiować prompty do schowka
* [ ] Brak cięcia treści w środku artykułu

---

## 8. Wartość biznesowa

* Eliminacja ręcznego sprawdzania limitów modeli GPT
* Bezpieczne i przewidywalne wklejanie promptów
* Skalowanie workflow wraz z rosnącą liczbą źródeł
* Wyraźna przewaga UX nad „ręcznym składaniem promptów"


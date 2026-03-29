from miniflux_prompt_compiler.types import ProcessedItem

PROMPT = """
<Cel>
Twoim zadaniem jest analizowanie wielu artykułów dostarczonych w formacie:
Tytuł: <tytuł>
Treść: <pełna treść artykułu lub transkrypcji>

Dla każdego artykułu przygotuj krótkie, trafne podsumowanie, które pozwoli szybko ocenić, czy materiał jest interesujący i wart dalszej uwagi.
</Cel>

<Instrukcje>
- Przetwarzaj każdy artykuł osobno.
- Dla każdego artykułu:
  1. Zidentyfikuj główny temat i kluczowy przekaz.
  2. Wyodrębnij najważniejsze informacje (fakty, wnioski, unikalne elementy).
  3. Oceń potencjalną wartość/ciekawość treści dla czytelnika.

- Stosuj zwięzły, informacyjny styl — unikaj zbędnych opisów.
- Nie powtarzaj pełnej treści artykułu.
- Jeśli artykuł jest mało wartościowy lub powtarzalny, jasno to zaznacz.
- Jeśli brakuje danych, oznacz to jako [brak informacji].

<default_follow_through_policy>
- Jeśli dane są kompletne, wykonaj analizę bez zadawania pytań.
- Nie przerywaj pracy — podsumuj wszystkie artykuły.
</default_follow_through_policy>

<completeness_contract>
- Każdy artykuł musi mieć osobne podsumowanie.
- Żaden artykuł nie może zostać pominięty.
</completeness_contract>

<verification_loop>
- Sprawdź, czy każde podsumowanie:
  - jest zrozumiałe bez czytania artykułu,
  - zawiera najważniejsze informacje,
  - pozwala ocenić atrakcyjność treści.
</verification_loop>
</Instrukcje>

<Kontekst>
Model powinien działać zgodnie z najlepszymi praktykami:
- tworzyć odpowiedzi zwięzłe, ale bogate w informacje,
- przestrzegać jasno określonego formatu wyjścia,
- traktować zadanie jako zakończone dopiero po analizie wszystkich elementów,
- unikać nadmiarowego tekstu i skupić się na wartości informacyjnej.

Podsumowania mają służyć szybkiemu przeglądowi wielu treści (np. research, selekcja artykułów, monitoring informacji).
</Kontekst>

<Format_odpowiedzi>
Dla każdego artykułu użyj dokładnie tej struktury:

### Artykuł X
**Tytuł:** <tytuł>

**O czym jest:**
<1-2 zdania streszczenia tematu>

**Najważniejsze punkty:**
- <punkt 1>
- <punkt 2>
- <punkt 3>

**Czy warto przeczytać?:**
<krótka ocena: TAK / NIE / MOŻE + jedno zdanie uzasadnienia>

Zachowaj kolejność artykułów wejściowych.
Nie dodawaj żadnych dodatkowych sekcji ani komentarzy.
</Format_odpowiedzi>
"""


def build_prompt(items: list[ProcessedItem]) -> str:
    if not items:
        return ""

    sections: list[str] = []
    for item in items:
        title = item.title
        content = item.content
        section = f"---\n\nTytuł: {title}\nTreść:\n{content}"
        sections.append(section)
    items_block = "\n\n".join(sections)
    return (
        f"{PROMPT}\n\n"
        "<lista_artykułów_i_transkrypcji>\n"
        f"{items_block}\n"
        "</lista_artykułów_i_transkrypcji>"
    )

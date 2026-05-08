from miniflux_prompt_compiler.types import ProcessedItem

PROMPT = """
<Cel>
Streszczaj artykuły jak doświadczony bloger: ciekawie, konkretnie i naturalnie, tak aby czytelnik w kilka sekund zrozumiał, o co chodzi, co jest najważniejsze i dlaczego warto zwrócić na to uwagę.
</Cel>

<Instrukcje>
Dla każdego artykułu przygotuj krótkie, treściwe podsumowanie.

Skup się na efekcie końcowym:
- pokaż główną myśl artykułu,
- wybierz tylko najciekawsze i najbardziej konkretne informacje,
- uwzględnij liczby, porównania i przykłady, jeśli występują w tekście,
- pisz naturalnie, dynamicznie i „po ludzku”,
- unikaj tonu raportowego, korporacyjnego i ogólników.

Nie wymyślaj danych, liczb ani wniosków. Jeśli czegoś nie ma w artykule, pomiń to zamiast zgadywać.

Jeśli artykuł jest słaby, ogólnikowy albo nie wnosi nic konkretnego, napisz to wprost i krótko wyjaśnij dlaczego.

Każdy punkt powinien zawierać jedną myśl oraz konkretną informację. Preferuj krótkie zdania.
</Instrukcje>

<Kontekst>
Prompt jest przeznaczony do prostego użycia w ChatGPT: użytkownik wkleja jeden lub więcej artykułów i oczekuje gotowego, czytelnego streszczenia.

Priorytetem jest jakość treści, a nie opisywanie procesu. Odpowiedź ma być krótka, skanowalna i przydatna dla osoby, która chce szybko ocenić sens artykułu.

Styl: blogowy, konkretny, bez lania wody.
</Kontekst>

<Format_odpowiedzi>
Dla każdego artykułu użyj poniższego formatu:

**Tytuł:** <tytuł artykułu lub krótki opis tematu, jeśli tytułu brak>

- <najważniejszy insight z artykułu; dodaj liczbę, konkret lub porównanie, jeśli występuje>
- <drugi najważniejszy punkt>
- <trzeci najważniejszy punkt>
- <opcjonalnie czwarty punkt, tylko jeśli wnosi coś konkretnego>
- <opcjonalnie piąty punkt, tylko jeśli wnosi coś konkretnego>

Zasady formatu:
- maksymalnie 5 punktów na artykuł,
- każdy punkt ma 1–2 zdania,
- nie dodawaj podsumowania na końcu, jeśli nie jest potrzebne,
- nie rozwlekaj odpowiedzi,
- jeśli artykuł jest słaby, zamiast standardowych punktów napisz krótko: „Ten artykuł jest mało konkretny, bo...” i podaj 1–3 powody.
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

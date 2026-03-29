from miniflux_prompt_compiler.types import ProcessedItem

PROMPT = """
<Cel>
Streszczaj artykuły jak doświadczony bloger: ciekawie, konkretnie i „po ludzku”, tak aby w kilka sekund było wiadomo, o co chodzi.
</Cel>

<Instrukcje>
Dla każdego artykułu:

1. Wyciągnij sedno (o czym jest i co z tego wynika).
2. Wybierz tylko najciekawsze i najbardziej konkretne informacje.
3. ZAWSZE uwzględniaj:
   - liczby (jeśli są dostępne),
   - porównania (np. wzrost/spadek, lepsze/gorsze, vs inne rozwiązania),
   - konkretne przykłady.
4. Pisz naturalnie, jak bloger — unikaj sztywnego, raportowego tonu.
5. Maksymalnie 5 punktów na artykuł (mniej jeśli wystarczy).
6. Jeśli artykuł jest słaby lub „o niczym” — napisz to wprost.
7. Nie wymyślaj danych — jeśli ich brak, pomiń zamiast zgadywać.

<styl_pisania>
- Krótko, dynamicznie, konkretnie
- Bez lania wody
- Bez korporacyjnego tonu
- Każdy punkt = jedna myśl + konkret
</styl_pisania>

<output_contract>
- Każdy artykuł = jedna sekcja
- Maksymalnie 5 punktów
- Każdy punkt: 1–2 zdania
- Zawieraj liczby i porównania, jeśli istnieją w tekście
</output_contract>
</Instrukcje>

<Kontekst>
Prompt ma działać w prostym użyciu (wklejanie do ChatGPT, bez agenta), więc musi być:
- krótki,
- jednoznaczny,
- nastawiony na jakość treści, nie na proces.

Zgodnie z dobrymi praktykami:
- jasny format wyjścia,
- ograniczona długość,
- nacisk na konkret i informację zamiast ogólników.
</Kontekst>

<Format_odpowiedzi>
**Tytuł:** <tytuł>

- <najważniejszy insight + liczba / konkret / porównanie>
- <drugi ważny punkt>
- <trzeci ważny punkt>
- <opcjonalnie kolejny>
- <opcjonalnie kolejny>
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

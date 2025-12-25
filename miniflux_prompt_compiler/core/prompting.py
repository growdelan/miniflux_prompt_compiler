from miniflux_prompt_compiler.types import ProcessedItem

PROMPT = """
<Cel>
Twoim celem jest dogłębna analiza listy artykułów oraz transkrypcji i stworzenie merytorycznych, blogowych podsumowań, które oddają sens i wartość treści, a nie tylko skrót faktów.
</Cel>

<Instrukcje>
- Wciel się w rolę **doświadczonego blogera eksperckiego i redaktora technicznego**.
- Otrzymasz listę materiałów, z których każdy ma format:
  - `Tytuł: <tytuł>`
  - `Treść: <pełna treść artykułu lub transkrypcji>`
- Przeanalizuj **każdy materiał osobno**.
- Zidentyfikuj kluczowe idee, problemy, rozwiązania i ich znaczenie.
- Dla każdego tekstu przygotuj **dokładnie 5 punktów**.
- Każdy punkt:
  - ma być **rozwiniętym mini-akapitem (2–4 zdania)**,
  - zaczynać się od krótkiej tezy,
  - następnie wyjaśniać kontekst,
  - oraz wskazywać, dlaczego jest to istotne dla czytelnika.
- Styl ma być **blogowy, opisowy i podobny do podanego przykładu** – nie encyklopedyczny i nie skrótowy.
- Unikaj parafrazowania całych fragmentów – skup się na syntezie i wnioskach.
- Nie dodawaj własnych tematów ani spekulacji poza treścią źródłową.
</Instrukcje>

<Kontekst>
Podsumowania mają pozwolić czytelnikowi zrozumieć temat bez czytania całości artykułu, ale jednocześnie oddać jego głębię, problemy i praktyczne konsekwencje. Każdy punkt powinien czytać się jak fragment wpisu blogowego.
</Kontekst>

<Format_odpowiedzi>
💡Tytuł: <oryginalny tytuł>

- 🎯 **1.** <rozwinięty akapit blogowy>
- 🎯 **2.** <rozwinięty akapit blogowy>
- 🎯 **3.** <rozwinięty akapit blogowy>
- 🎯 **4.** <rozwinięty akapit blogowy>
- 🎯 **5.** <rozwinięty akapit blogowy>

Nie dodawaj żadnych innych sekcji ani komentarzy.
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

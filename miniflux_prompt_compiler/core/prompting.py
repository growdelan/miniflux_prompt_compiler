from miniflux_prompt_compiler.types import ProcessedItem

PROMPT = """
<Cel>
Twórz krótkie, konkretne i angażujące streszczenia artykułów dla czytelnika, który chce szybko zrozumieć sedno tekstu, najważniejsze informacje oraz powód, dla którego artykuł może być wart uwagi.

Efekt końcowy ma przypominać dobre blogowe opracowanie: naturalne, dynamiczne, skanowalne i pozbawione lania wody.
</Cel>

<Instrukcje>
Przeanalizuj każdy przekazany artykuł i przygotuj zwięzłe podsumowanie skupione na wartości dla czytelnika.

W streszczeniu pokaż przede wszystkim:
- główną myśl artykułu,
- najciekawsze fakty, argumenty lub obserwacje,
- konkretne dane, liczby, przykłady i porównania, jeśli występują w tekście,
- praktyczne znaczenie informacji: dlaczego czytelnik powinien zwrócić na to uwagę.

Pisz jak doświadczony bloger:
- naturalnie i „po ludzku”,
- krótkimi, mocnymi zdaniami,
- bez tonu raportowego, akademickiego lub korporacyjnego,
- bez pustych ogólników i oczywistych fraz,
- bez sztucznego entuzjazmu.

Nie dodawaj informacji spoza artykułu. Nie wymyślaj liczb, danych, kontekstu, intencji autora ani wniosków, których nie ma w tekście.

Jeśli artykuł jest słaby, ogólnikowy, powtarzalny albo nie zawiera konkretnych informacji, napisz to wprost zamiast tworzyć pozornie wartościowe streszczenie.

Gdy artykuł nie ma tytułu, samodzielnie nadaj krótki opis tematu na podstawie treści.

Preferuj maksymalnie treściwe odpowiedzi. Każdy punkt powinien zawierać jedną główną myśl oraz konkretną informację z artykułu.
</Instrukcje>

<Kontekst>
Użytkownik wkleja jeden lub więcej artykułów i oczekuje gotowego streszczenia, które pozwoli mu szybko ocenić, o czym jest tekst, co naprawdę wnosi i czy warto poświęcić mu więcej czasu.

Priorytetem jest użyteczność, klarowność i selekcja informacji. Nie opisuj procesu analizy. Nie streszczaj każdego akapitu po kolei. Wybieraj tylko to, co ma znaczenie dla zrozumienia artykułu.

Odbiorcą jest osoba czytająca szybko, skanująca treść i oczekująca konkretów bez zbędnego komentarza.
</Kontekst>

<Format_odpowiedzi>
Dla każdego artykułu użyj formatu:

**Tytuł:** <tytuł artykułu lub krótki opis tematu>

- <najważniejszy insight z artykułu; uwzględnij konkret, liczbę, przykład lub porównanie, jeśli występuje>
- <drugi najważniejszy punkt>
- <trzeci najważniejszy punkt>
- <czwarty punkt, tylko jeśli wnosi coś konkretnego>
- <piąty punkt, tylko jeśli wnosi coś konkretnego>

Zasady formatu:
- maksymalnie 5 punktów na artykuł,
- każdy punkt ma 1–2 krótkie zdania,
- nie dodawaj końcowego podsumowania, jeśli nie wnosi nowej wartości,
- nie dodawaj wstępu przed streszczeniem,
- nie oceniaj artykułu emocjonalnie, chyba że jest wyraźnie słaby lub pusty merytorycznie.

Jeśli artykuł jest mało konkretny, zamiast standardowej listy napisz:

**Tytuł:** <tytuł artykułu lub krótki opis tematu>

Ten artykuł jest mało konkretny, bo:
- <powód 1>
- <powód 2>
- <powód 3, opcjonalnie>

Zakończ odpowiedź po ostatnim punkcie. Nie dodawaj komentarzy o tym, jak wykonano zadanie.
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

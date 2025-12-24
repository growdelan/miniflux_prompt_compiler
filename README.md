# Miniflux Prompt Compiler

Narzędzie, które automatycznie zamienia nieprzeczytane RSS-y i filmy z YouTube z Miniflux w jeden gotowy do wklejenia prompt tekstowy.

## Wymagania
- Python 3.13+
- `uv`
- `playwright` (opcjonalnie, tylko dla fallback)

## Konfiguracja
Utworz `.env` w katalogu projektu:

```env
MINIFLUX_API_TOKEN=...
```

## Uruchamianie
```sh
uv run main.py
```

Fallback Playwright po bledzie Jiny:
```sh
uv run main.py --playwright
```

Kontrola limitu tokenow i trybu liczenia:
```sh
uv run main.py --max-tokens 50000 --tokenizer auto
uv run main.py --max-tokens 32000 --tokenizer approx
```

Tryb nieinteraktywny (wypisuje prompty do stdout):
```sh
uv run main.py --no-interactive
```

Instalacja przegladarek Playwright (wymagane przy uzyciu fallbacku):
```sh
uv run playwright install
```

## Testy
```sh
python -m unittest discover -s tests
```

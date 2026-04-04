# Miniflux Prompt Compiler

Narzędzie, które automatycznie zamienia nieprzeczytane RSS-y i filmy z YouTube z Miniflux w jeden gotowy do wklejenia prompt tekstowy.

## Wymagania
- Python 3.13+
- `uv`
- `playwright` (opcjonalnie, tylko dla fallback)
- `trafilatura` (normalizacja HTML z Miniflux do markdown)

## Konfiguracja
Utworz `.env` w katalogu projektu:

```env
MINIFLUX_API_TOKEN=...
MINIFLUX_BASE_URL=http://localhost:8080
```

## Uruchamianie
```sh
uv run main.py
```

Nadpisanie adresu Miniflux (CLI ma pierwszenstwo nad .env):
```sh
uv run main.py --base-url http://localhost:8080
```

Fallback Playwright po bledzie Jiny:
```sh
uv run main.py --playwright
```

Ekstrakcja artykulow:
- najpierw Miniflux `fetch-content` (update_content=true),
- przy sukcesie Miniflux: konwersja HTML -> markdown przez `trafilatura` oraz cleanup powtarzalnego noise,
- potem Jina,
- na koncu (opcjonalnie) Playwright po bledzie Jiny.

Kontrola limitu tokenow i trybu liczenia:
```sh
uv run main.py --max-tokens 50000 --tokenizer auto
uv run main.py --max-tokens 32000 --tokenizer approx
```

Tryb nieinteraktywny (wypisuje prompty do stdout):
```sh
uv run main.py --no-interactive
```

Tryb samych linkow do newsow/artykulow (bez pobierania tresci, wpisy uwzglednione w wyniku sa oznaczane jako `read`):
```sh
uv run main.py --links
uv run main.py --links --no-interactive
```

Instalacja przegladarek Playwright (wymagane przy uzyciu fallbacku):
```sh
uv run playwright install
```

## Testy
```sh
uv run python -m unittest discover -s tests -p "test_*.py"
```

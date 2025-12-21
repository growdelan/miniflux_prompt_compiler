# Miniflux Prompt Compiler

Narzędzie, które automatycznie zamienia nieprzeczytane RSS-y i filmy z YouTube z Miniflux w jeden gotowy do wklejenia prompt tekstowy.

## Wymagania
- Python 3.13+
- `uv`

## Konfiguracja
Utworz `.env` w katalogu projektu:

```env
MINIFLUX_API_TOKEN=...
```

## Uruchamianie
```sh
uv run main.py
```

## Testy
```sh
python -m unittest discover -s tests
```

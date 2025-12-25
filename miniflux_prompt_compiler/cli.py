import argparse
import logging
import sys

from miniflux_prompt_compiler.app import run
from miniflux_prompt_compiler.core.tokenization import (
    MAX_PROMPT_TOKENS,
    TOKENIZER_OPTIONS,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Miniflux Prompt Compiler")
    parser.add_argument(
        "--playwright",
        action="store_true",
        help="Wlacz fallback Playwright po bledzie Jiny.",
    )
    interactive_group = parser.add_mutually_exclusive_group()
    interactive_group.add_argument(
        "--interactive",
        action="store_true",
        dest="interactive",
        help="Wlacz tryb interaktywny kopiowania promptow.",
    )
    interactive_group.add_argument(
        "--no-interactive",
        action="store_false",
        dest="interactive",
        help="Wylacz tryb interaktywny (wypisz prompty do stdout).",
    )
    parser.set_defaults(interactive=True)
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=MAX_PROMPT_TOKENS,
        help="Maksymalna liczba tokenow na prompt (domyslnie 50000).",
    )
    parser.add_argument(
        "--tokenizer",
        choices=sorted(TOKENIZER_OPTIONS),
        default="auto",
        help="Wybor tokenizera: auto, tiktoken, approx.",
    )
    return parser.parse_args(argv)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        args = parse_args(sys.argv[1:])
        message = run(
            use_playwright=args.playwright,
            interactive=args.interactive,
            max_tokens=args.max_tokens,
            tokenizer=args.tokenizer,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

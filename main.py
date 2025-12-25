from miniflux_prompt_compiler.adapters.clipboard import copy_to_clipboard
from miniflux_prompt_compiler.adapters.jina import (
    fetch_article_markdown,
    fetch_article_with_fallback,
)
from miniflux_prompt_compiler.adapters.miniflux_http import (
    fetch_unread_entries,
    mark_entry_read,
)
from miniflux_prompt_compiler.adapters.playwright_fetch import (
    fetch_article_with_playwright,
)
from miniflux_prompt_compiler.adapters.youtube import fetch_youtube_transcript
from miniflux_prompt_compiler.app import process_entry, run
from miniflux_prompt_compiler.cli import main, parse_args
from miniflux_prompt_compiler.config import load_env
from miniflux_prompt_compiler.core.chunking import build_prompts_with_chunking
from miniflux_prompt_compiler.core.prompting import PROMPT, build_prompt
from miniflux_prompt_compiler.core.tokenization import (
    MAX_PROMPT_TOKENS,
    TOKEN_LABELS,
    TOKENIZER_OPTIONS,
    count_tokens,
    label_for_tokens,
)
from miniflux_prompt_compiler.core.url_classify import (
    extract_youtube_id,
    is_youtube_shorts,
    is_youtube_url,
)

__all__ = [
    "MAX_PROMPT_TOKENS",
    "PROMPT",
    "TOKEN_LABELS",
    "TOKENIZER_OPTIONS",
    "build_prompt",
    "build_prompts_with_chunking",
    "copy_to_clipboard",
    "count_tokens",
    "extract_youtube_id",
    "fetch_article_markdown",
    "fetch_article_with_fallback",
    "fetch_article_with_playwright",
    "fetch_unread_entries",
    "fetch_youtube_transcript",
    "is_youtube_shorts",
    "is_youtube_url",
    "label_for_tokens",
    "load_env",
    "mark_entry_read",
    "parse_args",
    "process_entry",
    "run",
]


if __name__ == "__main__":
    raise SystemExit(main())

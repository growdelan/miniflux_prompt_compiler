import logging

TOKEN_LABELS = (
    (32000, "GPT-Instant"),
    (50000, "GPT-Thinking"),
)
TOKENIZER_OPTIONS = {"auto", "tiktoken", "approx"}


def count_tokens(text: str, tokenizer: str = "auto") -> int:
    if tokenizer not in TOKENIZER_OPTIONS:
        raise ValueError(f"Nieznany tokenizer: {tokenizer}")

    if tokenizer in {"auto", "tiktoken"}:
        try:
            import tiktoken
        except ImportError as exc:
            if tokenizer == "tiktoken":
                raise RuntimeError(
                    "Tokenizer tiktoken nie jest dostepny w srodowisku."
                ) from exc
            logging.info("Tokenizer: approx (fallback, wynik szacunkowy)")
            return max(1, len(text) // 4)
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    logging.info("Tokenizer: approx (wynik szacunkowy)")
    return max(1, len(text) // 4)


def label_for_tokens(count: int) -> str:
    for limit, label in TOKEN_LABELS:
        if count < limit:
            return label
    return "CHUNKING"

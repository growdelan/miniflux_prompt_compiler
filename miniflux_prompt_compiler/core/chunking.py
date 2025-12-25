import logging

from miniflux_prompt_compiler.core.prompting import build_prompt
from miniflux_prompt_compiler.core.tokenization import count_tokens
from miniflux_prompt_compiler.types import ProcessedItem


def build_prompts_with_chunking(
    items: list[ProcessedItem], max_tokens: int, tokenizer: str = "auto"
) -> list[str]:
    prompts: list[str] = []
    current: list[ProcessedItem] = []

    for item in items:
        current.append(item)
        prompt = build_prompt(current)
        if not prompt:
            current.pop()
            continue
        if count_tokens(prompt, tokenizer=tokenizer) <= max_tokens:
            continue

        current.pop()
        if current:
            prompts.append(build_prompt(current))
            current = [item]
            prompt = build_prompt(current)
            if prompt and count_tokens(prompt, tokenizer=tokenizer) <= max_tokens:
                continue

        logging.info("Item exceeds max token limit and was skipped")
        current = []

    if current:
        prompts.append(build_prompt(current))

    return prompts

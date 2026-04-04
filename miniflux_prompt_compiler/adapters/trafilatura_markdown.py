import re

import trafilatura

NOISE_PATTERNS = [
    r"(?im)^follow us\s*$",
    r"(?im)^font size\s*$",
    r"(?im)^save\s*$",
    r"(?im)^print\s*$",
    r"(?im)^rate story\s*$",
    r"(?im)^listen\s*$",
    r"(?im)^loading\.\.\.\s*$",
    r"(?im)^live events\s*$",
    r"(?im)^read more news on\s*$",
    r"(?im)^download the .* app.*$",
    r"(?im)^\s*you can now subscribe to our .*?$",
    r"(?im)^\s*catch all the .*?$",
    r"(?im)^faqs:?\s*$",
    r"(?im)^q:\s+.*$",
    r"(?im)^a:\s+.*$",
]

NOISE_LINE_CONTAINS = [
    "whatsapp channel",
    "follow channel",
    "read more news on",
    "download the economic times news app",
    "catch all the us news",
    "international breaking news events",
]


def cleanup_markdown(markdown: str) -> str:
    text = markdown
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, "", text)

    cleaned_lines: list[str] = []
    for line in text.splitlines():
        normalized = line.strip().lower()
        if not normalized:
            cleaned_lines.append("")
            continue
        if any(fragment in normalized for fragment in NOISE_LINE_CONTAINS):
            continue
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def html_to_clean_markdown(title: str, html: str) -> str:
    content = trafilatura.extract(
        html,
        output_format="markdown",
        include_links=False,
        include_images=False,
        include_tables=False,
        favor_precision=True,
        with_metadata=False,
    ) or ""
    content = cleanup_markdown(content)
    if not content:
        content = "_Nie udało się wyciągnąć treści artykułu_"
    return f"# {title}\n\n{content}"

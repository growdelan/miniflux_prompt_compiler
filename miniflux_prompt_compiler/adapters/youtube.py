
from miniflux_prompt_compiler.types import ContentFetchError


def _extract_text(item: object) -> str:
    if isinstance(item, dict):
        return str(item.get("text", "")).strip()
    text_value = getattr(item, "text", "")
    if isinstance(text_value, str):
        return text_value.strip()
    return ""


def fetch_youtube_transcript(video_id: str, preferred_language: str = "en") -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise ContentFetchError(
            "Brak zaleznosci youtube_transcript_api w srodowisku."
        ) from exc

    try:
        # Decyzja: obslugujemy oba API (stare get_transcript i nowe fetch),
        # bo biblioteka zmieniala sposob wywolania miedzy wersjami.
        get_transcript = getattr(YouTubeTranscriptApi, "get_transcript", None)
        fetch = getattr(YouTubeTranscriptApi, "fetch", None)
        if callable(get_transcript):
            transcript = get_transcript(video_id, languages=[preferred_language])
        elif callable(fetch):
            transcript = YouTubeTranscriptApi().fetch(
                video_id, languages=[preferred_language]
            )
        else:
            raise ContentFetchError("Nieznany interfejs youtube_transcript_api.")
    except Exception as exc:  # youtube_transcript_api rzuca kilka typow wyjatkow
        raise ContentFetchError(f"Brak transkrypcji YouTube: {exc}") from exc

    lines: list[str] = []
    if hasattr(transcript, "snippets"):
        snippets = getattr(transcript, "snippets", [])
        for snippet in snippets:
            lines.append(_extract_text(snippet))
    else:
        try:
            for item in transcript:
                lines.append(_extract_text(item))
        except TypeError:
            lines = []
    content = " ".join(line for line in lines if line)
    if not content.strip():
        raise ContentFetchError("Pusta transkrypcja YouTube.")
    return content

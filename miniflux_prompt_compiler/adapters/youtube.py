def fetch_youtube_transcript(video_id: str, preferred_language: str = "en") -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise RuntimeError(
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
            raise RuntimeError("Nieznany interfejs youtube_transcript_api.")
    except Exception as exc:  # youtube_transcript_api rzuca kilka typow wyjatkow
        raise RuntimeError(f"Brak transkrypcji YouTube: {exc}") from exc

    if hasattr(transcript, "snippets"):
        lines = [snippet.text for snippet in transcript]
    else:
        lines = [item.get("text", "") for item in transcript]
    content = " ".join(line for line in lines if line)
    if not content.strip():
        raise RuntimeError("Pusta transkrypcja YouTube.")
    return content

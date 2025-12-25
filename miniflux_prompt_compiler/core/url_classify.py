from urllib.parse import parse_qs, urlparse


def is_youtube_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    return host in {"youtube.com", "www.youtube.com", "youtu.be"}


def is_youtube_shorts(url: str) -> bool:
    parsed = urlparse(url)
    return "/shorts/" in parsed.path


def extract_youtube_id(url: str) -> str | None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host in {"youtube.com", "www.youtube.com"}:
        if parsed.path != "/watch":
            return None
        query = parse_qs(parsed.query)
        video_ids = query.get("v", [])
        return video_ids[0] if video_ids else None
    if host == "youtu.be":
        return parsed.path.lstrip("/") or None
    return None

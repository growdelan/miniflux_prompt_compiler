import tempfile
import unittest
from pathlib import Path

from main import run


class SmokeTest(unittest.TestCase):
    def test_run_reads_token_from_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("MINIFLUX_API_TOKEN=abc123\n", encoding="utf-8")

            def fake_fetcher(base_url: str, token: str) -> list[dict[str, object]]:
                return [
                    {"id": 1, "title": "Artykul", "url": "https://example.com/a"},
                    {"id": 2, "title": "Video", "url": "https://youtu.be/abc123"},
                    {
                        "id": 3,
                        "title": "Shorts",
                        "url": "https://www.youtube.com/shorts/xyz987",
                    },
                ]

            def fake_article_fetcher(url: str) -> str:
                return "content"

            def fake_youtube_fetcher(video_id: str) -> str:
                return "transcript"

            output = run(
                env_path=env_path,
                environ={},
                fetcher=fake_fetcher,
                article_fetcher=fake_article_fetcher,
                youtube_fetcher=fake_youtube_fetcher,
            )

        self.assertEqual(
            output, "Unread entries: 3; Success: 2; Failed: 0; Skipped: 1"
        )


if __name__ == "__main__":
    unittest.main()

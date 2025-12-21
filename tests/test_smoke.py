import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from main import (
    build_prompt,
    extract_youtube_id,
    is_youtube_shorts,
    is_youtube_url,
    run,
)


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

            marked: list[int] = []

            def fake_marker(base_url: str, token: str, entry_id: int) -> None:
                marked.append(entry_id)

            clipboard_values: list[str] = []

            def fake_clipboard(text: str) -> None:
                clipboard_values.append(text)

            output = run(
                env_path=env_path,
                environ={},
                fetcher=fake_fetcher,
                article_fetcher=fake_article_fetcher,
                youtube_fetcher=fake_youtube_fetcher,
                marker=fake_marker,
                clipboard=fake_clipboard,
            )

        self.assertEqual(
            output, "Unread entries: 3; Success: 2; Failed: 0; Skipped: 1"
        )
        self.assertEqual(marked, [1, 2])
        self.assertEqual(len(clipboard_values), 1)
        self.assertIn("Tytuł: Artykul", clipboard_values[0])
        self.assertIn("Treść:\ncontent", clipboard_values[0])


class MarkReadFallbackTest(unittest.TestCase):
    def test_mark_entry_read_falls_back_on_400(self) -> None:
        from main import mark_entry_read

        calls: list[tuple[str, str]] = []

        class DummyResponse:
            def __enter__(self) -> "DummyResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                return None

        def fake_urlopen(request, timeout=10):  # type: ignore[no-untyped-def]
            calls.append((request.method, request.full_url))
            if len(calls) == 1:
                raise urllib.error.HTTPError(
                    request.full_url, 400, "Bad Request", hdrs=None, fp=None
                )
            return DummyResponse()

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            mark_entry_read("http://example.com", "token", 123)

        self.assertEqual(
            calls,
            [
                ("PUT", "http://example.com/v1/entries?status=read"),
                ("PUT", "http://example.com/v1/entries"),
            ],
        )


class ClassificationTest(unittest.TestCase):
    def test_youtube_detection_and_shorts(self) -> None:
        self.assertTrue(is_youtube_url("https://youtube.com/watch?v=abc"))
        self.assertTrue(is_youtube_url("https://www.youtube.com/watch?v=abc"))
        self.assertTrue(is_youtube_url("https://youtu.be/abc"))
        self.assertFalse(is_youtube_url("https://example.com/watch?v=abc"))

        self.assertTrue(is_youtube_shorts("https://www.youtube.com/shorts/xyz"))
        self.assertFalse(is_youtube_shorts("https://www.youtube.com/watch?v=xyz"))

    def test_extract_youtube_id(self) -> None:
        self.assertEqual(
            extract_youtube_id("https://www.youtube.com/watch?v=abc123"), "abc123"
        )
        self.assertEqual(extract_youtube_id("https://youtu.be/xyz987"), "xyz987")
        self.assertIsNone(extract_youtube_id("https://www.youtube.com/shorts/xyz"))


class PromptBuildTest(unittest.TestCase):
    def test_build_prompt_wraps_items(self) -> None:
        prompt = build_prompt(
            [
                {"title": "Artykul", "content": "Tresc A"},
                {"title": "Video", "content": "Tresc B"},
            ]
        )

        self.assertIn("<lista_artykułów_i_transkrypcji>", prompt)
        self.assertIn("</lista_artykułów_i_transkrypcji>", prompt)
        self.assertIn("Tytuł: Artykul", prompt)
        self.assertIn("Treść:\nTresc A", prompt)
        self.assertIn("Tytuł: Video", prompt)
        self.assertIn("Treść:\nTresc B", prompt)

if __name__ == "__main__":
    unittest.main()

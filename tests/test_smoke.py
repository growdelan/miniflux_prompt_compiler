import io
import re
import tempfile
import unittest
import urllib.error
import requests
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from miniflux_prompt_compiler.app import run
from miniflux_prompt_compiler.core.chunking import build_prompts_with_chunking
from miniflux_prompt_compiler.core.prompting import build_prompt
from miniflux_prompt_compiler.core.tokenization import count_tokens, label_for_tokens
from miniflux_prompt_compiler.core.url_classify import (
    extract_youtube_id,
    is_youtube_shorts,
    is_youtube_url,
)
from miniflux_prompt_compiler.types import ProcessedItem


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


class SmokeTest(unittest.TestCase):
    def test_run_reads_token_from_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text(
                "MINIFLUX_API_TOKEN=abc123\nMINIFLUX_BASE_URL=http://miniflux.local\n",
                encoding="utf-8",
            )

            captured_base_urls: list[str] = []

            def fake_fetcher(base_url: str, token: str) -> list[dict[str, object]]:
                captured_base_urls.append(base_url)
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

            def fake_input_reader() -> None:
                return None

            output = run(
                env_path=env_path,
                environ={},
                fetcher=fake_fetcher,
                article_fetcher=fake_article_fetcher,
                youtube_fetcher=fake_youtube_fetcher,
                marker=fake_marker,
                clipboard=fake_clipboard,
                input_reader=fake_input_reader,
            )

        self.assertIn(
            "Unread entries: 3; Success: 2; Failed: 0; Skipped: 1", output
        )
        self.assertRegex(output, r"Tokens: \d+")
        self.assertIn("Label: GPT-Instant", output)
        self.assertEqual(marked, [1, 2])
        self.assertEqual(len(clipboard_values), 1)
        self.assertIn("Tytuł: Artykul", clipboard_values[0])
        self.assertIn("Treść:\ncontent", clipboard_values[0])
        self.assertEqual(captured_base_urls, ["http://miniflux.local"])


class MarkReadFallbackTest(unittest.TestCase):
    def test_mark_entry_read_falls_back_on_400(self) -> None:
        from miniflux_prompt_compiler.adapters.miniflux_http import mark_entry_read

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
                ProcessedItem(title="Artykul", content="Tresc A"),
                ProcessedItem(title="Video", content="Tresc B"),
            ]
        )

        self.assertIn("<lista_artykułów_i_transkrypcji>", prompt)
        self.assertIn("</lista_artykułów_i_transkrypcji>", prompt)
        self.assertIn("Tytuł: Artykul", prompt)
        self.assertIn("Treść:\nTresc A", prompt)
        self.assertIn("Tytuł: Video", prompt)
        self.assertIn("Treść:\nTresc B", prompt)


class TokenLabelTest(unittest.TestCase):
    def test_label_for_tokens_thresholds(self) -> None:
        self.assertEqual(label_for_tokens(0), "GPT-Instant")
        self.assertEqual(label_for_tokens(31_999), "GPT-Instant")
        self.assertEqual(label_for_tokens(32_000), "GPT-Thinking")
        self.assertEqual(label_for_tokens(49_999), "GPT-Thinking")
        self.assertEqual(label_for_tokens(50_000), "CHUNKING")

    def test_count_tokens_approx(self) -> None:
        self.assertEqual(count_tokens("abcd", tokenizer="approx"), 1)
        self.assertEqual(count_tokens("abcdefgh", tokenizer="approx"), 2)
        with self.assertRaises(ValueError):
            count_tokens("test", tokenizer="unknown")


class PromptChunkingTest(unittest.TestCase):
    def test_build_prompts_with_chunking_splits_on_limit(self) -> None:
        from miniflux_prompt_compiler.core import chunking

        items = [
            ProcessedItem(title="A", content="X"),
            ProcessedItem(title="B", content="Y"),
            ProcessedItem(title="C", content="Z"),
        ]

        def fake_build_prompt(current):  # type: ignore[no-untyped-def]
            return "|".join(item.title for item in current)

        def fake_count_tokens(text: str, **kwargs) -> int:
            return len(text.split("|")) if text else 0

        with mock.patch.object(chunking, "build_prompt", side_effect=fake_build_prompt):
            with mock.patch.object(chunking, "count_tokens", side_effect=fake_count_tokens):
                prompts = build_prompts_with_chunking(items, max_tokens=2)

        self.assertEqual(prompts, ["A|B", "C"])

    def test_build_prompts_with_chunking_skips_oversize(self) -> None:
        from miniflux_prompt_compiler.core import chunking

        items = [
            ProcessedItem(title="A", content="X"),
            ProcessedItem(title="BIG", content="Y"),
            ProcessedItem(title="B", content="Z"),
        ]

        def fake_build_prompt(current):  # type: ignore[no-untyped-def]
            return "|".join(item.title for item in current)

        def fake_count_tokens(text: str, **kwargs) -> int:
            return 10 if "BIG" in text else len(text.split("|"))

        with mock.patch.object(chunking, "build_prompt", side_effect=fake_build_prompt):
            with mock.patch.object(chunking, "count_tokens", side_effect=fake_count_tokens):
                with self.assertLogs(level="INFO") as logs:
                    prompts = build_prompts_with_chunking(items, max_tokens=2)

        self.assertEqual(prompts, ["A", "B"])
        self.assertTrue(
            any(
                "Item exceeds max token limit and was skipped" in strip_ansi(message)
                for message in logs.output
            )
        )


class InteractiveModeTest(unittest.TestCase):
    def test_run_interactive_waits_for_enter_single_prompt(self) -> None:
        from miniflux_prompt_compiler import app as app_module

        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("MINIFLUX_API_TOKEN=abc123\n", encoding="utf-8")

            def fake_fetcher(base_url: str, token: str) -> list[dict[str, object]]:
                return [
                    {"id": 1, "title": "Artykul", "url": "https://example.com/a"},
                ]

            def fake_article_fetcher(url: str) -> str:
                return "content"

            def fake_marker(base_url: str, token: str, entry_id: int) -> None:
                return None

            events: list[str] = []

            def fake_input_reader() -> None:
                events.append("input")

            def fake_clipboard(text: str) -> None:
                events.append(f"clipboard:{text}")

            with mock.patch.object(
                app_module,
                "build_prompts_with_chunking",
                return_value=["PROMPT1"],
            ):
                with mock.patch.object(app_module, "count_tokens", return_value=10):
                    output = run(
                        env_path=env_path,
                        environ={},
                        fetcher=fake_fetcher,
                        article_fetcher=fake_article_fetcher,
                        marker=fake_marker,
                        clipboard=fake_clipboard,
                        input_reader=fake_input_reader,
                        interactive=True,
                    )

        self.assertEqual(events, ["input", "clipboard:PROMPT1"])
        self.assertIn("Tokens: 10", output)

    def test_run_no_interactive_outputs_prompts(self) -> None:
        from miniflux_prompt_compiler import app as app_module

        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("MINIFLUX_API_TOKEN=abc123\n", encoding="utf-8")

            def fake_fetcher(base_url: str, token: str) -> list[dict[str, object]]:
                return [
                    {"id": 1, "title": "Artykul", "url": "https://example.com/a"},
                    {"id": 2, "title": "Video", "url": "https://youtu.be/abc123"},
                ]

            def fake_article_fetcher(url: str) -> str:
                return "content"

            def fake_youtube_fetcher(video_id: str) -> str:
                return "transcript"

            def fake_marker(base_url: str, token: str, entry_id: int) -> None:
                return None

            clipboard_values: list[str] = []

            def fake_clipboard(text: str) -> None:
                clipboard_values.append(text)

            def fake_input_reader() -> None:
                return None

            with mock.patch.object(
                app_module,
                "build_prompts_with_chunking",
                return_value=["PROMPT1", "PROMPT2"],
            ):
                with mock.patch.object(
                    app_module, "count_tokens", side_effect=[70_000, 10, 20]
                ):
                    buffer = io.StringIO()
                    with self.assertLogs(level="INFO") as logs:
                        with redirect_stdout(buffer):
                            output = run(
                                env_path=env_path,
                                environ={},
                                fetcher=fake_fetcher,
                                article_fetcher=fake_article_fetcher,
                                youtube_fetcher=fake_youtube_fetcher,
                                marker=fake_marker,
                                clipboard=fake_clipboard,
                                interactive=False,
                            )

        stdout = strip_ansi(buffer.getvalue())
        self.assertEqual(clipboard_values, [])
        self.assertTrue(
            any("Total tokens: 70000 -> CHUNKING" in message for message in logs.output)
        )
        self.assertTrue(
            any("Generated prompts: 2" in message for message in logs.output)
        )
        self.assertIn("Prompt 1/2 (10 tokenow - GPT-Instant)", stdout)
        self.assertIn("PROMPT1", stdout)
        self.assertIn("Prompt 2/2 (20 tokenow - GPT-Instant)", stdout)
        self.assertIn("PROMPT2", stdout)
        self.assertIn("Prompts: 2", output)
        self.assertIn("Label: CHUNKING", output)


class PlaywrightFlagTest(unittest.TestCase):
    def test_main_passes_playwright_flag(self) -> None:
        from miniflux_prompt_compiler import cli

        captured: dict[str, object] = {}

        def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
            captured.update(kwargs)
            return "ok"

        with mock.patch.object(cli, "run", side_effect=fake_run):
            with mock.patch.object(cli.sys, "argv", ["cli.py", "--playwright"]):
                exit_code = cli.main()

        self.assertEqual(exit_code, 0)
        self.assertTrue(captured.get("use_playwright"))

    def test_main_passes_base_url(self) -> None:
        from miniflux_prompt_compiler import cli

        captured: dict[str, object] = {}

        def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
            captured.update(kwargs)
            return "ok"

        with mock.patch.object(cli, "run", side_effect=fake_run):
            with mock.patch.object(
                cli.sys, "argv", ["cli.py", "--base-url", "http://example.com"]
            ):
                exit_code = cli.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(captured.get("base_url"), "http://example.com")


class PlaywrightFallbackTest(unittest.TestCase):
    def test_fetch_article_with_fallback_uses_fallback(self) -> None:
        from miniflux_prompt_compiler.adapters import jina
        from miniflux_prompt_compiler.types import ContentFetchError

        def fake_fallback(url: str) -> str:
            return "fallback content"

        with mock.patch.object(
            jina, "fetch_article_markdown", side_effect=ContentFetchError("fail")
        ):
            content = jina.fetch_article_with_fallback(
                "https://example.com",
                use_playwright=True,
                fallback_fetcher=fake_fallback,
            )

        self.assertEqual(content, "fallback content")


class JinaTimeoutTest(unittest.TestCase):
    def test_fetch_article_markdown_timeout_is_wrapped(self) -> None:
        from miniflux_prompt_compiler.adapters import jina
        from miniflux_prompt_compiler.types import ContentFetchError

        with mock.patch.object(
            jina.requests, "get", side_effect=requests.Timeout("timeout")
        ):
            with self.assertRaises(ContentFetchError):
                jina.fetch_article_markdown("https://example.com", retries=1)

if __name__ == "__main__":
    unittest.main()

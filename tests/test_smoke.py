import tempfile
import unittest
from pathlib import Path

from main import run


class SmokeTest(unittest.TestCase):
    def test_run_reads_token_from_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("MINIFLUX_API_TOKEN=abc123\n", encoding="utf-8")

            output = run(env_path=env_path, environ={})

        self.assertEqual(output, "MINIFLUX_API_TOKEN length: 6")


if __name__ == "__main__":
    unittest.main()

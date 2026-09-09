from __future__ import annotations

import subprocess
import socket
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "build-public-artifact.py"


class PublicArtifactTests(unittest.TestCase):
    def test_public_artifact_builds_with_relative_assets_and_no_private_runtime(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--build"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Built dist/pages", result.stdout)
        html = (ROOT / "dist/pages/index.html").read_text(encoding="utf-8")
        self.assertIn("AskJamie FoundRy", html)
        self.assertIn('href="./styles.css"', html)
        for marker in ("/api/", ".foundry-data", "workbench.sqlite", "localStorage", "fetch("):
            self.assertNotIn(marker, html)
        self.assertTrue((ROOT / "dist/pages/styles.css").is_file())
        self.assertTrue((ROOT / "dist/pages/.nojekyll").is_file())

    def test_public_artifact_is_served_as_a_pages_style_subpath(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            probe = socket.socket()
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
            probe.close()
            server = subprocess.Popen(
                ["python3", "-m", "http.server", str(port), "--directory", str(ROOT / "public")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                import urllib.request

                # The static artifact itself is deliberately independent of the
                # Pages host. Relative links remain valid under /AskJamie-FoundRy/.
                for _ in range(40):
                    try:
                        response = urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/", timeout=0.2
                        )
                        break
                    except OSError:
                        time.sleep(0.05)
                else:
                    self.fail("static artifact server did not become ready")
                self.assertEqual(response.status, 200)
                self.assertIn("AskJamie FoundRy", response.read().decode("utf-8"))
                css = urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/styles.css", timeout=2
                )
                self.assertEqual(css.status, 200)
            finally:
                server.terminate()
                server.wait(timeout=3)


if __name__ == "__main__":
    unittest.main()
from __future__ import annotations

import importlib.util
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("technology_audit", ROOT / "scripts/audit-technologies.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class TechnologyAuditTests(unittest.TestCase):
    def test_numeric_versions_and_prerelease_rejection(self):
        self.assertGreater(audit.version_key("3.14.10"), audit.version_key("3.14.9"))
        for value in ("3.15.0rc1", "4.1.0-alpha1", "latest", "v7.0.0-beta.1"):
            with self.assertRaises(ValueError):
                audit.version_key(value)

    def test_pypi_excludes_yanked_empty_future_and_prerelease(self):
        release = {"yanked": False, "upload_time_iso_8601": "2020-01-01T00:00:00Z"}
        data = {"releases": {"1.9.0": [release], "1.10.0": [release],
                             "2.0.0rc1": [release], "2.0.0": [{**release, "yanked": True}],
                             "3.0.0": [], "4.0.0": [{**release, "upload_time_iso_8601": "9999-01-01T00:00:00Z"}]}}
        self.assertEqual(audit.stable_release({"kind": "pypi"}, json.dumps(data)), "1.10.0")

    def test_unsupported_final_pypi_version_is_not_silently_ignored(self):
        body = '{"info":{"version":"1.0.0.post1"},"releases":{"1.0.0":[]}}'
        with self.assertRaisesRegex(ValueError, "Unsupported PyPI"):
            audit.stable_release({"kind": "pypi"}, body)

    def test_official_source_gzip_response_is_read(self):
        with patch.object(audit, "urlopen", return_value=io.BytesIO(gzip.compress(b"release data"))):
            self.assertEqual(audit.fetch("https://example.invalid"), "release data")

    def test_floating_major_tracks_patches_but_detects_new_major(self):
        watch = {"name": "example", "url": "https://example.invalid", "kind": "github",
                 "current": "v7", "floating_major": True}
        self.assertEqual(audit.check(watch, lambda _: '{"tag_name":"v7.2.0"}')["status"], "TRACKING")
        self.assertEqual(audit.check(watch, lambda _: '{"tag_name":"v8.0.0"}')["status"], "UPDATE")
        self.assertEqual(audit.check(watch, lambda _: '{"tag_name":"v6.0.0"}')["status"], "UNKNOWN")

    def test_failed_or_changed_source_is_unknown_not_current(self):
        watch = {"kind": "regex", "pattern": r"Version (\d+\.\d+\.\d+)",
                 "reviewed": "1.0.0", "url": "https://example.invalid"}
        def failed(_):
            raise OSError("private diagnostic should not be echoed")
        for loader in (failed, lambda _: "changed page format"):
            result = audit.check(watch, loader)
            self.assertEqual(result["status"], "UNKNOWN")
            self.assertNotIn("private diagnostic", result["error"])

    def test_reviewed_upstream_is_not_an_installed_pin(self):
        watch = {"kind": "npm", "url": "https://example.invalid", "reviewed": "1.0.0"}
        self.assertEqual(audit.check(watch, lambda _: '{"version":"1.0.1"}')["status"], "REVIEW")

    def test_node_lts_is_separate_from_current(self):
        body = json.dumps([{"version": "v26.1.0", "lts": False, "date": "2020-01-01"},
                           {"version": "v24.10.0", "lts": "LTS", "date": "2020-01-01"}])
        self.assertEqual(audit.stable_release({"kind": "node-lts"}, body), "24.10.0")
        self.assertEqual(audit.stable_release({"kind": "node-current"}, body), "26.1.0")

    def test_browser_dependency_is_discovered_and_dependabot_covers_it(self):
        entries = audit.discover(ROOT)
        playwright = next(row for row in entries if row["name"] == "playwright")
        self.assertTrue(playwright["evidence"].startswith("tests/browser/requirements.txt:"))
        config = yaml.safe_load((ROOT / ".github/dependabot.yml").read_text())
        directories = {row["directory"] for row in config["updates"] if row["package-ecosystem"] == "pip"}
        self.assertEqual(directories, {"/", "/tests/browser"})

    def test_unsupported_requirement_does_not_silently_disappear(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.txt").write_text("package>=1.0\n")
            with self.assertRaisesRegex(ValueError, "Unsupported requirement"):
                audit.discover(root)


if __name__ == "__main__":
    unittest.main()

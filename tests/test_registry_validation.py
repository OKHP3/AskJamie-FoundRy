"""Regression coverage for schema enforcement and private registry controls."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("registry_check", ROOT / "scripts/check-registry.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RegistryValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = yaml.safe_load((ROOT / "registry/index.yaml").read_text())

    def check(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.yaml"
            path.write_text(yaml.safe_dump(data))
            return module.check_registry(path, ROOT / "schemas/registry.schema.yaml", False)[0]

    def test_current_registry_passes(self):
        self.assertEqual([], self.check(self.data))

    def test_malformed_shapes_fail_without_traceback(self):
        for value in [None, [], {"repositories": "wrong"}, {**self.data, "repositories": [None]}]:
            with self.subTest(value=value):
                self.assertTrue(self.check(value))

    def test_schema_rejects_string_boolean_and_invalid_code(self):
        for field, value in [("public_graduation_allowed", "false"), ("code", "aj123")]:
            data = copy.deepcopy(self.data)
            data["repositories"][0][field] = value
            self.assertTrue(self.check(data))

    def test_firewall_and_client_identity_require_locked_private_record(self):
        for field, value in [("bfs_firewall", True), ("client_org", "example")]:
            data = copy.deepcopy(self.data)
            data["repositories"][0][field] = value
            self.assertTrue(self.check(data))

    def test_locked_record_cannot_allow_graduation(self):
        data = copy.deepcopy(self.data)
        data["repositories"][4]["public_graduation_allowed"] = True
        self.assertTrue(self.check(data))

    def test_additional_manifest_families_are_registry_compatible(self):
        for family in ["conversation-design", "rag-experiment"]:
            data = copy.deepcopy(self.data)
            data["repositories"][0]["family"] = family
            self.assertEqual([], self.check(data))

if __name__ == "__main__":
    unittest.main()

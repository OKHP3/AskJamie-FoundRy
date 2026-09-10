from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from workbench.model import normalize_draft
from workbench.service import evaluate_project
from workbench.store import InvalidBackup, MissingProject, StaleRevision, Store


def draft(**changes):
    value = {
        "title": "Recovery Guide",
        "slug": "recovery-guide",
        "code": "aj05",
        "family": "core-capability",
        "kind": "assistant",
        "purpose": "Keep recovery steps explicit and testable.",
        "audience": "People restoring private workbench data.",
        "source_text": "Synthetic source text for recovery testing.",
        "source_reference": "synthetic-note-1",
        "instructions": "Preserve the project history and evaluation evidence.",
        "output_contract": "Return a verified recovery procedure.",
        "constraints": "Use synthetic data only.",
        "client_org": "",
        "parent_capability": "",
        "bfs_firewall": False,
        "visibility_lock": "",
        "skill_ids": [],
        "workflow_steps": [],
        "decision": {},
        "eval_cases": [
            {
                "name": "Keeps scope tight",
                "input": "Restore the project.",
                "response": "Keep the scope tight and preserve the evidence trail.",
                "required": ["scope", "evidence"],
                "forbidden": ["production"],
            }
        ],
    }
    value.update(changes)
    return value


def create_project(store: Store, **changes):
    normalized, _ = normalize_draft(draft(**changes))
    return store.create(normalized), normalized


class RecoveryAcceptanceTests(unittest.TestCase):
    def test_evaluation_for_unknown_revision_leaves_state_unchanged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir))
            project, _ = create_project(store)
            evaluate_project(project, store)
            backup = store.backup()
            backup["evaluations"][0]["revision"] = 2
            with self.assertRaisesRegex(InvalidBackup, "unknown history revision"):
                store.import_backup(backup)
            self.assertEqual(store.get(project["id"])["revision"], 1)
            self.assertEqual(store.evaluations(project["id"])[0]["revision"], 1)

    def test_maximum_length_duplicate_retains_suffix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir))
            project, _ = create_project(store, title="t" * 4000, slug="s" * 4000)
            duplicate = store.duplicate(project["id"])
            self.assertEqual(duplicate["slug"], "s" * 3995 + "-copy")
            self.assertEqual(duplicate["title"], "t" * 3995 + " copy")
            another = store.duplicate(duplicate["id"])
            self.assertNotEqual(another["slug"], duplicate["slug"])
            self.assertNotEqual(another["title"], duplicate["title"])
            self.assertLessEqual(len(another["slug"]), 4000)

    def test_incomplete_history_import_preserves_existing_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir))
            project, normalized = create_project(store)
            for revision in (1, 2):
                store.update(project["id"], revision, dict(normalized, title=f"Revision {revision + 1}"))
            backup = store.backup()
            backup["history"] = [item for item in backup["history"] if item["revision"] != 2]
            with self.assertRaisesRegex(InvalidBackup, "incomplete history"):
                store.import_backup(backup)
            self.assertEqual([item["revision"] for item in store.history(project["id"])], [3, 2, 1])
            self.assertEqual(store.get(project["id"])["title"], "Revision 3")

    def test_duplicate_starts_private_revision_one_without_evaluation_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir))
            project, normalized = create_project(store)
            evaluate_project(project, store)

            duplicate = store.duplicate(project["id"])

            self.assertNotEqual(duplicate["id"], project["id"])
            self.assertEqual(duplicate["revision"], 1)
            self.assertEqual(duplicate["title"], "Recovery Guide copy")
            self.assertEqual(duplicate["slug"], "recovery-guide-copy")
            self.assertEqual(store.evaluations(duplicate["id"]), [])
            self.assertEqual([item["revision"] for item in store.history(duplicate["id"])], [1])

    def test_delete_cascades_history_and_evaluations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir))
            project, normalized = create_project(store)
            updated = store.update(project["id"], 1, dict(normalized, title="Recovery Guide v2"))
            evaluate_project(updated, store)

            store.delete(project["id"])

            with self.assertRaises(MissingProject):
                store.get(project["id"])
            self.assertEqual(store.list(), [])

    def test_backup_restore_preserves_projects_revisions_and_evaluations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            backup_dir = Path(temp_dir) / "backup"
            store = Store(source_dir)
            project, normalized = create_project(store)
            updated = store.update(project["id"], 1, dict(normalized, title="Recovery Guide v2"))
            record = evaluate_project(updated, store)

            shutil.copytree(source_dir, backup_dir)
            restored = Store(backup_dir)

            self.assertEqual([item["revision"] for item in restored.history(project["id"])], [2, 1])
            restored_project = restored.get(project["id"])
            self.assertEqual(restored_project["title"], "Recovery Guide v2")
            self.assertEqual(restored_project["revision"], 2)
            self.assertEqual([item["revision"] for item in restored.evaluations(project["id"])], [record["revision"]])
            self.assertEqual(restored.evaluations(project["id"])[0]["passed"], 1)

    def test_independent_data_directories_do_not_share_projects_or_evaluations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first_dir = Path(temp_dir) / "first"
            second_dir = Path(temp_dir) / "second"
            first_store = Store(first_dir)
            second_store = Store(second_dir)

            first_project, _ = create_project(first_store, slug="first-recovery", source_reference="synthetic-note-1")
            second_project, _ = create_project(second_store, slug="second-recovery", source_reference="synthetic-note-2", title="Second Recovery Guide")

            first_record = evaluate_project(first_store.get(first_project["id"]), first_store)
            second_record = evaluate_project(second_store.get(second_project["id"]), second_store)

            self.assertEqual([item["id"] for item in first_store.list()], [first_project["id"]])
            self.assertEqual([item["id"] for item in second_store.list()], [second_project["id"]])
            self.assertEqual([item["revision"] for item in first_store.history(first_project["id"])], [1])
            self.assertEqual([item["revision"] for item in second_store.history(second_project["id"])], [1])
            self.assertEqual([item["revision"] for item in first_store.evaluations(first_project["id"])], [first_record["revision"]])
            self.assertEqual([item["revision"] for item in second_store.evaluations(second_project["id"])], [second_record["revision"]])
            with self.assertRaises(MissingProject):
                first_store.get(second_project["id"])
            with self.assertRaises(MissingProject):
                second_store.get(first_project["id"])
            self.assertNotEqual(first_store.data_dir, second_store.data_dir)

    def test_restart_keeps_stale_revision_rejection_intact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "recovery"
            store = Store(data_dir)
            project, normalized = create_project(store)
            store.update(project["id"], 1, dict(normalized, title="Recovery Guide v2"))

            restarted = Store(data_dir)
            with self.assertRaises(StaleRevision):
                restarted.update(project["id"], 1, dict(normalized, title="Stale recovery edit"))
            self.assertEqual(restarted.get(project["id"])["revision"], 2)

    def test_versioned_import_replaces_state_and_malformed_import_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Store(Path(temp_dir) / "source")
            project, normalized = create_project(source)
            updated = source.update(project["id"], 1, dict(normalized, title="Imported revision"))
            evaluate_project(updated, source)
            backup = source.backup()

            target = Store(Path(temp_dir) / "target")
            local, _ = create_project(target, title="Keep this project", slug="keep-this-project")
            with self.assertRaisesRegex(InvalidBackup, "schema_version"):
                target.import_backup({**backup, "schema_version": "999"})
            self.assertEqual(target.get(local["id"])["title"], "Keep this project")

            self.assertEqual(target.import_backup(backup), 1)
            restored = target.get(project["id"])
            self.assertEqual(restored["title"], "Imported revision")
            self.assertEqual(restored["revision"], 2)
            self.assertEqual([item["revision"] for item in target.history(project["id"])], [2, 1])
            self.assertEqual(target.evaluations(project["id"])[0]["revision"], 2)


if __name__ == "__main__":
    unittest.main()

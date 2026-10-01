from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_release.py"
SPEC = importlib.util.spec_from_file_location("validate_release", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidateReleaseTests(unittest.TestCase):
    def make_release(self, root: Path) -> None:
        archive = root / "artifacts" / "relai-openai-v1.2.3.zip"
        archive.parent.mkdir(parents=True)
        archive.write_bytes(b"archive")
        skill = root / "copilot" / "skills" / "relai" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: relai\ndescription: Test\n---\n")
        inventory = []
        for path in (archive, skill):
            data = path.read_bytes()
            inventory.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "byte_size": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )
        inventory.sort(key=lambda entry: entry["path"])
        receipt = {
            "format": validator.FORMAT,
            "release_version": "1.2.3",
            "source_revision": "a" * 40,
            "export_format_version": 1,
            "package_digest": validator.package_digest(inventory),
            "inventory": inventory,
        }
        (root / "provenance.json").write_text(json.dumps(receipt) + "\n")

    def test_accepts_matching_release_and_ignores_owned_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_release(root)
            (root / "README.md").write_text("owned\n")
            self.assertEqual(validator.validate(root)["release_version"], "1.2.3")

    def test_rejects_untracked_generated_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_release(root)
            (root / "copilot" / "unexpected.txt").write_text("unexpected\n")
            with self.assertRaisesRegex(validator.ValidationError, "inventory mismatch"):
                validator.validate(root)

    def test_rejects_changed_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_release(root)
            (root / "artifacts" / "relai-openai-v1.2.3.zip").write_bytes(b"changed")
            with self.assertRaisesRegex(validator.ValidationError, "does not match provenance"):
                validator.validate(root)

    def test_rejects_release_without_versioned_openai_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_release(root)
            receipt = json.loads((root / "provenance.json").read_text())
            archive = root / "artifacts" / "relai-openai-v1.2.3.zip"
            archive.unlink()
            receipt["inventory"] = [
                entry
                for entry in receipt["inventory"]
                if entry["path"] != "artifacts/relai-openai-v1.2.3.zip"
            ]
            receipt["package_digest"] = validator.package_digest(receipt["inventory"])
            (root / "provenance.json").write_text(json.dumps(receipt) + "\n")
            with self.assertRaisesRegex(validator.ValidationError, "inventory is missing"):
                validator.validate(root)


if __name__ == "__main__":
    unittest.main()

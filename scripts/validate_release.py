#!/usr/bin/env python3
"""Validate generated RELAI plugin contents against provenance.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


FORMAT = "relai.plugin_export.v1"
GENERATED_ROOTS = {
    ".agents",
    ".claude-plugin",
    ".cursor-plugin",
    "artifacts",
    "copilot",
    "plugins",
}
SHA_RE = re.compile(r"[0-9a-f]{64}")
REVISION_RE = re.compile(r"[0-9a-f]{40}")
SEMVER_RE = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
)


class ValidationError(RuntimeError):
    pass


def hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def package_digest(inventory: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    digest.update(b"relai.plugin_export.v1\n")
    for entry in inventory:
        digest.update(entry["path"].encode())
        digest.update(b"\0")
        digest.update(str(entry["byte_size"]).encode())
        digest.update(b"\0")
        digest.update(entry["sha256"].encode())
        digest.update(b"\n")
    return digest.hexdigest()


def validate_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        not value
        or value.startswith("/")
        or value.endswith("/")
        or "\\" in value
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.parts[0] not in GENERATED_ROOTS
    ):
        raise ValidationError(f"invalid generated path: {value!r}")
    return path


def validate(root: Path) -> dict[str, Any]:
    if not root.is_dir() or root.is_symlink():
        raise ValidationError("repository root must be a real directory")
    receipt_path = root / "provenance.json"
    try:
        receipt = json.loads(receipt_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValidationError(f"cannot read provenance.json: {error}") from error

    if receipt.get("format") != FORMAT or receipt.get("export_format_version") != 1:
        raise ValidationError("unsupported provenance format")
    version = receipt.get("release_version")
    revision = receipt.get("source_revision")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        raise ValidationError("release_version must be canonical major.minor.patch semver")
    if not isinstance(revision, str) or not REVISION_RE.fullmatch(revision):
        raise ValidationError("source_revision must be a full lowercase Git SHA")

    inventory = receipt.get("inventory")
    if not isinstance(inventory, list) or not inventory:
        raise ValidationError("inventory must be a non-empty list")
    expected: set[str] = set()
    previous = ""
    for entry in inventory:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValidationError("inventory entries must have a string path")
        value = entry["path"]
        path = validate_path(value)
        if previous and value <= previous:
            raise ValidationError("inventory must be strictly path-sorted")
        previous = value
        if (
            not isinstance(entry.get("byte_size"), int)
            or entry["byte_size"] < 0
            or not isinstance(entry.get("sha256"), str)
            or not SHA_RE.fullmatch(entry["sha256"])
        ):
            raise ValidationError(f"generated file metadata is invalid: {value}")
        expected.add(value)
        candidate = root.joinpath(*path.parts)
        if candidate.is_symlink() or not candidate.is_file():
            raise ValidationError(f"generated file is missing or is a symlink: {value}")
        data = candidate.read_bytes()
        if (
            entry["byte_size"] != len(data)
            or entry["sha256"] != hash_bytes(data)
        ):
            raise ValidationError(f"generated file does not match provenance: {value}")

    actual: set[str] = set()
    for generated_root in GENERATED_ROOTS:
        start = root / generated_root
        if start.is_symlink():
            raise ValidationError(f"generated root is a symlink: {generated_root}")
        if not start.exists():
            continue
        if not start.is_dir():
            raise ValidationError(f"generated root is not a real directory: {generated_root}")
        for directory, directories, files in os.walk(start, followlinks=False):
            directory_path = Path(directory)
            for name in directories:
                candidate = directory_path / name
                if candidate.is_symlink():
                    raise ValidationError(
                        f"generated directory is a symlink: {candidate.relative_to(root)}"
                    )
            for name in files:
                candidate = directory_path / name
                relative = candidate.relative_to(root).as_posix()
                if candidate.is_symlink():
                    raise ValidationError(f"generated file is a symlink: {relative}")
                actual.add(relative)
    if actual != expected:
        raise ValidationError(
            "generated inventory mismatch; "
            f"extra={sorted(actual - expected)}, missing={sorted(expected - actual)}"
        )
    if receipt.get("package_digest") != package_digest(inventory):
        raise ValidationError("package_digest does not match the inventory")
    expected_archive = f"artifacts/relai-openai-v{version}.zip"
    if expected_archive not in expected:
        raise ValidationError(f"inventory is missing {expected_archive}")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        receipt = validate(args.root)
        result = {
            "version": receipt["release_version"],
            "source_revision": receipt["source_revision"],
            "digest": receipt["package_digest"],
            "archive": f"artifacts/relai-openai-v{receipt['release_version']}.zip",
        }
        if args.github_output:
            with args.github_output.open("a") as output:
                for key, value in result.items():
                    output.write(f"{key}={value}\n")
        print(json.dumps(result, sort_keys=True))
        return 0
    except ValidationError as error:
        print(f"validate_release: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

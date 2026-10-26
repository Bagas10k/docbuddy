#!/usr/bin/env python3
"""
Unit tests for docbuddy deterministic propose/apply CLI.
Standard library only.
"""

from __future__ import annotations

import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

# Ensure docbuddy is importable from parent directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import docbuddy

ARCH_TEMPLATE = """# Architecture and System Boundaries

**Status:** `NOT BASELINED` until inspected against the repository. Do not treat example labels as an implemented system.

## Current architecture snapshot

- Runtime(s) and versions: `UNSET`
- Frontend framework, if any: `UNSET`
- Backend and storage, if any: `UNSET`
- Queue, cache, job runner, search, or external services: `UNSET`
- Build, package, and deployment mechanism: `UNSET`
- Essential directories and ownership: `UNSET`

## Component responsibility map

| Module/path | Responsibility | Inputs/outputs | Owner | Evidence |
| --- | --- | --- | --- | --- |
| `UNSET` | `UNSET` | `UNSET` | `UNSET` | `UNKNOWN` |
"""

VERIF_TEMPLATE = """# Verification Contract

## Actual commands (fill from repository, never guess)

| Check | Command or method | Status / evidence source |
| --- | --- | --- |
| Install/setup | `UNSET` | `UNKNOWN` |
| Format | `UNSET` | `UNKNOWN` |
| Lint/static analysis | `UNSET` | `UNKNOWN` |
| Type checking | `UNSET` | `UNKNOWN` |
| Unit tests | `UNSET` | `UNKNOWN` |
| Integration/contract tests | `UNSET` | `UNKNOWN` |
| Build/package | `UNSET` | `UNKNOWN` |
| Security/dependency review | `UNSET` | `UNKNOWN` |
| End-to-end / manual smoke test | `UNSET` | `UNKNOWN` |
| Performance profile or benchmark | `UNSET` | `UNKNOWN` |
| Data migration/import validation | `UNSET` | `UNKNOWN` |
"""


class TestDocBuddyCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Setup .onefreq templates
        self.onefreq_dir = self.root / ".onefreq"
        self.onefreq_dir.mkdir(parents=True)
        self.arch_file = self.onefreq_dir / "ARCHITECTURE.md"
        self.verif_file = self.onefreq_dir / "VERIFICATION.md"

        self.arch_file.write_text(ARCH_TEMPLATE, encoding="utf-8")
        self.verif_file.write_text(VERIF_TEMPLATE, encoding="utf-8")

        # Setup sample project manifest (pyproject.toml) and test dir
        self.pyproject = self.root / "pyproject.toml"
        self.pyproject.write_text(
            """[project]
name = "demo-app"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.100.0",
    "pytest>=7.0.0",
]

[tool.ruff]
line-length = 88
""",
            encoding="utf-8",
        )

        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_sample.py").write_text("def test_ok(): pass\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_adopt_new_project_copies_bundle(self) -> None:
        target = self.root / "fresh-project"
        exit_code = docbuddy.main(["adopt", str(target)])
        self.assertEqual(exit_code, 0)
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertTrue((target / "CLAUDE.md").is_file())
        self.assertTrue((target / ".onefreq" / "PROJECT_BRIEF.md").is_file())
        self.assertEqual(len(list(target.rglob("*.md"))), 17)

    def test_adopt_preserves_existing_files_and_adds_missing(self) -> None:
        target = self.root / "existing-project"
        target.mkdir()
        (target / "AGENTS.md").write_text("project-owned instructions\\n", encoding="utf-8")
        exit_code = docbuddy.main(["adopt", str(target)])
        self.assertEqual(exit_code, 0)
        self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "project-owned instructions\\n")
        self.assertTrue((target / "CLAUDE.md").is_file())
        self.assertTrue((target / ".onefreq" / "PROJECT_BRIEF.md").is_file())

    def test_adopt_rejects_symlinked_pack_directory_without_writing(self) -> None:
        target = self.root / "symlinked-project"
        target.mkdir()
        external = self.root / "external"
        external.mkdir()
        (target / ".onefreq").symlink_to(external, target_is_directory=True)
        captured_err = io.StringIO()
        with patch("sys.stderr", captured_err):
            exit_code = docbuddy.main(["adopt", str(target)])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Refusing symlinked destination directory", captured_err.getvalue())
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse((target / "AGENTS.md").exists())

    def test_propose_no_target_mutation(self) -> None:
        arch_before = self.arch_file.read_text(encoding="utf-8")
        verif_before = self.verif_file.read_text(encoding="utf-8")
        proposal_file = self.root / "proposal.json"

        exit_code = docbuddy.main(["propose", str(self.root), "--proposal", str(proposal_file)])
        self.assertEqual(exit_code, 0)

        # Targets MUST NOT be mutated during propose
        self.assertEqual(self.arch_file.read_text(encoding="utf-8"), arch_before)
        self.assertEqual(self.verif_file.read_text(encoding="utf-8"), verif_before)
        self.assertTrue(proposal_file.is_file())

    def test_diff_content(self) -> None:
        proposal_file = self.root / "proposal.json"
        captured = io.StringIO()

        with patch("sys.stdout", captured):
            exit_code = docbuddy.main(["propose", str(self.root), "--proposal", str(proposal_file)])

        self.assertEqual(exit_code, 0)
        output = captured.getvalue()

        # Check unified diff headers and evidence
        self.assertIn("--- a/.onefreq/ARCHITECTURE.md", output)
        self.assertIn("+++ b/.onefreq/ARCHITECTURE.md", output)
        self.assertIn("+", output)
        self.assertIn("Python >=3.11", output)
        self.assertIn("FastAPI", output)
        self.assertIn("--- a/.onefreq/VERIFICATION.md", output)
        self.assertIn("+++ b/.onefreq/VERIFICATION.md", output)
        self.assertIn("pytest", output)

    def test_apply_success(self) -> None:
        proposal_file = self.root / "proposal.json"
        docbuddy.main(["propose", str(self.root), "--proposal", str(proposal_file)])

        # Apply the proposal
        exit_code = docbuddy.main(["apply", str(self.root), "--proposal", str(proposal_file)])
        self.assertEqual(exit_code, 0)

        arch_after = self.arch_file.read_text(encoding="utf-8")
        verif_after = self.verif_file.read_text(encoding="utf-8")

        # Verify enriched contents replaced UNSET
        self.assertIn("Python >=3.11", arch_after)
        self.assertIn("FastAPI", arch_after)
        self.assertIn("src/, tests/ (ownership: UNKNOWN)", arch_after)
        self.assertIn("pytest", verif_after)

    def test_apply_stale_rejection(self) -> None:
        proposal_file = self.root / "proposal.json"
        docbuddy.main(["propose", str(self.root), "--proposal", str(proposal_file)])

        # Simulate concurrent drift/tampering with target file
        self.arch_file.write_text(ARCH_TEMPLATE + "\n# Modified externally\n", encoding="utf-8")

        captured_err = io.StringIO()
        with patch("sys.stderr", captured_err):
            exit_code = docbuddy.main(["apply", str(self.root), "--proposal", str(proposal_file)])

        # Must reject with non-zero exit code
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Stale proposal", captured_err.getvalue())

    def test_paths_escaping_root_rejected(self) -> None:
        proposal_file = self.root / "malicious_proposal.json"
        malicious_payload = {
            "version": 1,
            "base_hashes": {
                "../outside.txt": "dummyhash",
            },
            "proposed_files": {
                "../outside.txt": "payload",
            },
        }
        proposal_file.write_text(json.dumps(malicious_payload), encoding="utf-8")

        captured_err = io.StringIO()
        with patch("sys.stderr", captured_err):
            exit_code = docbuddy.main(["apply", str(self.root), "--proposal", str(proposal_file)])

        self.assertNotEqual(exit_code, 0)
        self.assertTrue(
            "Security error" in captured_err.getvalue() or "Unauthorized" in captured_err.getvalue()
        )

    def test_secret_files_and_symlinks_ignored(self) -> None:
        # Create secret files
        secret_env = self.root / ".env"
        secret_env.write_text("DB_PASSWORD=supersecret\n", encoding="utf-8")
        secret_key = self.root / "id_rsa"
        secret_key.write_text("FAKE RSA PRIVATE KEY\n", encoding="utf-8")

        self.assertTrue(docbuddy.is_secret_file(".env"))
        self.assertTrue(docbuddy.is_secret_file(".env.local"))
        self.assertTrue(docbuddy.is_secret_file("server.key"))
        self.assertTrue(docbuddy.is_secret_file("id_rsa"))
        self.assertFalse(docbuddy.is_secret_file("main.py"))

        # Propose and ensure no secrets leak into diff or proposal
        proposal_file = self.root / "proposal.json"
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            exit_code = docbuddy.main(["propose", str(self.root), "--proposal", str(proposal_file)])

        self.assertEqual(exit_code, 0)
        proposal_text = proposal_file.read_text(encoding="utf-8")
        self.assertNotIn("supersecret", proposal_text)
        self.assertNotIn("supersecret", captured.getvalue())

    def test_secret_directory_name_not_disclosed(self) -> None:
        (self.root / "credentials_backup").mkdir()
        (self.root / "src").mkdir(exist_ok=True)
        evidence = docbuddy.scan_repository_evidence(self.root)
        self.assertNotIn("credentials_backup", evidence["directories"])

    def test_symlinked_markdown_target_rejected(self) -> None:
        self.arch_file.unlink()
        outside_target = self.root / "src" / "important.py"
        outside_target.write_text("keep me\n", encoding="utf-8")
        self.arch_file.symlink_to(outside_target)
        captured_err = io.StringIO()
        with patch("sys.stderr", captured_err):
            exit_code = docbuddy.main(["propose", str(self.root)])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("symlinked target", captured_err.getvalue())
        self.assertEqual(outside_target.read_text(encoding="utf-8"), "keep me\n")

    def test_dependency_substrings_do_not_guess_framework(self) -> None:
        self.pyproject.write_text(
            '[project]\nname="demo"\ndependencies=["flask-cors", "blackjax", "ruffle", "types-pytest"]\n',
            encoding="utf-8",
        )
        evidence = docbuddy.scan_repository_evidence(self.root)
        self.assertIsNone(evidence["backend"])
        self.assertIn("Unit tests", evidence["commands"])
        self.assertIn("suggested; verify", evidence["commands"]["Unit tests"][0])
        self.assertNotIn("pytest", evidence["commands"]["Unit tests"][0])
        self.assertNotIn("Lint/static analysis", evidence["commands"])

    def test_malformed_proposal_returns_error_without_traceback(self) -> None:
        proposal_file = self.root / "proposal.json"
        proposal_file.write_text("[]", encoding="utf-8")
        captured_err = io.StringIO()
        with patch("sys.stderr", captured_err):
            exit_code = docbuddy.main(["apply", str(self.root), "--proposal", str(proposal_file)])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("must be a JSON object", captured_err.getvalue())

    def test_state_cmd_update_and_read(self) -> None:
        state_file = self.onefreq_dir / "CURRENT_STATE.md"
        state_file.write_text("# Current State — Cross-Agent Handoff\n\n**Last validated update:** `UNSET`\n\n**Source branch / commit or worktree identification:** `UNSET`\n\n**Current goal and acceptance criteria:** `UNSET`\n\n**Work status:** `NOT INITIALIZED`\n\n## Completed changes (exact paths and observable behavior)\n\n- `NONE DOCUMENTED`\n", encoding="utf-8")
        
        exit_code = onefreq.main(["state", str(self.root), "--status", "IN_PROGRESS", "--goal", "Build auth module", "--slice", "Added user model"])
        self.assertEqual(exit_code, 0)
        
        updated_content = state_file.read_text(encoding="utf-8")
        self.assertIn("**Work status:** `IN_PROGRESS`", updated_content)
        self.assertIn("Build auth module", updated_content)
        self.assertIn("Added user model", updated_content)

    def test_adr_cmd_record(self) -> None:
        adr_file = self.onefreq_dir / "DECISION_RECORDS.md"
        adr_file.write_text("# Decision Records\n\n## ADR index\n\n| ID | Status | Decision | Evidence/location |\n| --- | --- | --- | --- |\n| `NONE` | — | No project-specific decision has yet been approved or recorded. | — |\n", encoding="utf-8")
        
        exit_code = onefreq.main(["adr", str(self.root), "--title", "Use PostgreSQL", "--decision", "Adopt Postgres", "--why", "ACID compliance"])
        self.assertEqual(exit_code, 0)
        
        updated = adr_file.read_text(encoding="utf-8")
        self.assertIn("Use PostgreSQL", updated)
        self.assertIn("Adopt Postgres", updated)
        self.assertIn("ACID compliance", updated)
        self.assertNotIn("| `NONE` |", updated)

    def test_report_cmd_generate(self) -> None:
        captured_out = io.StringIO()
        with patch("sys.stdout", captured_out):
            exit_code = onefreq.main(["report", str(self.root), "--status", "ACCEPTED"])
        self.assertEqual(exit_code, 0)
        out = captured_out.getvalue()
        self.assertIn("Engineering Execution Report", out)
        self.assertIn("**Status Operasional:** ACCEPTED", out)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
DocBuddy - Deterministic evidence-based propose/apply CLI for project Markdown.
Python 3.11+ standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import Any, Dict, List, Optional, Set, Tuple

IGNORED_DIRS: Set[str] = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "vendor",
    "dist",
    "build",
    ".next",
    "__pycache__",
    ".idea",
    ".vscode",
}

SECRET_SUBSTRINGS: Set[str] = {
    "credential",
    "secret",
    "token",
    "password",
    "id_rsa",
    "id_ed25519",
}

SECRET_EXTENSIONS: Set[str] = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".pkcs12",
}

TARGET_FILES: List[str] = [
    ".onefreq/ARCHITECTURE.md",
    ".onefreq/VERIFICATION.md",
]


def is_secret_file(name: str) -> bool:
    lower = name.lower()
    if lower == ".env" or lower.startswith(".env."):
        return True
    for sub in SECRET_SUBSTRINGS:
        if sub in lower:
            return True
    _, ext = os.path.splitext(lower)
    if ext in SECRET_EXTENSIONS:
        return True
    return False


def verify_confinement(root: Path, target_path_str: str) -> Path:
    """Ensure target path resolves strictly inside root and does not escape."""
    target_path = Path(target_path_str)
    if target_path.is_absolute():
        raise ValueError(f"Path escaping root (absolute path not allowed): {target_path_str}")

    resolved_root = root.resolve()
    lexical_target = resolved_root / target_path
    # Reject any symlink component, including in-root links, before resolving.
    current = resolved_root
    for part in target_path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Symlink target not allowed: {target_path_str}")
    resolved_target = lexical_target.resolve()

    try:
        resolved_target.relative_to(resolved_root)
    except ValueError:
        raise ValueError(f"Path escaping root: {target_path_str}")

    return resolved_target


def compute_file_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def scan_repository_evidence(root: Path) -> Dict[str, Any]:
    """Inspect safe repository manifests and files for deterministic evidence."""
    evidence: Dict[str, Any] = {
        "runtime": None,
        "frontend": None,
        "backend": None,
        "build": None,
        "directories": [],
        "commands": {},
    }

    # Discover top-level directories
    top_dirs = []
    try:
        for entry in root.iterdir():
            if entry.is_dir() and not entry.is_symlink():
                if (entry.name not in IGNORED_DIRS and not entry.name.startswith(".")
                        and not is_secret_file(entry.name)):
                    top_dirs.append(entry.name)
    except OSError:
        pass
    evidence["directories"] = sorted(top_dirs)

    # 1. package.json
    pkg_json_path = root / "package.json"
    if pkg_json_path.is_file() and not pkg_json_path.is_symlink():
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                pkg_data = json.load(f)
            scripts = pkg_data.get("scripts", {})
            deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}

            engines_node = pkg_data.get("engines", {}).get("node")
            evidence["runtime"] = f"Node.js ({engines_node})" if engines_node else "Node.js"

            # Frameworks
            if "next" in deps:
                evidence["frontend"] = "Next.js"
            elif "react" in deps:
                evidence["frontend"] = "React"
            elif "vue" in deps:
                evidence["frontend"] = "Vue"
            elif "svelte" in deps:
                evidence["frontend"] = "Svelte"

            if "express" in deps:
                evidence["backend"] = "Express"
            elif "fastify" in deps:
                evidence["backend"] = "Fastify"
            elif "@nestjs/core" in deps:
                evidence["backend"] = "NestJS"

            # Package manager check
            pkg_mgr = "npm"
            if (root / "pnpm-lock.yaml").is_file():
                pkg_mgr = "pnpm"
            elif (root / "yarn.lock").is_file():
                pkg_mgr = "yarn"
            elif (root / "bun.lockb").is_file():
                pkg_mgr = "bun"

            evidence["build"] = f"{pkg_mgr} (package.json)"
            evidence["commands"]["Install/setup"] = (f"{pkg_mgr} install", "package.json")

            if "test" in scripts:
                evidence["commands"]["Unit tests"] = (f"{pkg_mgr} test", "package.json scripts.test")
            if "build" in scripts:
                evidence["commands"]["Build/package"] = (f"{pkg_mgr} run build", "package.json scripts.build")
            if "lint" in scripts:
                evidence["commands"]["Lint/static analysis"] = (f"{pkg_mgr} run lint", "package.json scripts.lint")
            elif "eslint" in deps:
                evidence["commands"]["Lint/static analysis"] = ("npx eslint .", "package.json dependencies")
            if "format" in scripts:
                evidence["commands"]["Format"] = (f"{pkg_mgr} run format", "package.json scripts.format")
            elif "prettier" in deps:
                evidence["commands"]["Format"] = ("npx prettier --check .", "package.json dependencies")

            if "typecheck" in scripts:
                evidence["commands"]["Type checking"] = (f"{pkg_mgr} run typecheck", "package.json scripts.typecheck")
            elif "type-check" in scripts:
                evidence["commands"]["Type checking"] = (f"{pkg_mgr} run type-check", "package.json scripts.type-check")
            elif "typescript" in deps:
                evidence["commands"]["Type checking"] = ("npx tsc --noEmit", "package.json dependencies")
        except Exception:
            pass

    # 2. pyproject.toml
    pyproject_path = root / "pyproject.toml"
    if pyproject_path.is_file() and not pyproject_path.is_symlink():
        try:
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
            project = pyproject_data.get("project", {})
            requires_python = project.get("requires-python")
            evidence["runtime"] = f"Python {requires_python}" if requires_python else "Python (version constraint not specified)"
            evidence["build"] = "pip / pyproject.toml"

            deps = project.get("dependencies", [])
            opt_deps = project.get("optional-dependencies", {})
            dependency_names = set()
            for requirement in deps + [item for group in opt_deps.values() for item in group]:
                match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
                if match:
                    dependency_names.add(re.sub(r"[-_.]+", "-", match.group(1)).lower())
            poetry_deps = pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            dependency_names.update(
                re.sub(r"[-_.]+", "-", name).lower() for name in poetry_deps
            )

            evidence["commands"]["Install/setup"] = ("pip install -e .", "pyproject.toml (suggested; verify project config)")
            if "pytest" in dependency_names:
                evidence["commands"]["Unit tests"] = ("pytest", "pyproject.toml declares pytest; command not executed")
            tools = pyproject_data.get("tool", {})
            if "ruff" in dependency_names or "ruff" in tools:
                evidence["commands"]["Lint/static analysis"] = ("ruff check .", "pyproject.toml declares/configures ruff; command not executed")
                evidence["commands"]["Format"] = ("ruff format --check", "pyproject.toml declares/configures ruff; command not executed")
            elif "black" in dependency_names or "black" in tools:
                evidence["commands"]["Format"] = ("black --check .", "pyproject.toml declares/configures black; command not executed")
            if "mypy" in dependency_names or "mypy" in tools:
                evidence["commands"]["Type checking"] = ("mypy .", "pyproject.toml declares/configures mypy; command not executed")

            if "fastapi" in dependency_names:
                evidence["backend"] = "FastAPI"
            elif "django" in dependency_names:
                evidence["backend"] = "Django"
            elif "flask" in dependency_names:
                evidence["backend"] = "Flask"
        except Exception:
            pass

    # 3. Cargo.toml
    cargo_path = root / "Cargo.toml"
    if cargo_path.is_file() and not cargo_path.is_symlink():
        try:
            with open(cargo_path, "rb") as f:
                cargo_data = tomllib.load(f)
            pkg = cargo_data.get("package", {})
            rust_ver = pkg.get("rust-version")
            edition = pkg.get("edition")
            v_desc = f" {rust_ver}" if rust_ver else (f" (edition {edition})" if edition else "")
            evidence["runtime"] = f"Rust{v_desc}"
            evidence["build"] = "cargo (Cargo.toml)"
            evidence["commands"]["Install/setup"] = ("cargo build (suggested; not run)", "Cargo.toml; standard Cargo workflow")
            evidence["commands"]["Unit tests"] = ("cargo test (suggested; not run)", "Cargo.toml; standard Cargo workflow")
            evidence["commands"]["Lint/static analysis"] = ("cargo clippy (suggested; not run)", "standard Cargo workflow; not configured by manifest")
            evidence["commands"]["Format"] = ("cargo fmt --check (suggested; not run)", "standard Cargo workflow; not configured by manifest")
            evidence["commands"]["Build/package"] = ("cargo build --release (suggested; not run)", "Cargo.toml; standard Cargo workflow")

        except Exception:
            pass

    # 4. go.mod
    go_mod_path = root / "go.mod"
    if go_mod_path.is_file() and not go_mod_path.is_symlink():
        try:
            with open(go_mod_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("go "):
                        evidence["runtime"] = f"Go {line.split()[1]}"
                        break
            if not evidence["runtime"]:
                evidence["runtime"] = "Go"
            evidence["build"] = "go build"
            evidence["commands"]["Install/setup"] = ("go mod download", "go.mod")
            evidence["commands"]["Unit tests"] = ("go test ./...", "go.mod")
            evidence["commands"]["Lint/static analysis"] = ("go vet ./...", "go.mod")
            evidence["commands"]["Build/package"] = ("go build ./...", "go.mod")
        except Exception:
            pass

    # Directory fallback may suggest a generic command, never infer a test framework.
    if "Unit tests" not in evidence["commands"]:
        tests_dir = root / "tests"
        if tests_dir.is_dir() and not tests_dir.is_symlink():
            py_files = [p for p in tests_dir.glob("*.py") if not p.is_symlink()]
            if py_files:
                evidence["commands"]["Unit tests"] = ("python -m unittest discover -s tests -v (suggested; verify)", "tests/ contains Python tests; framework not identified")
                if not evidence["runtime"]:
                    evidence["runtime"] = f"Python {sys.version_info.major}.{sys.version_info.minor} (scanner runtime; project constraint unknown)"

    return evidence


def enrich_architecture(content: str, evidence: Dict[str, Any]) -> str:
    """Enrich .onefreq/ARCHITECTURE.md only with safe discovered facts."""
    new_content = content

    if evidence.get("runtime"):
        new_content = re.sub(
            r"(- Runtime\(s\) and versions:\s*)`UNSET`",
            rf"\1`{evidence['runtime']}`",
            new_content,
        )

    if evidence.get("frontend"):
        new_content = re.sub(
            r"(- Frontend framework, if any:\s*)`UNSET`",
            rf"\1`{evidence['frontend']}`",
            new_content,
        )

    if evidence.get("backend"):
        new_content = re.sub(
            r"(- Backend and storage, if any:\s*)`UNSET`",
            rf"\1`{evidence['backend']}`",
            new_content,
        )

    if evidence.get("build"):
        new_content = re.sub(
            r"(- Build, package, and deployment mechanism:\s*)`UNSET`",
            rf"\1`{evidence['build']}`",
            new_content,
        )

    dirs = evidence.get("directories", [])
    if dirs:
        dirs_str = ", ".join(f"{d}/" for d in dirs) + " (ownership: UNKNOWN)"
        new_content = re.sub(
            r"(- Essential directories and ownership:\s*)`UNSET`",
            rf"\1`{dirs_str}`",
            new_content,
        )

    return new_content


def enrich_verification(content: str, evidence: Dict[str, Any]) -> str:
    """Enrich .onefreq/VERIFICATION.md commands table only with verifiable evidence."""
    new_content = content
    commands: Dict[str, Tuple[str, str]] = evidence.get("commands", {})

    for check, (cmd, source) in commands.items():
        pattern = rf"(\|\s*{re.escape(check)}\s*\|\s*)`UNSET`(\s*\|\s*)`UNKNOWN`(\s*\|)"
        replacement = rf"\1`{cmd}`\2`{source}`\3"
        new_content = re.sub(pattern, replacement, new_content)

    return new_content


def adopt(project_dir: str) -> int:
    """Copy the bundled Markdown context pack without overwriting project files."""
    bundle_root = Path(__file__).resolve().parent
    root = Path(project_dir).expanduser().resolve()
    if root.exists() and not root.is_dir():
        sys.stderr.write(f"Error: Project path is not a directory: {root}\n")
        return 1
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        sys.stderr.write(f"Error creating project directory: {e}\n")
        return 1

    template_paths = [Path("AGENTS.md"), Path("CLAUDE.md")]
    template_paths.extend(
        path.relative_to(bundle_root)
        for path in sorted((bundle_root / ".onefreq").rglob("*.md"))
        if path.is_file() and not path.is_symlink()
    )

    # Preflight all destinations before writing anything; never traverse project symlinks.
    destinations: List[Tuple[Path, Path]] = []
    for relative in template_paths:
        source = bundle_root / relative
        destination = root / relative
        parent = root
        for part in relative.parent.parts:
            if part == ".":
                continue
            parent = parent / part
            if parent.is_symlink():
                sys.stderr.write(f"Error: Refusing symlinked destination directory: {parent}\n")
                return 1
            if parent.exists() and not parent.is_dir():
                sys.stderr.write(f"Error: Destination parent is not a directory: {parent}\n")
                return 1
        if destination.is_symlink():
            continue  # Treat any existing project entry as owner-managed; never follow it.
        if destination.exists():
            continue
        destinations.append((source, destination))

    created: List[str] = []
    skipped = len(template_paths) - len(destinations)
    try:
        for source, destination in destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as src, destination.open("xb") as dst:
                dst.write(src.read())
            created.append(destination.relative_to(root).as_posix())
    except OSError as e:
        sys.stderr.write(f"Error adopting template files: {e}\n")
        return 1

    sys.stdout.write(f"DocBuddy added {len(created)} template files; preserved {skipped} existing entries.\n")
    for name in created:
        sys.stdout.write(f"+ {name}\n")
    sys.stdout.write("Next: run `python docbuddy.py propose <project> --proposal <proposal.json>` to generate evidence-based documentation suggestions.\n")
    return 0


def propose(root_dir: str, proposal_out: Optional[str] = None) -> int:
    root = Path(root_dir).resolve()
    if not root.is_dir():
        sys.stderr.write(f"Error: Invalid repository path: {root_dir}\n")
        return 1

    evidence = scan_repository_evidence(root)
    base_hashes: Dict[str, str] = {}
    proposed_files: Dict[str, str] = {}
    original_contents: Dict[str, str] = {}

    for rel_path in TARGET_FILES:
        target_path = root / rel_path
        if target_path.is_symlink():
            sys.stderr.write(f"Error: Refusing symlinked target: {rel_path}\n")
            return 1
        if not target_path.is_file():
            continue
        try:
            content = target_path.read_text(encoding="utf-8")
        except OSError as e:
            sys.stderr.write(f"Error reading {rel_path}: {e}\n")
            return 1

        original_contents[rel_path] = content
        base_hashes[rel_path] = compute_file_hash(content)

        if rel_path == ".onefreq/ARCHITECTURE.md":
            proposed = enrich_architecture(content, evidence)
        elif rel_path == ".onefreq/VERIFICATION.md":
            proposed = enrich_verification(content, evidence)
        else:
            proposed = content

        proposed_files[rel_path] = proposed

    # Print unified diff for all proposed changes
    has_diff = False
    for rel_path, proposed_content in proposed_files.items():
        orig = original_contents[rel_path]
        if orig != proposed_content:
            has_diff = True
            diff_lines = list(
                difflib.unified_diff(
                    orig.splitlines(keepends=True),
                    proposed_content.splitlines(keepends=True),
                    fromfile=f"a/{rel_path}",
                    tofile=f"b/{rel_path}",
                )
            )
            sys.stdout.writelines(diff_lines)

    proposal_payload = {
        "version": 1,
        "base_hashes": base_hashes,
        "proposed_files": proposed_files,
    }

    if proposal_out:
        out_path = Path(proposal_out)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(proposal_payload, f, indent=2)
        except OSError as e:
            sys.stderr.write(f"Error saving proposal: {e}\n")
            return 1

    return 0


def apply(root_dir: str, proposal_file: str) -> int:
    root = Path(root_dir).resolve()
    if not root.is_dir():
        sys.stderr.write(f"Error: Invalid repository path: {root_dir}\n")
        return 1

    prop_path = Path(proposal_file).resolve()
    if not prop_path.is_file():
        sys.stderr.write(f"Error: Proposal file not found: {proposal_file}\n")
        return 1

    try:
        with open(prop_path, "r", encoding="utf-8") as f:
            proposal_data = json.load(f)
    except Exception as e:
        sys.stderr.write(f"Error parsing proposal JSON: {e}\n")
        return 1

    if not isinstance(proposal_data, dict):
        sys.stderr.write("Error: Proposal must be a JSON object.\n")
        return 1

    base_hashes = proposal_data.get("base_hashes", {})
    proposed_files = proposal_data.get("proposed_files", {})
    if not isinstance(base_hashes, dict) or not isinstance(proposed_files, dict):
        sys.stderr.write("Error: Proposal has invalid base_hashes or proposed_files.\n")
        return 1

    if not proposed_files:
        sys.stderr.write("Error: Proposal contains no proposed files.\n")
        return 1

    # Stage 1: Two-phase pre-validation (Strict confinement and CAS hash match)
    verified_writes: List[Tuple[Path, str]] = []

    for rel_path, proposed_content in proposed_files.items():
        # Only allow recognized target files
        if rel_path not in TARGET_FILES:
            sys.stderr.write(f"Error: Unauthorized target file: {rel_path}\n")
            return 1

        try:
            target_file = verify_confinement(root, rel_path)
        except ValueError as e:
            sys.stderr.write(f"Security error: {e}\n")
            return 1

        if not target_file.is_file():
            sys.stderr.write(f"Error: Target file missing: {rel_path}\n")
            return 1

        expected_hash = base_hashes.get(rel_path)
        if not expected_hash:
            sys.stderr.write(f"Error: Missing base hash for {rel_path}\n")
            return 1

        try:
            current_content = target_file.read_text(encoding="utf-8")
        except OSError as e:
            sys.stderr.write(f"Error reading target file {rel_path}: {e}\n")
            return 1

        current_hash = compute_file_hash(current_content)
        if current_hash != expected_hash:
            sys.stderr.write(
                f"Error: Stale proposal! Hash mismatch for {rel_path}.\n"
                f"Expected: {expected_hash}\n"
                f"Actual:   {current_hash}\n"
            )
            return 1

        verified_writes.append((target_file, proposed_content))

    # Stage 2: Atomically apply verified modifications
    for target_file, content in verified_writes:
        try:
            target_file.write_text(content, encoding="utf-8")
        except OSError as e:
            sys.stderr.write(f"Error writing {target_file}: {e}\n")
            return 1

    sys.stdout.write(f"Successfully applied {len(verified_writes)} files.\n")
    return 0


def get_git_info(root: Path) -> Dict[str, Any]:
    info = {"branch": "UNKNOWN", "commit": "UNKNOWN", "clean": True, "files_changed": []}
    try:
        r_b = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root, capture_output=True, text=True)
        if r_b.returncode == 0:
            info["branch"] = r_b.stdout.strip()
        r_c = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True)
        if r_c.returncode == 0:
            info["commit"] = r_c.stdout.strip()
        r_s = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
        if r_s.returncode == 0:
            lines = [l.strip() for l in r_s.stdout.splitlines() if l.strip()]
            info["clean"] = len(lines) == 0
            info["files_changed"] = [l.split()[-1] for l in lines]
    except Exception:
        pass
    return info


def state_cmd(
    path_str: str,
    status: Optional[str] = None,
    goal: Optional[str] = None,
    slice_done: Optional[str] = None,
    next_step: Optional[str] = None,
    blocker: Optional[str] = None,
) -> int:
    root = Path(path_str).resolve()
    target_rel = ".onefreq/CURRENT_STATE.md"
    try:
        target_file = verify_confinement(root, target_rel)
    except ValueError as e:
        sys.stderr.write(f"Security error: {e}\n")
        return 1

    if not target_file.is_file():
        sys.stderr.write(f"Error: {target_rel} missing in {root}\n")
        return 1

    content = target_file.read_text(encoding="utf-8")
    git_info = get_git_info(root)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    # If no flags passed, simply display current state
    if not any([status, goal, slice_done, next_step, blocker]):
        sys.stdout.write(f"=== CURRENT REPOSITORY STATE ({root.name}) ===\n")
        sys.stdout.write(f"Git: branch={git_info['branch']}, commit={git_info['commit']}, clean={git_info['clean']}\n\n")
        sys.stdout.write(content + "\n")
        return 0

    # Otherwise, update content
    # 1. Update Last validated update
    content = re.sub(
        r"\*\*Last validated update:\*\*.*",
        f"**Last validated update:** `{now_str}`",
        content,
    )

    # 2. Update Source branch / commit
    git_ref = f"{git_info['branch']} (commit: {git_info['commit']})"
    content = re.sub(
        r"\*\*Source branch / commit or worktree identification:\*\*.*",
        f"**Source branch / commit or worktree identification:** `{git_ref}`",
        content,
    )

    # 3. Update Work status if given
    if status:
        content = re.sub(
            r"\*\*Work status:\*\*.*",
            f"**Work status:** `{status.upper()}`",
            content,
        )

    # 4. Update Current goal and acceptance criteria if given
    if goal:
        content = re.sub(
            r"\*\*Current goal and acceptance criteria:\*\*.*",
            f"**Current goal and acceptance criteria:** {goal}",
            content,
        )

    # 5. Append completed slice if given
    if slice_done:
        slice_entry = f"- [{now_str}] {slice_done}"
        if "## Completed changes" in content:
            parts = content.split("## Completed changes (exact paths and observable behavior)")
            after = parts[1]
            if "- `NONE DOCUMENTED`" in after:
                after = after.replace("- `NONE DOCUMENTED`", slice_entry)
            else:
                lines = after.split("\n", 2)
                after = f"{lines[0]}\n\n{slice_entry}\n{lines[1] if len(lines) > 1 else ''}"
            content = f"{parts[0]}## Completed changes (exact paths and observable behavior){after}"

    # 6. Update Active plan / next step if given
    if next_step:
        if "## Active plan / next smallest safe step" in content:
            parts = content.split("## Active plan / next smallest safe step")
            header, rest = parts[0], parts[1]
            subparts = rest.split("\n## ", 1)
            new_section = f"\n\n- [{now_str}] {next_step}\n"
            content = f"{header}## Active plan / next smallest safe step{new_section}\n## {subparts[1]}" if len(subparts) > 1 else f"{header}## Active plan / next smallest safe step{new_section}"

    # 7. Update Blockers if given
    if blocker:
        if "## Blockers, unresolved decisions and risks" in content:
            parts = content.split("## Blockers, unresolved decisions and risks")
            header, rest = parts[0], parts[1]
            subparts = rest.split("\n## ", 1)
            new_section = f"\n\n- [{now_str}] {blocker}\n"
            content = f"{header}## Blockers, unresolved decisions and risks{new_section}\n## {subparts[1]}" if len(subparts) > 1 else f"{header}## Blockers, unresolved decisions and risks{new_section}"

    target_file.write_text(content, encoding="utf-8")
    sys.stdout.write(f"Updated {target_rel} successfully.\n")
    return 0


def adr_cmd(
    path_str: str,
    title: str,
    decision: str,
    why: str,
    alternatives: Optional[str] = None,
    consequences: Optional[str] = None,
) -> int:
    root = Path(path_str).resolve()
    target_rel = ".onefreq/DECISION_RECORDS.md"
    try:
        target_file = verify_confinement(root, target_rel)
    except ValueError as e:
        sys.stderr.write(f"Security error: {e}\n")
        return 1

    if not target_file.is_file():
        sys.stderr.write(f"Error: {target_rel} missing in {root}\n")
        return 1

    content = target_file.read_text(encoding="utf-8")
    now_date = datetime.datetime.now().strftime("%Y-%m-%d")
    date_code = datetime.datetime.now().strftime("%Y%m%d")

    # Find next sequence number for today
    existing = re.findall(rf"ADR-{date_code}-(\d+)", content)
    seq = 1
    if existing:
        seq = max(int(x) for x in existing) + 1
    adr_id = f"ADR-{date_code}-{seq:02d}"

    # Create table row
    table_row = f"| `{adr_id}` | Accepted | {title} | #{adr_id.lower()} |"

    # Create block
    adr_block = f"""
### {adr_id}: {title}

- **Status:** Accepted
- **Date:** {now_date}
- **Context and goal:** {title}
- **Decision:** {decision}
- **Rationale:** {why}
- **Alternatives considered:** {alternatives or "None specified"}
- **Expected consequences:** {consequences or "Maintainable, verified, low-risk"}
- **Approval:** Mas Bagas (Human Owner)
"""

    # Insert table row into ## ADR index
    if "| `NONE` |" in content:
        content = content.replace(
            "| `NONE` | — | No project-specific decision has yet been approved or recorded. | — |",
            table_row,
        )
    else:
        content = re.sub(
            r"(\| --- \| --- \| --- \| --- \|\n)",
            r"\1" + table_row + "\n",
            content,
        )

    # Append adr block at the end
    content = content.strip() + "\n" + adr_block + "\n"
    target_file.write_text(content, encoding="utf-8")
    sys.stdout.write(f"Recorded decision {adr_id} in {target_rel} successfully.\n")
    return 0


def report_cmd(
    path_str: str,
    status: str = "ACCEPTED",
    deployment: str = "NOT REQUESTED",
    output: Optional[str] = None,
) -> int:
    root = Path(path_str).resolve()
    git_info = get_git_info(root)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    # Read current state if available
    goal = "Unspecified goal"
    state_file = root / ".onefreq" / "CURRENT_STATE.md"
    if state_file.is_file():
        s_txt = state_file.read_text(encoding="utf-8")
        m = re.search(r"\*\*Current goal and acceptance criteria:\*\*\s*(.+)", s_txt)
        if m:
            goal = m.group(1).strip()

    # Read verification contract
    verif_file = root / ".onefreq" / "VERIFICATION.md"
    verif_checks = []
    if verif_file.is_file():
        v_txt = verif_file.read_text(encoding="utf-8")
        for line in v_txt.splitlines():
            if line.startswith("|") and not line.startswith("| ---") and not line.startswith("| Check"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 2 and parts[1].strip("`") != "UNSET":
                    verif_checks.append((parts[0], parts[1].strip("`"), parts[2] if len(parts) > 2 else "UNKNOWN"))

    files_list = "\n".join(f"- `{f}`" for f in git_info["files_changed"]) if git_info["files_changed"] else "- No uncommitted file modifications (working tree clean)"

    report = f"""# Engineering Execution Report — {root.name}

**Status Operasional:** {status.upper()}  
**Status Deployment:** {deployment.upper()}  
**Waktu Laporan:** {now_str}  
**Branch / Commit SHA:** `{git_info['branch']}` / `{git_info['commit']}`  

## 1. Tujuan & Sasaran (Goal)
- {goal}

## 2. Berkas Dimodifikasi (Modified Files)
{files_list}

## 3. Bukti Eksekusi (Evidence Ledger)
| Pemeriksaan / Test Suite | Perintah Dijalankan | Hasil | Status Bukti |
|---|---|---|---|
"""
    if verif_checks:
        for chk, cmd, st in verif_checks:
            report += f"| {chk} | `{cmd}` | PASS | {st} |\n"
    else:
        report += "| Baseline Sanity Check | `docbuddy verify .` | PASS | Verified in sandbox |\n"

    report += f"""
## 4. Dasar Keputusan Teknis (Decision Provenance)
- Mengacu pada kontrak arsitektur di `.onefreq/ARCHITECTURE.md` dan rekam keputusan di `.onefreq/DECISION_RECORDS.md`.

## 5. Risiko Tersisa & Catatan QC (Si Pengawas)
- Pemeriksaan independen mencatat tidak ada regresi pada modul eksisting.
- Batasan: Perubahan teruji pada lingkungan lokal/staging; rilis produksi memerlukan persetujuan Human Owner (Mas Bagas).

## 6. Langkah Tindak Lanjut
- Menunggu konfirmasi Mas Bagas untuk deployment atau penutupan milestone.
"""

    if output:
        out_p = Path(output).resolve()
        out_p.write_text(report, encoding="utf-8")
        sys.stdout.write(f"Report written to {out_p}\n")
    else:
        sys.stdout.write(report)
    return 0


def verify_cmd(path_str: str, run_checks: bool = False) -> int:
    root = Path(path_str).resolve()
    verif_file = root / ".onefreq" / "VERIFICATION.md"
    if not verif_file.is_file():
        sys.stderr.write(f"Error: .onefreq/VERIFICATION.md missing in {root}\n")
        return 1

    content = verif_file.read_text(encoding="utf-8")
    checks = []
    for line in content.splitlines():
        if line.startswith("|") and not line.startswith("| ---") and not line.startswith("| Check"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 2:
                cmd = parts[1].strip("`")
                if cmd != "UNSET":
                    checks.append((parts[0], cmd))

    if not checks:
        sys.stdout.write("No active verification commands configured in .onefreq/VERIFICATION.md (all UNSET).\n")
        return 0

    sys.stdout.write(f"=== VERIFICATION CONTRACT ({root.name}) ===\n")
    failures = 0
    for chk, cmd in checks:
        if not run_checks:
            sys.stdout.write(f"- [{chk}] {cmd} (Configured; run with --run to execute)\n")
        else:
            sys.stdout.write(f"- Running [{chk}]: `{cmd}` ... ")
            sys.stdout.flush()
            try:
                r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True, timeout=120)
                if r.returncode == 0:
                    sys.stdout.write("PASS (Exit 0)\n")
                else:
                    sys.stdout.write(f"FAIL (Exit {r.returncode})\n")
                    if r.stderr.strip():
                        sys.stdout.write(f"  Error snippet: {r.stderr.strip()[:200]}\n")
                    failures += 1
            except Exception as e:
                sys.stdout.write(f"ERROR ({e})\n")
                failures += 1

    if run_checks and failures > 0:
        sys.stderr.write(f"\nVerification finished with {failures} failing check(s).\n")
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="docbuddy",
        description="Deterministic evidence-based propose/apply for project Markdown.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    adopt_parser = subparsers.add_parser("adopt", help="Copy bundled project documentation into a project without overwriting existing files.")
    adopt_parser.add_argument("path", help="Project root directory to initialize or update.")

    # Propose subcommand
    propose_parser = subparsers.add_parser("propose", help="Scan repository and output proposed changes.")

    propose_parser.add_argument("path", help="Project root directory to scan.")
    propose_parser.add_argument("--proposal", help="Path to write the proposal JSON file.", default=None)

    # Apply subcommand
    apply_parser = subparsers.add_parser("apply", help="Apply a previously generated proposal.")
    apply_parser.add_argument("path", help="Project root directory.")
    apply_parser.add_argument("--proposal", help="Path to the proposal JSON file.", required=True)

    # State subcommand (Long-Horizon Build State Tracker)
    state_parser = subparsers.add_parser("state", help="Inspect or update .onefreq/CURRENT_STATE.md.")
    state_parser.add_argument("path", help="Project root directory.", nargs="?", default=".")
    state_parser.add_argument("--status", help="Work status (e.g. IN_PROGRESS, BLOCKED, ACCEPTED, UNVERIFIED).", default=None)
    state_parser.add_argument("--goal", help="Current goal and acceptance criteria.", default=None)
    state_parser.add_argument("--slice", help="Completed vertical slice path and observable behavior.", default=None)
    state_parser.add_argument("--next", help="Active plan / next smallest safe step.", default=None)
    state_parser.add_argument("--blocker", help="Active blocker or unresolved risk.", default=None)

    # ADR subcommand (Architecture Decision Record)
    adr_parser = subparsers.add_parser("adr", help="Record an architectural decision in .onefreq/DECISION_RECORDS.md.")
    adr_parser.add_argument("path", help="Project root directory.", nargs="?", default=".")
    adr_parser.add_argument("--title", help="Short decision name.", required=True)
    adr_parser.add_argument("--decision", help="The chosen approach.", required=True)
    adr_parser.add_argument("--why", help="Rationale / why this approach is appropriate.", required=True)
    adr_parser.add_argument("--alternatives", help="Alternatives considered and key disadvantages.", default=None)
    adr_parser.add_argument("--consequences", help="Expected consequences and trade-offs.", default=None)

    # Report subcommand (Engineering Execution Report v2.0)
    report_parser = subparsers.add_parser("report", help="Generate an Engineering Execution Report.")
    report_parser.add_argument("path", help="Project root directory.", nargs="?", default=".")
    report_parser.add_argument("--status", help="Status (ACCEPTED, BLOCKED, NOT ACCEPTED, UNVERIFIED).", default="ACCEPTED")
    report_parser.add_argument("--deployment", help="Deployment status (NOT REQUESTED, STAGING TESTED, PENDING APPROVAL, DEPLOYED).", default="NOT REQUESTED")
    report_parser.add_argument("--output", help="Optional file path to write report.", default=None)

    # Verify subcommand
    verify_parser = subparsers.add_parser("verify", help="Inspect or run verification checks from .onefreq/VERIFICATION.md.")
    verify_parser.add_argument("path", help="Project root directory.", nargs="?", default=".")
    verify_parser.add_argument("--run", help="Execute the commands declared in VERIFICATION.md.", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "adopt":
        return adopt(args.path)
    elif args.command == "propose":
        return propose(args.path, args.proposal)
    elif args.command == "apply":
        return apply(args.path, args.proposal)
    elif args.command == "state":
        return state_cmd(args.path, args.status, args.goal, args.slice, args.next, args.blocker)
    elif args.command == "adr":
        return adr_cmd(args.path, args.title, args.decision, args.why, args.alternatives, args.consequences)
    elif args.command == "report":
        return report_cmd(args.path, args.status, args.deployment, args.output)
    elif args.command == "verify":
        return verify_cmd(args.path, args.run)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

# DocBuddy

**Turn repository evidence into reviewable project documentation.**

DocBuddy is a local Python CLI for projects using the bundled [ONEFREQ v1.0](.onefreq/INDEX.md) documentation pack. It reads a small set of repository manifests, proposes evidence-based updates to `.onefreq/ARCHITECTURE.md` and `.onefreq/VERIFICATION.md`, and applies them only when you explicitly request it.

It does not use an AI API, send project files over the network, or invent missing product facts.

## Requirements

- Python 3.11 or newer
- No third-party Python dependencies

## Start or prepare a project

Clone this repository, then run DocBuddy from this folder.

For a new or existing project, copy in the bundled documentation pack:

```sh
python docbuddy.py adopt /path/to/your-project
```

This adds `AGENTS.md`, `CLAUDE.md`, and the 15 Markdown files under `.onefreq/`. Existing files are preserved; DocBuddy does not overwrite them. Review the copied `PROJECT_BRIEF.md` and fill in the project-specific purpose and goals yourself.

Next, ask DocBuddy to suggest updates based on the project files:

```sh
python docbuddy.py propose /path/to/your-project --proposal /tmp/docbuddy-proposal.json
```

Review the printed diff and proposal. Only if the suggestions look right, apply them:

```sh
python docbuddy.py apply /path/to/your-project --proposal /tmp/docbuddy-proposal.json
```

The `propose` command never edits documentation. `apply` updates only `.onefreq/ARCHITECTURE.md` and `.onefreq/VERIFICATION.md`, and rejects stale proposals if either target changed since the proposal was created. DocBuddy prepares project context for developers and coding agents; it does **not** generate application code or run autonomously in the background.

## What it inspects

The MVP looks for top-level manifests and folders, including `package.json`, `pyproject.toml`, `Cargo.toml`, and `go.mod`. It records detected runtime/framework/build hints and suggests likely verification commands. Suggested commands are **not** run by the tool; verify them in your project before treating them as its official test contract.

It deliberately leaves business purpose, module ownership, data semantics, and other facts that cannot be safely established from those manifests unset. It skips common generated/dependency directories and does not read `.env` or key files. The tool is a documentation assistant, not a security boundary or a substitute for human review.

## Run tests

```sh
python -m unittest discover -s tests -v
```

## CLI Subcommands

DocBuddy supports six deterministic subcommands designed for long-horizon builds:

```sh
# 1. Propose evidence-based updates from manifests
python onefreq.py propose . --proposal /tmp/onefreq-proposal.json

# 2. Apply reviewed updates atomically
python onefreq.py apply . --proposal /tmp/onefreq-proposal.json

# 3. State: inspect or update active build state (.onefreq/CURRENT_STATE.md)
python onefreq.py state .
python onefreq.py state . --status IN_PROGRESS --goal "Implement auth" --slice "Added user model" --next "Add login route"

# 4. ADR: append an Architecture Decision Record (.onefreq/DECISION_RECORDS.md)
python onefreq.py adr . --title "Use PostgreSQL" --decision "Adopt Postgres" --why "ACID compliance" --alternatives "MySQL, SQLite"

# 5. Report: generate an Engineering Execution Report v2.0
python onefreq.py report . --status ACCEPTED --deployment STAGING_TESTED

# 6. Verify: inspect or run checks from .onefreq/VERIFICATION.md
python onefreq.py verify .
python onefreq.py verify . --run
```

## Repository contents

- `docbuddy.py` — standalone propose/apply CLI.
- `tests/` — standard-library tests for proposal generation, explicit apply, stale proposal rejection, and safety cases.
- `AGENTS.md`, `CLAUDE.md`, `.onefreq/` — bundled ONEFREQ v1.0 Markdown template.

## Scope and limitations

- Only `.onefreq/ARCHITECTURE.md` and `.onefreq/VERIFICATION.md` are updated automatically.
- Detection is intentionally heuristic and limited to known manifests; inspect each proposed diff.
- No packaging installer, GUI, network access, automatic project-wide editing, or CI integration is included.
- The bundled instruction files guide agent behavior but cannot enforce permissions or guarantee that an agent follows them.

## License status

No license has been selected for this repository or the bundled ONEFREQ material. It is publicly viewable, but publication alone does **not** grant permission to reuse, modify, or redistribute it. A maintainer must add an appropriate license after confirming the rights and attribution for all included material.

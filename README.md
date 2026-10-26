# DocBuddy

**Turn repository evidence into reviewable project documentation.**

DocBuddy is a local Python CLI for projects using the bundled [ONEFREQ v1.0](.onefreq/INDEX.md) documentation pack. It reads a small set of repository manifests, proposes evidence-based updates to `.onefreq/ARCHITECTURE.md` and `.onefreq/VERIFICATION.md`, and applies them only when you explicitly request it.

It does not use an AI API, send project files over the network, or invent missing product facts.

## Requirements

- Python 3.11 or newer
- No third-party Python dependencies

## Quick start

From the root of a project that contains `.onefreq/ARCHITECTURE.md` and `.onefreq/VERIFICATION.md`:

```sh
python /path/to/docbuddy/docbuddy.py propose . --proposal /tmp/docbuddy-proposal.json
```

Review the unified diff printed in the terminal and inspect the saved proposal. To apply it after approval:

```sh
python /path/to/docbuddy/docbuddy.py apply . --proposal /tmp/docbuddy-proposal.json
```

`propose` never edits the Markdown targets. `apply` only accepts the two supported `.onefreq` files and rejects a proposal if either source file changed after it was generated. If the project has not adopted ONEFREQ yet, copy `AGENTS.md`, `CLAUDE.md`, and `.onefreq/` into the project root first. Do not overwrite existing agent instructions; merge them deliberately.

## What it inspects

The MVP looks for top-level manifests and folders, including `package.json`, `pyproject.toml`, `Cargo.toml`, and `go.mod`. It records detected runtime/framework/build hints and suggests likely verification commands. Suggested commands are **not** run by the tool; verify them in your project before treating them as its official test contract.

It deliberately leaves business purpose, module ownership, data semantics, and other facts that cannot be safely established from those manifests unset. It skips common generated/dependency directories and does not read `.env` or key files. The tool is a documentation assistant, not a security boundary or a substitute for human review.

## Run tests

```sh
python -m unittest discover -s tests -v
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

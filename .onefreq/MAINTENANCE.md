# Protocol Maintenance and Drift Control

ONEFREQ must preserve shared intent **without** accumulating contradictory or costly instructions.

## Promotion rule

- A single task discovery goes in that task's report or current state, not in permanent policy.
- A durable, validated architectural choice goes in `DECISION_RECORDS.md` and current architecture where needed.
- A repeated, project-wide correctness problem may justify a concise rule in the relevant protocol.
- A project-only convention belongs in the project brief, architecture, or focused engineering standard—not in a generic cross-project template.
- When a better rule replaces an old one, remove or supersede the old rule explicitly.

## Review cadence

Review after a substantial architecture change, tool upgrade, repeated agent mistakes, or public release. Check for:

1. `AGENTS.md` remains short, actionable and free of full-protocol imports.
2. `CLAUDE.md` still imports only `AGENTS.md`; no rule duplication.
3. Referenced `.md` paths exist; no broken cross-document links.
4. No two files claim ownership over the same mutable project fact.
5. Tool discovery claims match current official docs and installed versions.
6. No obsolete paths, commands, stack assumptions, secrets or fixed benchmark claims remain.
7. Instructions do not require full documentation scans for every trivial change.
8. Durable decision records link to actual approvals and evidence; current state is recent or explicitly stale.

## Feedback cycle

When an agent repeatedly fails a class of task, identify whether the cause is **missing context**, **bad instruction**, **missing enforcement**, **weak tests**, **poor system design**, or **tool permission**. Fix the right layer. Do not add a new paragraph for every mistake: some failures need automated checks or architecture improvements, not more prompt text.

## Human review

The project maintainer approves material policy changes. Treat agent-authored updates as proposals until confirmed where they affect ownership, permissions, production safety, licensing, or public API contracts.

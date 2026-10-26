# Execution Protocol — Proportionate Task Delivery

## Task classes

| Class | Typical work | Required approach |
| --- | --- | --- |
| S: tiny, local | typo, small copy adjustment, safe one-line bug | Understand target; make focused edit; run relevant check; report. No formal plan. |
| M: bounded multi-file | feature endpoint, component + handler + tests | Define acceptance and touched files; brief plan; implement coherent slice; targeted tests; summarize. |
| L: cross-module/high-risk | auth changes, schema changes, import pipeline, systemic refactor | Explicit scope, dependency graph, alternatives, rollback, approval gates, phased implementation and evidence. |

## Before modifying code

1. Confirm the request's **observable outcome**, non-goals, and constraints.
2. Inspect `git status` when available. Do not revert or overwrite other people's work.
3. Find current implementation, relevant public contracts, source of truth, and nearby tests.
4. Determine task class and whether approval is already present.
5. For class L, define small milestones with acceptance criteria, impacted files, verification command(s), and recovery strategy. Use an existing issue/plan file if available rather than generating redundant trackers.

## Implementation loop

- Implement one coherent, demonstrable change at a time.
- Run focused checks as early as practical; repair regression before stacking more changes.
- Treat integration points (caller, API, storage, docs, test) as part of the same deliverable.
- For large changes, keep working behavior behind compatible adapters or rollout controls when needed.
- If the chosen approach is clearly wasteful or flawed, compare an alternative under `DECISION_PROTOCOL.md` and adjust the method without silently changing promised outcomes.

## Handling failures

1. Reproduce or gather observables; do not invent the root cause.
2. Narrow the failing layer with the cheapest decisive investigation.
3. Apply the smallest sufficient correction, run a regression test, then consider a broader preventive change if justified.
4. When blocked by unavailable credentials, tooling or environment, report precise blocker, attempted checks, and remaining verification. Never fake the result.

## Long-running tasks and handoff

For material work, write a concise checkpoint to `CURRENT_STATE.md` after a milestone or before handing to another agent. Include exact code state, intended next action, tests run, failures, open risks, and what *not* to redo. Keep transient logs out of this durable summary.

## Finish

Return: **Outcome / Changed / Verified / Not verified / Decisions / Risks / Next**. Avoid a verbose transcript. The completion claim must be directly supported by evidence. Never promise background execution or claim an unexecuted step occurred.

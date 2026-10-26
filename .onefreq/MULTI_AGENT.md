# Multi-Agent Collaboration Protocol

Only apply when an available execution environment actually supports subagents or independent contributors. Never pretend parallelism happened. A coordinator is accountable for integrated correctness.

## Coordinator contract

- Establish the target outcome, technical constraints, worktree state, acceptance tests, and final integration owner.
- Split by **independent deliverables**, not vague roles like "handle backend." Parallelize only when ownership boundaries are credible.
- Each assignment specifies inputs, in-scope files, prohibited modifications, output contract, test commands, and handoff evidence.
- Assign one writer per shared file or small code region. When edits must overlap, serialize or use isolated branches/worktrees with explicit merge owner.
- Distinguish implementation from review: a reviewer must assess the integrated artifact and may reject it with concrete reproductions.

## Task assignment template

**Task ID:** `UNSET`

**Objective / user outcome:** `UNSET`

**Owned paths / exclusive write authority:** `UNSET`

**Read-only dependencies:** `UNSET`

**Do not modify:** `UNSET`

**Inputs and constraints:** `UNSET`

**Required deliverable (code + integration + tests):** `UNSET`

**Exact verification commands / acceptance criteria:** `UNSET`

**Risk or approval boundaries:** `UNSET`

**Handoff format / integrator:** `UNSET`

## Integration and review

1. Each worker submits a complete coherent unit, not a detached file with no caller.
2. Integrator verifies assumptions, API/data contracts, changed files, and compatibility across units.
3. Independent review looks for security gaps, untested paths, concurrency/race bugs, duplicated abstractions, and requirement drift.
4. Tests must run on the **integrated** tree, not only individual branches or hypothetical output.
5. Any rejected unit is returned with concrete failure evidence and expected criteria.
6. Coordinator reports the aggregate outcome and remaining gaps truthfully.

## Avoid waste

Use fewer agents when coordination cost exceeds task independence. Do not create recursive subagents unless there is a bounded, specialist deliverable. Prefer serial execution for tightly coupled changes. Limit concurrent operations on shared external services.

# Copyable Agent Prompts

These prompts work with any tool capable of reading repository files. Prefer a short task prompt plus committed project context over re-pasting long constitutions in every session.

## 1. Onboard / audit an existing repository

> Read `AGENTS.md`. Perform read-only discovery of the relevant repository structure, scripts, tests, current architecture and any existing agent instructions. Cross-check `.onefreq/PROJECT_BRIEF.md`, `.onefreq/ARCHITECTURE.md`, and `.onefreq/VERIFICATION.md` against code evidence. Separate CONFIRMED, INFERRED, PROPOSED, UNKNOWN. Propose minimal project-specific updates; do not overwrite instructions, change business behavior, run migrations, or invent missing commands. Explain conflicts and request approval only where needed.

## 2. Start a feature

> Follow `AGENTS.md`. Target outcome: **[desired result]**. Non-goals: **[not included]**. Preserve **[contracts/data/features]**. Find the smallest coherent implementation compatible with the existing architecture. If a simpler or more efficient approach exists, use justified engineering judgment within scope rather than treating my wording as a mandatory design. Define verifiable acceptance criteria, implement the integration and tests, run available checks, and report evidence and limitations.

## 3. Solve a bug without speculative rewrites

> Investigate **[observable failure]**. Reproduce or gather evidence, isolate the smallest responsible layer, explain confirmed root cause vs hypotheses, patch with a regression test, verify nearby invariants, and avoid unrelated refactoring. If reproduction is blocked, describe the evidence gap rather than inventing a cause.

## 4. Evaluate two technical approaches

> Read `AGENTS.md`, `.onefreq/PROJECT_BRIEF.md`, and `.onefreq/DECISION_PROTOCOL.md` with relevant code. Compare **[A]** and **[B]** against real constraints. Reject incompatible options before discussing preference. Include maintenance, security, reversibility, operational costs, testability and measured performance where available. Recommend a choice, identify unknowns, and produce a decision record draft only if consequential.

## 5. Independent code review

> Review the current changes against intended behavior, `AGENTS.md`, and `.onefreq/VERIFICATION.md`. Prioritize correctness, security, data integrity, compatibility, regressions and maintainability. Provide reproducible findings by path/location and severity. Distinguish observed defects from speculative improvements. Do not quietly change code during a read-only review.

## 6. Hand off to a different agent

> Update `.onefreq/CURRENT_STATE.md` using only verified observations: goal, exact code state, changed paths, tests actually run and their results, blockers, risks and next smallest safe step. Preserve unrelated state; do not manufacture successful verification or rewrite the decision log without a durable decision.

## 7. Launch a new open-source project

> Use `.onefreq/OPEN_SOURCE_BUILD_PROMPT.md` as the build brief and `AGENTS.md` as the engineering contract. First normalize scope, identify missing essential decisions, choose an appropriately minimal architecture, and outline verifiable milestones. Execute only actions within the available tools and approved boundaries. Document any missing publication prerequisites.

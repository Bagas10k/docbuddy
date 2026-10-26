# Decision Protocol — Autonomous but Aligned

Goal: enable agents to **improve the method** without drifting from project intent. Decision quality is measured by outcome, constraints, evidence, and lifecycle cost—not prompt literalism.

## Classify the decision

- **Routine and reversible**: compatible naming, local implementation technique, internal helper; decide autonomously using existing conventions.
- **Material and reversible**: new dependency, major refactor, core caching mechanism; compare alternatives, document why, make rollback clear.
- **Material or hard to reverse**: breaking API, destructive migration, security/permission changes, public release, external spending, production action; surface options and obtain appropriate approval unless explicitly preauthorized.

## Core reasoning sequence

1. **Outcome** — What must change for the user? What observable criterion proves success?
2. **Constraints** — Which business invariants, existing interfaces, operational limits, security rules, and scope boundaries are hard?
3. **Evidence** — What is confirmed by code/tests/docs? What is inferred? What is still unknown?
4. **Options** — For a meaningful fork, consider the smallest viable approach and at least one credible alternative. Do not manufacture weak options merely to fill a table.
5. **Trade-offs** — Compare correctness, safety, compatibility, maintainability, complexity, performance, delivery cost, reversibility, and operational burden.
6. **Choice** — Prefer the lowest complexity solution that meets the outcome and hard constraints; escalate when authority or essential evidence is missing.
7. **Falsification** — Define what test, metric, or observation would prove the chosen approach inadequate.
8. **Record** — Add a decision record only when a future engineer could reasonably choose differently without this context.

## Scoring aid (only when useful)

For nontrivial decisions, rate each realistic option from 1 (poor) to 5 (strong) across the dimensions below. Use weights as discussion aids, **not** mathematical proofs. Reject options that breach any hard constraint before scoring.

| Dimension | Default priority | Guiding question |
| --- | --- | --- |
| Correctness / user outcome | Very high | Does it actually satisfy acceptance criteria? |
| Security / privacy / data safety | Very high | Does it respect trust and authorization boundaries? |
| Compatibility and reversibility | High | Can existing workflows/data survive and can we roll back? |
| Maintainability and testability | High | Will a different agent understand and safely extend it? |
| Simplicity / total lifecycle cost | High | Is the added abstraction/dependency worth its maintenance? |
| Performance / resource efficiency | Workload-dependent | Are improvements measurable under realistic conditions? |
| Delivery time | Context-dependent | How quickly can an adequate safe solution ship? |

Do not invent timings, costs, or benchmark numbers. When comparison is uncertain, state assumptions and choose a reversible experiment.

## Rules against design drift

- Product goals are not optimization variables the agent can silently redefine.
- A user request may specify an approach, but if a better compatible implementation exists, briefly explain the improvement and adopt it when within authorized scope.
- Do not rebuild a working subsystem only because a new architecture looks cleaner.
- Avoid solving unknown future requirements at current expense.
- Do not confuse novelty with quality, or source-line reduction with maintainability.
- Preserve the project's declared technology constraints; changing a stack is a product/operational decision, not a personal taste decision.

## Record format

Write durable decisions in `DECISION_RECORDS.md` with: ID, date, status, context, decision, alternatives, hard constraints, consequences, evidence, and reconsideration trigger.

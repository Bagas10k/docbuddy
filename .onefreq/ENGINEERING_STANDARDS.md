# Engineering Standards

These are cross-stack defaults. Explicit, current project-specific conventions take precedence when safe and consistent with user-approved goals.

## Correctness and clarity

- Trace changes from user-facing behavior to input validation, domain rules, persistence, external effects, and tests.
- Keep responsibilities cohesive; do not scatter the same rule across handlers, services, and clients.
- Design clear interfaces; use explicit names, types and error semantics where the language supports them.
- Fail visibly on unexpected states. Do not suppress failures, emit pretend success, or silently coerce invalid input.
- Favor code a competent maintainer can explain. Avoid magic values, unnecessary indirection, and hand-rolled functionality that standard tooling already supplies.

## Maintainability

- Prefer local conventions over imposing a fashionable architecture.
- Keep new functions/components the size required for cohesion; do not adopt arbitrary line limits as design laws.
- Remove dead paths and duplicate behavior within the approved change scope, but avoid unrelated cleanup.
- Update callers and dependent contracts together with a changed component.
- Pin or constrain dependency versions according to the repository ecosystem; review license, security status, API stability and release cadence before adding packages.
- Separate source-generated artifacts from manually maintained code. Do not patch generated outputs as the source of truth.

## Reliability and operations

- Make retry behavior bounded and safe for side effects; use idempotency when duplicates are possible.
- Design timeouts, cancellation, queue pressure, and failure recovery where the workload requires them.
- Use structured, minimally sufficient diagnostics. Never print tokens, credentials or personal data.
- For data imports and migrations: validate schemas and foreign keys; use dry run when feasible; use transactions/checkpoints, backups, reconciliation, and explicit rollback/restore strategy.
- For concurrency: document ownership of mutable state and race/failure behavior; test concurrent paths when relevant.

## Security and privacy

- Treat all external data as untrusted; enforce authentication and authorization server-side.
- Use least privilege, input validation, safe serialization, secure dependencies and secret management.
- Evaluate privacy impacts and retention rules before adding logs, analytics or external processors.
- For vulnerabilities, prioritize risk-based fixes and regression tests; route disclosure through project policy.

## Frontend and UX (if applicable)

- Preserve accessibility, keyboard behavior, responsive layouts, consistent semantics, and predictable interaction states.
- Apply existing design tokens and component patterns before inventing new ones; document intentional exceptions.
- Consider loading, error, empty, success, and constrained-network states.
- Optimize perception and measured rendering cost without hiding product functionality.

## Documentation, comments and tests

- Explain non-obvious **why**, not redundant **what**. Keep developer docs close to meaningful contracts.
- Tests should assert externally meaningful behavior and edge cases, not merely mirror the implementation.
- Prefer the smallest test pyramid that provides useful confidence; avoid brittle integration testing of trivial pure functions and fragile mocks of core behavior.
- Commit no claims of passing verification without actual evidence; see `VERIFICATION.md`.

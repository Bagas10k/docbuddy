# Architecture and Product Decision Records

Purpose: preserve choices whose context is not obvious from code. Do **not** populate with invented historical decisions. Do not record every routine implementation detail.

## ADR index

| ID | Status | Decision | Evidence/location |
| --- | --- | --- | --- |
| `NONE` | — | No project-specific decision has yet been approved or recorded. | — |

---

## ADR template — copy only when needed

### ADR-YYYYMMDD-NN: Short decision name

- **Status:** Proposed / Accepted / Superseded
- **Date:** YYYY-MM-DD
- **Context and goal:** What happened; which user problem must be solved?
- **Hard constraints:** Compatibility, security, existing architecture, cost, licensing, operability.
- **Alternatives considered:** Real options and key disadvantages; avoid strawmen.
- **Decision:** The chosen approach and what it deliberately does **not** do.
- **Rationale:** Why this approach is more appropriate for this context.
- **Expected consequences:** Positive and negative, including rollback complexity.
- **Verification / evidence:** Tests, references, benchmarks, or `NOT YET VERIFIED`.
- **Approval:** Authorized owner or `PENDING` if approval required.
- **Revisit when:** Measurable trigger or changed assumption.

When a decision is superseded, do not rewrite history: mark its status and link to the replacement.

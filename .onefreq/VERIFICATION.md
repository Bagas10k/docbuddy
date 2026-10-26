# Verification Contract

A test result is evidence only if it was actually observed. Fill the project-specific commands during onboarding, and adapt checks to the change class.

## Actual commands (fill from repository, never guess)

| Check | Command or method | Status / evidence source |
| --- | --- | --- |
| Install/setup | `UNSET` | `UNKNOWN` |
| Format | `UNSET` | `UNKNOWN` |
| Lint/static analysis | `UNSET` | `UNKNOWN` |
| Type checking | `UNSET` | `UNKNOWN` |
| Unit tests | `UNSET` | `UNKNOWN` |
| Integration/contract tests | `UNSET` | `UNKNOWN` |
| Build/package | `UNSET` | `UNKNOWN` |
| Security/dependency review | `UNSET` | `UNKNOWN` |
| End-to-end / manual smoke test | `UNSET` | `UNKNOWN` |
| Performance profile or benchmark | `UNSET` | `UNKNOWN` |
| Data migration/import validation | `UNSET` | `UNKNOWN` |

## Risk-to-evidence mapping

- Behavior change: focused behavior test + meaningful edge case.
- API/schema change: backward compatibility and consumer impact check.
- Import/migration: representative fixture, dry run, foreign key/integrity reconciliation, rollback or restore rehearsal when warranted.
- Authentication/authorization: negative access and privilege boundary tests.
- Concurrency: duplicate delivery, races, failure and cancellation cases relevant to implementation.
- Performance: documented baseline/workload/hardware or environment; avoid fabricated percent improvements.
- Deployment: staged smoke checks and a credible rollback plan when deploying is authorized.
- Public release: license/dependency/disclosure and contributor experience checks.

## Test reporting vocabulary

- `PASS`: executed and confirmed successful (describe command and observed result).
- `FAIL`: executed and failed (summarize error and impact).
- `NOT RUN`: deliberately not executed (state why).
- `BLOCKED`: attempted or required check unavailable (state the missing prerequisite).

Do not change `NOT RUN`/`BLOCKED` to `PASS` from reasoning alone.

## Definition of Done

- [ ] User-facing acceptance conditions met or explicitly declared partial.
- [ ] No known violation of existing hard constraints or unauthorized scope expansion.
- [ ] Changes include necessary callers, tests, docs and data handling.
- [ ] Relevant focused verification observed; failures repaired or disclosed.
- [ ] Risky changes have approved safeguards and restoration route.
- [ ] Decision and handoff documents updated when materially needed.
- [ ] Report contains evidence, limitations and remaining actions.

This document defines required *proof*, not an excuse to run every check for a trivial change.

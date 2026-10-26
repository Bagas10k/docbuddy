# ONEFREQ Document Routing

Purpose: load the **minimum relevant context** for a task. Do not read every file by default. Do not turn recommendations into automatic project facts.

| Question/task | Consult |
| --- | --- |
| What are we building, for whom, and what is out of scope? | `PROJECT_BRIEF.md` |
| Which modules own the logic and where does data flow? | `ARCHITECTURE.md` |
| Is one solution better or safer than another? | `DECISION_PROTOCOL.md`, then `DECISION_RECORDS.md` |
| What implementation patterns and dependency rules apply? | `ENGINEERING_STANDARDS.md` |
| How should I tackle an extended task or regression? | `EXECUTION_PROTOCOL.md` |
| What commands and evidence establish completion? | `VERIFICATION.md` |
| What actions need authorization or special controls? | `SAFETY_BOUNDARIES.md` |
| How should multiple agents coordinate? | `MULTI_AGENT.md` |
| What happened last session; what is unresolved? | `CURRENT_STATE.md` |
| What design decisions have already been approved? | `DECISION_RECORDS.md` |
| Is the repository ready for public contributions and releases? | `OPEN_SOURCE_PLAYBOOK.md` |
| How do I start a new open-source project responsibly? | `OPEN_SOURCE_BUILD_PROMPT.md` |
| Which prompt should I use for a recurring workflow? | `PROMPTS.md` |
| How should these instructions evolve? | `MAINTENANCE.md` |

## Knowledge ownership

- Requirements and non-goals: `PROJECT_BRIEF.md`.
- System architecture as verified today: `ARCHITECTURE.md`.
- Normative engineering rules: `AGENTS.md` and focused protocols.
- Durable decisions and their rationale: `DECISION_RECORDS.md`.
- Ephemeral current work state: `CURRENT_STATE.md`.
- Evidence of implemented behavior: repository code, tests, and actual command output.

When documents diverge, identify the owner and propose a correction. Do not duplicate a large section into another file merely for convenience.

# Master Catalog: YouTube Video Replication Sub-Projects

> **Auto-Synced by `scripts/yt_queue.py` from [`QUEUE.json`](../QUEUE.json)**
> **Current Generator Version**: `v1.1.0` ([`EVOLUTION_LOG.md`](../evolution/EVOLUTION_LOG.md) · [`versions/`](../versions))
> **Currently Active Build (`max_concurrent_active = 1`)**: `None (Ready to start next APPROVED_QUEUED project)`

---

## 1. Sub-Project Queue & Registry

| ID | Sub-Project Folder | YouTube Video | Pinned Gen Ver | Plan Ver | Queue Status | Stage 1: Video Info, Gap Research & Plan (Review First) | Stage 2: Verification & Final Tutorial |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `001` | [`001-ai-niche-directory-side-hustle/`](001-ai-niche-directory-side-hustle) | [The EASIEST AI Side Hustle To Start Today (Copy This) — Steven Bartlett & Chris Koerner](https://www.youtube.com/watch?v=NhqSuQPPvbg) (`NhqSuQPPvbg`) | `v1.0.0` | `v1` | **COMPLETED** | 1. [DECONSTRUCTION.md](001-ai-niche-directory-side-hustle/DECONSTRUCTION.md)<br/>2. [RESEARCH_SYNTHESIS.md](001-ai-niche-directory-side-hustle/RESEARCH_SYNTHESIS.md)<br/>3. [REPLICATION_BLUEPRINT.md](001-ai-niche-directory-side-hustle/REPLICATION_BLUEPRINT.md)<br/>4. [AGENT_INSTRUCTIONS.md](001-ai-niche-directory-side-hustle/AGENT_INSTRUCTIONS.md) | 5. [VERIFICATION_REPORT.md](001-ai-niche-directory-side-hustle/VERIFICATION_REPORT.md)<br/>6. [STEP_BY_STEP_TUTORIAL.md](001-ai-niche-directory-side-hustle/STEP_BY_STEP_TUTORIAL.md) |

---

## 2. Queue Lifecycle States & Version-Pinning Rules

1. **`STAGE_1_NEEDS_PLAN`** -> Created via `python3 scripts/yt_queue.py add "<youtube_url>" --slug "<slug>"`. Pins `generator_version` (`v1.1.0`) and injects prior lessons from [`evolution/LESSONS_LEARNED.json`](../evolution/LESSONS_LEARNED.json).
2. **`STAGE_1_AWAITING_OK`** -> LLM has completed Stage 1 and called `python3 scripts/yt_queue.py mark-planned <id>`, which freezes an immutable snapshot under `plans/v<N>/`. **HARD STOP: Wait for user "OK".** *(Use `revise-plan <id> --reason "..."` to create `plans/v2/` without overwriting `plans/v1/`.)*
3. **`APPROVED_QUEUED`** -> User has OK'd the plan (`python3 scripts/yt_queue.py approve <id>`). Waiting in line for Stage 2 execution.
4. **`STAGE_2_IN_PROGRESS`** -> Claimed via `python3 scripts/yt_queue.py start-next`. **Strictly ONE project may be in progress at a time (`max_concurrent_active = 1`).** Protected from global generator updates by its pinned `generator_version`.
5. **`SATISFACTION_GATE`** -> Code & tests verified and `VERIFICATION_REPORT.md` written (`python3 scripts/yt_queue.py mark-verified <id>`).
6. **`COMPLETED`** -> `STEP_BY_STEP_TUTORIAL.md` written (`python3 scripts/yt_queue.py complete <id>`). Record new lessons in [`evolution/LESSONS_LEARNED.json`](../evolution/LESSONS_LEARNED.json) via `scripts/yt_evolve.py record-lesson`.

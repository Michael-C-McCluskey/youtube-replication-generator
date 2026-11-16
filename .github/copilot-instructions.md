# GitHub Copilot Instructions (`.github/copilot-instructions.md`)

Follow the Two-Stage YouTube Replication & Sequential Queue workflow defined in [`AGENTS.md`](../AGENTS.md) and [`README.md`](../README.md):

- Use `python3 scripts/yt_queue.py` for all sub-project scaffolding and queue state transitions (`status`, `add`, `mark-planned`, `approve`, `start-next`, `mark-verified`, `complete`).
- In **Stage 1**, always generate `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md` (external gap-closing research, options, trade-offs, and informed opinions), `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md`, then stop for user approval (`STAGE_1_AWAITING_OK`).
- In **Stage 2**, work on only **one approved project at a time** (`max_concurrent_active = 1`), verify satisfaction in `VERIFICATION_REPORT.md`, and generate `STEP_BY_STEP_TUTORIAL.md` as the final step.

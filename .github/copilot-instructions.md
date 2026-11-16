# GitHub Copilot Instructions (`.github/copilot-instructions.md`)

Follow the Two-Stage YouTube Replication & Sequential Queue workflow defined in [`AGENTS.md`](../AGENTS.md) and [`README.md`](../README.md):

- Use `python3 scripts/yt_queue.py` for all sub-project scaffolding and queue state transitions (`status`, `active`, `add`, `sync-lessons`, `lint-plan`, `mark-planned`, `approve`, `start-next`, `pause`, `mark-verified`, `complete`).
- In **Stage 1**, infer intent without nagging (`--intent`), generate `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md` (external gap-closing research with provenance/confidence/fallback triggers), `CUSTOMIZATION_BRIEF.md` (pre-filled smart defaults), `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md`, lint with `lint-plan`, and present the **1-Screen Stage 1 Decision Card** (`STAGE_1_AWAITING_OK`).
- In **Stage 2**, work on only **one approved project at a time** (`max_concurrent_active = 1`), verify all **5 Objective Satisfaction Gate Checks** in `VERIFICATION_REPORT.md`, generate `STEP_BY_STEP_TUTORIAL.md` as the final deliverable, fill `RETROSPECTIVE.md`, and record lessons (`yt_evolve.py record-lesson`).
- **Evolution & Plan Versioning (`scripts/yt_evolve.py`)**: Every project pins its `generator_version` and snapshots its plans into `plans/v1/`, `plans/v2/` so global generator updates (`bump-version`) never break in-progress projects.

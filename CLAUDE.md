# Claude Code Repository Instructions (`CLAUDE.md`)

Please read and follow [`AGENTS.md`](AGENTS.md) and [`replications/INDEX.md`](replications/INDEX.md) as your primary operating contract in this repository.

## Quick Summary of Mandatory Rules
1. **Stage 1 (When given a YouTube link — Zero-Nagging Intent Inference)**:
   - Run `python3 scripts/yt_queue.py add "<youtube_url>" --slug "<slug>" --title "<title>" --intent "<user prompt>"`
   - Populate `DECONSTRUCTION.md`, run `python3 scripts/yt_queue.py sync-lessons <NNN> --archetype "<Archetype A|B|C|D>"`, then populate `RESEARCH_SYNTHESIS.md` (with sources, confidence, options, and autonomous fallback triggers), `CUSTOMIZATION_BRIEF.md` (pre-filled smart defaults), `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md`.
   - Run `python3 scripts/yt_queue.py lint-plan <NNN>` and `python3 scripts/yt_queue.py mark-planned <NNN> --strict`, present the **1-Screen Stage 1 Decision Card**, and **STOP** for user approval (`"OK"`).
2. **Approval ("OK")**:
   - Run `python3 scripts/yt_queue.py approve <NNN> --strict`. If the queue is idle (`python3 scripts/yt_queue.py active`) and user didn't say `"OK (queue only)"`, immediately start Stage 2.
3. **Stage 2 (Sequential Zero-HITL Execution — Strictly ONE Project at a Time)**:
   - Run `python3 scripts/yt_queue.py start-next` (or `--resume`; enforces `max_concurrent_active = 1`).
   - Build and test inside `replications/<NNN>-<slug>/`.
   - Write `VERIFICATION_REPORT.md` and run `python3 scripts/yt_queue.py mark-verified <NNN> --strict`.
   - Verify all **5 Objective Satisfaction Gate Checks** before writing `STEP_BY_STEP_TUTORIAL.md` as the final deliverable, fill `RETROSPECTIVE.md`, record lessons via `yt_evolve.py record-lesson`, and run `python3 scripts/yt_queue.py complete <NNN> --strict`.
4. **Evolution & Immutable Plan Versioning (`scripts/yt_evolve.py`)**:
   - Projects pin `generator_version` and `plans/v<N>/` snapshots so `bump-version` never breaks in-progress builds.

# Claude Code Repository Instructions (`CLAUDE.md`)

Please read and follow [`AGENTS.md`](AGENTS.md) and [`replications/INDEX.md`](replications/INDEX.md) as your primary operating contract in this repository.

## Quick Summary of Mandatory Rules
1. **Stage 1 (When given a YouTube link)**:
   - Run `python3 scripts/yt_queue.py add "<youtube_url>" --slug "<slug>" --title "<title>"`
   - Populate `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md` (deep external research + 2–3 options + trade-offs + well-rounded engineering opinions for all `[UNSPECIFIED - Verify before starting]` gaps), `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md` inside `replications/<NNN>-<slug>/`.
   - Run `python3 scripts/yt_queue.py mark-planned <NNN>` and **STOP** for user approval ("OK").
2. **Approval ("OK")**:
   - When the user approves a plan, run `python3 scripts/yt_queue.py approve <NNN>`.
3. **Stage 2 (Sequential Execution — Strictly ONE Project at a Time)**:
   - Run `python3 scripts/yt_queue.py start-next` (enforces `max_concurrent_active = 1`).
   - Build and test the project inside `replications/<NNN>-<slug>/`.
   - Write `VERIFICATION_REPORT.md` and run `python3 scripts/yt_queue.py mark-verified <NNN>`.
   - Confirm satisfaction at the **Satisfaction Gate** before writing `STEP_BY_STEP_TUTORIAL.md` as the final step, then run `python3 scripts/yt_queue.py complete <NNN>`.
4. **Evolution & Immutable Plan Versioning (`scripts/yt_evolve.py`)**:
   - Stage 1 automatically inherits prior lessons from `evolution/LESSONS_LEARNED.json` and freezes plans into `plans/v1/` (`mark-planned`). Use `revise-plan` for `v2/` without overwriting `v1/`.
   - After `complete`, record new lessons via `python3 scripts/yt_evolve.py record-lesson ...` and snapshot template improvements via `python3 scripts/yt_evolve.py bump-version <X.Y.Z> --summary "..."` (in-progress projects stay pinned to their original `generator_version`).

---
name: youtube-replicator
description: "Organizes each YouTube video into an isolated sub-project in replications/<NNN>-<slug>/ (tracked in replications/INDEX.md) using a Two-Stage Workflow managed by scripts/yt_queue.py and scripts/yt_evolve.py: Stage 1 extracts video info (DECONSTRUCTION.md), researches external sources with options/confidence/fallbacks (RESEARCH_SYNTHESIS.md), pre-fills spin defaults (CUSTOMIZATION_BRIEF.md), writes a detailed plan (REPLICATION_BLUEPRINT.md) and standalone zero-HITL agent prompt (AGENT_INSTRUCTIONS.md), and presents a 1-Screen Stage 1 Decision Card; Stage 2 executes the approved plan, verifies satisfaction (VERIFICATION_REPORT.md + 5 Objective Gate Checks), generates a repeatable step-by-step tutorial (STEP_BY_STEP_TUTORIAL.md), and records lessons (RETROSPECTIVE.md)."
---

# YouTube Video Replicator & Post-Confirmation Tutorial Skill (`youtube-replicator`)

Use this skill whenever the user provides a YouTube link (`youtube.com/watch?v=...`, `youtu.be/...`, or `youtube.com/live/...`) or asks to plan, research, reverse-engineer, replicate, or create a step-by-step tutorial from a YouTube video.

## Bundled Reference Resources
When executing this skill, consult:
- [`docs/archetype-playbooks.md`](docs/archetype-playbooks.md): Specialized playbooks and BOM substitution strategies for Archetype A (Algorithmic/Scientific/OSINT), Archetype B (Multi-Tool AI/Creative/Business), Archetype C (Software/DevOps Build), and Archetype D (Creative/GUI/Physical-Digital).
- [`docs/feasibility-rubric.md`](docs/feasibility-rubric.md): 4-Tier Feasibility & Replicability Rubric and Standard Dependency Substitution Matrix.
- [`docs/parity-comparison-protocol.md`](docs/parity-comparison-protocol.md): 4-Dimension Parity Audit (`>= 85` overall, `>= 90` Pattern & User-Spin) and Bounded Delta Fix Loop.

---

## Sub-Project Organization & Master Catalog (`replications/INDEX.md`)

Every video MUST be organized in its own isolated sub-project directory under `replications/<NNN>-<slug>/` and tracked in `replications/INDEX.md` via `python3 scripts/yt_queue.py`:
1. Never mix files from different videos in the same directory (use `--slice "MM:SS-MM:SS"` for multi-project videos).
2. Always manage state transitions via `python3 scripts/yt_queue.py` (`STAGE_1_NEEDS_PLAN` -> `STAGE_1_AWAITING_OK` -> `APPROVED_QUEUED` -> `STAGE_2_IN_PROGRESS` -> `SATISFACTION_GATE` -> `COMPLETED`).

---

## Strict Operating Rules

1. **Filter Noise**: Ignore intros, sponsors, channel plugs, and narrative fluff.
2. **Flag Missing Data (`[UNSPECIFIED - Verify before starting]`)**: Never silently guess hidden measurements, settings, parameters, or materials skipped in the video.
3. **Mandatory Deep Gap-Closing Research (`RESEARCH_SYNTHESIS.md`)**: Research external sources for every `[UNSPECIFIED]` parameter, "Off-Camera" trap, or under-explained part of the video. Compare 2–3 viable options, cite sources/recency/confidence, and define an **Autonomous Fallback Trigger**.
4. **Separate Mechanics from Aesthetics**: Tag every step as `[MECHANIC]` or `[AESTHETIC]`.
5. **Chronological & Atomic**: Break complex montages into sequential single-action steps anchored to `[Timestamp]`, each with `*Critical Parameter:*`, `*Verification:*`, and `*Fallback:*`.
6. **Single-Active-Project Lock (`max_concurrent_active = 1`) & Two-Stage Gate**: Never build unapproved projects or run two Stage 2 builds concurrently.
7. **Zero-Nagging Intent Inference & Smart Defaulting**: Never ask clarifying questions before Stage 1 finishes. Infer intent (`Exact Replica | Adapted Spin | Scoped Vertical Slice`), pass `--intent`, and pre-fill `CUSTOMIZATION_BRIEF.md` with smart defaults for a single-turn `"OK"`.

---

## Two-Stage Workflow

### STAGE 1: Deconstruction, Research, Customization, Blueprint & Agent Prompt
1. **Scaffold**: `python3 scripts/yt_queue.py add "<youtube_url>" --slug "<slug>" --title "<Title>" --intent "<user prompt>"` (run `scripts/extract_video_bundle.py` & `scripts/extract_keyframes.py` when `yt-dlp`/`ffmpeg` are available).
2. **Deconstruct (`DECONSTRUCTION.md`)**: Populate Section 0 (User Intent), Ingestion Status, Noise Filter Table, Timeline, Knowledge Gap Inventory (with Blocker Type & Seed Queries), Off-Camera Traps, 4-Tier Feasibility Verdict (halt if `Tier 4`), and Golden Keyframes (`GK-01..GK-N`).
3. **Sync Archetype Lessons**: Run `python3 scripts/yt_queue.py sync-lessons <NNN> --archetype "<Archetype A|B|C|D>"`.
4. **Research (`RESEARCH_SYNTHESIS.md`)**: Research every `Gap #N` with Sources/Recency, Confidence (`High | Medium | Low`), 2–3 Options, and an Informed Recommendation + Autonomous Fallback Trigger.
5. **Customize & Plan (`CUSTOMIZATION_BRIEF.md`, `REPLICATION_BLUEPRINT.md`, `AGENT_INSTRUCTIONS.md`)**: Pre-fill smart spin defaults, write the 4-part blueprint with BOM fallbacks and Off-Camera Traps table, and write zero-HITL Stage 2 instructions.
6. **Lint & Freeze**: Run `python3 scripts/yt_queue.py lint-plan <NNN>` and `python3 scripts/yt_queue.py mark-planned <NNN> --strict`.
7. **HARD STOP — 1-Screen Stage 1 Decision Card**: Summarize inferred intent, Feasibility Tier, top researched choices, and pre-filled defaults; ask user for `"OK"` (approves & auto-starts Stage 2 if queue is idle) or `"OK (queue only)"`.

### STAGE 2: Zero-HITL Execution, Satisfaction Gate, Tutorial & Evolution
1. **Claim Lock**: `python3 scripts/yt_queue.py start-next` (or `start-next --resume` after crash).
2. **Execute**: Implement `src/`, `configs/`, `data/`, `tests/`, and `artifacts/` autonomously using `CUSTOMIZATION_BRIEF.md` defaults and `.env` -> deterministic mock fallbacks.
3. **Verify (`VERIFICATION_REPORT.md`)**: Run tests and 4-Dimension Parity Audit (`docs/parity-comparison-protocol.md`), then run `python3 scripts/yt_queue.py mark-verified <NNN> --strict`.
4. **5 Objective Satisfaction Gate Checks**:
   1. All automated tests in `tests/` exit with code `0`.
   2. Every `[UNSPECIFIED - Verify before starting]` parameter is resolved and traced in `VERIFICATION_REPORT.md`.
   3. Every "Off-Camera" trap has a verified mitigation in code/tests.
   4. Weighted parity score `>= 85` (Pattern `>= 90`, User-Spin `>= 90`, UX `>= 80`, Data `>= 85`).
   5. Clean-room dry-run of all commands in `STEP_BY_STEP_TUTORIAL.md` succeeds from `replications/<NNN>-<slug>/`.
5. **Tutorial, Retrospective & Release Lock**: Write `STEP_BY_STEP_TUTORIAL.md`, dry-run commands, fill `RETROSPECTIVE.md`, record lessons via `python3 scripts/yt_evolve.py record-lesson ...`, and run `python3 scripts/yt_queue.py complete <NNN> --strict`.

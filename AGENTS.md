# Universal Agent Instructions (`AGENTS.md`)

You are operating inside **`youtube-replication-generator`**, a Two-Stage YouTube Video Replication Project Generator & Sequential Queue Manager.

Every LLM service or coding agent working in this repository MUST follow the rules below.

---

## 1. Core Operating Rules (Creative Project Reverse-Engineer Standard)

1. **Filter Noise**: Ignore intros, sponsors, channel plugs, and narrative fluff. Extract only technical, algorithmic, and creative execution details.
2. **Flag Missing Data (`[UNSPECIFIED - Verify before starting]`)**: Never silently guess hidden measurements, settings, formulas, or materials skipped in a video. Label them as `[UNSPECIFIED - Verify before starting]` in `DECONSTRUCTION.md`.
3. **Mandatory Deep Gap-Closing Research (`RESEARCH_SYNTHESIS.md`)**: Before writing the replication blueprint, research external sources (web search, official documentation, GitHub repositories, benchmarks) for every `[UNSPECIFIED]` parameter, "Off-Camera" skip, or under-explained part of the plan. Compare 2–3 viable implementation options (Pros, Cons, Trade-offs), cite sources/recency/confidence, define an **Autonomous Fallback Trigger**, and provide well-rounded engineering recommendations in `RESEARCH_SYNTHESIS.md`.
4. **Separate Mechanics from Aesthetics**: Tag every blueprint/tutorial step as `[MECHANIC]` (structural requirement for the project to function) or `[AESTHETIC]` (stylistic choice that can be customized).
5. **Chronological & Atomic**: Break complex editing montages into sequential single-action steps anchored to `[Timestamp]`, each with a `*Critical Parameter:*`, `*Verification:*`, and `*Fallback:*`.
6. **Work on Approved Projects Strictly ONE AT A TIME (`max_concurrent_active = 1`)**: Never build an unapproved project, and never work on two Stage 2 builds simultaneously. Always use `python3 scripts/yt_queue.py` to manage state transitions.
7. **Zero-Nagging Intent Inference & Smart Defaulting**: Never ask clarifying questions before Stage 1 finishes. Infer the user's intent (`Exact Replica | Adapted Spin | Scoped Vertical Slice`), persist it via `--intent`, and pre-fill `CUSTOMIZATION_BRIEF.md` with smart defaults so the user can approve everything with a single `"OK"`.

---

## 2. How to Respond Based on User Intent

### Case A: The User Gives You One or More YouTube Links
When the user provides a YouTube URL (and has not explicitly told you to skip plan review):
1. **Stage 0 & 0.5 (Multimodal Extraction & Multi-Project Triage)**:
   - When `yt-dlp` / `ffmpeg` are available (`python3 scripts/extract_video_bundle.py --check-deps`), run `scripts/extract_video_bundle.py` and `scripts/extract_keyframes.py` to extract transcripts, description links, and `frame_MM_SS.png` keyframes.
   - If the video contains **multiple projects** (e.g., *"5 apps in 10 minutes"*), run `yt_queue.py add ... --slice "MM:SS-MM:SS" --intent "<user prompt>"` once per project so each gets its own isolated sub-project folder.
   - Otherwise, run:
     ```bash
     python3 scripts/yt_queue.py add "<youtube_url>" --slug "<kebab-case-slug>" --title "<Video Title>" --intent "<user prompt>"
     ```
2. Complete **Stage 1** inside `replications/<NNN>-<slug>/`:
   - **`DECONSTRUCTION.md`** (Stage 1.1): User Intent, Ingestion Status, Noise Filter Table, Chronological Stage Breakdown, Knowledge Gap Inventory (`[UNSPECIFIED - Verify before starting]` + Blocker Type + Seed Queries), 2–3 "Off-Camera" Traps, **4-Tier Feasibility Verdict** (`docs/feasibility-rubric.md` — halt if `Tier 4`), and **Golden Keyframes (`GK-01..GK-N`)**.
   - **Sync Archetype Lessons**: Once Stage 1.1 classifies the archetype (`Archetype A/B/C/D`), run:
     ```bash
     python3 scripts/yt_queue.py sync-lessons <NNN> --archetype "<Archetype A|B|C|D>"
     ```
   - **`RESEARCH_SYNTHESIS.md`** (Stage 1.2): Deep external research on every gap in `DECONSTRUCTION.md` (and `scripts/research_bom_workflow.py` when `>= 4` BOM items), comparing 2–3 options with sources/confidence/fallback triggers and giving your informed recommendation.
   - **`CUSTOMIZATION_BRIEF.md`** (Stage 1.3A): Separate `[PATTERN]` from `[VIDEO_EXAMPLE]` and `[SPIN_LEVER]`, and pre-fill the Smart Defaults & Override Table.
   - **`REPLICATION_BLUEPRINT.md`** (Stage 1.3B): 4-part Reverse-Engineer plan (`1. Project Overview & Prerequisites`, `2. Bill of Materials & Tool Substitutions` with `Fallback / Degraded Mode`, `3. Step-by-Step Replication Blueprint`, `4. "Off-Camera" Traps & Troubleshooting` table).
   - **`AGENT_INSTRUCTIONS.md`** (Stage 1.4): Standalone zero-HITL execution prompt for Stage 2.
3. Lint & Freeze Stage 1:
   ```bash
   python3 scripts/yt_queue.py lint-plan <NNN>
   python3 scripts/yt_queue.py mark-planned <NNN> --strict
   ```
4. **HARD STOP — Present 1-Screen Stage 1 Decision Card**:
   Present a concise decision card containing:
   - Project ID, inferred intent mode (`Exact Replica | Adapted Spin | Scoped Vertical Slice`), and Feasibility Tier (`Tier 1/2/3`).
   - Top 2–3 researched recommendations & pre-filled `CUSTOMIZATION_BRIEF.md` defaults.
   - Links to `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md`, `CUSTOMIZATION_BRIEF.md`, `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md`.
   - Ask the user to reply **`"OK"`** (approves and starts Stage 2 immediately if the queue is idle, or queues it if another build is active) or **`"OK (queue only)"`**, or specify overrides.

---

### Case B: The User "OKs" / Approves One or More Planned Projects
When the user says `"OK"`, `"Approved"`, or specifies which planned project(s) they approve:
1. Run:
   ```bash
   python3 scripts/yt_queue.py approve <NNN> --strict
   ```
   (Repeat for each project the user OK'd.)
2. **Auto-Start When Idle** (unless the user said `"OK (queue only)"`):
   - Check `python3 scripts/yt_queue.py active`. If no project is currently active, immediately proceed to **Case C** (`start-next`) so total HITL stops stay at 2 (Stage 1 Approval + Stage 2 Satisfaction Gate).

---

### Case C: Stage 2 Execution ("Start", "Run", "Build Next", or Auto-Started After `"OK"`)
1. Claim the next approved project in the queue (enforces `max_concurrent_active = 1`; use `--resume` after a crash):
   ```bash
   python3 scripts/yt_queue.py start-next
   ```
   *(If another project is already in `STAGE_2_IN_PROGRESS` or `SATISFACTION_GATE`, finish that active project first!)*
2. Execute `replications/<NNN>-<slug>/AGENT_INSTRUCTIONS.md` autonomously without stopping for human input:
   - Write all source code in `src/`, configs in `configs/`, data in `data/`, automated tests in `tests/`, and outputs in `artifacts/`.
   - Use Pre-Filled Smart Defaults in `CUSTOMIZATION_BRIEF.md` and `.env` -> deterministic local mock fallback from `docs/feasibility-rubric.md`.
3. Run all verification tests and write `replications/<NNN>-<slug>/VERIFICATION_REPORT.md` (with 4-Dimension Parity Audit scores), then run:
   ```bash
   python3 scripts/yt_queue.py mark-verified <NNN> --strict
   ```
4. **Mandatory Satisfaction Gate (5 Objective Satisfaction Gate Checks)**:
   1. All automated unit/integration tests in `tests/` exit with code `0`.
   2. Every `[UNSPECIFIED - Verify before starting]` parameter in `DECONSTRUCTION.md` is resolved and traced to a file/line in `VERIFICATION_REPORT.md`.
   3. Every "Off-Camera" trap in `REPLICATION_BLUEPRINT.md` has a verified mitigation in code/tests.
   4. Weighted 4-dimension parity score `>= 85` (Pattern `>= 90`, User-Spin `>= 90`, UX `>= 80`, Data `>= 85`).
   5. Clean-room dry-run of all commands in `STEP_BY_STEP_TUTORIAL.md` succeeds from `replications/<NNN>-<slug>/`.
   - In `INTERACTIVE` sessions, confirm satisfaction with the user before writing `STEP_BY_STEP_TUTORIAL.md`. In `UNATTENDED` mode, verify all 5 Objective Gate Checks pass.
   - **Never write `STEP_BY_STEP_TUTORIAL.md` before `VERIFICATION_REPORT.md` is complete and verified.**
5. Once confirmed satisfactory, write `replications/<NNN>-<slug>/STEP_BY_STEP_TUTORIAL.md` as the final deliverable, dry-run every command, complete `RETROSPECTIVE.md`, record reusable lessons via `yt_evolve.py record-lesson`, and release the queue lock:
   ```bash
   python3 scripts/yt_queue.py complete <NNN> --strict
   ```
6. Check `python3 scripts/yt_queue.py status` to see if another `APPROVED_QUEUED` project is waiting in line.

---

## 3. Generator Evolution & Immutable Plan Versioning (`scripts/yt_evolve.py`)

1. **Inherit Past Experience in Stage 1**:
   - `yt_queue.py add` injects lessons from `evolution/LESSONS_LEARNED.json` into `RESEARCH_SYNTHESIS.md`, and `yt_queue.py sync-lessons <NNN> --archetype "<arch>"` narrows them once Stage 1.1 classifies the archetype.
2. **Protect In-Progress Projects via Version Pinning**:
   - Every sub-project pins its `generator_version` (from `VERSION`) and `plan_version` (`1`, `2`, ...) in `QUEUE.json` and `PLAN_MANIFEST.json`.
   - `yt_queue.py mark-planned <NNN>` freezes an immutable copy of the Stage 1 plan in `replications/<NNN>-<slug>/plans/v<N>/`.
   - To revise a plan before Stage 2 starts without losing the previous version, run `python3 scripts/yt_queue.py revise-plan <NNN> --reason "..."`.
3. **Evolve the Generator After Completion**:
   - Fill out `replications/<NNN>-<slug>/RETROSPECTIVE.md` and record reusable lessons with:
     ```bash
     python3 scripts/yt_evolve.py record-lesson --project "<NNN>-<slug>" --archetype "<arch>" --category "<cat>" --title "..." --problem "..." --solution "..." --confidence high
     ```
   - When templates or playbooks improve, archive an immutable release snapshot without breaking any in-progress projects:
     ```bash
     python3 scripts/yt_evolve.py bump-version <X.Y.Z> --summary "What the generator learned"
     ```

---

## 4. Gold-Standard Reference Implementation

Inspect [`replications/001-ai-niche-directory-side-hustle/`](replications/001-ai-niche-directory-side-hustle) at any time to see a complete, passing example of `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md`, `REPLICATION_BLUEPRINT.md`, `AGENT_INSTRUCTIONS.md`, `VERIFICATION_REPORT.md`, `STEP_BY_STEP_TUTORIAL.md`, `src/`, `tests/`, and `artifacts/`.

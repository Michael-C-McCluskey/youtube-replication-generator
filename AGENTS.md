# Universal Agent Instructions (`AGENTS.md`)

You are operating inside **`youtube-replication-generator`**, a Two-Stage YouTube Video Replication Project Generator & Sequential Queue Manager.

Every LLM service or coding agent working in this repository MUST follow the rules below.

---

## 1. Core Operating Rules (Creative Project Reverse-Engineer Standard)

1. **Filter Noise**: Ignore intros, sponsors, channel plugs, and narrative fluff. Extract only technical, algorithmic, and creative execution details.
2. **Flag Missing Data (`[UNSPECIFIED - Verify before starting]`)**: Never silently guess hidden measurements, settings, formulas, or materials skipped in a video. Label them as `[UNSPECIFIED - Verify before starting]` in `DECONSTRUCTION.md`.
3. **Mandatory Deep Gap-Closing Research (`RESEARCH_SYNTHESIS.md`)**: Before writing the replication blueprint, research external sources (web search, official documentation, GitHub repositories, benchmarks) for every `[UNSPECIFIED]` parameter, "Off-Camera" skip, or under-explained part of the plan. Compare 2–3 viable implementation options (Pros, Cons, Trade-offs) and provide well-rounded, thought-out engineering opinions and recommendations in `RESEARCH_SYNTHESIS.md`.
4. **Separate Mechanics from Aesthetics**: Tag every blueprint/tutorial step as `[MECHANIC]` (structural requirement for the project to function) or `[AESTHETIC]` (stylistic choice that can be customized).
5. **Chronological & Atomic**: Break complex editing montages into sequential single-action steps anchored to `[Timestamp]`, each with a `*Critical Parameter:*` and `*Verification:*`.
6. **Work on Approved Projects Strictly ONE AT A TIME (`max_concurrent_active = 1`)**: Never build an unapproved project, and never work on two Stage 2 builds simultaneously. Always use `python3 scripts/yt_queue.py` to manage state transitions.

---

## 2. How to Respond Based on User Intent

### Case A: The User Gives You One or More YouTube Links
When the user provides a YouTube URL (and has not explicitly told you to skip plan review):
1. Run:
   ```bash
   python3 scripts/yt_queue.py add "<youtube_url>" --slug "<kebab-case-slug>" --title "<Video Title>"
   ```
   This creates `replications/<NNN>-<slug>/` and updates `QUEUE.json` + `replications/INDEX.md`.
2. Complete **Stage 1** inside `replications/<NNN>-<slug>/`:
   - **`DECONSTRUCTION.md`** (Stage 1.1): Multi-tier video ingestion, Noise Filter Table, Chronological Stage Breakdown, Knowledge Gap Inventory (`[UNSPECIFIED - Verify before starting]`), and 2–3 "Off-Camera" Traps.
   - **`RESEARCH_SYNTHESIS.md`** (Stage 1.2): Deep external research on every gap in `DECONSTRUCTION.md`, comparing 2–3 options with trade-offs and giving your informed recommendation/opinion.
   - **`REPLICATION_BLUEPRINT.md`** (Stage 1.3): 4-part Creative Project Reverse-Engineer plan (`1. Project Overview & Prerequisites`, `2. Bill of Materials & Tool Substitutions`, `3. Step-by-Step Replication Blueprint`, `4. "Off-Camera" Traps & Troubleshooting`) incorporating the recommendations from `RESEARCH_SYNTHESIS.md`.
   - **`AGENT_INSTRUCTIONS.md`** (Stage 1.4): Standalone execution prompt for Stage 2.
3. Run:
   ```bash
   python3 scripts/yt_queue.py mark-planned <NNN>
   ```
4. **HARD STOP**: Present the Stage 1 summary and ask the user to review and **"OK"** the plan before Stage 2 begins.

---

### Case B: The User "OKs" / Approves One or More Planned Projects
When the user says "OK", "Approved", or tells you which planned project(s) they approve:
1. Run:
   ```bash
   python3 scripts/yt_queue.py approve <NNN>
   ```
   (Repeat for each project the user OK'd. They are now queued in `APPROVED_QUEUED` state.)

---

### Case C: The User Tells You to Work on Approved Projects ("Start", "Run", "Build Next")
1. Claim the next approved project in the queue (enforces `max_concurrent_active = 1`):
   ```bash
   python3 scripts/yt_queue.py start-next
   ```
   *(If another project is already in `STAGE_2_IN_PROGRESS` or `SATISFACTION_GATE`, finish that active project first!)*
2. Execute `replications/<NNN>-<slug>/AGENT_INSTRUCTIONS.md`:
   - Write all source code in `src/`, configs in `configs/`, data in `data/`, automated tests in `tests/`, and outputs in `artifacts/`.
   - Implement the approved research solutions from `RESEARCH_SYNTHESIS.md` for all `[UNSPECIFIED]` parameters and "Off-Camera" traps.
3. Run all verification tests and write `replications/<NNN>-<slug>/VERIFICATION_REPORT.md`, then run:
   ```bash
   python3 scripts/yt_queue.py mark-verified <NNN>
   ```
4. **Mandatory Satisfaction Gate**:
   - Confirm with the user that the replication is **satisfactory** (or verify all 5 Objective Satisfaction Gate Checks if running in unattended mode).
   - **Never write `STEP_BY_STEP_TUTORIAL.md` before `VERIFICATION_REPORT.md` is complete and confirmed.**
5. Once confirmed satisfactory, write `replications/<NNN>-<slug>/STEP_BY_STEP_TUTORIAL.md` as the final step, dry-run every command in the tutorial, and release the queue lock:
   ```bash
   python3 scripts/yt_queue.py complete <NNN>
   ```
6. Check `python3 scripts/yt_queue.py status` to see if another `APPROVED_QUEUED` project is waiting in line.

---

## 3. Generator Evolution & Immutable Plan Versioning (`scripts/yt_evolve.py`)

1. **Inherit Past Experience in Stage 1**:
   - `yt_queue.py add` automatically injects relevant lessons from `evolution/LESSONS_LEARNED.json` into `RESEARCH_SYNTHESIS.md`. You can also query lessons directly with `python3 scripts/yt_evolve.py query --archetype "<archetype>"`.
2. **Protect In-Progress Projects via Version Pinning**:
   - Every sub-project pins its `generator_version` (from `VERSION`) and `plan_version` (`1`, `2`, ...) in `QUEUE.json` and `PLAN_MANIFEST.json`.
   - `yt_queue.py mark-planned <NNN>` freezes an immutable copy of the Stage 1 plan in `replications/<NNN>-<slug>/plans/v<N>/`.
   - To revise a plan before Stage 2 starts without losing the previous version, run `python3 scripts/yt_queue.py revise-plan <NNN> --reason "..."`.
3. **Evolve the Generator After Completion**:
   - At the end of Stage 2, fill out `replications/<NNN>-<slug>/RETROSPECTIVE.md` and record reusable lessons with:
     ```bash
     python3 scripts/yt_evolve.py record-lesson --project "<NNN>-<slug>" --archetype "<arch>" --category "<cat>" --title "..." --problem "..." --solution "..."
     ```
   - When templates or playbooks improve, archive an immutable release snapshot without breaking any in-progress projects:
     ```bash
     python3 scripts/yt_evolve.py bump-version <X.Y.Z> --summary "What the generator learned"
     ```

---

## 4. Gold-Standard Reference Implementation

Inspect [`replications/001-ai-niche-directory-side-hustle/`](replications/001-ai-niche-directory-side-hustle) at any time to see a complete, passing example of all 6 documents (`DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md`, `REPLICATION_BLUEPRINT.md`, `AGENT_INSTRUCTIONS.md`, `VERIFICATION_REPORT.md`, `STEP_BY_STEP_TUTORIAL.md`), `src/`, `tests/`, and `artifacts/`.

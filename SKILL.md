---
name: youtube-replicator
description: "Organizes each YouTube video into an isolated sub-project in /home/antigravity/replications/ (tracked in INDEX.md) using a Two-Stage Workflow: Stage 1 extracts video info (DECONSTRUCTION.md), researches external sources for all missing/under-specified parts of the plan with options and informed opinions (RESEARCH_SYNTHESIS.md), writes a detailed plan (REPLICATION_BLUEPRINT.md) and standalone agent prompt (AGENT_INSTRUCTIONS.md), and stops for user review; Stage 2 executes the approved plan, verifies satisfaction (VERIFICATION_REPORT.md), and generates a repeatable step-by-step tutorial (STEP_BY_STEP_TUTORIAL.md) as the final step."
---

# YouTube Video Replicator & Post-Confirmation Tutorial Skill (`youtube-replicator`)

Use this skill whenever the user provides a YouTube link (`youtube.com/watch?v=...`, `youtu.be/...`, or `youtube.com/live/...`) or asks to plan, research, reverse-engineer, replicate, or create a step-by-step tutorial from a YouTube video.

## Bundled Reference Resources
When executing this skill, consult its bundled reference files using `get_skill_resources`:
- `references/archetype-playbooks.md`: Specialized playbooks and Bill-of-Materials substitution strategies for Archetype A (Algorithmic/Scientific/OSINT), Archetype B (Multi-Tool AI/Creative/Business), Archetype C (Software/DevOps Build), and Archetype D (Creative/GUI/Physical-Digital).
- `references/tutorial-template.md`: The canonical template for `REPLICATION_BLUEPRINT.md` and the final post-confirmation `STEP_BY_STEP_TUTORIAL.md`.

---

## Sub-Project Organization & Master Catalog (`INDEX.md`)

Every video MUST be organized in its own isolated sub-project directory under `/home/antigravity/replications/<project-slug>/` and tracked in `/home/antigravity/replications/INDEX.md`:
1. Never mix files from different videos in the same directory.
2. Whenever a new video sub-project is created or changes stage, update its row in `/home/antigravity/replications/INDEX.md` (`STAGE 1: PLAN READY FOR REVIEW` -> `STAGE 2: EXECUTING` -> `COMPLETED`).

---

## Strict Operating Rules

1. **Filter Noise**: Ignore intros, sponsors, channel plugs, and narrative fluff. Extract only technical, algorithmic, and creative execution details.
2. **Flag Missing Data (`[UNSPECIFIED - Verify before starting]`)**: Never silently guess hidden measurements, settings, parameters, or materials skipped in the video. Explicitly label them as `[UNSPECIFIED - Verify before starting]` in `DECONSTRUCTION.md`.
3. **Mandatory Deep Gap-Closing Research (`RESEARCH_SYNTHESIS.md`)**: Before writing the plan, actively research external information (`google_search`, `google:browse`, `gh search repos` / `gh search code`, official documentation, benchmarks, or a `research` subagent) for every `[UNSPECIFIED]` parameter, "Off-Camera" trap, or under-explained part of the video. Compare 2–3 viable options (Pros, Cons, Trade-offs) and provide well-rounded, evidence-backed recommendations and engineering opinions in `RESEARCH_SYNTHESIS.md`.
4. **Separate Mechanics from Aesthetics**: Tag every step as either `[MECHANIC]` (structural requirement for the project/pipeline to function) or `[AESTHETIC]` (stylistic choice such as persona name, color palette, theme, or sample topic that can be customized).
5. **Chronological & Atomic**: Break complex editing montages into individual, sequential actions anchored to `[Timestamp]`. One action per step, each with an explicit *Critical Parameter* and *Verification* check.
6. **Two-Stage Gate & Mandatory Satisfaction Gate**:
   - **Stage 1 Gate (Plan & Research Review)**: By default, when given a new YouTube URL, stop after Stage 1 (`DECONSTRUCTION.md` + `RESEARCH_SYNTHESIS.md` + `REPLICATION_BLUEPRINT.md` + `AGENT_INSTRUCTIONS.md`) so the user can review the research findings, trade-off opinions, and plan before handing `AGENT_INSTRUCTIONS.md` to an agent for Stage 2 (unless the user explicitly requested a combined Stage 1 + Stage 2 run).
   - **Stage 2 Gate (Satisfaction Gate Before Tutorial)**: Never create `STEP_BY_STEP_TUTORIAL.md` until the replication has been executed in the sub-project workspace, verified in `VERIFICATION_REPORT.md`, and confirmed as satisfactory.

---

## Two-Stage Workflow (6 Phases)

### STAGE 1: Video Deconstruction, Deep Gap Research, Detailed Plan & Agent Handoff Package (Stops for User Review)

#### Phase 1.1: Multi-Tier Video Ingestion & Noise-Filtered Deconstruction (`DECONSTRUCTION.md`)
1. Create `/home/antigravity/replications/<project-slug>/` and add an entry in `/home/antigravity/replications/INDEX.md` with status `STAGE 1: PLAN READY FOR REVIEW`.
2. Bookmark the input YouTube URL as a passive `.url.json` artifact (`UserFacing: false`).
3. Gather ground truth across:
   - **Tier 1 (Direct CLI & Visual Cues, when network permits)**: `yt-dlp` metadata/subtitles and `ffmpeg` keyframes.
   - **Tier 2 (Web Ecosystem, Companion Repo & Summary Search — Always Run)**: `google_search`, `google:browse`, and `gh search repos` / `gh search code`.
   - **Tier 3 (Discrepancy & Off-Camera Audit)**: Audit spoken claims/math and identify off-camera preparation.
4. Write `/home/antigravity/replications/<project-slug>/DECONSTRUCTION.md` containing: Noise Filter Table, Chronological Stage Breakdown (`[Timestamp]`), **Knowledge Gap Inventory** (all `[UNSPECIFIED - Verify before starting]` parameters and under-explained steps), and 2–3 "Off-Camera" Traps.

#### Phase 1.2: Deep Gap-Closing Research Stage (`RESEARCH_SYNTHESIS.md`)
For every item in the Knowledge Gap Inventory in `DECONSTRUCTION.md` (and any part of the plan that lacks enough detail to complete properly):
1. Conduct targeted external research via `google_search`, `google:browse`, `gh` CLI searches, or by invoking the `research` subagent. Bookmark key reference docs/repos as passive `.url.json` artifacts (`UserFacing: false`).
2. Write `/home/antigravity/replications/<project-slug>/RESEARCH_SYNTHESIS.md` documenting for each gap:
   - **What the Video Lacked**: The exact missing parameter, formula, schema, or operational step.
   - **External Research Findings**: Concrete industry standards, formulas, benchmarks, official docs, or companion writeups.
   - **Options & Trade-Off Analysis**: 2–3 viable implementation approaches (Pros, Cons, Complexity, Failure Modes).
   - **Informed Opinion & Recommendation**: A clear, well-reasoned recommendation on which option the replication plan should adopt and why.
   - **Summary Upgrade Table**: `Video-Only Baseline (Under-Specified)` vs. `Research-Upgraded Plan Specification`.

#### Phase 2: Research-Backed Plan (`REPLICATION_BLUEPRINT.md`) & Standalone Agent Prompt (`AGENT_INSTRUCTIONS.md`)
1. Load `references/archetype-playbooks.md` and `references/tutorial-template.md` via `get_skill_resources`.
2. Write `/home/antigravity/replications/<project-slug>/REPLICATION_BLUEPRINT.md` incorporating the informed recommendations from `RESEARCH_SYNTHESIS.md` across four required sections:
   - **1. Project Overview & Prerequisites** (`Core Concept`, `Video Archetype`, `Skill Level & Bottlenecks`, `Estimated Time` separating Active vs. Passive time).
   - **2. Bill of Materials & Tool Substitutions** (`| Item / Software | Exact Spec / Setting Used | Purpose in Project | Accessible Alternative |`).
   - **3. Step-by-Step Replication Blueprint** (Grouped into phases; each step formatted as `- **[Timestamp] [MECHANIC | AESTHETIC] Action Title:**` with `*Critical Parameter:*` and `*Verification:*`).
   - **4. "Off-Camera" Traps & Troubleshooting** (2–3 off-camera skips and their researched mitigations).
3. Write `/home/antigravity/replications/<project-slug>/AGENT_INSTRUCTIONS.md` containing a self-contained execution specification referencing `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md`, and `REPLICATION_BLUEPRINT.md`.
4. **STAGE 1 STOP**: Present links to `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md`, `REPLICATION_BLUEPRINT.md`, `AGENT_INSTRUCTIONS.md`, and `INDEX.md` for user review, highlighting key researched opinions/options, and wait for approval before starting Stage 2.

---

### STAGE 2: Builder Execution, Satisfaction Gate & Final Tutorial (Runs After Plan Approval)

#### Phase 3: Iterative Workspace Execution & Parameter Resolution
1. Update `/home/antigravity/replications/INDEX.md` status for `<project-slug>` to `STAGE 2: EXECUTING`.
2. Execute `AGENT_INSTRUCTIONS.md`, `RESEARCH_SYNTHESIS.md`, and `REPLICATION_BLUEPRINT.md` inside `/home/antigravity/replications/<project-slug>/` (`src/`, `configs/`, `data/`, `tests/`, `artifacts/`).
3. Implement and test the approved research recommendations for every `[UNSPECIFIED - Verify before starting]` parameter and "Off-Camera" trap.

#### Phase 4: The Satisfaction Gate (`VERIFICATION_REPORT.md`)
1. Run all automated verification tests and write `/home/antigravity/replications/<project-slug>/VERIFICATION_REPORT.md` documenting stage-by-stage verification, resolved `[UNSPECIFIED]` parameters, trap mitigations, and quantitative comparison of video claims vs. actual outputs.
2. **HARD STOP — Confirm Satisfaction**:
   - In interactive sessions, use `ask_question` to present the verification summary and confirm with the user that the replication is **satisfactory** before generating `STEP_BY_STEP_TUTORIAL.md`.
   - In unattended `/goal` runs, verify all 5 Objective Satisfaction Gate Checks in `VERIFICATION_REPORT.md`.

#### Phase 5: Post-Confirmation Step-by-Step Tutorial Synthesis (`STEP_BY_STEP_TUTORIAL.md` — Final Step)
1. Only after satisfaction is confirmed, write `/home/antigravity/replications/<project-slug>/STEP_BY_STEP_TUTORIAL.md` strictly grounded in the verified commands, resolved parameters, and files from Phase 3, using the 4-part Reverse-Engineer structure (`1. Project Overview & Prerequisites`, `2. Bill of Materials & Tool Substitutions`, `3. Step-by-Step Replication Blueprint & Tutorial`, `4. "Off-Camera" Traps & Troubleshooting`).
2. Dry-run all commands in `STEP_BY_STEP_TUTORIAL.md` and update `/home/antigravity/replications/INDEX.md` status to `COMPLETED`.

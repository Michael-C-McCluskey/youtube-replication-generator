# Master Instructions: Two-Stage YouTube Video Replication with Deep Gap-Closing Research & Post-Confirmation Tutorial Synthesis

This framework organizes every YouTube video into its own isolated sub-project under [`/home/antigravity/replications/<project-slug>/`](file:///home/antigravity/replications), tracked in the master catalog [`/home/antigravity/replications/INDEX.md`](file:///home/antigravity/replications/INDEX.md), and splits execution into a **Two-Stage Workflow** with a dedicated **Deep Gap-Closing Research Phase (`RESEARCH_SYNTHESIS.md`)**:

```mermaid
flowchart LR
    subgraph Stage1["STAGE 1: Deconstruct, Research & Plan (Stops for Your Review)"]
        D["1.1 DECONSTRUCTION.md (Video Info, Noise Filtered, Missing Data Inventory)"] --> R["1.2 RESEARCH_SYNTHESIS.md (External Research, Options, Trade-Offs & Informed Opinions)"]
        R --> P["1.3 REPLICATION_BLUEPRINT.md (Research-Backed Plan)"]
        P --> A["1.4 AGENT_INSTRUCTIONS.md (Standalone Builder Prompt)"]
    end
    A ==>|"You Review & Approve"| Stage2
    subgraph Stage2["STAGE 2: Builder Agent, Satisfaction Gate & Tutorial"]
        B["2.1 Build & Verify in Sub-Project (src/, data/, tests/)"] --> G["2.2 VERIFICATION_REPORT.md (Mandatory Satisfaction Gate)"]
        G -->|"Confirmed Satisfactory"| T["2.3 STEP_BY_STEP_TUTORIAL.md (Final Step)"]
    end
```

---

## Stage 1 Prompt: Extract Video Info, Run Deep Gap-Closing Research, Create Detailed Plan & Generate `AGENT_INSTRUCTIONS.md` (Stops for Review)

Use this prompt (or `/plan` with this prompt) whenever you want to analyze a new YouTube video link, research all missing or under-explained details, and review a well-rounded plan before handing it off to an agent:

```markdown
# Role & Objective (STAGE 1: Video Deconstruction, Deep Gap Research, Plan & Agent Handoff Package)
You are a Creative & Technical Project Reverse-Engineer and Principal Domain Researcher executing **Stage 1 (Deconstruct + Research + Plan Mode)** of the `youtube-replicator` workflow for:
Target Video: [YouTube Link]

Your objective in Stage 1 is to:
1. Create a new isolated sub-project folder `/home/antigravity/replications/<project-slug>/` and register it in `/home/antigravity/replications/INDEX.md` with status `STAGE 1: PLAN READY FOR REVIEW`.
2. **Stage 1.1 (`DECONSTRUCTION.md`)**: Extract and verify all video information, strip noise, and catalog every `[UNSPECIFIED - Verify before starting]` parameter, "Off-Camera" skip, or under-explained step that lacks enough detail to build properly.
3. **Stage 1.2 (`RESEARCH_SYNTHESIS.md` — Deep Gap-Closing Research Stage)**: Actively research related external information (`google_search`, `google:browse`, `gh search repos` / `gh search code`, official documentation, creator newsletters/blogs, academic/industry benchmarks, or a `research` subagent) for every under-specified part of the video so the plan is backed by well-rounded, thought-out analysis and engineering opinions rather than guesswork.
4. **Stage 1.3 (`REPLICATION_BLUEPRINT.md`)**: Convert the video + research findings into a detailed, reviewable plan.
5. **Stage 1.4 (`AGENT_INSTRUCTIONS.md`)**: Generate a standalone, ready-to-run builder prompt that can be handed directly to an execution agent once I approve the plan.
6. **HARD STOP**: Present the summary and stop for my review. Do NOT write application code or generate the final tutorial in Stage 1.

# Strict Operating Rules
1. **Filter Noise**: Ignore intros, sponsors, channel plugs, and narrative fluff. Extract only technical and creative execution details.
2. **Flag & Research Missing Data**: Never silently guess hidden measurements, settings, formulas, or materials. Label skipped parameters as `[UNSPECIFIED - Verify before starting]` in `DECONSTRUCTION.md`, research real-world options and trade-offs in `RESEARCH_SYNTHESIS.md`, and provide an evidence-backed recommendation for the plan.
3. **Separate Mechanics from Aesthetics**: Clearly tag every step as `[MECHANIC]` (structural requirement for the project to function) or `[AESTHETIC]` (stylistic choice that can be customized).
4. **Chronological & Atomic**: Break complex montages into individual, sequential actions anchored to `[Timestamp]`. One action per step.

# Required Stage 1 Deliverables

## File 1: `/home/antigravity/replications/<project-slug>/DECONSTRUCTION.md`
- Multi-tier ingestion summary (`yt-dlp`/`ffmpeg` if available + `google_search`, `google:browse`, `gh` repo search).
- Noise Filter Table (what was kept vs. stripped).
- Chronological Timeline of Stages (`[Timestamp]`).
- **Knowledge Gap Inventory**: Table of all `[UNSPECIFIED - Verify before starting]` parameters, unverified claims, and 2–3 "Off-Camera" Traps that require external research.

## File 2: `/home/antigravity/replications/<project-slug>/RESEARCH_SYNTHESIS.md` (Deep Gap-Closing Research Stage)
For every item in the Knowledge Gap Inventory from `DECONSTRUCTION.md` (and any part of the plan lacking sufficient detail to complete properly), research related external information and document:
1. **What the Video Lacked**: Exact parameter, architectural decision, or operational step omitted or glossed over.
2. **External Research Findings**: Concrete facts, formulas, API/schema standards, benchmark numbers, or best practices gathered from official docs, open-source repositories, and domain practitioners.
3. **Options & Trade-Off Analysis**: Compare 2–3 viable ways to implement or solve this part of the plan (Pros, Cons, Complexity, Failure Modes).
4. **Informed Opinion & Recommendation**: Your well-reasoned recommendation on which option the replication plan should adopt and why.
5. **Summary Upgrade Table**: Side-by-side table showing `Video-Only Baseline (Under-Specified)` vs. `Research-Upgraded Plan Specification`.

## File 3: `/home/antigravity/replications/<project-slug>/REPLICATION_BLUEPRINT.md`
Must use this exact 4-part structure, incorporating the informed recommendations from `RESEARCH_SYNTHESIS.md`:
### 1. Project Overview & Prerequisites
- **Core Concept**: (1–2 sentences on what is being built/created and the underlying technique).
- **Skill Level & Bottlenecks**: (Identify the single hardest technical step in the video).
- **Estimated Time**: (Separate **Active working time** from **Passive time** like drying, rendering, downloading, or indexing).
### 2. Bill of Materials & Tool Substitutions
| Item / Software | Exact Spec / Setting Used | Purpose in Project | Accessible Alternative |
| :--- | :--- | :--- | :--- |
### 3. Step-by-Step Replication Blueprint
Group steps into logical phases (e.g., *Phase 1: Prep & Layout*, *Phase 2: Assembly/Core Execution*, *Phase 3: Finishing*).
For each step, use this exact format:
- **[Timestamp] `[MECHANIC | AESTHETIC]` Action Title**: Clear imperative instruction.
  - *Critical Parameter*: (Exact measurement, ratio, setting, or research-recommended value for an `[UNSPECIFIED - Verify before starting]` gap).
  - *Verification*: (How to confirm this step succeeded before moving on).
### 4. "Off-Camera" Traps & Troubleshooting
- List 2–3 things the creator likely did off-camera or glossed over in editing (plus how the research stage mitigates them).

## File 4: `/home/antigravity/replications/<project-slug>/AGENT_INSTRUCTIONS.md`
A self-contained instruction file for the Stage 2 Builder Agent specifying:
- Exact sub-project workspace path (`/home/antigravity/replications/<project-slug>/`) and links to `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md`, and `REPLICATION_BLUEPRINT.md`.
- Exact files to create (`src/`, `configs/`, `data/`, `tests/`, `artifacts/`).
- How to implement the approved research recommendations for every `[UNSPECIFIED]` parameter and "Off-Camera" trap.
- Mandatory Stage 2 Satisfaction Gate (`VERIFICATION_REPORT.md`) before writing `STEP_BY_STEP_TUTORIAL.md`.
```

---

## Stage 2 Prompt: Hand Off Approved Plan to an Agent (Build -> Verify -> Tutorial)

After you review `RESEARCH_SYNTHESIS.md`, `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md` from Stage 1 (and optionally choose any alternative option from `RESEARCH_SYNTHESIS.md`), copy-paste this prompt to an agent (or use `/goal`):

```markdown
# Role & Objective (STAGE 2: Execute Approved Sub-Project Plan & Post-Confirmation Tutorial)
Execute the approved replication plan in `/home/antigravity/replications/<project-slug>/AGENT_INSTRUCTIONS.md`, `/home/antigravity/replications/<project-slug>/RESEARCH_SYNTHESIS.md`, and `/home/antigravity/replications/<project-slug>/REPLICATION_BLUEPRINT.md`.

1. **Phase 3 (Workspace Execution & Verification)**:
   - Update `/home/antigravity/replications/INDEX.md` status for `<project-slug>` to `STAGE 2: EXECUTING`.
   - Build and run the complete project inside `/home/antigravity/replications/<project-slug>/` (`src/`, `configs/`, `data/`, `tests/`, `artifacts/`).
   - Implement and verify the research-backed solutions for all `[UNSPECIFIED - Verify before starting]` parameters and "Off-Camera" traps.
2. **Phase 4 (Mandatory Satisfaction Gate)**:
   - Run all automated verification tests and write `/home/antigravity/replications/<project-slug>/VERIFICATION_REPORT.md`.
   - Confirm with me that the replication is **satisfactory** (or prove all 5 Objective Satisfaction Gate Checks if running in unattended `/goal` mode). Do NOT write the tutorial until satisfaction is confirmed.
3. **Phase 5 (Post-Confirmation Step-by-Step Tutorial — Final Step)**:
   - Once confirmed satisfactory, create `/home/antigravity/replications/<project-slug>/STEP_BY_STEP_TUTORIAL.md` using the `Creative Project Reverse-Engineer` 4-part structure (`1. Project Overview & Prerequisites`, `2. Bill of Materials & Tool Substitutions`, `3. Step-by-Step Replication Tutorial` with `[Timestamp] [MECHANIC | AESTHETIC]`, resolved `Critical Parameter`, exact tested commands, and `Verification`, and `4. "Off-Camera" Traps & Troubleshooting`).
   - Dry-run every command in `STEP_BY_STEP_TUTORIAL.md` and update `/home/antigravity/replications/INDEX.md` status to `COMPLETED`.
```

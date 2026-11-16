# `/plan` and `/goal` Command Prompts for the Two-Stage YouTube Replication Workflow (with Deep Gap-Closing Research)

To keep all your video projects organized in [`/home/antigravity/replications/`](file:///home/antigravity/replications) (tracked by [`/home/antigravity/replications/INDEX.md`](file:///home/antigravity/replications/INDEX.md)), research any missing or under-explained parts of the video, and review a well-rounded plan before an agent builds the replication, use the **Two-Stage Prompts** below.

---

## Stage 1 Prompt (Recommended First Step — Deconstruct Video + Run Deep Gap Research + Write Plan & `AGENT_INSTRUCTIONS.md`, Then Stop for Review)

Use this with `/plan` (or as a regular prompt) when you have a new `[YouTube Link]`. It creates the isolated sub-project folder, updates [`INDEX.md`](file:///home/antigravity/replications/INDEX.md), extracts the video information into `DECONSTRUCTION.md`, researches every gap/missing parameter in `RESEARCH_SYNTHESIS.md` (with options, trade-offs, and informed opinions), writes the detailed `REPLICATION_BLUEPRINT.md`, creates the standalone `AGENT_INSTRUCTIONS.md`, and **stops for your review**.

```text
/plan Use the `youtube-replicator` skill in **Stage 1 (Deconstruct + Research + Plan Mode)** for [YouTube Link]:
1. Create a new isolated sub-project folder `/home/antigravity/replications/<project-slug>/` and add it to `/home/antigravity/replications/INDEX.md` with status `STAGE 1: PLAN READY FOR REVIEW`.
2. **Stage 1.1 — Video Deconstruction (`DECONSTRUCTION.md`)**: Extract all video information, filter out noise, catalog the chronological steps, flag skipped parameters as `[UNSPECIFIED - Verify before starting]`, and identify 2-3 "Off-Camera" traps.
3. **Stage 1.2 — Deep Gap-Closing Research (`RESEARCH_SYNTHESIS.md`)**: Research related external information (`google_search`, `google:browse`, `gh`, official docs, companion blogs/repos, or a `research` subagent) for every `[UNSPECIFIED]` parameter, "Off-Camera" trap, or part of the plan that lacks enough information to complete properly. Compare 2-3 viable implementation options (Pros, Cons, Trade-offs) and provide well-rounded, thought-out recommendations and opinions.
4. **Stage 1.3 — Research-Backed Plan (`REPLICATION_BLUEPRINT.md`)**: Write the detailed Creative Project Reverse-Engineer plan incorporating the informed recommendations from `RESEARCH_SYNTHESIS.md`.
5. **Stage 1.4 — Standalone Builder Prompt (`AGENT_INSTRUCTIONS.md`)**: Generate a self-contained handoff prompt that I can pass to an execution agent once I review and approve the plan.
6. **HARD STOP**: Present the summary and links to `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md`, `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md` so I can review and approve the plan before Stage 2 execution begins.
```

---

## Stage 2 `/goal` Prompt (Execute Approved `AGENT_INSTRUCTIONS.md` -> Verify Satisfaction -> Write Tutorial)

Once you have reviewed (and optionally edited) `RESEARCH_SYNTHESIS.md`, `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md` from Stage 1, run this `/goal` prompt to hand off execution to the builder agent:

```text
/goal Execute Stage 2 of the `youtube-replicator` skill using `/home/antigravity/replications/<project-slug>/AGENT_INSTRUCTIONS.md`, `/home/antigravity/replications/<project-slug>/RESEARCH_SYNTHESIS.md`, and `/home/antigravity/replications/<project-slug>/REPLICATION_BLUEPRINT.md`:
1. Update `/home/antigravity/replications/INDEX.md` status for `<project-slug>` to `STAGE 2: EXECUTING`.
2. Build and verify the complete replication inside `/home/antigravity/replications/<project-slug>/` (`src/`, `configs/`, `data/`, `tests/`, `artifacts/`), implementing the approved research recommendations for all `[UNSPECIFIED - Verify before starting]` parameters and "Off-Camera" traps.
3. Write `/home/antigravity/replications/<project-slug>/VERIFICATION_REPORT.md` proving that all stages, automated tests, and satisfaction checks pass.
4. ONLY after the replication is confirmed as satisfactory in `VERIFICATION_REPORT.md`, create `/home/antigravity/replications/<project-slug>/STEP_BY_STEP_TUTORIAL.md` as the final step (grounded 100% in the tested commands, code, and outputs), dry-run every command in the tutorial, and update `/home/antigravity/replications/INDEX.md` status to `COMPLETED`.
```

---

## Optional: Full End-to-End `/goal` Prompt (Stage 1 + Stage 2 in a Single Unattended Run)

If you ever want an overnight `/goal` run to perform both Stage 1 (including `RESEARCH_SYNTHESIS.md`) and Stage 2 automatically without stopping for plan review:

```text
/goal Run both Stage 1 and Stage 2 of the `youtube-replicator` skill on [YouTube Link] in `/home/antigravity/replications/<project-slug>/`:
1. Register the sub-project in `/home/antigravity/replications/INDEX.md`.
2. Generate `DECONSTRUCTION.md`, `RESEARCH_SYNTHESIS.md` (researching external options, trade-offs, and well-rounded opinions for every `[UNSPECIFIED - Verify before starting]` gap and "Off-Camera" trap), `REPLICATION_BLUEPRINT.md`, and `AGENT_INSTRUCTIONS.md`.
3. Execute `AGENT_INSTRUCTIONS.md` end-to-end inside `/home/antigravity/replications/<project-slug>/` and verify all automated tests pass.
4. Confirm satisfaction in `VERIFICATION_REPORT.md` across all 5 Objective Satisfaction Gate Checks.
5. Generate `STEP_BY_STEP_TUTORIAL.md` as the final step after satisfaction is verified, and mark the project `COMPLETED` in `/home/antigravity/replications/INDEX.md`.
```

# Stage 1.4: Standalone Agent Execution Instructions (`{{PROJECT_ID}}-{{SLUG}}`)

> **Stage 2 Handoff Command**:
> Once this plan is approved (`python3 scripts/yt_queue.py approve {{PROJECT_ID}}`), the active builder agent claims this project via `python3 scripts/yt_queue.py start-next` and executes the instructions below inside `replications/{{PROJECT_ID}}-{{SLUG}}/`.

---

## 1. Sub-Project Context & Approved Inputs
- **Project ID**: `{{PROJECT_ID}}`
- **Sub-Project Workspace**: `replications/{{PROJECT_ID}}-{{SLUG}}/`
- **Target Video**: {{YOUTUBE_URL}}
- **Stage 1.1 Deconstruction**: [`DECONSTRUCTION.md`](DECONSTRUCTION.md)
- **Stage 1.2 Research Synthesis**: [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md)
- **Stage 1.3 Approved Blueprint**: [`REPLICATION_BLUEPRINT.md`](REPLICATION_BLUEPRINT.md)

---

## 2. Builder Agent Execution Checklist (Stage 2)
1. **Single-Active-Project Lock**: Ensure `python3 scripts/yt_queue.py start-next` has marked `{{PROJECT_ID}}` as `STAGE_2_IN_PROGRESS`. Never work on more than one sub-project at a time.
2. **Execute [`REPLICATION_BLUEPRINT.md`](REPLICATION_BLUEPRINT.md) & [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md)**:
   - Implement all source code in `src/`, configs in `configs/`, data in `data/`, tests in `tests/`, and outputs in `artifacts/`.
   - Implement the approved research recommendations for every `[UNSPECIFIED - Verify before starting]` parameter and "Off-Camera" trap.
3. **Mandatory Satisfaction Gate (`VERIFICATION_REPORT.md`)**:
   - Run all automated tests (`unittest` / verification CLI) and write `VERIFICATION_REPORT.md`.
   - Run `python3 scripts/yt_queue.py mark-verified {{PROJECT_ID}}`.
   - Confirm with the user that the replication is **satisfactory** (or pass all 5 Objective Satisfaction Gate Checks in unattended mode) **before** creating `STEP_BY_STEP_TUTORIAL.md`.
4. **Final Step (`STEP_BY_STEP_TUTORIAL.md`)**:
   - Once satisfaction is confirmed, generate `STEP_BY_STEP_TUTORIAL.md` as the final step, dry-run every command in the tutorial, and run `python3 scripts/yt_queue.py complete {{PROJECT_ID}}`.

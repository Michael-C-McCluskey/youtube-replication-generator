# Stage 1.4: Standalone Agent Execution Instructions (`{{PROJECT_ID}}-{{SLUG}}`)

> **Stage 2 Handoff Command**:
> Once this plan is approved (`python3 scripts/yt_queue.py approve {{PROJECT_ID}}`), the active builder agent claims this project via `python3 scripts/yt_queue.py start-next` (or `--resume` after a crash) and executes the instructions below for `replications/{{PROJECT_ID}}-{{SLUG}}/`.

---

## 0. User Prompt, Pinned Versions & Execution Mode
- **User Prompt / Intent**: {{USER_INTENT}}
- **Pinned Generator Version**: `v{{GENERATOR_VERSION}}`
- **Pinned Plan Version**: `v{{PLAN_VERSION}}`
- **Execution Mode**: `UNATTENDED` *(default for autonomous Stage 2 execution; only pause at the final Satisfaction Gate in `INTERACTIVE` sessions)*
- **Repo-Root Command Rule**: Always run `yt_queue.py` and `yt_evolve.py` from the repository root (or pass `--root <repo_root>`, e.g., `python3 ../../scripts/yt_queue.py --root ../.. <cmd>` when inside `replications/{{PROJECT_ID}}-{{SLUG}}/`).

---

## 1. Sub-Project Context & Approved Inputs
- **Project ID**: `{{PROJECT_ID}}`
- **Sub-Project Workspace**: `replications/{{PROJECT_ID}}-{{SLUG}}/`
- **Target Video**: {{YOUTUBE_URL}}
- **Stage 1.1 Deconstruction**: [`DECONSTRUCTION.md`](DECONSTRUCTION.md)
- **Stage 1.2 Research Synthesis**: [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md)
- **Stage 1.3A User Spin & Customization**: [`CUSTOMIZATION_BRIEF.md`](CUSTOMIZATION_BRIEF.md)
- **Stage 1.3B Approved Blueprint**: [`REPLICATION_BLUEPRINT.md`](REPLICATION_BLUEPRINT.md)

---

## 2. Autonomous Fallbacks (Zero-HITL During Stage 2)
1. **Default Spin Fallback**: If any row in `CUSTOMIZATION_BRIEF.md` says `*Keep default*` or is unspecified, execute the Pre-Filled Smart Default (or the video's `[VIDEO_EXAMPLE]` + `[PATTERN]`) without stopping to ask the user.
2. **BOM Mock-Adapter Fallback**: Never halt waiting for paid API keys or cloud credentials. Read `.env` if present; otherwise run the deterministic local mock/fixture defined in `docs/feasibility-rubric.md` and `RESEARCH_SYNTHESIS.md`.

---

## 3. Builder Agent Execution Checklist (Stage 2)
1. **Single-Active-Project Lock**: Ensure `python3 scripts/yt_queue.py start-next` (or `start-next --resume`) has marked `{{PROJECT_ID}}` as `STAGE_2_IN_PROGRESS`. Never work on more than one sub-project at a time.
2. **Execute [`REPLICATION_BLUEPRINT.md`](REPLICATION_BLUEPRINT.md) & [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md)**:
   - Implement all source code in `src/`, configs in `configs/`, data in `data/`, tests in `tests/`, and outputs in `artifacts/`.
   - Implement the approved research recommendations (and fallback triggers if needed) for every `[UNSPECIFIED - Verify before starting]` parameter and "Off-Camera" trap.
3. **Mandatory Satisfaction Gate (`VERIFICATION_REPORT.md`)**:
   - Run all automated tests (`python3 -m unittest discover -s tests -v`) and write `VERIFICATION_REPORT.md` using the 4-Dimension Parity Audit (`docs/parity-comparison-protocol.md`).
   - Run `python3 scripts/yt_queue.py mark-verified {{PROJECT_ID}} --strict`.
   - **5 Objective Satisfaction Gate Checks** (must all pass in `UNATTENDED` mode; confirm with user in `INTERACTIVE` mode before writing the tutorial):
     1. All automated unit/integration tests in `tests/` exit with code `0`.
     2. Every `[UNSPECIFIED - Verify before starting]` parameter in `DECONSTRUCTION.md` is resolved and traced to a file/line in `VERIFICATION_REPORT.md`.
     3. Every "Off-Camera" trap in `REPLICATION_BLUEPRINT.md` has a verified mitigation in code/tests.
     4. Weighted 4-dimension parity score `>= 85` (Pattern `>= 90`, User-Spin `>= 90`, UX `>= 80`, Data `>= 85`).
     5. Clean-room dry-run of all commands in `STEP_BY_STEP_TUTORIAL.md` succeeds from `replications/{{PROJECT_ID}}-{{SLUG}}/`.
4. **Final Step (`STEP_BY_STEP_TUTORIAL.md` + `RETROSPECTIVE.md`)**:
   - Once satisfaction is confirmed, generate `STEP_BY_STEP_TUTORIAL.md` as the final deliverable, dry-run every command in it, complete `RETROSPECTIVE.md`, record reusable lessons via `python3 scripts/yt_evolve.py record-lesson ...`, and run `python3 scripts/yt_queue.py complete {{PROJECT_ID}} --strict`.

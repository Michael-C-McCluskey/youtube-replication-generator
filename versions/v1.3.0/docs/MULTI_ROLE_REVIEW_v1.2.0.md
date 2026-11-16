# Multi-Role Architecture & Quality Review (`v1.2.0` -> `v1.3.0`)

**Date**: 2026-11-16
**Reviewed Version**: `v1.2.0`
**Review Panel**:
1. **Intent & UX Architect** (`intent-architect`) — Zero-nagging intent inference, minimal-prompt UX, Stage 1 Decision Card, single-turn approval.
2. **Research & Synthesis Lead** (`research-lead`) — Multi-tier ingestion, source provenance & confidence scoring, gap-to-blueprint traceability, autonomous fallback paths.
3. **Autonomous Agent Systems Engineer** (`agent-engineer`) — Zero-HITL Stage 2 execution, concurrency/locking, crash recovery, cross-LLM entrypoint alignment.
4. **QA & Evolution Auditor** (`qa-auditor`) — Content-aware gate linting, Tier 4 hard-stop enforcement, 4-dimension parity audit, self-evolution loop & version isolation.

---

## 1. Consensus Strengths of `v1.2.0`

Across all four roles, the following architectural foundations were rated strong and worth preserving:

1. **Strict Two-Stage State Machine & Single-Active-Project Lock (`max_concurrent_active = 1`)**: Clean separation between unlimited parallel Stage 1 planning (`STAGE_1_PLANNING` -> `PLANNED_AWAITING_APPROVAL` -> `APPROVED_QUEUED`) and serialized Stage 2 execution (`STAGE_2_IN_PROGRESS` -> `SATISFACTION_GATE` -> `COMPLETED`) in [`scripts/yt_queue.py`](file:///home/antigravity/youtube-replication-generator/scripts/yt_queue.py).
2. **Immutable Plan Snapshots & Generator Version Pinning**: `PLAN_MANIFEST.json`, `plans/v<N>/` snapshots, and `versions/v<X.Y.Z>/` archives protect in-progress builds from global generator upgrades.
3. **Structured Gap-Closing & `[MECHANIC]`/`[AESTHETIC]` + `[PATTERN]`/`[SPIN_LEVER]` Separation**: Explicit `[UNSPECIFIED - Verify before starting]` tagging in `DECONSTRUCTION.md`, 2–3 option trade-off analysis in `RESEARCH_SYNTHESIS.md`, and `[SPIN_LEVER]` protection during parity audits prevent silent guessing and preserve user customization.
4. **Closed-Loop Self-Evolution Foundation**: `evolution/LESSONS_LEARNED.json`, `evolution/EVOLUTION_LOG.md`, and `scripts/yt_evolve.py` provide persistent cross-project learning.

---

## 2. Critical Gaps Identified (Prioritized Across All 4 Roles)

### P0 — Intent & UX Friction (Why Agents Still Over-Ask or Lose Intent)
- **No Zero-Nagging Intent Inference Rule**: Agents could pause during Stage 1 to ask clarifying questions instead of inferring `Exact Replica | Adapted Spin | Scoped Vertical Slice` and pre-filling smart defaults.
- **Unpersisted `user_intent`**: `yt_queue.py add` did not capture `--intent`, so `DECONSTRUCTION.md` and `AGENT_INSTRUCTIONS.md` could lose the original user prompt.
- **Blank `...` Placeholders in `CUSTOMIZATION_BRIEF.template.md`**: Left Stage 2 agents unsure whether to stop or proceed when the user only typed `"OK"`.
- **Two-Step Queue Approval Friction**: Case B (`approve`) and Case C (`start-next`) forced an unnecessary extra turn when the queue was idle, instead of offering a **1-Screen Stage 1 Decision Card** where a single `"OK"` approves and immediately starts Stage 2 if idle.

### P0 — Autonomous Stage 2 Execution Traps (Why External Agents Halt Mid-Build)
- **Undefined "5 Objective Satisfaction Gate Checks"**: `AGENTS.md` and `AGENT_INSTRUCTIONS.template.md` referenced *"5 Objective Satisfaction Gate Checks in unattended mode"* without ever defining them.
- **Working-Directory Path Ambiguity**: `AGENT_INSTRUCTIONS.template.md` told agents to work inside `replications/<NNN>-<slug>/` while running relative `python3 scripts/yt_queue.py ...` commands (which fail unless run from repo root or given `--root`).
- **Missing BOM Mock-Adapter & Default Spin Fallbacks**: Stage 2 agents lacked explicit instructions to fall back to `.env` -> deterministic local mock (or `VIDEO_EXAMPLE` + `PATTERN` if `CUSTOMIZATION_BRIEF.md` was left at defaults) instead of halting for human input.
- **Cross-Document Drift**: `SKILL.md`, `docs/parity-comparison-protocol.md`, `docs/feasibility-rubric.md`, and `replications/001-.../AGENT_INSTRUCTIONS.md` contained stale paths (`projects/<slug>/`, `.agents/skills/copycat-builder/...`) and conflicting 3-vs-4 archetype taxonomies.

### P0 — Toothless Verification & Plan-Quality Gates
- **50-Byte Size Check Bypass**: `_verify_stage_1_files()`, `mark_verified()`, and `complete_project()` only checked `st_size >= 50`. Completely unfilled templates with `{{...}}` tokens, `...` placeholders, `Tier 4` Hard Stops, unchecked `- [ ]` boxes, or failing parity scores (`< 85`) passed every gate.
- **`VERIFICATION_REPORT.template.md` Not Scaffolded**: `add_project()` omitted `VERIFICATION_REPORT.template.md` from `template_map`.

### P1 — Research Provenance, Fallback Paths, & State-Machine Hardening
- **Missing Provenance & Confidence in `RESEARCH_SYNTHESIS.template.md`**: No required source URLs, SDK/doc dates, confidence ratings (`High | Medium | Low`), or autonomous fallback triggers (`Adopt Option B; if <trigger>, fall back to Option A`), plus a duplicate `## 3.` heading.
- **`yt_queue.py` Concurrency & Crash Recovery**:
  - Needed `fcntl.flock` locking + atomic temp-file `os.replace()` for `QUEUE.json`.
  - `len(projects) + 1` ID allocation risked collisions if any project was removed.
  - Missing `active`, `pause`, and `start-next --resume` for crash recovery.
  - Duplicate `plan_version=1` entries in `PLAN_MANIFEST.json`.
- **Self-Evolution Loop & Version Isolation**:
  - `add_project()` defaulted `archetype="TBD (Classify in Stage 1.1)"`, causing *all* lessons to be injected indiscriminately; no `refresh-lessons` / `sync-lessons` hook existed after Stage 1.1 classification.
  - `yt_evolve.py record-lesson` lacked `confidence`, `evidence`, `tags`, `status`, category validation, and safe ID allocation; `query_lessons` lacked ranked matching and `--category` / `--min-confidence` / `--limit`.
  - `yt_evolve.py bump-version` did not validate monotonic semver (`new > old`) and did not archive `scripts/` or `evolution/LESSONS_LEARNED.json`.

---

## 3. `v1.3.0` Action Plan Implemented

| Area | Concrete Deliverables |
| :--- | :--- |
| **Intent & UX** | Operating Rule #7 (Zero-Nagging Intent Inference), 1-Screen Stage 1 Decision Card, single-turn `OK` -> `approve` + `start-next` when idle, `--intent` flag on `yt_queue.py add`, `CUSTOMIZATION_BRIEF.md` in `STAGE_1_REQUIRED_FILES`, Pre-Filled Defaults & Override Table. |
| **Research & Synthesis** | Fixed duplicate `## 3.` heading, added Sources/Recency/Confidence/Fallback Trigger per `Gap #N`, `<!-- LESSONS:START/END -->` markers, `Blocker Type` & `Seed Queries` in `DECONSTRUCTION.template.md`, `Fallback` & `Off-Camera Traps` table in `REPLICATION_BLUEPRINT.template.md`. |
| **Autonomous Stage 2** | Defined the **5 Objective Satisfaction Gate Checks**, repo-root `--root` / path rules, Execution Mode (`INTERACTIVE` vs. `UNATTENDED`), Default Spin & BOM Mock-Adapter Fallbacks in `AGENT_INSTRUCTIONS.template.md` and `AGENTS.md`, plus `RETROSPECTIVE.md` + `record-lesson` integration. |
| **Queue & Evolution Hardening** | `fcntl.flock` + atomic writes, safe max-ID allocation, `active` / `pause` / `start-next --resume` / `lint-plan` / `sync-lessons` in `yt_queue.py`, content-aware Stage 1 & Stage 2 gate linting (placeholders, `Tier 4` block, parity score floors, checkboxes, retrospective check), `PLAN_MANIFEST.json` deduplication, `VERIFICATION_REPORT.template.md` scaffolding, `yt_evolve.py` monotonic semver + `scripts/` & `evolution/` snapshotting + `refresh-lessons` + ranked `query`. |
| **Docs & Tests** | Unified 4-archetype taxonomy and repo paths across `SKILL.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `README.md`, `docs/feasibility-rubric.md`, `docs/parity-comparison-protocol.md`; expanded `tests/` with gate-linting, crash-recovery, and multimodal script tests. |

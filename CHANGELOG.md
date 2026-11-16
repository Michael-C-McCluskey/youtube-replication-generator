# Generator Changelog

All notable evolutions to **`youtube-replication-generator`** (templates, playbooks, queue rules, and learned patterns) are recorded here. Each release is archived immutably under `versions/v<X.Y.Z>/` so in-progress sub-projects pinned to older versions never break.

---

## [1.2.0] - 2026-11-16
### Evolved From `v1.1.0`
- Merged CopyCat Builder multimodal keyframe scripts, 4-Tier Feasibility Gate, Stage 0.5 Multi-Project Triage (--slice), User Spin Customization Brief, and Stage 5 Parity Audit Protocol
- Immutable snapshot archived at `versions/v1.2.0/`. Existing in-progress sub-projects remain safely pinned to their original `generator_version`.

## [1.1.0] - 2026-11-16
### Added
- **Self-Evolving Learning & Retrospective Engine (`evolution/` + `scripts/yt_evolve.py`)**:
  - Added `evolution/LESSONS_LEARNED.json` and `evolution/EVOLUTION_LOG.md`, seeded with 3 verified lessons from `001-ai-niche-directory-side-hustle`.
  - Added `templates/RETROSPECTIVE.template.md` so every completed project captures new traps, parameter formulas, and template improvements.
  - Added `scripts/yt_evolve.py` (`record-lesson`, `query`, `bump-version`) so Stage 1 automatically inherits past lessons for the target archetype.
- **Immutable Plan & Generator Versioning (`versions/` + `plans/vN/` + `QUEUE.json` Pinning)**:
  - Archived `v1.0.0` under `versions/v1.0.0/` and `v1.1.0` under `versions/v1.1.0/`.
  - `scripts/yt_queue.py` now pins `generator_version` and `plan_version` per sub-project in `QUEUE.json` and `PLAN_MANIFEST.json`, snapshots plans into `replications/<NNN>-<slug>/plans/v1/`, and supports `revise-plan` without overwriting prior versions.

## [1.0.0] - 2026-11-16
### Added
- Initial release of the Two-Stage YouTube Replication Project Generator (`yt_queue.py`), Deep Gap-Closing Research stage (`RESEARCH_SYNTHESIS.md`), Single-Active-Project Lock (`max_concurrent_active = 1`), cross-LLM entrypoints (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `SKILL.md`), and reference project `001-ai-niche-directory-side-hustle`.

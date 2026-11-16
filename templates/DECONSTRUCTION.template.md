# Stage 1.1: Video Ingestion & Noise-Filtered Deconstruction (`{{PROJECT_ID}}-{{SLUG}}`)

- **Project ID**: `{{PROJECT_ID}}`
- **Sub-Project Folder**: `replications/{{PROJECT_ID}}-{{SLUG}}/`
- **Target Video URL**: {{YOUTUBE_URL}}
- **Video ID**: `{{VIDEO_ID}}`
- **Timestamp Slice**: `{{TIMESTAMP_SLICE}}`
- **Title**: {{TITLE}}

---

## 0. User Prompt & Inferred Intent
- **Raw User Request / Intent**: {{USER_INTENT}}
- **Inferred Execution Mode**: `Exact Replica` | `Adapted Spin` | `Scoped Vertical Slice` *(inferred from prompt without nagging; override in `CUSTOMIZATION_BRIEF.md`)*

---

## 1. Multi-Tier Ingestion Summary
- **Ingestion Status**: Tier 1 (`OK` / `Blocked` / `Skipped`) | Tier 2 (`URLs found`) | Tier 3 (`Claims audited`)
- **Tier 1 (Direct CLI & Visual Keyframes)**: Run `python3 scripts/extract_video_bundle.py "{{YOUTUBE_URL}}"` and `python3 scripts/extract_keyframes.py` when network/tools permit.
- **Tier 2 (Web Ecosystem & Companion Repo Search)**: Document external writeups, companion GitHub repos, or transcript summaries.
- **Tier 3 (Discrepancy & Off-Camera Audit)**: Document fact-checks on spoken claims/math.

---

## 2. Noise Filter Table (Strict Operating Rule #1)

| Segment / Timestamp | Content in Video | Classification | Action Taken |
| :--- | :--- | :--- | :--- |
| `00:00–00:45` | Intro, sponsor read, channel plug | `[NOISE]` | Stripped from blueprint |
| `00:45–...` | Core technical/creative execution | `[SIGNAL]` | Retained & decomposed |

---

## 3. Chronological Timeline of Stages
- **[00:45–...] Stage 1**: ...
- **[...–...] Stage 2**: ...

---

## 4. Knowledge Gap Inventory (`[UNSPECIFIED - Verify before starting]`)

| Gap ID | Timestamp | Parameter / Step Skipped in Video | Blocker Type | Seed Search Queries / Companion Repos | Why It Matters for Replication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gap #1** | `[MM:SS]` | `[UNSPECIFIED - Verify before starting]` ... | `Hard Spec` \| `Soft Heuristic` | `"<tool/library>" <param> docs` | Must be researched in `RESEARCH_SYNTHESIS.md` |

---

## 5. "Off-Camera" Traps Identified
1. **Trap #1**: ...
2. **Trap #2**: ...
3. **Trap #3**: ...

---

## 6. 4-Tier Feasibility & Replicability Verdict (`docs/feasibility-rubric.md`)
- **Archetype**: `Archetype A (Algorithmic / Scientific / OSINT)` | `Archetype B (Multi-Tool AI / Business)` | `Archetype C (Software / DevOps Build)` | `Archetype D (Creative / GUI / Physical-Digital)`
- **Hard vs. Soft Blockers**: ...
- **Verdict**: `Tier 1 (Direct Replica)` | `Tier 2 (Functional Equivalent)` | `Tier 3 (Scoped Vertical Slice)` | `Tier 4 (Non-Replicable Hard Stop)`

---

## 7. Golden Keyframes (`GK-01..GK-N`) for Stage 2 Parity Audit

| Keyframe ID | Timestamp | Expected State / Output |
| :--- | :--- | :--- |
| `GK-01` | `[MM:SS]` | ... |

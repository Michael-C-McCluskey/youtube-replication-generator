# Stage 1 Reference: Feasibility & Replicability Rubric

Use this rubric during **Stage 1.1** (`DECONSTRUCTION.md`) after completing Stage 0 signal extraction (`scripts/extract_video_bundle.py` and `scripts/extract_keyframes.py`) to determine whether a YouTube project can be replicated and at what fidelity tier.

---

## 1. Project Overview & Bottleneck Profile

Every `replications/<NNN>-<slug>/DECONSTRUCTION.md` and `REPLICATION_BLUEPRINT.md` must establish:
1. **Core Concept**: 1–2 crisp sentences explaining what is being built and the core technical/creative mechanism.
2. **Skill Level & Single Hardest Technical Bottleneck**: Identify the single hardest step or failure-prone piece in the entire project (e.g., WebGL shader coordinate mapping, OAuth callback state sync, real-time SSE streaming parser, physics collision stability).
3. **Estimated Time Split**:
   - **Active Working / Build Time**: Engineering, coding, configuration, and debugging effort.
   - **Passive / Compute Time**: Dependency installation (`npm install`/`pip`), container builds, model weight downloads, vector indexing, or rendering/baking.

---

## 2. Project Archetype Classifier (Unified 4-Archetype Taxonomy)

Assign one **Primary Archetype** (matching [`docs/archetype-playbooks.md`](archetype-playbooks.md) and [`SKILL.md`](../SKILL.md)), then run `python3 scripts/yt_queue.py sync-lessons <NNN> --archetype "<Archetype>"`:

| Archetype | Typical Examples | Primary Runtime Target |
| :--- | :--- | :--- |
| **Archetype A: Algorithmic / Scientific / OSINT** | Signal processing, Doppler/RF localization, quantitative finance, geospatial pipelines, data science | Python / NumPy / SciPy CLI & reproducible notebooks |
| **Archetype B: Multi-Tool AI / Creative / Business** | AI directories, RAG/agent pipelines, multi-API SaaS workflows, automated content/lead engines | Python / Node.js services + local JSON/SQLite + mock/live adapters |
| **Archetype C: Software / DevOps Build** | Next.js/React/Vite dashboards, FastAPI/Express CRUD apps, browser extensions, CI/CD & CLI tools | Browser (`localhost:PORT`) + Terminal / API server |
| **Archetype D: Creative / GUI / Physical-Digital** | HTML5 Canvas/WebGL/Three.js/P5.js sketches, shaders, 2D/3D browser games, Pygame simulations | Browser Canvas/WebGL or Desktop Window (`Pygame`) |

---

## 3. Hard Blockers vs. Soft Blockers Audit

### Hard Blockers (Potential Tier 4 Stop)
- **Physical Hardware Dependency**: Requires non-simulated sensors, Arduino/Raspberry Pi GPIO hardware, VR/custom peripherals, or proprietary physical rigs.
- **Opaque Proprietary Core**: The video demos a black-box SaaS/internal system whose core algorithm, weights, or database logic is never shown and cannot be reasonably reconstructed from observable behavior.
- **Inaccessible Private Training Data**: Project value depends strictly on an unreleased dataset or private model checkpoint.
- **CGI / Concept Mockup**: Video is an After Effects/Blender UI concept animation rather than functioning software (look for impossible frame-perfect timings, missing cursors, or unbuildable interactions).

### Soft Blockers (Solvable via BOM Substitutions -> Tier 2)
- Paid APIs (OpenAI, Anthropic, ElevenLabs, Stripe, Twilio, Google Maps).
- Hosted databases or managed auth (Supabase, Firebase, Auth0, Clerk, PlanetScale).
- Paid stock photos, custom 3D models, or commercial sound effects.
- Production hosting features (custom domains, CDN edge caching, email delivery).

---

## 4. Bill of Materials (BOM) & Tool Substitutions Guide

Every observed framework, library, API, runtime, and media asset must be entered into the **BOM Table** in `REPLICATION_BLUEPRINT.md`:

`| Item / Software | Exact Spec / Setting Used | Purpose in Project | Accessible Alternative | Fallback / Degraded Mode |`

If any exact spec, library version, or parameter is omitted by the video, tag it `[UNSPECIFIED - Verify before starting]` rather than guessing silently.

### Standard Dependency Substitution Matrix

| Observed Dependency | Local Accessible Alternative | Parity Preservation Rule |
| :--- | :--- | :--- |
| **Paid LLM / Vision / TTS API** | Configurable adapter: read real `.env` API key if present, otherwise run deterministic local mock/replay mode | Mock must emit the exact JSON schema, markdown structure, and streaming chunk cadence observed in the video. |
| **Cloud Auth (Clerk, Auth0, Supabase Auth)** | Local dev session provider + one-click demo user switcher | Keep the same user object shape (`id`, `name`, `avatar`, `role`) and protected route middleware semantics. |
| **Hosted Postgres / Vector DB** | Local SQLite / JSON store / in-process vector index (or FAISS/Chroma local) | Auto-seed demo rows on boot so initial views match video keyframes. |
| **Paid Webhooks (Stripe, Slack, Resend)** | Local webhook simulator endpoint + simulated event log UI | Trigger identical UI/DB state transitions locally. |
| **Proprietary Images / Audio / 3D Assets** | Procedural SVG/Canvas graphics, `generate_image`, or deterministic local fixtures | Match aspect ratios, palette, and layout bounds of the original asset. |

---

## 5. Four-Tier Replicability Verdict Criteria

| Verdict | Criteria | Required Action |
| :--- | :--- | :--- |
| **Tier 1 — Direct Replica** | 100% of core logic, stack, and assets can run locally with zero functional substitutions. | Proceed to Stage 1.2 & Stage 2. |
| **Tier 2 — Functional Equivalent** | Core UX and behavior are fully replicable locally using documented BOM Substitutions (e.g., local DB + mock LLM adapter). | Proceed to Stage 1.2; highlight BOM substitutions on the Stage 1 Decision Card. |
| **Tier 3 — Scoped Vertical Slice** | Video covers a vast multi-module product or multi-part series; only the primary demonstrated user journey is practical within scope. | Define strict In-Scope vs. Out-of-Scope boundaries in `DECONSTRUCTION.md`; obtain `"OK"` on the Stage 1 Decision Card. |
| **Tier 4 — Non-Replicable (Hard Stop)** | Blocked by physical hardware, non-inferable proprietary black boxes, or fake CGI concept renders. | **STOP immediately.** Present exact `[MM:SS]` blockers and propose 1–2 closest viable Tier 2/3 software alternatives. (`yt_queue.py` blocks `mark-planned`/`approve` for Tier 4 unless `--force-archive`.) |

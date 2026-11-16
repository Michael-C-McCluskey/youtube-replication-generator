# Video Archetype Playbooks & Bill of Materials Substitutions

When reverse-engineering and replicating a YouTube video, classify it into one of these four archetypes (or a hybrid) during **Phase 2 (`REPLICATION_BLUEPRINT.md`)**. Use the corresponding playbook to design your **Bill of Materials & Tool Substitutions**, separate **`[MECHANIC]`** from **`[AESTHETIC]`**, resolve **`[UNSPECIFIED - Verify before starting]`** parameters, and pre-empt **"Off-Camera" Traps**.

---

## Archetype A: Algorithmic, Scientific, or OSINT Concept Demo
*Example: Colsto's "I discovered a sound that leaks your exact location (and it's everywhere)" (`UytYrhYLOKI`)*

### Characteristics
- Long-form conceptual narrative explaining physics, mathematics, signal processing, machine learning, or security/OSINT techniques.
- Rarely shows line-by-line installation commands on screen; instead shows visualizations (spectrograms, heatmaps, graphs) and high-level pipeline stages.

### Replication Playbook
1. **Companion Repo Discovery First**:
   - Search GitHub (`gh search repos`, `gh search code`) and technical blogs (`google_search`) for the video ID, title, or core algorithm name. Viral technical demos frequently have open-source implementations released by the creator or community within days (e.g., `digitalis-p/doppler-locate`, `dopplerprint`).
2. **Mathematical & Stage Decomposition**:
   - Break the concept into discrete data-processing stages (e.g., `Audio Extraction -> Spectrogram -> Matched Filter -> Curve Fit -> External Archive Matching -> Heatmap`).
   - Tag core mathematical transformations and filter thresholds as `[MECHANIC]`, and visualization styling or sample clip choice as `[AESTHETIC]`.
3. **Bill of Materials Substitutions**:
   - **CUDA / GPU Kernels** -> Substitute with CPU fallbacks (`numba`, `scipy`, `numpy`, `onnxruntime` CPU) under `[LOCAL-ADAPTED]`.
   - **Multi-Gigabyte External Archives** (e.g., 3.5 GB/day ADS-B archives, CommonCrawl shards) -> Run the local detection/compute stages in full (`[LOCAL-FULL]`), and substitute the massive archive stage with a bounded regional/time sample or included `cases/` fixture (`[LOCAL-ADAPTED]`), while documenting the full-scale fetch command in the tutorial.

### Typical "Off-Camera" Traps
- **Signal/Data Noise Rejection**: Real-world recordings contain confounding signals (e.g., road vehicles `< 150 m` or `< 30 m/s` mimicking aircraft Doppler curves).
- **Compression Artifacts**: YouTube's Opus/AAC audio compression or H.264 video compression degrades high-frequency features compared to raw studio files.

---

## Archetype B: Multi-Tool AI, Creative, or Digital Business Workflow
*Example: "I Tried The LAZIEST Way to Make Money With AI" (`LlhTEttKcwQ`)*

### Characteristics
- Multi-step challenge or operational pipeline chaining LLMs (Claude, ChatGPT), media generators (Higgsfield, Midjourney, ElevenLabs), video editors (Cinema Studio, CapCut), social platforms (Instagram, TikTok), and digital storefronts (Stan Store, Gumroad).

### Replication Playbook
1. **Separate `[MECHANIC]` from `[AESTHETIC]`**:
   - `[MECHANIC]`: Multi-niche testing framework, prompt/skill architecture, hook-body-CTA script structure, `9:16` `1080x1920` vertical video specs, and interactive outcome-driven digital product structure (e.g., a 30-day habit tracker workbook with daily rules and checkboxes instead of a passive ebook).
   - `[AESTHETIC]`: Specific character personas (*Amos*, *Grandma Vivienna*, *Sienna*), niche aesthetics, and brand colors.
2. **Bill of Materials Substitutions**:
   - **Proprietary LLM Skills / Connectors** -> Build local, version-controlled Markdown prompt templates and automation scripts (`[LOCAL-FULL]`).
   - **Paid Avatar / Image SaaS (e.g., Higgsfield)** -> Generate real reference character/scene images using Antigravity's `generate_image` tool (`[LOCAL-ADAPTED]`) AND provide the exact copy-paste prompt pack for the external tool.
   - **GUI Video Editors (Cinema Studio / CapCut)** -> Build an automated `ffmpeg` vertical video assembly script (`1080x1920`, `9:16`, audio muxing + burned-in captions) (`[LOCAL-ADAPTED]`).
   - **Digital Product Offer** -> Build the complete, interactive HTML + print-ready PDF product locally (`[LOCAL-FULL]`).
   - **Social Posting & Storefront Checkout (Instagram, Stan Store, PayPal)** -> Package a turnkey Launch Kit (bio copy, 10-post schedule, pricing tiers, storefront description) under `[HITL-PACKAGED]`.

### Typical "Off-Camera" Traps
- **Prompt Iteration & Age/Style Realism**: Creators only show the winning image after 10+ failed generations (e.g., AI rendering a "101-year-old elder" as a glossy 50-year-old unless explicit skin texture and lighting constraints are added).
- **Spoken Arithmetic / Revenue Inconsistencies**: Auto-captions and creator storytelling often contain math errors; always audit unit economics independently.

---

## Archetype C: Software Engineering, Web App, or DevOps Build

### Characteristics
- Step-by-step coding, architecture, or infrastructure tutorial.

### Replication Playbook
1. **Flag `[UNSPECIFIED]` Versions & Env Vars**: Creators often hide `.env` files, `tsconfig.json`, or exact package versions. Tag them as `[UNSPECIFIED - Verify before starting]` and resolve compatible versions in `pyproject.toml` or `package.json`.
2. **Automated Verification**: Run unit tests, typechecks, builds, and headless checks before presenting the Satisfaction Gate.

---

## Archetype D: GUI, Node-Graph, or Creative Fabrication Walkthrough

### Characteristics
- Heavy reliance on visual node graphs (ComfyUI, Blender Geometry Nodes, Unreal Blueprints) or studio/physical parameters.

### Replication Playbook
1. **Visual Keyframe Parameter Extraction**: Sample high-resolution keyframes (`ffmpeg`) whenever node inspector panels or parameter sliders are visible on screen.
2. **Declarative Export**: Represent the visual workflow as a declarative JSON/YAML/Python specification so users can import or run it without manually wiring dozens of nodes.

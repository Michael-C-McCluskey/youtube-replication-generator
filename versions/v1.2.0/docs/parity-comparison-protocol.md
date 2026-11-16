# Stage 5 Reference: Pattern Fidelity & User-Spin Verification Protocol

Use this protocol during **Stage 5** to empirically verify your running project in `projects/<project-slug>/` against:
1. The **core skills, processes, and patterns** (`[PATTERN]`) extracted in `video_reverse_spec.md`, and
2. The user's **custom spin & requirements** captured in `customization_brief.md`.

---

## 1. Pre-Audit Verification Gate

Before starting Stage 5 comparison:
1. All `STUB-01..STUB-N` unit/API/DOM tests and `M1 -> M4` build/typecheck checks pass inside the sandbox.
2. **Custom User-Spin Mode** executes end-to-end on fresh user inputs with zero hardcoded creator text (and the optional **Reference Example Preset** loads cleanly if included in `customization_brief.md`).
3. Zero unwired/dead buttons or console errors exist.

---

## 2. Staging Reference Keyframes (Web / Browser Games / Creative Coding)

Antigravity's `browser` subagent runs in an isolated sandbox and can only read reference images staged inside `<ArtifactDirectory>/browser_sandbox/references/` using single-segment filenames.

1. Run `python .agents/skills/copycat-builder/scripts/stage_golden_frames.py --frames-dir <ArtifactDirectory>/scratch/copycat/<project-slug>/frames --artifact-dir <ArtifactDirectory> --timestamps <MM:SS,MM:SS,...>` to copy the 5–10 Golden Keyframes into `<ArtifactDirectory>/browser_sandbox/references/` as `video_MM_SS.png` (for example, `video_00_32.png`, `video_04_18.png`).
2. Never place staged files inside the project workspace.

---

## 3. Executing the Empirical Comparison

### Path A: Web Apps, UIs & Browser Canvas / Games
1. **Start Local Server**: Launch the replica's dev or preview server (`BypassSandbox: true` on Windows so the `browser` subagent and user can reach `http://localhost:<PORT>`).
2. **Delegate to `browser` Subagent** (`Model: "flash"`):
   - Provide exact paths to the staged reference frames in `<ArtifactDirectory>/browser_sandbox/references/video_MM_SS.png`.
   - Instruct the subagent to:
     - Inspect each staged reference frame with `read_file`.
     - Open `http://localhost:<PORT>` at a desktop viewport matching the video (default `1280x720` or `1440x900`).
     - Drive the exact interactions mapped to `GK-01..GK-N` (clicks, inputs, toggles, keyboard controls for games/canvas).
     - Capture screenshots at each matching state (`replica_MM_SS.png`), record console/network errors, and report layout/styling/behavioral discrepancies.
3. **Host-Fact & Direct Vision Cross-Check**:
   - Verify every origin and screenshot claimed by the `browser` subagent against the hidden `BROWSER_HOST_FACTS` message.
   - Read both the Golden Keyframes (`video_MM_SS.png`) and the replica screenshots directly via `read_file` in the main agent before scoring!

### Path B: CLI Tools, Backend Services & AI/ML Pipelines
1. **Run Deterministic Trace Harness**: Execute the replica via `run_command` using the exact CLI flags, sample fixture inputs, or HTTP requests observed in `video_reverse_spec.md`.
   - For local HTTP APIs tested via `curl`/Python inside the sandbox, start the server, probe it, and stop it within the **same** `run_command` call.
2. **Capture & Diff Evidence**: Save stdout/stderr, ANSI table structure, JSON payloads, streaming cadence, and exit codes into `<ArtifactDirectory>/scratch/copycat/<project-slug>/cli_parity_trace.txt`.
3. **Visual Comparison**: Inspect terminal/API keyframes from the video via `read_file` side-by-side with captured trace output.

### Path C: Desktop Games / Simulations (e.g., Pygame)
1. Run deterministic simulation/headless state tests verifying tick loop, physics boundaries, scoring, and state transitions (`Title -> Play -> GameOver`) against `video_reverse_spec.md`.
2. Capture rendered surface frames to PNG at matching gameplay timestamps (`replica_MM_SS.png`) if headless/offscreen rendering is supported, and inspect side-by-side with `video_MM_SS.png` via `read_file`.

---

## 4. Quantitative 4-Dimension Verification Rubric (0–100)

Record results in `<ArtifactDirectory>/parity_audit_report.md` (following `templates/INSTRUCTION_BLUEPRINT_TEMPLATE.md`). Never penalize a project for intentionally differing from the video creator's demo text, branding, or styling where `customization_brief.md` requested a custom spin:

| Dimension | Weight | Evaluation Criteria | Pass Threshold |
| :--- | :--- | :--- | :--- |
| **1. Pattern & Process Fidelity** | **35%** | All core `[PATTERN]` skills, workflows, and architectural steps taught in the video execute faithfully end-to-end. | `>= 90` |
| **2. User-Spin & Customization Execution** | **35%** | Every custom domain, feature twist, and dynamic input from `customization_brief.md` works end-to-end with 0 dead buttons or hardcoded text. | `>= 90` |
| **3. UX, Polish & Adaptability** | **15%** | Clean, cohesive UI/CLI, transitions, and responsiveness tailored to the user's chosen aesthetic (or matching `GK` visuals if 1:1 visual clone was requested). | `>= 80` |
| **4. Data, Robustness & Teachability** | **15%** | Parameterized inputs, safe `.env`/fallback handling, clear pattern documentation, and valid outputs. | `>= 85` |
| **Weighted Overall Score** | **100%** | `0.35*Pattern + 0.35*UserSpin + 0.15*UX + 0.15*Data` | **`>= 85`** |

---

## 5. Bounded Delta Fix Loop (Max 2 Iterations)

1. **Audit Verdict**:
   - **PASS**: Weighted Overall `>= 85`, Pattern Fidelity `>= 90`, User-Spin Execution `>= 90`, UX `>= 80`, Data `>= 85`, and `0` critical pattern/spin failures.
   - **FAIL**: Any dimension below threshold or any critical `[PATTERN]` or `customization_brief.md` feature broken/missing.
2. **Delta Fix Cycle (Loops 1 & 2)**:
   - Log every discrepancy as `[DELTA-XX]` linked to its `GK-XX` and `REQ-XX` ID, noting whether it is `[MECHANICS]` or `[AESTHETICS]`.
   - Fix `[MECHANICS]` deltas before `[AESTHETICS]` deltas in `projects/<project-slug>/`.
   - Re-run affected builds/tests and re-audit the impacted Golden Keyframes.
3. **Hard Loop Cap**:
   - Execute **at most 2 Delta Fix Loops**. If thresholds still fall short after Loop 2 (e.g., due to an `[UNSPECIFIED]` creator parameter or Tier 2 mock boundary), stop looping and document every remaining gap transparently in `parity_audit_report.md` and `walkthrough.md`.

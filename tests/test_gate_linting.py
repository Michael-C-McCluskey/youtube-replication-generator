#!/usr/bin/env python3
"""
Unit tests for v1.3.0 strict gate linting, crash recovery, archetype lesson syncing,
monotonic semver enforcement, and safe ID/manifest handling.
"""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from yt_evolve import EvolutionError, EvolutionManager
from yt_queue import QueueError, ReplicationQueueManager


class TestGateLintingAndHardening(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="yt_gate_test_"))
        shutil.copytree(REPO_ROOT / "templates", self.temp_dir / "templates")
        shutil.copytree(REPO_ROOT / "docs", self.temp_dir / "docs")
        shutil.copytree(REPO_ROOT / "scripts", self.temp_dir / "scripts")
        (self.temp_dir / "VERSION").write_text("1.2.0\n", encoding="utf-8")
        (self.temp_dir / "CHANGELOG.md").write_text("# Changelog\n\n---\n\n", encoding="utf-8")
        self.evo = EvolutionManager(self.temp_dir)
        self.mgr = ReplicationQueueManager(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_intent_persistence_scaffolding_and_manifest_dedup(self):
        proj = self.mgr.add_project(
            "https://www.youtube.com/watch?v=UytYrhYLOKI",
            slug="doppler-test",
            title="Doppler Test",
            user_intent="Build an Adapted Spin for maritime AIS signals",
        )
        proj_dir = self.temp_dir / proj["folder"]
        self.assertEqual(proj["user_intent"], "Build an Adapted Spin for maritime AIS signals")
        self.assertTrue((proj_dir / "VERIFICATION_REPORT.md").exists())
        decon = (proj_dir / "DECONSTRUCTION.md").read_text(encoding="utf-8")
        self.assertIn("Build an Adapted Spin for maritime AIS signals", decon)
        agent_inst = (proj_dir / "AGENT_INSTRUCTIONS.md").read_text(encoding="utf-8")
        self.assertIn("v1.2.0", agent_inst)
        self.assertIn("5 Objective Satisfaction Gate Checks", agent_inst)

        self.mgr.mark_planned("001")
        manifest = json.loads((proj_dir / "PLAN_MANIFEST.json").read_text(encoding="utf-8"))
        v1_revs = [r for r in manifest["revisions"] if r["plan_version"] == 1]
        self.assertEqual(len(v1_revs), 1)
        self.assertEqual(v1_revs[0]["note"], "Stage 1 plan frozen for user review")

    def test_02_strict_stage1_linting_and_tier4_block(self):
        proj = self.mgr.add_project(
            "https://www.youtube.com/watch?v=UytYrhYLOKI",
            slug="lint-test",
            title="Lint Test",
        )
        proj_dir = self.temp_dir / proj["folder"]

        # Boilerplate templates fail strict mark-planned
        with self.assertRaises(QueueError) as ctx:
            self.mgr.mark_planned("001", strict=True)
        self.assertIn("placeholder", str(ctx.exception).lower())

        # Tier 4 verdict blocks even non-strict mark-planned unless force_archive=True
        decon_path = proj_dir / "DECONSTRUCTION.md"
        decon_path.write_text(
            "# Deconstruction\n- **Verdict**: Tier 4 (Non-Replicable Hard Stop)\nGap #1\n",
            encoding="utf-8",
        )
        with self.assertRaises(QueueError) as ctx4:
            self.mgr.mark_planned("001")
        self.assertIn("Tier 4", str(ctx4.exception))

        # Populate valid clean Stage 1 files -> strict mark-planned succeeds
        decon_path.write_text(
            "# Deconstruction\n- **Verdict**: Tier 2 (Functional Equivalent)\n| **Gap #1** | 01:00 | Threshold | Hard Spec | query | why |\n",
            encoding="utf-8",
        )
        (proj_dir / "RESEARCH_SYNTHESIS.md").write_text(
            "# Research\n<!-- LESSONS:START -->\n- None\n<!-- LESSONS:END -->\n### Gap #1 (01:00): Threshold\n- **Confidence**: High\n- **Informed Recommendation**: Adopt Option B.\n",
            encoding="utf-8",
        )
        (proj_dir / "CUSTOMIZATION_BRIEF.md").write_text(
            "# Customization\n| Spin | Default | Override |\n| Niche | Local | Keep default |\n",
            encoding="utf-8",
        )
        (proj_dir / "REPLICATION_BLUEPRINT.md").write_text(
            "# Blueprint\n- **[01:00] [MECHANIC] Step 1.1:** Build scorer.\n  - *Critical Parameter:* 0.65\n  - *Verification:* Test passes\n",
            encoding="utf-8",
        )
        (proj_dir / "AGENT_INSTRUCTIONS.md").write_text(
            "# Agent Instructions\nExecute Stage 2.\n" + ("x" * 60),
            encoding="utf-8",
        )
        planned = self.mgr.mark_planned("001", strict=True)
        self.assertEqual(planned["status"], "STAGE_1_AWAITING_OK")

    def test_03_strict_verification_and_retrospective_gates(self):
        proj = self.mgr.add_project(
            "https://www.youtube.com/watch?v=UytYrhYLOKI",
            slug="ver-test",
            title="Ver Test",
        )
        proj_dir = self.temp_dir / proj["folder"]
        self.mgr.mark_planned("001")
        self.mgr.approve_project("001")
        self.mgr.start_next()

        # Unchecked box + failing score blocked in strict mode
        (proj_dir / "VERIFICATION_REPORT.md").write_text(
            "# Report\n| **1. Pattern & Process Fidelity** | 35% | 75 | >= 90 | Low |\n- [ ] Unchecked item\n",
            encoding="utf-8",
        )
        with self.assertRaises(QueueError):
            self.mgr.mark_verified("001", strict=True)

        # Passing 4-dimension scores + all boxes checked
        (proj_dir / "VERIFICATION_REPORT.md").write_text(
            "# Report\n"
            "| **Pattern & Process Fidelity** | `35%` | `95` | `>= 90` | OK |\n"
            "| **User-Spin & Customization Execution** | `35%` | `92` | `>= 90` | OK |\n"
            "| **UX, Polish & Adaptability** | `15%` | `88` | `>= 80` | OK |\n"
            "| **Data, Robustness & Teachability** | `15%` | `90` | `>= 85` | OK |\n"
            "| **Weighted Overall Score** | `100%` | `92.1` | `>= 85` | OK |\n"
            "- [x] All commands exited 0.\n",
            encoding="utf-8",
        )
        verified = self.mgr.mark_verified("001", strict=True)
        self.assertEqual(verified["status"], "SATISFACTION_GATE")

        # Complete blocked while RETROSPECTIVE.md is untouched boilerplate
        (proj_dir / "STEP_BY_STEP_TUTORIAL.md").write_text(
            "# Tutorial\nStep 1: Run tests.\n" + ("y" * 60),
            encoding="utf-8",
        )
        with self.assertRaises(QueueError):
            self.mgr.complete_project("001", strict=True)

        (proj_dir / "RETROSPECTIVE.md").write_text(
            "# Retrospective\n- **Worked on first pass**: Automated tests and scorer.\n",
            encoding="utf-8",
        )
        completed = self.mgr.complete_project("001", strict=True)
        self.assertEqual(completed["status"], "COMPLETED")

    def test_04_crash_recovery_resume_pause_and_safe_ids(self):
        p1 = self.mgr.add_project("https://youtu.be/UytYrhYLOKI", slug="one")
        p2 = self.mgr.add_project("https://youtu.be/LlhTEttKcwQ", slug="two")
        self.mgr.mark_planned("001")
        self.mgr.approve_project("001")
        self.mgr.start_next("001")

        # start-next --resume returns active 001 without error
        resumed = self.mgr.start_next(resume=True)
        self.assertEqual(resumed["id"], "001")

        # pause returns 001 to APPROVED_QUEUED and releases active lock
        paused = self.mgr.pause_project("001")
        self.assertEqual(paused["status"], "APPROVED_QUEUED")
        self.assertIsNone(self.mgr.get_active_project(self.mgr.load_queue()))

        # Simulate removal of p1 from QUEUE.json -> next ID must be 003, not 002
        data = self.mgr.load_queue()
        data["projects"] = [p for p in data["projects"] if p["id"] != "001"]
        self.mgr.save_queue(data)
        p3 = self.mgr.add_project("https://youtu.be/NhqSuQPPvbg", slug="three")
        self.assertEqual(p3["id"], "003")

    def test_05_evolution_sync_lessons_and_monotonic_semver(self):
        self.evo.record_lesson(
            project="001-a",
            archetype="Archetype A",
            category="parameter-formula",
            title="Doppler shift window",
            problem="Missing FFT window size",
            solution="Use Hann window 4096.",
            confidence="high",
        )
        self.evo.record_lesson(
            project="002-b",
            archetype="Archetype B",
            category="bom-substitution",
            title="Local SQLite fallback",
            problem="Hosted DB unavailable",
            solution="Use SQLite with auto-seed.",
            confidence="medium",
        )
        # Invalid category raises EvolutionError
        with self.assertRaises(EvolutionError):
            self.evo.record_lesson(
                project="002-b",
                archetype="Archetype B",
                category="made-up-category",
                title="Bad",
                problem="p",
                solution="s",
            )

        proj = self.mgr.add_project("https://youtu.be/UytYrhYLOKI", slug="arch-a")
        res = self.mgr.sync_lessons("001", archetype="Archetype A")
        self.assertEqual(res["lessons_injected"], 1)
        research_md = (self.temp_dir / proj["folder"] / "RESEARCH_SYNTHESIS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Doppler shift window", research_md)
        self.assertNotIn("Local SQLite fallback", research_md)

        # Monotonic semver rejects downgrade or equal version
        with self.assertRaises(EvolutionError):
            self.evo.bump_version("1.2.0", summary="Same version")
        with self.assertRaises(EvolutionError):
            self.evo.bump_version("1.1.0", summary="Downgrade")

        bump = self.evo.bump_version("1.3.0", summary="Valid bump")
        self.assertEqual(bump["new_version"], "1.3.0")
        self.assertTrue((self.temp_dir / "versions" / "v1.3.0" / "scripts" / "yt_queue.py").exists())
        self.assertTrue((self.temp_dir / "versions" / "v1.3.0" / "evolution" / "LESSONS_LEARNED.json").exists())


if __name__ == "__main__":
    unittest.main()

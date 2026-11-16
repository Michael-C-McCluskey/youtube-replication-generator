#!/usr/bin/env python3
"""
Unit tests for scripts/yt_evolve.py and plan/generator version pinning in scripts/yt_queue.py.
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


class TestEvolutionAndVersioning(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="yt_evolve_test_"))
        shutil.copytree(REPO_ROOT / "templates", self.temp_dir / "templates")
        shutil.copytree(REPO_ROOT / "docs", self.temp_dir / "docs")
        (self.temp_dir / "VERSION").write_text("1.1.0\n", encoding="utf-8")
        (self.temp_dir / "CHANGELOG.md").write_text("# Changelog\n\n---\n\n", encoding="utf-8")
        self.evo = EvolutionManager(self.temp_dir)
        self.mgr = ReplicationQueueManager(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_record_and_query_lessons_injects_into_new_project(self):
        lesson = self.evo.record_lesson(
            project="001-demo",
            archetype="Archetype B/C",
            category="off-camera-trap",
            title="Validate JSON-LD before HTML compile",
            problem="Broken schema nodes silently fail rich snippets.",
            solution="Run schema_validator.py before build_directory.py.",
        )
        self.assertEqual(lesson["id"], "L-001")
        self.assertEqual(lesson["generator_version_added"], "1.1.0")
        self.assertTrue((self.temp_dir / "evolution" / "EVOLUTION_LOG.md").exists())

        queried = self.evo.query_lessons(archetype="Archetype B/C")
        self.assertEqual(len(queried), 1)

        proj = self.mgr.add_project(
            "https://www.youtube.com/watch?v=UytYrhYLOKI",
            slug="doppler-demo",
            title="Doppler Demo",
            archetype="Archetype B/C",
        )
        research_md = (self.temp_dir / proj["folder"] / "RESEARCH_SYNTHESIS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Validate JSON-LD before HTML compile", research_md)
        self.assertEqual(proj["generator_version"], "1.1.0")
        self.assertEqual(proj["plan_version"], 1)

    def test_02_plan_revision_preserves_v1_and_version_bump_protects_in_progress(self):
        # Project 001 starts on v1.1.0
        p1 = self.mgr.add_project(
            "https://www.youtube.com/watch?v=UytYrhYLOKI",
            slug="project-one",
            title="Project One",
        )
        p1_dir = self.temp_dir / p1["folder"]
        self.mgr.mark_planned("001")
        self.assertTrue((p1_dir / "plans" / "v1" / "REPLICATION_BLUEPRINT.md").exists())

        # Revise plan -> archives v1 and bumps plan_version to 2
        revised = self.mgr.revise_plan("001", reason="Add CPU fallback option")
        self.assertEqual(revised["plan_version"], 2)
        self.assertTrue((p1_dir / "plans" / "v1" / "REPLICATION_BLUEPRINT.md").exists())

        # Re-mark planned on v2 and approve & start Stage 2
        self.mgr.mark_planned("001")
        self.assertTrue((p1_dir / "plans" / "v2" / "REPLICATION_BLUEPRINT.md").exists())
        self.mgr.approve_project("001")
        started = self.mgr.start_next()
        self.assertEqual(started["generator_version"], "1.1.0")

        # Cannot revise plan while STAGE_2_IN_PROGRESS
        with self.assertRaises(QueueError):
            self.mgr.revise_plan("001", reason="Should fail during build")

        # Bump global generator to 1.2.0 while 001 is in progress
        bump = self.evo.bump_version("1.2.0", summary="Learned new audio DSP trick")
        self.assertEqual(bump["new_version"], "1.2.0")
        self.assertTrue((self.temp_dir / "versions" / "v1.2.0" / "templates").exists())

        # New project 002 uses v1.2.0, while in-progress 001 stays pinned to v1.1.0!
        p2 = self.mgr.add_project(
            "https://www.youtube.com/watch?v=LlhTEttKcwQ",
            slug="project-two",
            title="Project Two",
        )
        self.assertEqual(p2["generator_version"], "1.2.0")

        queue_data = self.mgr.load_queue()
        p1_reloaded = self.mgr.find_project(queue_data, "001")
        self.assertEqual(p1_reloaded["generator_version"], "1.1.0")
        self.assertEqual(p1_reloaded["status"], "STAGE_2_IN_PROGRESS")


if __name__ == "__main__":
    unittest.main()

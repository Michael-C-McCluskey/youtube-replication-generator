#!/usr/bin/env python3
"""
Unit tests for scripts/yt_queue.py (YouTube Replication Project Generator & Sequential Queue Manager).
"""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from yt_queue import QueueError, ReplicationQueueManager, extract_video_id


class TestYouTubeReplicationQueue(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="yt_queue_test_"))
        shutil.copytree(REPO_ROOT / "templates", self.temp_dir / "templates")
        self.mgr = ReplicationQueueManager(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_extract_video_id(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/watch?v=NhqSuQPPvbg"),
            "NhqSuQPPvbg",
        )
        self.assertEqual(
            extract_video_id("https://youtu.be/UytYrhYLOKI?t=2"),
            "UytYrhYLOKI",
        )
        self.assertEqual(
            extract_video_id("https://www.youtube.com/live/LlhTEttKcwQ"),
            "LlhTEttKcwQ",
        )

    def test_02_add_scaffolds_subproject_and_syncs_index(self):
        proj = self.mgr.add_project(
            "https://www.youtube.com/watch?v=UytYrhYLOKI",
            slug="doppler-geolocation",
            title="Aircraft Doppler Geolocation",
        )
        self.assertEqual(proj["id"], "001")
        self.assertEqual(proj["status"], "STAGE_1_NEEDS_PLAN")
        proj_dir = self.temp_dir / proj["folder"]
        self.assertTrue((proj_dir / "DECONSTRUCTION.md").exists())
        self.assertTrue((proj_dir / "RESEARCH_SYNTHESIS.md").exists())
        self.assertTrue((proj_dir / "REPLICATION_BLUEPRINT.md").exists())
        self.assertTrue((proj_dir / "AGENT_INSTRUCTIONS.md").exists())
        self.assertTrue((self.temp_dir / "replications" / "INDEX.md").exists())

    def test_03_single_active_project_lock_and_full_lifecycle(self):
        # Add two projects
        p1 = self.mgr.add_project(
            "https://www.youtube.com/watch?v=UytYrhYLOKI",
            slug="doppler-geolocation",
            title="Doppler Geolocation",
        )
        p2 = self.mgr.add_project(
            "https://www.youtube.com/watch?v=LlhTEttKcwQ",
            slug="ai-influencer-workbook",
            title="AI Influencer Workbook",
        )
        self.assertEqual(p1["id"], "001")
        self.assertEqual(p2["id"], "002")

        # Mark both planned and approve ("OK") both projects
        self.mgr.mark_planned("001")
        self.mgr.mark_planned("002")
        self.mgr.approve_project("001")
        self.mgr.approve_project("002")

        # Start next -> claims 001 (oldest APPROVED_QUEUED)
        started = self.mgr.start_next()
        self.assertEqual(started["id"], "001")
        self.assertEqual(started["status"], "STAGE_2_IN_PROGRESS")

        # Attempting to start-next again while 001 is active MUST fail (Single-Active-Project Lock)
        with self.assertRaises(QueueError) as ctx:
            self.mgr.start_next()
        self.assertIn("SINGLE-ACTIVE-PROJECT LOCK VIOLATION", str(ctx.exception))

        # Attempting to complete 001 before VERIFICATION_REPORT.md and STEP_BY_STEP_TUTORIAL.md exist MUST fail
        with self.assertRaises(QueueError):
            self.mgr.complete_project("001")

        # Write VERIFICATION_REPORT.md and enter SATISFACTION_GATE
        p1_dir = self.temp_dir / p1["folder"]
        (p1_dir / "VERIFICATION_REPORT.md").write_text(
            "# Verification Report\nAll 5 checks pass with exit code 0 and full metrics.\n",
            encoding="utf-8",
        )
        verified = self.mgr.mark_verified("001")
        self.assertEqual(verified["status"], "SATISFACTION_GATE")

        # Lock is still held during SATISFACTION_GATE
        with self.assertRaises(QueueError):
            self.mgr.start_next()

        # Write STEP_BY_STEP_TUTORIAL.md and complete 001
        (p1_dir / "STEP_BY_STEP_TUTORIAL.md").write_text(
            "# Step-by-Step Tutorial\nComplete post-confirmation tutorial grounded in verified code.\n",
            encoding="utf-8",
        )
        completed = self.mgr.complete_project("001")
        self.assertEqual(completed["status"], "COMPLETED")

        # Now that 001 is COMPLETED, the lock is released and start-next claims 002!
        started_2 = self.mgr.start_next()
        self.assertEqual(started_2["id"], "002")
        self.assertEqual(started_2["status"], "STAGE_2_IN_PROGRESS")


if __name__ == "__main__":
    unittest.main()

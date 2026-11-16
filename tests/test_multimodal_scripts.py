#!/usr/bin/env python3
"""
Behavioral tests for multimodal helper scripts (stage_golden_frames.py, extract_keyframes.py).
"""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestMultimodalScripts(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="yt_mm_test_"))
        self.frames_dir = self.temp_dir / "frames"
        self.artifact_dir = self.temp_dir / "artifacts"
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_stage_golden_frames_creates_single_segment_pngs(self):
        (self.frames_dir / "frame_00_32.png").write_bytes(b"\x89PNG\r\n\x1a\nfake1")
        (self.frames_dir / "frame_04_18.png").write_bytes(b"\x89PNG\r\n\x1a\nfake2")

        res = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "scripts" / "stage_golden_frames.py"),
                "--frames-dir",
                str(self.frames_dir),
                "--artifact-dir",
                str(self.artifact_dir),
                "--timestamps",
                "00:32,04:18",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        ref_dir = self.artifact_dir / "browser_sandbox" / "references"
        self.assertTrue((ref_dir / "video_00_32.png").exists())
        self.assertTrue((ref_dir / "video_04_18.png").exists())

    def test_02_extract_keyframes_help(self):
        res = subprocess.run(
            ["python3", str(REPO_ROOT / "scripts" / "extract_keyframes.py"), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr)


if __name__ == "__main__":
    unittest.main()

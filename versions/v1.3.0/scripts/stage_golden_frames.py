#!/usr/bin/env python3
"""Stage 5 helper: copy Golden Keyframes into <ArtifactDir>/browser_sandbox/references/ as video_MM_SS.png.

The `browser` subagent can only read single-segment filenames staged under that directory.
Each requested timestamp is matched to the nearest extracted frame (frame_MM_SS.png).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

FRAME_RE = re.compile(r"^frame_(\d+)_(\d{2})\.png$")
TS_RE = re.compile(r"^(?:(\d+):)?(\d+):(\d{2})$|^(\d+)_(\d{2})$")


def parse_ts(text: str) -> int:
    """Parse MM:SS, H:MM:SS, or MM_SS into seconds."""
    text = text.strip()
    m = TS_RE.match(text)
    if not m:
        raise ValueError(f"Bad timestamp '{text}' (use MM:SS or MM_SS)")
    if m.group(4) is not None:
        return int(m.group(4)) * 60 + int(m.group(5))
    hours = int(m.group(1) or 0)
    return hours * 3600 + int(m.group(2)) * 60 + int(m.group(3))


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage Golden Keyframes into browser_sandbox/references/.")
    parser.add_argument("--frames-dir", required=True, help="Directory containing frame_MM_SS.png files.")
    parser.add_argument("--artifact-dir", required=True, help="Conversation artifact directory (parent of browser_sandbox/).")
    parser.add_argument("--timestamps", required=True, help="Comma-separated golden timestamps, e.g. 00:32,04:18,08_42.")
    parser.add_argument("--tolerance-sec", type=int, default=5, help="Max distance to the nearest frame (default 5).")
    args = parser.parse_args()

    frames_dir = Path(args.frames_dir).resolve()
    available: list[tuple[int, Path]] = []
    for p in frames_dir.glob("frame_*.png"):
        m = FRAME_RE.match(p.name)
        if m:
            available.append((int(m.group(1)) * 60 + int(m.group(2)), p))
    if not available:
        print(f"No frame_MM_SS.png files found in {frames_dir}", file=sys.stderr)
        return 1

    dest_dir = Path(args.artifact_dir).resolve() / "browser_sandbox" / "references"
    dest_dir.mkdir(parents=True, exist_ok=True)

    staged, missing = [], []
    for raw in [t for t in args.timestamps.split(",") if t.strip()]:
        want = parse_ts(raw)
        sec, src = min(available, key=lambda a: abs(a[0] - want))
        if abs(sec - want) > args.tolerance_sec:
            missing.append({"requested": raw.strip(), "nearest_sec": sec})
            continue
        name = f"video_{sec // 60:02d}_{sec % 60:02d}.png"
        shutil.copyfile(src, dest_dir / name)
        staged.append({"requested": raw.strip(), "staged_as": name, "path": str(dest_dir / name)})

    print(json.dumps({"status": "ok" if not missing else "partial", "references_dir": str(dest_dir), "staged": staged, "missing": missing}, indent=2))
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())

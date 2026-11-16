#!/usr/bin/env python3
"""Stage 0 helper: Extract scene-change, montage-burst, and chapter keyframes with ffmpeg."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PTS_TIME_RE = re.compile(r"pts_time:\s*([0-9]+(?:\.[0-9]+)?)")
DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")

PRIORITY_RANK = {
    "chapter_anchor": 4,
    "scene_change": 3,
    "montage_burst": 2,
    "interval_fallback": 1,
}


def format_mm_ss(seconds: float) -> str:
    """Format seconds as MM_SS for deterministic filenames."""
    total = max(0, int(round(seconds)))
    mins, secs = divmod(total, 60)
    return f"{mins:02d}_{secs:02d}"


def format_mmss_colon(seconds: float) -> str:
    """Format seconds as MM:SS for human-readable index metadata."""
    return format_mm_ss(seconds).replace("_", ":")


def probe_duration(video_path: Path, manifest: dict[str, Any] | None) -> float:
    """Determine video duration from manifest, ffprobe, or ffmpeg header output."""
    if manifest and float(manifest.get("duration_sec") or 0.0) > 0:
        return float(manifest["duration_sec"])

    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        proc = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return float(proc.stdout.strip())

    proc = subprocess.run(["ffmpeg", "-i", str(video_path)], capture_output=True, text=True)
    match = DURATION_RE.search(proc.stderr)
    if match:
        hrs, mins, secs = int(match.group(1)), int(match.group(2)), float(match.group(3))
        return hrs * 3600 + mins * 60 + secs
    return 0.0


def detect_scene_timestamps(video_path: Path, threshold: float) -> list[float]:
    """Run ffmpeg scene-change detection and parse pts_time stamps from stderr."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(video_path),
        "-vf",
        f"select='gt(scene,{threshold})',showinfo",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stamps: list[float] = []
    for line in proc.stderr.splitlines():
        if "showinfo" in line:
            match = PTS_TIME_RE.search(line)
            if match:
                stamps.append(float(match.group(1)))
    return stamps


def in_intervals(ts: float, intervals: list[dict[str, Any]]) -> bool:
    """Return True if timestamp falls inside any half-open [start, end) interval."""
    return any(float(iv.get("start", 0.0)) <= ts < float(iv.get("end", 0.0)) for iv in intervals)


def hard_noise(manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Intervals that are dropped entirely (sponsors/plugs). Soft noise (intro/outro) is kept but tagged."""
    return [iv for iv in ((manifest or {}).get("noise_intervals") or []) if iv.get("kind", "hard") == "hard"]


def soft_noise(manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [iv for iv in ((manifest or {}).get("noise_intervals") or []) if iv.get("kind") == "soft"]


def select_timestamps(
    duration_sec: float,
    scene_stamps: list[float],
    manifest: dict[str, Any] | None,
    interval_sec: float,
    montage_interval_sec: float,
    max_frames: int,
) -> list[dict[str, Any]]:
    """Combine scene, montage-burst, chapter, and interval anchors with deduplication and cap."""
    noise_intervals = hard_noise(manifest)
    montage_candidates = (manifest or {}).get("montage_candidates") or []
    chapters = (manifest or {}).get("chapters") or []

    raw_candidates: list[dict[str, Any]] = []

    for ch in chapters:
        ts = float(ch.get("start_time", 0.0))
        if not in_intervals(ts, noise_intervals):
            raw_candidates.append({"ts": ts, "source": "chapter_anchor"})

    for ts in scene_stamps:
        if not in_intervals(ts, noise_intervals):
            raw_candidates.append({"ts": ts, "source": "scene_change"})

    for iv in montage_candidates:
        cur = float(iv.get("start", 0.0))
        end = float(iv.get("end", cur))
        while cur <= end:
            if not in_intervals(cur, noise_intervals):
                raw_candidates.append({"ts": cur, "source": "montage_burst"})
            cur += max(1.0, montage_interval_sec)

    # Uniform fallback anchors only when other signals are sparse; interval adapts to short videos.
    if duration_sec > 0 and len(raw_candidates) < 10:
        step = min(max(2.0, interval_sec), max(2.0, duration_sec / 10.0))
        cur = min(1.0, duration_sec / 2.0)
        while cur < duration_sec:
            if not in_intervals(cur, noise_intervals):
                raw_candidates.append({"ts": cur, "source": "interval_fallback"})
            cur += step

    # Deduplicate within 2.0s while keeping higher-priority source.
    raw_candidates.sort(key=lambda item: (item["ts"], -PRIORITY_RANK[item["source"]]))
    deduped: list[dict[str, Any]] = []
    for item in raw_candidates:
        if not deduped or abs(item["ts"] - deduped[-1]["ts"]) >= 2.0:
            deduped.append(item)
        elif PRIORITY_RANK[item["source"]] > PRIORITY_RANK[deduped[-1]["source"]]:
            deduped[-1] = item

    # Over the cap: always keep chapter anchors, then evenly thin the rest across the timeline.
    if len(deduped) > max_frames:
        anchors = [d for d in deduped if d["source"] == "chapter_anchor"][:max_frames]
        rest = [d for d in deduped if d["source"] != "chapter_anchor"]
        slots = max_frames - len(anchors)
        if slots > 0 and rest:
            step = len(rest) / float(slots)
            rest = [rest[int(i * step)] for i in range(slots)]
        else:
            rest = []
        deduped = sorted(anchors + rest, key=lambda d: d["ts"])

    return deduped



def extract_png(video_path: Path, timestamp: float, dest: Path) -> bool:
    """Seek to timestamp and extract a single PNG frame."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{timestamp:.2f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0 and dest.exists()


def lookup_context(timestamp: float, manifest: dict[str, Any] | None) -> tuple[str, str]:
    """Find active chapter title and nearby transcript text (+/- 8s) for a frame timestamp."""
    if not manifest:
        return "", ""

    chapter_title = ""
    for ch in manifest.get("chapters") or []:
        if float(ch.get("start_time", 0.0)) <= timestamp <= float(ch.get("end_time", 0.0)):
            chapter_title = str(ch.get("title", ""))
            break

    snippets = [
        str(seg.get("text", ""))
        for seg in (manifest.get("transcript") or [])
        if abs(float(seg.get("start", 0.0)) - timestamp) <= 8.0
    ]
    return chapter_title, " ".join(snippets).strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage 0 CopyCat Builder helper: extract scene-change, montage-burst, and chapter PNG keyframes."
    )
    parser.add_argument("--video", required=True, help="Path to local video file (.mp4/.mkv/.webm).")
    parser.add_argument("--output-dir", required=True, help="Directory to write frame_MM_SS.png files and video_context_index.json.")
    parser.add_argument("--manifest", help="Optional path to video_manifest.json from extract_video_bundle.py.")
    parser.add_argument("--scene-threshold", type=float, default=0.28, help="ffmpeg scene change sensitivity (default: 0.28).")
    parser.add_argument("--interval-sec", type=float, default=25.0, help="Fallback uniform interval in seconds (default: 25.0).")
    parser.add_argument("--montage-interval-sec", type=float, default=3.0, help="High-density interval for detected montages (default: 3.0).")
    parser.add_argument("--max-frames", type=int, default=40, help="Maximum keyframes to extract (default: 40).")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        print(
            json.dumps(
                {
                    "status": "error",
                    "missing": ["ffmpeg"],
                    "install_hint": "winget install Gyan.FFmpeg  # then restart shell so ffmpeg is on PATH",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    video_path = Path(args.video).resolve()
    if not video_path.exists():
        print(f"Video file not found: {video_path}", file=sys.stderr)
        return 1

    manifest: dict[str, Any] | None = None
    if args.manifest:
        manifest_path = Path(args.manifest).resolve()
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    out_dir = Path(args.output_dir).resolve()
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    duration_sec = probe_duration(video_path, manifest)
    scene_stamps = detect_scene_timestamps(video_path, args.scene_threshold)
    selected = select_timestamps(
        duration_sec=duration_sec,
        scene_stamps=scene_stamps,
        manifest=manifest,
        interval_sec=args.interval_sec,
        montage_interval_sec=args.montage_interval_sec,
        max_frames=args.max_frames,
    )

    records: list[dict[str, Any]] = []
    soft = soft_noise(manifest)
    for item in selected:
        ts = float(item["ts"])
        fname = f"frame_{format_mm_ss(ts)}.png"
        dest = frames_dir / fname
        if extract_png(video_path, ts, dest):
            chapter, excerpt = lookup_context(ts, manifest)
            records.append(
                {
                    "timestamp_sec": round(ts, 2),
                    "timestamp_mmss": format_mmss_colon(ts),
                    "segment_type": item["source"],
                    "in_soft_noise_intro_outro": in_intervals(ts, soft),
                    "chapter": chapter,
                    "transcript_excerpt": excerpt,
                    "keyframe_path": str(dest),
                    "filename": fname,
                }
            )

    if shutil.which("ffprobe") is None and not manifest:
        print("warning: duration may be unknown (no ffprobe/manifest); only scene frames used.", file=sys.stderr)

    index_payload = {
        "video_file": str(video_path),
        "duration_sec": round(duration_sec, 2),
        "scene_threshold": args.scene_threshold,
        "noise_intervals_filtered": (manifest or {}).get("noise_intervals") or [],
        "frames_extracted": len(records),
        "keyframes": records,
    }

    index_path = out_dir / "video_context_index.json"
    index_path.write_text(json.dumps(index_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "ok",
                "index_path": str(index_path),
                "frames_dir": str(frames_dir),
                "frames_extracted": len(records),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

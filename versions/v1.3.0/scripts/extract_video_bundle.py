#!/usr/bin/env python3
"""Stage 0 helper: Preflight check and YouTube metadata, link, transcript, and video extractor."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

HARD_NOISE_KEYWORDS = (
    "sponsor",
    "sponsored",
    "channel plug",
    "subscribe",
    "patreon",
    "merch",
    "giveaway",
    "ad read",
    "promo",
)

# Intro/outro chapters often contain the final-demo preview (a Golden Keyframe), so they are
# only tagged as soft noise: frames are still extracted but flagged `in_soft_noise_intro_outro`.
SOFT_NOISE_KEYWORDS = (
    "intro",
    "introduction",
    "outro",
    "conclusion",
    "wrap up",
    "wrap-up",
)

TRANSCRIPT_NOISE_PHRASES = (
    "this video is sponsored by",
    "sponsored by",
    "check out the link in the description",
    "smash that like",
    "hit the subscribe",
    "don't forget to subscribe",
)

MONTAGE_CHAPTER_KEYWORDS = (
    "timelapse",
    "time-lapse",
    "time lapse",
    "montage",
    "speedrun",
    "speed build",
    "fast forward",
    "fast-forward",
    "sped up",
)

URL_RE = re.compile(r"https?://[^\s<>()\[\]\"']+")
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def format_mmss(seconds: float) -> str:
    """Format seconds as zero-padded MM:SS (allowing >59 minutes cleanly)."""
    total = max(0, int(round(seconds)))
    mins, secs = divmod(total, 60)
    return f"{mins:02d}:{secs:02d}"


def check_dependencies() -> dict[str, Any]:
    """Check availability of yt-dlp, youtube-transcript-api, ffmpeg, and ffprobe."""
    yt_dlp_mod = importlib.util.find_spec("yt_dlp") is not None
    yt_dlp_cli = shutil.which("yt-dlp") is not None
    transcript_mod = importlib.util.find_spec("youtube_transcript_api") is not None
    ffmpeg_cli = shutil.which("ffmpeg") is not None
    ffprobe_cli = shutil.which("ffprobe") is not None

    missing: list[str] = []
    install_hints: list[str] = []

    if not (yt_dlp_mod or yt_dlp_cli):
        missing.append("yt-dlp")
        install_hints.append("pip install yt-dlp")
    if not transcript_mod:
        missing.append("youtube-transcript-api")
        install_hints.append("pip install youtube-transcript-api")
    if not ffmpeg_cli:
        missing.append("ffmpeg")
        install_hints.append("winget install Gyan.FFmpeg  # or add ffmpeg to PATH")

    return {
        "python": sys.version.split()[0],
        "yt_dlp": {"python_module": yt_dlp_mod, "cli": yt_dlp_cli, "available": yt_dlp_mod or yt_dlp_cli},
        "youtube_transcript_api": {"python_module": transcript_mod, "available": transcript_mod},
        "ffmpeg": {"cli": ffmpeg_cli, "available": ffmpeg_cli},
        "ffprobe": {"cli": ffprobe_cli, "available": ffprobe_cli},
        "all_required_present": len(missing) == 0,
        "missing": missing,
        "install_hints": install_hints,
    }


def extract_video_id(url_or_id: str) -> str:
    """Extract an 11-character YouTube video ID from common URL forms or raw ID."""
    candidate = url_or_id.strip()
    if VIDEO_ID_RE.match(candidate):
        return candidate

    parsed = urlparse(candidate)
    host = parsed.netloc.lower()
    path_parts = [p for p in parsed.path.split("/") if p]

    if "youtu.be" in host and path_parts:
        vid = path_parts[0]
        if VIDEO_ID_RE.match(vid):
            return vid

    if "youtube.com" in host or "youtube-nocookie.com" in host:
        qs = parse_qs(parsed.query)
        if "v" in qs and VIDEO_ID_RE.match(qs["v"][0]):
            return qs["v"][0]
        for prefix in ("shorts", "embed", "live"):
            if len(path_parts) >= 2 and path_parts[0] == prefix and VIDEO_ID_RE.match(path_parts[1]):
                return path_parts[1]

    raise ValueError(f"Could not extract a valid YouTube video ID from: {url_or_id}")


def categorize_description_links(description: str) -> dict[str, list[str]]:
    """Extract and categorize external URLs found in a video description."""
    raw_urls = URL_RE.findall(description or "")
    cleaned: list[str] = []
    seen: set[str] = set()
    for url in raw_urls:
        url = url.rstrip(".,;:)")
        if url not in seen:
            seen.add(url)
            cleaned.append(url)

    buckets: dict[str, list[str]] = {
        "github_repos": [],
        "gists": [],
        "sandboxes": [],
        "docs_or_other": [],
    }
    for url in cleaned:
        lower = url.lower()
        if "gist.github.com" in lower:
            buckets["gists"].append(url)
        elif "github.com" in lower or "gitlab.com" in lower:
            buckets["github_repos"].append(url)
        elif any(s in lower for s in ("codepen.io", "replit.com", "stackblitz.com", "codesandbox.io", "huggingface.co/spaces")):
            buckets["sandboxes"].append(url)
        else:
            buckets["docs_or_other"].append(url)
    return buckets


SOCIAL_SKIP_DOMAINS = ("discord.gg", "discord.com", "twitter.com", "x.com", "instagram.com", "facebook.com", "tiktok.com")


def resolve_description_links(links: dict[str, list[str]], out_dir: Path | None = None, timeout: float = 12.0) -> list[dict[str, Any]]:
    """Follow redirects on description URLs, save linked page text, and promote repo/gist/sandbox URLs."""
    import urllib.request

    all_urls = (
        links.get("github_repos", [])
        + links.get("gists", [])
        + links.get("sandboxes", [])
        + links.get("docs_or_other", [])
    )
    resolved: list[dict[str, Any]] = []
    hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    res_dir = (out_dir / "linked_resources") if out_dir else None
    if res_dir:
        res_dir.mkdir(parents=True, exist_ok=True)

    for idx, url in enumerate(all_urls[:15]):
        if any(dom in url.lower() for dom in SOCIAL_SKIP_DOMAINS):
            resolved.append({"source_url": url, "final_url": url, "skipped": "social_link"})
            continue
        try:
            req = urllib.request.Request(url, headers=hdr)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                final_url = resp.geturl()
                raw = resp.read(524288).decode("utf-8", errors="replace")
            title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.IGNORECASE | re.DOTALL)
            title = " ".join(title_m.group(1).split()) if title_m else ""
            lower_final = final_url.lower()
            if "gist.github.com" in lower_final and final_url not in links["gists"]:
                links["gists"].append(final_url)
            elif ("github.com" in lower_final or "gitlab.com" in lower_final) and final_url not in links["github_repos"]:
                links["github_repos"].append(final_url)
            elif any(s in lower_final for s in ("codepen.io", "replit.com", "stackblitz.com", "codesandbox.io", "huggingface.co/spaces")) and final_url not in links["sandboxes"]:
                links["sandboxes"].append(final_url)
            saved_file = None
            embedded_assets: list[str] = []
            if res_dir:
                saved_path = res_dir / f"resource_{idx:02d}.html"
                saved_path.write_text(raw, encoding="utf-8")
                saved_file = str(saved_path)
                # Follow SSR contentUrl (.bin) and embedded .md/.pdf assets if present
                for bin_url in re.findall(r'https://[^\s"\'<>\\]+\.bin', raw)[:3]:
                    try:
                        bdata = urllib.request.urlopen(urllib.request.Request(bin_url, headers=hdr), timeout=timeout).read()
                        btext = bdata.decode("utf-8", errors="ignore")
                        chunks = [c.strip() for c in re.findall(r"[ -~\n\r\t\u2013\u2014\u2018\u2019\u201c\u201d\u2026]{12,}", btext) if len(c.strip()) >= 12]
                        bpath = res_dir / f"resource_{idx:02d}_content.md"
                        bpath.write_text("\n".join(chunks), encoding="utf-8")
                        embedded_assets.append(str(bpath))
                        for doc_url in dict.fromkeys(re.findall(r'https://[^\s"\'<>\\()]+\.(?:md|pdf|json)', btext)):
                            try:
                                dname = Path(urlparse(doc_url).path).name
                                ddest = res_dir / dname
                                ddest.write_bytes(urllib.request.urlopen(urllib.request.Request(doc_url, headers=hdr), timeout=timeout).read())
                                embedded_assets.append(str(ddest))
                            except Exception:  # noqa: BLE001
                                pass
                    except Exception:  # noqa: BLE001
                        pass
            resolved.append({"source_url": url, "final_url": final_url, "title": title, "saved_html": saved_file, "embedded_assets": embedded_assets})
        except Exception as exc:  # noqa: BLE001
            resolved.append({"source_url": url, "error": str(exc)})
    return resolved



def fetch_metadata(url: str) -> dict[str, Any]:
    """Fetch video metadata via yt_dlp Python module or CLI without downloading media."""
    if importlib.util.find_spec("yt_dlp") is not None:
        import yt_dlp  # type: ignore

        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return dict(info)

    yt_cli = shutil.which("yt-dlp")
    if yt_cli:
        proc = subprocess.run(
            [yt_cli, "--dump-single-json", "--no-warnings", "--skip-download", url],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(proc.stdout)

    raise RuntimeError("yt-dlp is not installed (neither Python package `yt_dlp` nor CLI `yt-dlp`).")


def fetch_transcript(video_id: str) -> tuple[list[dict[str, Any]], str]:
    """Fetch timestamped transcript entries using youtube-transcript-api."""
    if importlib.util.find_spec("youtube_transcript_api") is None:
        return [], "missing_youtube_transcript_api"

    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore

    raw_items: list[Any] = []
    source = "youtube_transcript_api"

    try:
        # Support both youtube-transcript-api >= 1.0 instance API and 0.x static API.
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            raw_items = YouTubeTranscriptApi.get_transcript(video_id)
        else:
            api = YouTubeTranscriptApi()
            fetched = api.fetch(video_id)
            raw_items = list(fetched)
    except Exception as exc:  # noqa: BLE001
        return [], f"transcript_unavailable: {exc}"

    normalized: list[dict[str, Any]] = []
    for item in raw_items:
        if isinstance(item, dict):
            start = float(item.get("start", 0.0))
            duration = float(item.get("duration", 0.0))
            text = str(item.get("text", "")).strip()
        else:
            start = float(getattr(item, "start", 0.0))
            duration = float(getattr(item, "duration", 0.0))
            text = str(getattr(item, "text", "")).strip()
        if text:
            normalized.append(
                {
                    "start": round(start, 2),
                    "duration": round(duration, 2),
                    "mmss": format_mmss(start),
                    "text": " ".join(text.split()),
                }
            )
    return normalized, source


def fetch_captions_from_info(info: dict[str, Any]) -> list[dict[str, Any]]:
    """Fallback transcript: pull json3 captions listed in yt-dlp metadata (manual first, then auto)."""
    import urllib.request

    for pool_name in ("subtitles", "automatic_captions"):
        pool = info.get(pool_name) or {}
        langs = [k for k in pool if k == "en" or k.startswith("en-") or k.startswith("en_")]
        for lang in langs:
            for fmt in pool[lang]:
                if fmt.get("ext") != "json3" or not fmt.get("url"):
                    continue
                try:
                    with urllib.request.urlopen(fmt["url"], timeout=20) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                except Exception:  # noqa: BLE001
                    continue
                items: list[dict[str, Any]] = []
                for ev in data.get("events", []):
                    text = "".join(seg.get("utf8", "") for seg in ev.get("segs", []) or []).strip()
                    if not text:
                        continue
                    start = float(ev.get("tStartMs", 0)) / 1000.0
                    dur = float(ev.get("dDurationMs", 0)) / 1000.0
                    items.append({"start": round(start, 2), "duration": round(dur, 2), "mmss": format_mmss(start), "text": " ".join(text.split())})
                if items:
                    return items
    return []


def detect_noise_and_montages(
    chapters: list[dict[str, Any]],
    transcript: list[dict[str, Any]],
    duration_sec: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Identify likely noise intervals (sponsors/intros) and silent/rapid montage windows."""
    noise_intervals: list[dict[str, Any]] = []
    montage_candidates: list[dict[str, Any]] = []

    for ch in chapters:
        title = str(ch.get("title", "")).strip()
        lower = title.lower()
        start = float(ch.get("start_time", 0.0))
        end = float(ch.get("end_time", duration_sec))
        if any(kw in lower for kw in HARD_NOISE_KEYWORDS) or any(kw in lower for kw in SOFT_NOISE_KEYWORDS):
            kind = "hard" if any(kw in lower for kw in HARD_NOISE_KEYWORDS) else "soft"
            noise_intervals.append(
                {
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "mmss_range": f"{format_mmss(start)}-{format_mmss(end)}",
                    "reason": f"chapter:{title}",
                    "kind": kind,
                }
            )
        elif any(kw in lower for kw in MONTAGE_CHAPTER_KEYWORDS):
            montage_candidates.append(
                {
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "mmss_range": f"{format_mmss(start)}-{format_mmss(end)}",
                    "reason": f"chapter:{title}",
                }
            )

    for idx, entry in enumerate(transcript):
        lower = entry["text"].lower()
        if any(phrase in lower for phrase in TRANSCRIPT_NOISE_PHRASES):
            start = float(entry["start"])
            end = min(duration_sec or start + 30.0, start + 30.0)
            noise_intervals.append(
                {
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "mmss_range": f"{format_mmss(start)}-{format_mmss(end)}",
                    "reason": "transcript_sponsor_or_plug_phrase",
                    "kind": "hard",
                }
            )

        if idx + 1 < len(transcript):
            gap_start = float(entry["start"]) + float(entry["duration"])
            gap_end = float(transcript[idx + 1]["start"])
            if gap_end - gap_start >= 8.0:
                montage_candidates.append(
                    {
                        "start": round(gap_start, 2),
                        "end": round(gap_end, 2),
                        "mmss_range": f"{format_mmss(gap_start)}-{format_mmss(gap_end)}",
                        "reason": f"narration_silence_gap_{round(gap_end - gap_start, 1)}s",
                    }
                )

    return noise_intervals, montage_candidates


def download_bounded_video(url: str, output_dir: Path, max_height: int, has_ffmpeg: bool) -> str:
    """Download a bounded-resolution MP4 stream into output_dir/video.mp4."""
    target_template = str(output_dir / "video.%(ext)s")
    fmt = (
        f"bestvideo[height<={max_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={max_height}][ext=mp4]/best[height<={max_height}]"
        if has_ffmpeg
        else f"best[height<={max_height}][ext=mp4]/best[height<={max_height}]"
    )

    if importlib.util.find_spec("yt_dlp") is not None:
        import yt_dlp  # type: ignore

        opts: dict[str, Any] = {
            "format": fmt,
            "outtmpl": target_template,
            "quiet": True,
            "noprogress": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    else:
        yt_cli = shutil.which("yt-dlp")
        if not yt_cli:
            raise RuntimeError("yt-dlp is required to download video.")
        subprocess.run(
            [yt_cli, "-q", "--no-progress", "-f", fmt, "--merge-output-format", "mp4", "-o", target_template, url],
            check=True,
        )

    for ext in ("mp4", "mkv", "webm"):
        candidate = output_dir / f"video.{ext}"
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError("yt-dlp finished without creating a local video file.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage 0 CopyCat Builder helper: check tools and extract YouTube metadata, links, transcript, and bounded video."
    )
    parser.add_argument("--url", help="YouTube video URL or 11-character video ID.")
    parser.add_argument("--output-dir", help="Target directory for extracted artifacts (e.g., <ArtifactDir>/scratch/copycat/<slug>).")
    parser.add_argument("--download-video", action="store_true", help="Download <= max-height MP4 stream for keyframe extraction.")
    parser.add_argument("--max-height", type=int, default=720, help="Maximum video vertical resolution to download (default: 720).")
    parser.add_argument("--check-deps", action="store_true", help="Check dependency availability and print JSON report.")
    parser.add_argument("--resolve-manifest", help="Resolve description links in an existing video_manifest.json in-place.")
    args = parser.parse_args()

    deps = check_dependencies()
    if args.check_deps and not args.url and not args.resolve_manifest:
        print(json.dumps(deps, indent=2))
        return 0

    if args.resolve_manifest:
        mpath = Path(args.resolve_manifest).resolve()
        mdata = json.loads(mpath.read_text(encoding="utf-8"))
        mdata["resolved_description_links"] = resolve_description_links(mdata["description_links"], mpath.parent)
        mpath.write_text(json.dumps(mdata, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"status": "ok", "resolved_description_links": mdata["resolved_description_links"], "description_links": mdata["description_links"]}, indent=2))
        return 0

    if not args.url or not args.output_dir:
        parser.error("--url and --output-dir are required unless running --check-deps standalone.")

    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    video_id = extract_video_id(args.url)
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    info = fetch_metadata(canonical_url)

    duration_sec = float(info.get("duration") or 0.0)
    chapters = [
        {
            "title": c.get("title", ""),
            "start_time": float(c.get("start_time", 0.0)),
            "end_time": float(c.get("end_time", duration_sec)),
            "mmss_range": f"{format_mmss(float(c.get('start_time', 0.0)))}-{format_mmss(float(c.get('end_time', duration_sec)))}",
        }
        for c in (info.get("chapters") or [])
    ]

    description = str(info.get("description") or "")
    links = categorize_description_links(description)
    resolved_links = resolve_description_links(links, out_dir)
    transcript, transcript_source = fetch_transcript(video_id)
    if not transcript:
        fallback = fetch_captions_from_info(info)
        if fallback:
            transcript, transcript_source = fallback, "yt_dlp_caption_fallback"
    noise_intervals, montage_candidates = detect_noise_and_montages(chapters, transcript, duration_sec)

    video_path: str | None = None
    if args.download_video:
        video_path = download_bounded_video(canonical_url, out_dir, args.max_height, deps["ffmpeg"]["available"])

    transcript_txt_path = out_dir / "transcript_timestamped.txt"
    transcript_lines = [f"[{item['mmss']}] {item['text']}" for item in transcript]
    transcript_txt_path.write_text("\n".join(transcript_lines), encoding="utf-8")

    manifest = {
        "video_id": video_id,
        "url": canonical_url,
        "title": info.get("title", ""),
        "uploader": info.get("uploader", ""),
        "duration_sec": duration_sec,
        "duration_mmss": format_mmss(duration_sec),
        "tags": info.get("tags") or [],
        "description": description,
        "description_links": links,
        "resolved_description_links": resolved_links,
        "chapters": chapters,
        "noise_intervals": noise_intervals,
        "montage_candidates": montage_candidates,
        "transcript_source": transcript_source,
        "transcript_count": len(transcript),
        "transcript": transcript,
        "transcript_file": str(transcript_txt_path),
        "video_file": video_path,
        "dependencies_snapshot": deps,
    }

    manifest_path = out_dir / "video_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "manifest_path": str(manifest_path),
                "transcript_file": str(transcript_txt_path),
                "video_file": video_path,
                "chapters": len(chapters),
                "transcript_segments": len(transcript),
                "noise_intervals_detected": len(noise_intervals),
                "montage_candidates_detected": len(montage_candidates),
                "official_repo_links": links["github_repos"] + links["gists"] + links["sandboxes"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Stage 0/2 run_workflow script: parallel multimodal keyframe batch inspection."""

import json
from pathlib import Path

BATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "timestamp_mmss": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["ui_token", "code_tree", "cli_cmd", "montage_action", "architecture"],
                    },
                    "detail": {"type": "string"},
                    "tag": {"type": "string"},
                },
                "required": ["timestamp_mmss", "category", "detail", "tag"],
            },
        },
        "golden_candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "timestamp_mmss": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["timestamp_mmss", "reason"],
            },
        },
        "unspecified_flags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["observations", "golden_candidates", "unspecified_flags"],
}


def build_batch_prompt(batch: list[dict]) -> str:
    """Build a self-contained prompt for inspecting one batch of keyframe PNGs."""
    lines = []
    for kf in batch:
        mmss = kf.get("timestamp_mmss", "00:00")
        ch = kf.get("chapter", "")
        seg = kf.get("segment_type", "")
        excerpt = kf.get("transcript_excerpt", "")
        path = kf.get("keyframe_path", "")
        lines.append(f"- [{mmss}] ({seg}, chapter='{ch}') path={path} | transcript: {excerpt}")
    frame_list = "\n".join(lines)
    return (
        "Inspect each keyframe PNG below using `read_file` and extract concrete technical/visual facts.\n"
        "Rules:\n"
        "- Only report details directly visible in the frames or transcript; tag every observation `[OBSERVED @ MM:SS]`.\n"
        "- Flag blurred/cut-off/omitted critical parameters (versions, colors, constants, flags) in `unspecified_flags`.\n"
        "- Mark standout frames (landing state, core workflow, hero result) in `golden_candidates`.\n\n"
        f"Frames:\n{frame_list}"
    )


index_path = Path(args["index_path"])
batch_size = int(args.get("batch_size", 6))
index_data = json.loads(index_path.read_text(encoding="utf-8"))
keyframes = index_data.get("keyframes", [])

batches = [keyframes[i : i + batch_size] for i in range(0, len(keyframes), batch_size)]

phase("Inspect Keyframe Batches")
if batches:
    results = await parallel(
        batches,
        lambda b: agent(
            build_batch_prompt(b),
            schema=BATCH_SCHEMA,
            role=f"Frames {b[0].get('timestamp_mmss', '?')}-{b[-1].get('timestamp_mmss', '?')}",
            model="flash",
        ),
    )
else:
    results = []

merged = {
    "index_path": str(index_path),
    "frames_inspected": len(keyframes),
    "batches": len(batches),
    "observations": [obs for r in results for obs in r.get("observations", [])],
    "golden_candidates": [gk for r in results for gk in r.get("golden_candidates", [])],
    "unspecified_flags": sorted({u for r in results for u in r.get("unspecified_flags", [])}),
}

log(
    f"Inspected {merged['frames_inspected']} frames across {merged['batches']} batch(es): "
    f"{len(merged['observations'])} observations, "
    f"{len(merged['golden_candidates'])} golden candidates, "
    f"{len(merged['unspecified_flags'])} unspecified flags."
)
print(json.dumps(merged, indent=2, ensure_ascii=False))

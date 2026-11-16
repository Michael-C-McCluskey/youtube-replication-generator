"""Stage 2A run_workflow script: parallel external research across BOM & unspecified items."""

import json

ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "item": {"type": "string"},
        "source_urls": {"type": "array", "items": {"type": "string"}},
        "resolved_params": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "parameter": {"type": "string"},
                    "value": {"type": "string"},
                    "tag": {"type": "string"},
                },
                "required": ["parameter", "value", "tag"],
            },
        },
        "traps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "trap": {"type": "string"},
                    "mitigation": {"type": "string"},
                    "tag": {"type": "string"},
                },
                "required": ["trap", "mitigation", "tag"],
            },
        },
        "robustness_notes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "upgrade": {"type": "string"},
                    "milestone": {"type": "string"},
                    "tag": {"type": "string"},
                },
                "required": ["upgrade", "milestone", "tag"],
            },
        },
    },
    "required": ["item", "source_urls", "resolved_params", "traps", "robustness_notes"],
}


def build_research_prompt(concept: str, item: str, unspecified: list[str]) -> str:
    """Build a self-contained web research prompt for one BOM item or topic."""
    unspec_text = "\n".join(f"- {u}" for u in unspecified) if unspecified else "- (none)"
    return (
        f"Project concept: {concept}\n"
        f"Target BOM item / library / technique: {item}\n"
        f"Open [UNSPECIFIED] parameters in the project:\n{unspec_text}\n\n"
        "Use `search_web` to find official docs, current stable/working versions, similar open-source examples, "
        "and common setup pitfalls for this item.\n"
        "Rules:\n"
        "- Tag every resolved parameter, trap, and robustness upgrade as `[RESEARCHED: <URL>]`.\n"
        "- Robustness notes (validation, error handling, pinned versions, tests, config) must preserve 100% "
        "visual and functional parity with the demonstrated video behavior.\n"
        "- If sources conflict or a parameter cannot be confirmed, omit it from `resolved_params`."
    )


project_concept = str(args.get("project_concept", ""))
bom_items = list(args.get("bom_items") or [])
unspecified_items = list(args.get("unspecified_items") or [])

targets = list(bom_items)
if not targets and unspecified_items:
    targets = list(unspecified_items)

phase("External Research Fan-Out")
if targets:
    results = await parallel(
        targets,
        lambda item: agent(
            build_research_prompt(project_concept, str(item), unspecified_items),
            schema=ITEM_SCHEMA,
            role=f"Research: {str(item)[:36]}",
            model="flash",
        ),
    )
else:
    results = []

summary = {
    "project_concept": project_concept,
    "items_researched": len(targets),
    "results": results,
    "all_source_urls": sorted({u for r in results for u in r.get("source_urls", [])}),
    "all_resolved_params": [p for r in results for p in r.get("resolved_params", [])],
    "all_traps": [t for r in results for t in r.get("traps", [])],
    "all_robustness_notes": [n for r in results for n in r.get("robustness_notes", [])],
}

log(
    f"Researched {summary['items_researched']} item(s): "
    f"{len(summary['all_source_urls'])} source URLs, "
    f"{len(summary['all_resolved_params'])} resolved params, "
    f"{len(summary['all_traps'])} traps, "
    f"{len(summary['all_robustness_notes'])} robustness upgrades."
)
print(json.dumps(summary, indent=2, ensure_ascii=False))

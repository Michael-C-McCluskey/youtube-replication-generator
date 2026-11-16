#!/usr/bin/env python3
"""
YouTube Replication Generator Evolution & Versioning Engine (yt_evolve.py).

Allows the generator logic to learn from completed sub-projects without breaking
any projects currently in progress:
1. `record-lesson`: Captures a verified lesson learned into `evolution/LESSONS_LEARNED.json`
   and regenerates `evolution/EVOLUTION_LOG.md`.
2. `query`: Queries past lessons by archetype or keyword so new Stage 1 plans
   automatically inherit prior experience.
3. `bump-version`: Archives an immutable snapshot of `templates/` and `docs/` under
   `versions/v<X.Y.Z>/`, updates `VERSION` and `CHANGELOG.md`, and leaves all
   in-progress projects pinned to their original `generator_version`.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Dict, List, Optional


class EvolutionError(Exception):
    """Raised on invalid version bumps or malformed evolution inputs."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class EvolutionManager:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.version_file = self.root_dir / "VERSION"
        self.changelog_file = self.root_dir / "CHANGELOG.md"
        self.versions_dir = self.root_dir / "versions"
        self.evolution_dir = self.root_dir / "evolution"
        self.lessons_file = self.evolution_dir / "LESSONS_LEARNED.json"
        self.evolution_log_file = self.evolution_dir / "EVOLUTION_LOG.md"

    def get_current_version(self) -> str:
        if not self.version_file.exists():
            return "1.0.0"
        return self.version_file.read_text(encoding="utf-8").strip()

    def load_lessons(self) -> Dict[str, Any]:
        if not self.lessons_file.exists():
            return {"schema_version": "1.0", "lessons": []}
        return json.loads(self.lessons_file.read_text(encoding="utf-8"))

    def save_lessons(self, data: Dict[str, Any]) -> None:
        self.evolution_dir.mkdir(parents=True, exist_ok=True)
        self.lessons_file.write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        self.sync_evolution_log(data)

    def record_lesson(
        self,
        project: str,
        archetype: str,
        category: str,
        title: str,
        problem: str,
        solution: str,
    ) -> Dict[str, Any]:
        data = self.load_lessons()
        next_idx = len(data["lessons"]) + 1
        lesson = {
            "id": f"L-{next_idx:03d}",
            "source_project": project.strip(),
            "archetype": archetype.strip(),
            "category": category.strip(),
            "title": title.strip(),
            "problem": problem.strip(),
            "solution": solution.strip(),
            "generator_version_added": self.get_current_version(),
            "created_at": utc_now_iso(),
        }
        data["lessons"].append(lesson)
        self.save_lessons(data)
        return lesson

    def query_lessons(
        self, archetype: Optional[str] = None, keyword: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        data = self.load_lessons()
        results: List[Dict[str, Any]] = []
        arch_q = archetype.lower().strip() if archetype else ""
        kw_q = keyword.lower().strip() if keyword else ""

        for lesson in data["lessons"]:
            lesson_arch = lesson.get("archetype", "").lower()
            if arch_q:
                if (
                    "all" not in lesson_arch
                    and arch_q not in lesson_arch
                    and lesson_arch not in arch_q
                ):
                    continue
            if kw_q:
                hay = " ".join(
                    [
                        lesson.get("title", ""),
                        lesson.get("problem", ""),
                        lesson.get("solution", ""),
                        lesson.get("category", ""),
                    ]
                ).lower()
                if kw_q not in hay:
                    continue
            results.append(lesson)
        return results

    def format_lessons_markdown(
        self, archetype: Optional[str] = None
    ) -> str:
        lessons = self.query_lessons(archetype=archetype)
        if not lessons:
            return "- *No prior lessons recorded for this archetype yet.*"
        lines = []
        for lsn in lessons:
            lines.append(
                f"- **`{lsn['id']}` ({lsn['archetype']} · {lsn['category']}) — {lsn['title']}**: "
                f"{lsn['solution']} *(Learned from `{lsn['source_project']}` in `v{lsn['generator_version_added']}`)*"
            )
        return "\n".join(lines)

    def sync_evolution_log(self, data: Dict[str, Any]) -> None:
        rows = []
        for lsn in data["lessons"]:
            rows.append(
                f"| `{lsn['id']}` | `{lsn['source_project']}` | {lsn['archetype']} | `{lsn['category']}` | {lsn['title']} | "
                f"**Problem:** {lsn['problem']}<br/>**Solution:** {lsn['solution']} | `v{lsn['generator_version_added']}` |"
            )
        table = (
            "\n".join(rows)
            if rows
            else "| — | — | — | — | No lessons recorded yet | — | — |"
        )
        content = f"""# Generator Evolution & Learning Log (`EVOLUTION_LOG.md`)

> **Auto-Synced by `scripts/yt_evolve.py` from [`LESSONS_LEARNED.json`](LESSONS_LEARNED.json)**
> Current Generator Version: **`v{self.get_current_version()}`** — Archived versions live in [`versions/`](../versions) so in-progress sub-projects stay pinned and unbroken.

---

## 1. Recorded Lessons Learned

| Lesson ID | Source Sub-Project | Archetype | Category | Title | Problem & Solution | Added In |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table}
"""
        self.evolution_dir.mkdir(parents=True, exist_ok=True)
        self.evolution_log_file.write_text(content, encoding="utf-8")

    def bump_version(self, new_version: str, summary: str) -> Dict[str, Any]:
        ver = new_version.lstrip("v").strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+", ver):
            raise EvolutionError(
                f"Version '{new_version}' must follow semantic versioning (e.g., 1.2.0)."
            )

        target_snapshot = self.versions_dir / f"v{ver}"
        if target_snapshot.exists():
            raise EvolutionError(
                f"Version snapshot '{target_snapshot}' already exists and is immutable."
            )

        target_snapshot.mkdir(parents=True, exist_ok=True)
        for folder in ("templates", "docs"):
            src = self.root_dir / folder
            if src.exists():
                shutil.copytree(src, target_snapshot / folder)
        (target_snapshot / "VERSION").write_text(ver + "\n", encoding="utf-8")

        old_ver = self.get_current_version()
        self.version_file.write_text(ver + "\n", encoding="utf-8")

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_entry = f"""## [{ver}] - {today}
### Evolved From `v{old_ver}`
- {summary.strip()}
- Immutable snapshot archived at `versions/v{ver}/`. Existing in-progress sub-projects remain safely pinned to their original `generator_version`.

"""
        if self.changelog_file.exists():
            existing = self.changelog_file.read_text(encoding="utf-8")
            marker = "---\n\n"
            if marker in existing:
                head, tail = existing.split(marker, 1)
                self.changelog_file.write_text(
                    head + marker + new_entry + tail, encoding="utf-8"
                )
            else:
                self.changelog_file.write_text(
                    existing + "\n" + new_entry, encoding="utf-8"
                )
        else:
            self.changelog_file.write_text(
                f"# Generator Changelog\n\n---\n\n{new_entry}", encoding="utf-8"
            )

        return {
            "previous_version": old_ver,
            "new_version": ver,
            "snapshot_dir": str(target_snapshot),
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="YouTube Replication Generator Evolution & Versioning CLI"
    )
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Repository root directory",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record-lesson", help="Record a new verified lesson learned")
    rec.add_argument("--project", required=True, help="Source sub-project ID-slug")
    rec.add_argument("--archetype", required=True, help="Target archetype (e.g., Archetype B/C)")
    rec.add_argument("--category", required=True, help="Lesson category (e.g., off-camera-trap)")
    rec.add_argument("--title", required=True, help="Short descriptive title")
    rec.add_argument("--problem", required=True, help="What failed or was under-specified")
    rec.add_argument("--solution", required=True, help="Verified reusable solution")

    qry = sub.add_parser("query", help="Query past lessons by archetype or keyword")
    qry.add_argument("--archetype", default=None, help="Archetype filter")
    qry.add_argument("--keyword", default=None, help="Keyword filter")

    bmp = sub.add_parser(
        "bump-version",
        help="Snapshot current templates/docs into versions/vX.Y.Z/ and bump VERSION",
    )
    bmp.add_argument("new_version", help="Semantic version (e.g., 1.2.0)")
    bmp.add_argument("--summary", required=True, help="Summary of what the generator learned")

    args = parser.parse_args()
    mgr = EvolutionManager(Path(args.root))

    try:
        if args.command == "record-lesson":
            lesson = mgr.record_lesson(
                project=args.project,
                archetype=args.archetype,
                category=args.category,
                title=args.title,
                problem=args.problem,
                solution=args.solution,
            )
            print(json.dumps({"action": "recorded_lesson", "lesson": lesson}, indent=2))
        elif args.command == "query":
            lessons = mgr.query_lessons(archetype=args.archetype, keyword=args.keyword)
            print(json.dumps({"count": len(lessons), "lessons": lessons}, indent=2))
        elif args.command == "bump-version":
            res = mgr.bump_version(args.new_version, summary=args.summary)
            print(json.dumps({"action": "bumped_version", **res}, indent=2))
        return 0
    except EvolutionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

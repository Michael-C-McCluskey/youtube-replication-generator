#!/usr/bin/env python3
"""
YouTube Replication Generator Evolution & Versioning Engine (yt_evolve.py).

Allows the generator logic to learn from completed sub-projects without breaking
any projects currently in progress:
1. `record-lesson`: Captures a verified lesson learned into `evolution/LESSONS_LEARNED.json`
   and regenerates `evolution/EVOLUTION_LOG.md`.
2. `query`: Queries past lessons by archetype, category, confidence, or keyword so
   Stage 1 plans automatically inherit prior experience.
3. `refresh-lessons`: Updates the `<!-- LESSONS:START --> ... <!-- LESSONS:END -->`
   block in a sub-project's `RESEARCH_SYNTHESIS.md` once Stage 1.1 classifies its archetype.
4. `validate-stage1`: Runs cross-file Stage 1 gap-to-research traceability checks.
5. `bump-version`: Enforces monotonic semver, archives an immutable snapshot of
   `templates/`, `docs/`, `scripts/`, and `evolution/LESSONS_LEARNED.json` under
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
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


ALLOWED_CATEGORIES = {
    "off-camera-trap",
    "parameter-formula",
    "bom-substitution",
    "research-resilience",
    "monetization-cold-start",
    "verification-gap",
}

CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


class EvolutionError(Exception):
    """Raised on invalid version bumps or malformed evolution inputs."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_semver(version_str: str) -> Tuple[int, int, int]:
    ver = version_str.lstrip("v").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", ver):
        raise EvolutionError(
            f"Version '{version_str}' must follow semantic versioning (e.g., 1.3.0)."
        )
    major, minor, patch = (int(part) for part in ver.split("."))
    return (major, minor, patch)


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
            return {"schema_version": "1.1", "lessons": []}
        return json.loads(self.lessons_file.read_text(encoding="utf-8"))

    def save_lessons(self, data: Dict[str, Any]) -> None:
        self.evolution_dir.mkdir(parents=True, exist_ok=True)
        self.lessons_file.write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        self.sync_evolution_log(data)

    def _next_lesson_id(self, lessons: List[Dict[str, Any]]) -> str:
        max_num = 0
        for lsn in lessons:
            m = re.match(r"^L-(\d+)$", str(lsn.get("id", "")).strip())
            if m:
                max_num = max(max_num, int(m.group(1)))
        return f"L-{max_num + 1:03d}"

    def record_lesson(
        self,
        project: str,
        archetype: str,
        category: str,
        title: str,
        problem: str,
        solution: str,
        confidence: str = "medium",
        evidence: str = "",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        clean_cat = category.strip().lower()
        if clean_cat not in ALLOWED_CATEGORIES:
            raise EvolutionError(
                f"Invalid lesson category '{category}'. Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}"
            )
        clean_conf = confidence.strip().lower()
        if clean_conf not in CONFIDENCE_RANK:
            raise EvolutionError(
                f"Invalid confidence '{confidence}'. Allowed: high, medium, low"
            )

        data = self.load_lessons()
        norm_title = re.sub(r"\s+", " ", title.strip().lower())
        norm_arch = re.sub(r"\s+", " ", archetype.strip().lower())
        for existing in data["lessons"]:
            if existing.get("status", "active") != "active":
                continue
            ex_title = re.sub(r"\s+", " ", existing.get("title", "").strip().lower())
            ex_arch = re.sub(r"\s+", " ", existing.get("archetype", "").strip().lower())
            if ex_title == norm_title and ex_arch == norm_arch:
                existing["problem"] = problem.strip()
                existing["solution"] = solution.strip()
                existing["confidence"] = clean_conf
                if evidence.strip():
                    existing["evidence"] = evidence.strip()
                if tags:
                    existing["tags"] = [t.strip() for t in tags if t.strip()]
                existing["updated_at"] = utc_now_iso()
                self.save_lessons(data)
                return existing

        lesson = {
            "id": self._next_lesson_id(data["lessons"]),
            "source_project": project.strip(),
            "archetype": archetype.strip(),
            "category": clean_cat,
            "title": title.strip(),
            "problem": problem.strip(),
            "solution": solution.strip(),
            "confidence": clean_conf,
            "evidence": evidence.strip(),
            "tags": [t.strip() for t in (tags or []) if t.strip()],
            "status": "active",
            "generator_version_added": self.get_current_version(),
            "created_at": utc_now_iso(),
        }
        data["lessons"].append(lesson)
        self.save_lessons(data)
        return lesson

    def query_lessons(
        self,
        archetype: Optional[str] = None,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        min_confidence: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        data = self.load_lessons()
        scored: List[Tuple[int, str, Dict[str, Any]]] = []
        arch_q = archetype.lower().strip() if archetype else ""
        kw_q = keyword.lower().strip() if keyword else ""
        cat_q = category.lower().strip() if category else ""
        min_rank = CONFIDENCE_RANK.get(min_confidence.lower().strip(), 0) if min_confidence else 0

        for lesson in data["lessons"]:
            if lesson.get("status", "active") != "active":
                continue
            conf_val = CONFIDENCE_RANK.get(str(lesson.get("confidence", "medium")).lower(), 2)
            if conf_val < min_rank:
                continue
            if cat_q and lesson.get("category", "").lower() != cat_q:
                continue

            lesson_arch = lesson.get("archetype", "").lower()
            score = conf_val * 10
            if arch_q:
                if "all" in lesson_arch:
                    score += 10
                elif arch_q in lesson_arch or lesson_arch in arch_q:
                    score += 30
                else:
                    # Also match Archetype letter e.g. "Archetype B" vs "B"
                    arch_letters = set(re.findall(r"\b([a-d])\b", arch_q))
                    lesson_letters = set(re.findall(r"\b([a-d])\b", lesson_arch))
                    if arch_letters and (arch_letters & lesson_letters):
                        score += 25
                    else:
                        continue

            if kw_q:
                hay = " ".join(
                    [
                        lesson.get("title", ""),
                        lesson.get("problem", ""),
                        lesson.get("solution", ""),
                        lesson.get("category", ""),
                        " ".join(lesson.get("tags", [])),
                    ]
                ).lower()
                if kw_q not in hay:
                    continue
                score += 15

            scored.append((score, lesson.get("id", ""), lesson))

        scored.sort(key=lambda item: (-item[0], item[1]))
        results = [item[2] for item in scored]
        if limit is not None and limit > 0:
            results = results[:limit]
        return results

    def format_lessons_markdown(
        self, archetype: Optional[str] = None, limit: Optional[int] = 10
    ) -> str:
        lessons = self.query_lessons(archetype=archetype, limit=limit)
        if not lessons:
            return "- *No prior lessons recorded for this archetype yet.*"
        lines = []
        for lsn in lessons:
            conf = str(lsn.get("confidence", "medium")).upper()
            lines.append(
                f"- **`{lsn['id']}` ({lsn['archetype']} · {lsn['category']} · {conf}) — {lsn['title']}**: "
                f"{lsn['solution']} *(Learned from `{lsn['source_project']}` in `v{lsn['generator_version_added']}`)*"
            )
        return "\n".join(lines)

    def refresh_project_lessons(
        self, project_dir: Path, archetype: str, limit: int = 10
    ) -> int:
        res_path = project_dir / "RESEARCH_SYNTHESIS.md"
        if not res_path.exists():
            raise EvolutionError(f"Missing RESEARCH_SYNTHESIS.md in {project_dir}")
        lessons = self.query_lessons(archetype=archetype, limit=limit)
        md_block = self.format_lessons_markdown(archetype=archetype, limit=limit)
        text = res_path.read_text(encoding="utf-8")
        start_marker = "<!-- LESSONS:START -->"
        end_marker = "<!-- LESSONS:END -->"
        if start_marker in text and end_marker in text:
            pattern = re.compile(
                re.escape(start_marker) + r".*?" + re.escape(end_marker),
                re.DOTALL,
            )
            replacement = f"{start_marker}\n{md_block}\n{end_marker}"
            updated = pattern.sub(replacement, text, count=1)
            res_path.write_text(updated, encoding="utf-8")
        return len(lessons)

    def validate_stage1(self, project_dir: Path) -> List[str]:
        """Cross-checks Stage 1 Gap-to-Research traceability and placeholder hygiene."""
        errors: List[str] = []
        decon_path = project_dir / "DECONSTRUCTION.md"
        res_path = project_dir / "RESEARCH_SYNTHESIS.md"
        bp_path = project_dir / "REPLICATION_BLUEPRINT.md"

        if not decon_path.exists() or not res_path.exists() or not bp_path.exists():
            return ["Missing one or more required Stage 1 markdown files."]

        decon_txt = decon_path.read_text(encoding="utf-8")
        res_txt = res_path.read_text(encoding="utf-8")
        bp_txt = bp_path.read_text(encoding="utf-8")

        # Every Gap #N in DECONSTRUCTION.md must appear in RESEARCH_SYNTHESIS.md
        decon_gaps = sorted(set(re.findall(r"Gap\s+#(\d+)", decon_txt)))
        for gid in decon_gaps:
            if not re.search(rf"Gap\s+#{gid}\b", res_txt):
                errors.append(
                    f"Gap #{gid} from DECONSTRUCTION.md is missing in RESEARCH_SYNTHESIS.md."
                )

        # Unresolved [UNSPECIFIED - Verify before starting] must not leak into RESEARCH_SYNTHESIS/BLUEPRINT
        # except inside the Summary Table baseline column or explicit references.
        if "[UNSPECIFIED - Verify before starting]" in bp_txt:
            errors.append(
                "REPLICATION_BLUEPRINT.md still contains unresolved '[UNSPECIFIED - Verify before starting]'."
            )

        # Each ### Gap #N heading in RESEARCH_SYNTHESIS.md should declare Confidence:
        gap_sections = re.split(r"^###\s+Gap\s+#\d+.*$", res_txt, flags=re.MULTILINE)
        if len(gap_sections) > 1:
            for idx, sec in enumerate(gap_sections[1:], start=1):
                if "Confidence" not in sec:
                    errors.append(
                        f"RESEARCH_SYNTHESIS.md Gap section #{idx} is missing a 'Confidence:' rating."
                    )

        return errors

    def sync_evolution_log(self, data: Dict[str, Any]) -> None:
        rows = []
        for lsn in data["lessons"]:
            conf = str(lsn.get("confidence", "medium")).upper()
            rows.append(
                f"| `{lsn['id']}` | `{lsn['source_project']}` | {lsn['archetype']} | `{lsn['category']}` | {conf} | {lsn['title']} | "
                f"**Problem:** {lsn['problem']}<br/>**Solution:** {lsn['solution']} | `v{lsn['generator_version_added']}` |"
            )
        table = (
            "\n".join(rows)
            if rows
            else "| — | — | — | — | — | No lessons recorded yet | — | — |"
        )
        content = f"""# Generator Evolution & Learning Log (`EVOLUTION_LOG.md`)

> **Auto-Synced by `scripts/yt_evolve.py` from [`LESSONS_LEARNED.json`](LESSONS_LEARNED.json)**
> Current Generator Version: **`v{self.get_current_version()}`** — Archived versions live in [`versions/`](../versions) so in-progress sub-projects stay pinned and unbroken.

---

## 1. Recorded Lessons Learned

| Lesson ID | Source Sub-Project | Archetype | Category | Confidence | Title | Problem & Solution | Added In |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table}
"""
        self.evolution_dir.mkdir(parents=True, exist_ok=True)
        self.evolution_log_file.write_text(content, encoding="utf-8")

    def bump_version(self, new_version: str, summary: str) -> Dict[str, Any]:
        ver = new_version.lstrip("v").strip()
        new_tuple = parse_semver(ver)
        old_ver = self.get_current_version()
        old_tuple = parse_semver(old_ver)

        if new_tuple <= old_tuple:
            raise EvolutionError(
                f"New version '{ver}' must be strictly greater than current version '{old_ver}'."
            )

        target_snapshot = self.versions_dir / f"v{ver}"
        if target_snapshot.exists():
            raise EvolutionError(
                f"Version snapshot '{target_snapshot}' already exists and is immutable."
            )

        target_snapshot.mkdir(parents=True, exist_ok=True)
        for folder in ("templates", "docs", "scripts"):
            src = self.root_dir / folder
            if src.exists():
                shutil.copytree(
                    src,
                    target_snapshot / folder,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
        if self.lessons_file.exists():
            (target_snapshot / "evolution").mkdir(parents=True, exist_ok=True)
            shutil.copy2(
                self.lessons_file, target_snapshot / "evolution" / "LESSONS_LEARNED.json"
            )
        (target_snapshot / "VERSION").write_text(ver + "\n", encoding="utf-8")

        self.version_file.write_text(ver + "\n", encoding="utf-8")

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_entry = f"""## [{ver}] - {today}
### Evolved From `v{old_ver}`
- {summary.strip()}
- Immutable snapshot archived at `versions/v{ver}/` (`templates/`, `docs/`, `scripts/`, `evolution/LESSONS_LEARNED.json`). Existing in-progress sub-projects remain safely pinned to their original `generator_version`.

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
    rec.add_argument(
        "--category",
        required=True,
        help=f"Lesson category ({', '.join(sorted(ALLOWED_CATEGORIES))})",
    )
    rec.add_argument("--title", required=True, help="Short descriptive title")
    rec.add_argument("--problem", required=True, help="What failed or was under-specified")
    rec.add_argument("--solution", required=True, help="Verified reusable solution")
    rec.add_argument(
        "--confidence",
        default="medium",
        choices=["high", "medium", "low"],
        help="Confidence level of this lesson",
    )
    rec.add_argument("--evidence", default="", help="Supporting URL or file path")
    rec.add_argument("--tags", default="", help="Comma-separated tags")

    qry = sub.add_parser("query", help="Query past lessons by archetype or keyword")
    qry.add_argument("--archetype", default=None, help="Archetype filter")
    qry.add_argument("--keyword", default=None, help="Keyword filter")
    qry.add_argument("--category", default=None, help="Category filter")
    qry.add_argument("--min-confidence", default=None, choices=["high", "medium", "low"])
    qry.add_argument("--limit", type=int, default=None, help="Maximum lessons to return")

    ref = sub.add_parser(
        "refresh-lessons",
        help="Re-inject archetype-matched lessons into a sub-project's RESEARCH_SYNTHESIS.md",
    )
    ref.add_argument("--project-dir", required=True, help="Path to replications/<NNN>-<slug>/")
    ref.add_argument("--archetype", required=True, help="Classified archetype")
    ref.add_argument("--limit", type=int, default=10, help="Max lessons to inject")

    val = sub.add_parser(
        "validate-stage1",
        help="Validate Stage 1 gap-to-research traceability for a sub-project",
    )
    val.add_argument("--project-dir", required=True, help="Path to replications/<NNN>-<slug>/")

    bmp = sub.add_parser(
        "bump-version",
        help="Snapshot current templates/docs/scripts into versions/vX.Y.Z/ and bump VERSION",
    )
    bmp.add_argument("new_version", help="Semantic version (e.g., 1.3.0)")
    bmp.add_argument("--summary", required=True, help="Summary of what the generator learned")

    args = parser.parse_args()
    mgr = EvolutionManager(Path(args.root))

    try:
        if args.command == "record-lesson":
            tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
            lesson = mgr.record_lesson(
                project=args.project,
                archetype=args.archetype,
                category=args.category,
                title=args.title,
                problem=args.problem,
                solution=args.solution,
                confidence=args.confidence,
                evidence=args.evidence,
                tags=tags,
            )
            print(json.dumps({"action": "recorded_lesson", "lesson": lesson}, indent=2))
        elif args.command == "query":
            lessons = mgr.query_lessons(
                archetype=args.archetype,
                keyword=args.keyword,
                category=args.category,
                min_confidence=args.min_confidence,
                limit=args.limit,
            )
            print(json.dumps({"count": len(lessons), "lessons": lessons}, indent=2))
        elif args.command == "refresh-lessons":
            count = mgr.refresh_project_lessons(
                Path(args.project_dir), archetype=args.archetype, limit=args.limit
            )
            print(json.dumps({"action": "refreshed_lessons", "count": count}, indent=2))
        elif args.command == "validate-stage1":
            errs = mgr.validate_stage1(Path(args.project_dir))
            if errs:
                print(json.dumps({"valid": False, "errors": errs}, indent=2))
                return 1
            print(json.dumps({"valid": True, "errors": []}, indent=2))
        elif args.command == "bump-version":
            res = mgr.bump_version(args.new_version, summary=args.summary)
            print(json.dumps({"action": "bumped_version", **res}, indent=2))
        return 0
    except EvolutionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

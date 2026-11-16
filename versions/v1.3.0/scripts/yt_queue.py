#!/usr/bin/env python3
"""
YouTube Replication Project Generator & Sequential Queue Manager (yt_queue.py).

Enforces the Two-Stage Workflow, Version Pinning, Content-Aware Linting, and Evolution Loop:
1. Stage 1 (Deconstruct + Deep Gap Research + Customization Brief + Blueprint + Agent Instructions):
   - `add <youtube_url> --slug <slug> [--intent "..."]` scaffolds `replications/<NNN>-<slug>/`,
     pins `generator_version` + `plan_version=1`, and injects prior lessons from
     `evolution/LESSONS_LEARNED.json`.
   - `sync-lessons <id> --archetype "<arch>"` updates archetype & refreshes injected lessons.
   - `lint-plan <id>` runs strict Stage 1 placeholder, Tier 4, and gap-traceability checks.
   - `mark-planned <id>` snapshots Stage 1 files into `plans/v<N>/` and transitions
     to `STAGE_1_AWAITING_OK`.
   - `revise-plan <id> --reason "..."` archives the current plan to `plans/v<N>/`,
     increments `plan_version` to `N+1`, and prepares a safe revision without
     mutating prior versions or breaking other in-progress projects.
2. User Review & Approval ("OK"):
   - `approve <id>` transitions a reviewed project to `APPROVED_QUEUED`.
3. Stage 2 (Sequential Builder Execution — Strictly ONE Project at a Time):
   - `start-next [--resume]` enforces `max_concurrent_active = 1` (with `--resume` for crash recovery).
   - `active` / `pause <id>` inspect or pause the currently active build.
   - `mark-verified <id>` verifies `VERIFICATION_REPORT.md` and enters `SATISFACTION_GATE`.
   - `complete <id>` verifies `VERIFICATION_REPORT.md` + `STEP_BY_STEP_TUTORIAL.md`
     exist, marks the project `COMPLETED`, and releases the Single-Active-Project Lock.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from yt_evolve import EvolutionManager

VALID_STATES = [
    "STAGE_1_NEEDS_PLAN",
    "STAGE_1_AWAITING_OK",
    "APPROVED_QUEUED",
    "STAGE_2_IN_PROGRESS",
    "SATISFACTION_GATE",
    "COMPLETED",
]

STAGE_1_REQUIRED_FILES = [
    "DECONSTRUCTION.md",
    "RESEARCH_SYNTHESIS.md",
    "CUSTOMIZATION_BRIEF.md",
    "REPLICATION_BLUEPRINT.md",
    "AGENT_INSTRUCTIONS.md",
]

STAGE_1_SNAPSHOT_FILES = list(STAGE_1_REQUIRED_FILES)


class QueueError(Exception):
    """Raised when a queue state transition or lock constraint is violated."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_video_id(youtube_url: str) -> str:
    """Extracts the 11-character YouTube video ID from a URL or raw ID."""
    cleaned = youtube_url.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", cleaned):
        return cleaned
    parsed = urlparse(cleaned)
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        vid = parsed.path.lstrip("/").split("/")[0]
        if vid:
            return vid
    if parsed.query:
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]
    path_parts = [p for p in parsed.path.split("/") if p]
    for prefix in ("live", "shorts", "embed", "v"):
        if prefix in path_parts:
            idx = path_parts.index(prefix)
            if idx + 1 < len(path_parts):
                return path_parts[idx + 1]
    return "unknown_vid"


def sanitize_slug(raw_slug: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", raw_slug.lower().strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        raise QueueError("Slug cannot be empty after sanitization.")
    return slug


class ReplicationQueueManager:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.queue_file = self.root_dir / "QUEUE.json"
        self.lock_file = self.root_dir / "QUEUE.lock"
        self.replications_dir = self.root_dir / "replications"
        self.templates_dir = self.root_dir / "templates"
        self.index_file = self.replications_dir / "INDEX.md"
        self.evolution = EvolutionManager(self.root_dir)

    @contextmanager
    def _queue_lock(self) -> Iterator[None]:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        with open(self.lock_file, "a+", encoding="utf-8") as lock_fh:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)

    def _resolve_templates_dir(self, generator_version: Optional[str] = None) -> Path:
        if generator_version:
            pinned = self.root_dir / "versions" / f"v{generator_version}" / "templates"
            if pinned.exists():
                return pinned
        return self.templates_dir

    def load_queue(self) -> Dict[str, Any]:
        if not self.queue_file.exists():
            return {
                "schema_version": "1.2",
                "current_generator_version": self.evolution.get_current_version(),
                "max_concurrent_active": 1,
                "active_project_id": None,
                "projects": [],
            }
        data = json.loads(self.queue_file.read_text(encoding="utf-8"))
        data["current_generator_version"] = self.evolution.get_current_version()
        return data

    def save_queue(self, data: Dict[str, Any]) -> None:
        self.replications_dir.mkdir(parents=True, exist_ok=True)
        data["current_generator_version"] = self.evolution.get_current_version()
        payload = json.dumps(data, indent=2) + "\n"
        fd, tmp_name = tempfile.mkstemp(
            dir=str(self.root_dir), prefix=".QUEUE.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_fh:
                tmp_fh.write(payload)
            os.replace(tmp_name, self.queue_file)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        self.sync_index_md(data)

    def find_project(
        self, data: Dict[str, Any], identifier: str
    ) -> Dict[str, Any]:
        ident = identifier.strip().lower()
        for proj in data["projects"]:
            if (
                proj["id"].lower() == ident
                or proj["slug"].lower() == ident
                or f"{proj['id']}-{proj['slug']}".lower() == ident
                or proj.get("video_id", "").lower() == ident
            ):
                return proj
        raise QueueError(f"Project '{identifier}' not found in QUEUE.json.")

    def get_active_project(
        self, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        for proj in data["projects"]:
            if proj["status"] in ("STAGE_2_IN_PROGRESS", "SATISFACTION_GATE"):
                return proj
        return None

    def _write_plan_manifest(self, proj: Dict[str, Any], note: str) -> None:
        proj_dir = self.root_dir / proj["folder"]
        manifest_path = proj_dir / "PLAN_MANIFEST.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        else:
            manifest = {
                "project_id": proj["id"],
                "slug": proj["slug"],
                "pinned_generator_version": proj["generator_version"],
                "current_plan_version": proj["plan_version"],
                "revisions": [],
            }
        manifest["pinned_generator_version"] = proj["generator_version"]
        manifest["current_plan_version"] = proj["plan_version"]
        entry = {
            "plan_version": proj["plan_version"],
            "generator_version": proj["generator_version"],
            "snapshot_path": f"plans/v{proj['plan_version']}",
            "note": note,
            "timestamp": utc_now_iso(),
        }
        revisions = manifest.get("revisions", [])
        replaced = False
        for idx, rev in enumerate(revisions):
            if rev.get("plan_version") == proj["plan_version"]:
                revisions[idx] = entry
                replaced = True
                break
        if not replaced:
            revisions.append(entry)
        manifest["revisions"] = revisions
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    def _snapshot_plan_files(self, proj: Dict[str, Any], note: str) -> Path:
        proj_dir = self.root_dir / proj["folder"]
        ver = proj.get("plan_version", 1)
        snap_dir = proj_dir / "plans" / f"v{ver}"
        snap_dir.mkdir(parents=True, exist_ok=True)
        for fname in STAGE_1_SNAPSHOT_FILES:
            src = proj_dir / fname
            if src.exists():
                shutil.copy2(src, snap_dir / fname)
        self._write_plan_manifest(proj, note=note)
        return snap_dir

    def add_project(
        self,
        youtube_url: str,
        slug: str,
        title: str = "",
        archetype: str = "TBD (Classify in Stage 1.1)",
        timestamp_slice: str = "Full Video",
        user_intent: str = "",
    ) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            clean_slug = sanitize_slug(slug)
            video_id = extract_video_id(youtube_url)

            for existing in data["projects"]:
                if existing["slug"] == clean_slug:
                    raise QueueError(
                        f"A project with slug '{clean_slug}' already exists ({existing['id']})."
                    )

            existing_nums = [
                int(p["id"]) for p in data["projects"] if str(p.get("id", "")).isdigit()
            ]
            next_num = max(existing_nums, default=0) + 1
            project_id = f"{next_num:03d}"
            folder_name = f"{project_id}-{clean_slug}"
            project_rel_dir = f"replications/{folder_name}"
            project_abs_dir = self.root_dir / project_rel_dir

            for subdir in ("src", "configs", "data", "tests", "artifacts", "plans"):
                (project_abs_dir / subdir).mkdir(parents=True, exist_ok=True)

            gen_version = self.evolution.get_current_version()
            tmpl_dir = self._resolve_templates_dir(gen_version)
            prior_lessons_md = self.evolution.format_lessons_markdown(
                archetype=None if "TBD" in archetype else archetype
            )
            display_title = title.strip() or f"YouTube Replication {project_id} ({clean_slug})"
            clean_intent = (
                user_intent.strip()
                or f"Replicate the core workflow taught in {youtube_url.strip()} with clean local defaults."
            )
            replacements = {
                "{{PROJECT_ID}}": project_id,
                "{{SLUG}}": clean_slug,
                "{{YOUTUBE_URL}}": youtube_url.strip(),
                "{{VIDEO_ID}}": video_id,
                "{{TIMESTAMP_SLICE}}": timestamp_slice.strip() or "Full Video",
                "{{TITLE}}": display_title,
                "{{USER_INTENT}}": clean_intent,
                "{{GENERATOR_VERSION}}": gen_version,
                "{{PLAN_VERSION}}": "1",
                "{{PRIOR_LESSONS_INJECTED}}": prior_lessons_md,
            }

            template_map = {
                "DECONSTRUCTION.template.md": "DECONSTRUCTION.md",
                "RESEARCH_SYNTHESIS.template.md": "RESEARCH_SYNTHESIS.md",
                "CUSTOMIZATION_BRIEF.template.md": "CUSTOMIZATION_BRIEF.md",
                "REPLICATION_BLUEPRINT.template.md": "REPLICATION_BLUEPRINT.md",
                "AGENT_INSTRUCTIONS.template.md": "AGENT_INSTRUCTIONS.md",
                "VERIFICATION_REPORT.template.md": "VERIFICATION_REPORT.md",
                "RETROSPECTIVE.template.md": "RETROSPECTIVE.md",
            }
            for tmpl_name, target_name in template_map.items():
                tmpl_path = tmpl_dir / tmpl_name
                target_path = project_abs_dir / target_name
                if not target_path.exists():
                    if tmpl_path.exists():
                        content = tmpl_path.read_text(encoding="utf-8")
                        for k, v in replacements.items():
                            content = content.replace(k, v)
                    else:
                        content = f"# {target_name} ({project_id}-{clean_slug})\n\nTarget Video: {youtube_url}\n"
                    target_path.write_text(content, encoding="utf-8")

            now = utc_now_iso()
            project_entry = {
                "id": project_id,
                "slug": clean_slug,
                "folder": project_rel_dir,
                "youtube_url": youtube_url.strip(),
                "video_id": video_id,
                "timestamp_slice": timestamp_slice.strip() or "Full Video",
                "title": display_title,
                "user_intent": clean_intent,
                "archetype": archetype,
                "generator_version": gen_version,
                "plan_version": 1,
                "status": "STAGE_1_NEEDS_PLAN",
                "created_at": now,
                "updated_at": now,
                "approved_at": None,
                "started_at": None,
                "completed_at": None,
            }
            self._write_plan_manifest(project_entry, note="Initial scaffold")
            data["projects"].append(project_entry)
            self.save_queue(data)
            return project_entry

    def lint_stage_1(
        self, proj: Dict[str, Any], strict: bool = False, force_archive: bool = False
    ) -> List[str]:
        proj_dir = self.root_dir / proj["folder"]
        errors: List[str] = []

        for fname in STAGE_1_REQUIRED_FILES:
            fpath = proj_dir / fname
            if not fpath.exists() or fpath.stat().st_size < 50:
                errors.append(f"Missing or empty Stage 1 file: {fname}")
                continue
            txt = fpath.read_text(encoding="utf-8")
            unreplaced = re.findall(r"\{\{[A-Z0-9_]+\}\}", txt)
            if unreplaced:
                errors.append(
                    f"{fname} contains unreplaced template token(s): {', '.join(sorted(set(unreplaced)))}"
                )
            if strict:
                if re.search(r"(^|\n)[^\n]*:\s*\.\.\.\s*($|\n)", txt) or "| ... |" in txt:
                    errors.append(f"{fname} still contains unfilled '...' placeholder(s).")

        decon_path = proj_dir / "DECONSTRUCTION.md"
        if decon_path.exists():
            decon_txt = decon_path.read_text(encoding="utf-8")
            # Active Tier 4 verdict check (matches "**Verdict**: Tier 4" without the template choice list)
            if not force_archive and re.search(
                r"\*\*Verdict\*\*:\s*`?Tier 4\b(?![^`\n]*\|)", decon_txt, re.IGNORECASE
            ):
                errors.append(
                    "DECONSTRUCTION.md has a Tier 4 (Non-Replicable Hard Stop) verdict. Cannot proceed without --force-archive."
                )

        if strict:
            errors.extend(self.evolution.validate_stage1(proj_dir))
            bp_path = proj_dir / "REPLICATION_BLUEPRINT.md"
            if bp_path.exists():
                bp_txt = bp_path.read_text(encoding="utf-8")
                if "[MECHANIC]" not in bp_txt and "[AESTHETIC]" not in bp_txt:
                    errors.append(
                        "REPLICATION_BLUEPRINT.md must tag steps with [MECHANIC] or [AESTHETIC]."
                    )
                if "*Critical Parameter:*" not in bp_txt or "*Verification:*" not in bp_txt:
                    errors.append(
                        "REPLICATION_BLUEPRINT.md steps must include '*Critical Parameter:*' and '*Verification:*'."
                    )
        return errors

    def lint_verification(self, proj: Dict[str, Any], strict: bool = False) -> List[str]:
        proj_dir = self.root_dir / proj["folder"]
        errors: List[str] = []
        ver_file = proj_dir / "VERIFICATION_REPORT.md"
        if not ver_file.exists() or ver_file.stat().st_size < 50:
            return [f"Missing or empty {proj['folder']}/VERIFICATION_REPORT.md"]
        txt = ver_file.read_text(encoding="utf-8")
        unreplaced = re.findall(r"\{\{[A-Z0-9_]+\}\}", txt)
        if unreplaced:
            errors.append(
                f"VERIFICATION_REPORT.md contains unreplaced token(s): {', '.join(sorted(set(unreplaced)))}"
            )
        if strict:
            if "| ... |" in txt or re.search(r":\s*\.\.\.\s*$", txt, re.MULTILINE):
                errors.append("VERIFICATION_REPORT.md still contains unfilled '...' placeholders.")
            if re.search(r"-\s*\[\s\]\s+", txt):
                errors.append("VERIFICATION_REPORT.md has unchecked '- [ ]' checklist items.")
            # Parse 4-dimension scores if present
            score_patterns = {
                "Pattern & Process Fidelity": 90.0,
                "User-Spin & Customization Execution": 90.0,
                "UX, Polish & Adaptability": 80.0,
                "Data, Robustness & Teachability": 85.0,
                "Weighted Overall Score": 85.0,
            }
            for label, floor in score_patterns.items():
                m = re.search(
                    rf"\*\*{re.escape(label)}\*\*[^|\n]*\|[^|\n]*\|[^|\n]*?(\d+(?:\.\d+)?)",
                    txt,
                )
                if not m:
                    errors.append(f"VERIFICATION_REPORT.md missing numeric score for '{label}'.")
                else:
                    val = float(m.group(1))
                    if val < floor:
                        errors.append(
                            f"VERIFICATION_REPORT.md '{label}' score {val} is below pass threshold {floor}."
                        )
        return errors

    def _verify_stage_1_files(
        self, proj: Dict[str, Any], strict: bool = False, force_archive: bool = False
    ) -> None:
        errors = self.lint_stage_1(proj, strict=strict, force_archive=force_archive)
        if errors:
            raise QueueError(
                f"Cannot complete Stage 1 for '{proj['id']}-{proj['slug']}': "
                + "; ".join(errors)
            )

    def sync_lessons(self, identifier: str, archetype: str) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            proj = self.find_project(data, identifier)
            proj["archetype"] = archetype.strip()
            proj["updated_at"] = utc_now_iso()
            proj_dir = self.root_dir / proj["folder"]
            count = self.evolution.refresh_project_lessons(proj_dir, archetype=archetype)
            self.save_queue(data)
            return {"project": proj, "lessons_injected": count}

    def mark_planned(
        self, identifier: str, strict: bool = False, force_archive: bool = False
    ) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            proj = self.find_project(data, identifier)
            self._verify_stage_1_files(proj, strict=strict, force_archive=force_archive)
            if "plan_version" not in proj:
                proj["plan_version"] = 1
            if "generator_version" not in proj:
                proj["generator_version"] = self.evolution.get_current_version()
            self._snapshot_plan_files(proj, note="Stage 1 plan frozen for user review")
            proj["status"] = "STAGE_1_AWAITING_OK"
            proj["updated_at"] = utc_now_iso()
            self.save_queue(data)
            return proj

    def revise_plan(self, identifier: str, reason: str) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            proj = self.find_project(data, identifier)
            if proj["status"] in ("STAGE_2_IN_PROGRESS", "SATISFACTION_GATE", "COMPLETED"):
                raise QueueError(
                    f"Cannot revise plan for '{proj['id']}-{proj['slug']}' while in '{proj['status']}' — in-progress/completed builds stay pinned to protect execution."
                )
            self._snapshot_plan_files(
                proj, note=f"Archived before revision: {reason.strip()}"
            )
            proj["plan_version"] = proj.get("plan_version", 1) + 1
            proj["status"] = "STAGE_1_NEEDS_PLAN"
            proj["updated_at"] = utc_now_iso()
            self.save_queue(data)
            return proj

    def approve_project(
        self, identifier: str, strict: bool = False, force_archive: bool = False
    ) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            proj = self.find_project(data, identifier)
            if proj["status"] not in ("STAGE_1_AWAITING_OK", "STAGE_1_NEEDS_PLAN"):
                raise QueueError(
                    f"Project '{proj['id']}-{proj['slug']}' is in status '{proj['status']}' and cannot be approved."
                )
            self._verify_stage_1_files(proj, strict=strict, force_archive=force_archive)
            snap_dir = (
                self.root_dir
                / proj["folder"]
                / "plans"
                / f"v{proj.get('plan_version', 1)}"
            )
            if not snap_dir.exists():
                self._snapshot_plan_files(proj, note="Auto-snapshotted on approval")
            now = utc_now_iso()
            proj["status"] = "APPROVED_QUEUED"
            proj["approved_at"] = now
            proj["updated_at"] = now
            self.save_queue(data)
            return proj

    def start_next(
        self, identifier: Optional[str] = None, resume: bool = False
    ) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            active = self.get_active_project(data)
            if active is not None:
                if resume and (
                    identifier is None
                    or identifier.strip().lower()
                    in (
                        active["id"].lower(),
                        active["slug"].lower(),
                        f"{active['id']}-{active['slug']}".lower(),
                    )
                ):
                    return active
                raise QueueError(
                    f"SINGLE-ACTIVE-PROJECT LOCK VIOLATION: Project '{active['id']}-{active['slug']}' is currently in '{active['status']}'. "
                    f"You must finish and mark '{active['id']}' as COMPLETED before starting another project (or pass --resume)."
                )

            if identifier:
                proj = self.find_project(data, identifier)
                if proj["status"] != "APPROVED_QUEUED":
                    raise QueueError(
                        f"Project '{proj['id']}-{proj['slug']}' has status '{proj['status']}'. Only 'APPROVED_QUEUED' projects (OK'd by the user) can be started."
                    )
            else:
                approved_list = [
                    p for p in data["projects"] if p["status"] == "APPROVED_QUEUED"
                ]
                if not approved_list:
                    raise QueueError(
                        "No projects are currently in 'APPROVED_QUEUED' status. Ask the user to review and 'OK' a planned project first."
                    )
                proj = approved_list[0]

            now = utc_now_iso()
            proj["status"] = "STAGE_2_IN_PROGRESS"
            proj["started_at"] = proj.get("started_at") or now
            proj["updated_at"] = now
            data["active_project_id"] = proj["id"]
            self.save_queue(data)
            return proj

    def pause_project(self, identifier: str) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            proj = self.find_project(data, identifier)
            if proj["status"] != "STAGE_2_IN_PROGRESS":
                raise QueueError(
                    f"Project '{proj['id']}-{proj['slug']}' must be in 'STAGE_2_IN_PROGRESS' to pause (current: '{proj['status']}')."
                )
            proj["status"] = "APPROVED_QUEUED"
            proj["updated_at"] = utc_now_iso()
            if data.get("active_project_id") == proj["id"]:
                data["active_project_id"] = None
            self.save_queue(data)
            return proj

    def mark_verified(self, identifier: str, strict: bool = False) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            proj = self.find_project(data, identifier)
            if proj["status"] != "STAGE_2_IN_PROGRESS":
                raise QueueError(
                    f"Project '{proj['id']}-{proj['slug']}' must be in 'STAGE_2_IN_PROGRESS' to mark verified (current: '{proj['status']}')."
                )
            errors = self.lint_verification(proj, strict=strict)
            if errors:
                raise QueueError(
                    "Cannot enter SATISFACTION_GATE: " + "; ".join(errors)
                )
            proj["status"] = "SATISFACTION_GATE"
            proj["updated_at"] = utc_now_iso()
            self.save_queue(data)
            return proj

    def complete_project(
        self, identifier: str, strict: bool = False
    ) -> Dict[str, Any]:
        with self._queue_lock():
            data = self.load_queue()
            proj = self.find_project(data, identifier)
            if proj["status"] not in ("SATISFACTION_GATE", "STAGE_2_IN_PROGRESS"):
                raise QueueError(
                    f"Project '{proj['id']}-{proj['slug']}' must be in 'SATISFACTION_GATE' or 'STAGE_2_IN_PROGRESS' to complete (current: '{proj['status']}')."
                )
            proj_dir = self.root_dir / proj["folder"]
            ver_errors = self.lint_verification(proj, strict=strict)
            if ver_errors:
                raise QueueError("Satisfaction Gate violation: " + "; ".join(ver_errors))

            tut_file = proj_dir / "STEP_BY_STEP_TUTORIAL.md"
            if not tut_file.exists() or tut_file.stat().st_size < 50:
                raise QueueError(
                    f"Tutorial requirement violation: '{proj['folder']}/STEP_BY_STEP_TUTORIAL.md' must be created as the final step before marking COMPLETED."
                )
            tut_txt = tut_file.read_text(encoding="utf-8")
            if re.search(r"\{\{[A-Z0-9_]+\}\}", tut_txt):
                raise QueueError(
                    f"'{proj['folder']}/STEP_BY_STEP_TUTORIAL.md' still contains unreplaced template tokens."
                )
            if strict:
                retro_file = proj_dir / "RETROSPECTIVE.md"
                if not retro_file.exists() or retro_file.stat().st_size < 50:
                    raise QueueError(
                        f"'{proj['folder']}/RETROSPECTIVE.md' must be completed before marking COMPLETED in strict mode."
                    )
                retro_txt = retro_file.read_text(encoding="utf-8")
                if "- **Worked on first pass**: ..." in retro_txt:
                    raise QueueError(
                        f"'{proj['folder']}/RETROSPECTIVE.md' still contains untouched boilerplate."
                    )

            now = utc_now_iso()
            proj["status"] = "COMPLETED"
            proj["completed_at"] = now
            proj["updated_at"] = now
            if data.get("active_project_id") == proj["id"]:
                data["active_project_id"] = None
            self.save_queue(data)
            return proj

    def sync_index_md(self, data: Dict[str, Any]) -> None:
        active = self.get_active_project(data)
        active_banner = (
            f"**Currently Active Build (`max_concurrent_active = 1`)**: `{active['id']}-{active['slug']}` (`{active['status']}` · pinned to `v{active.get('generator_version', '1.0.0')}` / `plan v{active.get('plan_version', 1)}`)"
            if active
            else "**Currently Active Build (`max_concurrent_active = 1`)**: `None (Ready to start next APPROVED_QUEUED project)`"
        )
        gen_ver = self.evolution.get_current_version()

        rows: List[str] = []
        for p in data["projects"]:
            folder_name = f"{p['id']}-{p['slug']}"
            stage1_links = (
                f"1. [DECONSTRUCTION.md]({folder_name}/DECONSTRUCTION.md)<br/>"
                f"2. [RESEARCH_SYNTHESIS.md]({folder_name}/RESEARCH_SYNTHESIS.md)<br/>"
                f"3. [CUSTOMIZATION_BRIEF.md]({folder_name}/CUSTOMIZATION_BRIEF.md)<br/>"
                f"4. [REPLICATION_BLUEPRINT.md]({folder_name}/REPLICATION_BLUEPRINT.md)<br/>"
                f"5. [AGENT_INSTRUCTIONS.md]({folder_name}/AGENT_INSTRUCTIONS.md)"
            )
            stage2_links = (
                f"6. [VERIFICATION_REPORT.md]({folder_name}/VERIFICATION_REPORT.md)<br/>"
                f"7. [STEP_BY_STEP_TUTORIAL.md]({folder_name}/STEP_BY_STEP_TUTORIAL.md)"
            )
            rows.append(
                f"| `{p['id']}` | [`{folder_name}/`]({folder_name}) | [{p['title']}]({p['youtube_url']}) (`{p['video_id']}`) | `v{p.get('generator_version', '1.0.0')}` | `v{p.get('plan_version', 1)}` | **{p['status']}** | {stage1_links} | {stage2_links} |"
            )

        table_body = (
            "\n".join(rows)
            if rows
            else "| — | — | No projects in queue | — | — | — | — | — |"
        )

        content = f"""# Master Catalog: YouTube Video Replication Sub-Projects

> **Auto-Synced by `scripts/yt_queue.py` from [`QUEUE.json`](../QUEUE.json)**
> **Current Generator Version**: `v{gen_ver}` ([`EVOLUTION_LOG.md`](../evolution/EVOLUTION_LOG.md) · [`versions/`](../versions))
> {active_banner}

---

## 1. Sub-Project Queue & Registry

| ID | Sub-Project Folder | YouTube Video | Pinned Gen Ver | Plan Ver | Queue Status | Stage 1: Video Info, Gap Research & Plan (Review First) | Stage 2: Verification & Final Tutorial |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{table_body}

---

## 2. Queue Lifecycle States & Version-Pinning Rules

1. **`STAGE_1_NEEDS_PLAN`** -> Created via `python3 scripts/yt_queue.py add "<youtube_url>" --slug "<slug>" --intent "<intent>"`. Pins `generator_version` (`v{gen_ver}`) and injects prior lessons from [`evolution/LESSONS_LEARNED.json`](../evolution/LESSONS_LEARNED.json).
2. **`STAGE_1_AWAITING_OK`** -> LLM has completed Stage 1 and called `python3 scripts/yt_queue.py mark-planned <id>`, which freezes an immutable snapshot under `plans/v<N>/`. **HARD STOP: Present 1-Screen Stage 1 Decision Card and wait for user "OK".**
3. **`APPROVED_QUEUED`** -> User has OK'd the plan (`python3 scripts/yt_queue.py approve <id>`). Waiting in line for Stage 2 execution.
4. **`STAGE_2_IN_PROGRESS`** -> Claimed via `python3 scripts/yt_queue.py start-next`. **Strictly ONE project may be in progress at a time (`max_concurrent_active = 1`).** Protected from global generator updates by its pinned `generator_version`.
5. **`SATISFACTION_GATE`** -> Code & tests verified and `VERIFICATION_REPORT.md` written (`python3 scripts/yt_queue.py mark-verified <id>`).
6. **`COMPLETED`** -> `STEP_BY_STEP_TUTORIAL.md` written (`python3 scripts/yt_queue.py complete <id>`). Record new lessons in [`evolution/LESSONS_LEARNED.json`](../evolution/LESSONS_LEARNED.json) via `scripts/yt_evolve.py record-lesson`.
"""
        self.replications_dir.mkdir(parents=True, exist_ok=True)
        self.index_file.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="YouTube Replication Sub-Project Generator & Sequential Queue Manager"
    )
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Repository root directory (defaults to parent of scripts/)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show queue summary and active lock status")
    subparsers.add_parser("active", help="Show currently active Stage 2 project if any")

    add_p = subparsers.add_parser(
        "add", help="Scaffold a new video sub-project in Stage 1"
    )
    add_p.add_argument("youtube_url", help="YouTube video URL")
    add_p.add_argument("--slug", required=True, help="Short kebab-case project slug")
    add_p.add_argument("--title", default="", help="Human-readable video/project title")
    add_p.add_argument(
        "--archetype",
        default="TBD (Classify in Stage 1.1)",
        help="Video archetype classification",
    )
    add_p.add_argument(
        "--slice",
        dest="timestamp_slice",
        default="Full Video",
        help="Timestamp slice (e.g., 02:15-08:40) for multi-project videos (Stage 0.5)",
    )
    add_p.add_argument(
        "--intent",
        dest="user_intent",
        default="",
        help="Original user prompt / inferred intent summary",
    )

    sync_p = subparsers.add_parser(
        "sync-lessons",
        help="Update project archetype and refresh RESEARCH_SYNTHESIS.md lessons",
    )
    sync_p.add_argument("identifier", help="Project ID (e.g., 002) or slug")
    sync_p.add_argument("--archetype", required=True, help="Classified archetype")

    lint_p = subparsers.add_parser(
        "lint-plan",
        help="Run strict Stage 1 and/or Verification linting on a sub-project",
    )
    lint_p.add_argument("identifier", help="Project ID (e.g., 002) or slug")
    lint_p.add_argument(
        "--include-verification",
        action="store_true",
        help="Also lint VERIFICATION_REPORT.md",
    )

    plan_p = subparsers.add_parser(
        "mark-planned",
        help="Verify Stage 1 files exist, snapshot plans/vN/, and transition to STAGE_1_AWAITING_OK",
    )
    plan_p.add_argument("identifier", help="Project ID (e.g., 002) or slug")
    plan_p.add_argument("--strict", action="store_true", help="Enforce strict placeholder & gap linting")
    plan_p.add_argument("--force-archive", action="store_true", help="Allow Tier 4 projects to be archived")

    rev_p = subparsers.add_parser(
        "revise-plan",
        help="Archive current plan to plans/vN/ and start a new plan revision (vN+1)",
    )
    rev_p.add_argument("identifier", help="Project ID (e.g., 002) or slug")
    rev_p.add_argument("--reason", required=True, help="Reason for plan revision")

    app_p = subparsers.add_parser(
        "approve", help="Mark a planned project as OK'd by the user (APPROVED_QUEUED)"
    )
    app_p.add_argument("identifier", help="Project ID (e.g., 002) or slug")
    app_p.add_argument("--strict", action="store_true", help="Enforce strict placeholder & gap linting")
    app_p.add_argument("--force-archive", action="store_true", help="Allow Tier 4 projects")

    start_p = subparsers.add_parser(
        "start-next",
        help="Start Stage 2 on the next APPROVED_QUEUED project (enforces max 1 active project)",
    )
    start_p.add_argument(
        "--id",
        dest="identifier",
        default=None,
        help="Optional specific project ID/slug to start (must be APPROVED_QUEUED)",
    )
    start_p.add_argument(
        "--resume",
        action="store_true",
        help="Return the currently active Stage 2 project if one is already running",
    )

    pause_p = subparsers.add_parser(
        "pause",
        help="Pause an active STAGE_2_IN_PROGRESS project back to APPROVED_QUEUED",
    )
    pause_p.add_argument("identifier", help="Project ID (e.g., 002) or slug")

    ver_p = subparsers.add_parser(
        "mark-verified",
        help="Verify VERIFICATION_REPORT.md exists and transition to SATISFACTION_GATE",
    )
    ver_p.add_argument("identifier", help="Project ID (e.g., 002) or slug")
    ver_p.add_argument("--strict", action="store_true", help="Enforce strict parity score & checklist linting")

    comp_p = subparsers.add_parser(
        "complete",
        help="Verify VERIFICATION_REPORT.md + STEP_BY_STEP_TUTORIAL.md exist, mark COMPLETED, and release lock",
    )
    comp_p.add_argument("identifier", help="Project ID (e.g., 002) or slug")
    comp_p.add_argument("--strict", action="store_true", help="Enforce strict verification & retrospective linting")

    args = parser.parse_args()
    mgr = ReplicationQueueManager(Path(args.root))

    try:
        if args.command == "status":
            data = mgr.load_queue()
            mgr.sync_index_md(data)
            active = mgr.get_active_project(data)
            summary = {
                "current_generator_version": data.get("current_generator_version"),
                "max_concurrent_active": data.get("max_concurrent_active", 1),
                "active_project": (
                    f"{active['id']}-{active['slug']} ({active['status']})"
                    if active
                    else None
                ),
                "counts_by_status": {
                    st: sum(1 for p in data["projects"] if p["status"] == st)
                    for st in VALID_STATES
                },
                "projects": [
                    {
                        "id": p["id"],
                        "slug": p["slug"],
                        "generator_version": p.get("generator_version", "1.0.0"),
                        "plan_version": p.get("plan_version", 1),
                        "status": p["status"],
                        "folder": p["folder"],
                        "youtube_url": p["youtube_url"],
                    }
                    for p in data["projects"]
                ],
            }
            print(json.dumps(summary, indent=2))
        elif args.command == "active":
            data = mgr.load_queue()
            active = mgr.get_active_project(data)
            print(
                json.dumps(
                    {
                        "active_project": active,
                        "instructions_path": f"{active['folder']}/AGENT_INSTRUCTIONS.md"
                        if active
                        else None,
                    },
                    indent=2,
                )
            )
        elif args.command == "add":
            proj = mgr.add_project(
                args.youtube_url,
                slug=args.slug,
                title=args.title,
                archetype=args.archetype,
                timestamp_slice=args.timestamp_slice,
                user_intent=args.user_intent,
            )
            print(json.dumps({"action": "added", "project": proj}, indent=2))
        elif args.command == "sync-lessons":
            res = mgr.sync_lessons(args.identifier, archetype=args.archetype)
            print(json.dumps({"action": "synced_lessons", **res}, indent=2))
        elif args.command == "lint-plan":
            data = mgr.load_queue()
            proj = mgr.find_project(data, args.identifier)
            errs = mgr.lint_stage_1(proj, strict=True)
            if args.include_verification:
                errs.extend(mgr.lint_verification(proj, strict=True))
            print(json.dumps({"valid": len(errs) == 0, "errors": errs}, indent=2))
            return 0 if not errs else 1
        elif args.command == "mark-planned":
            proj = mgr.mark_planned(
                args.identifier, strict=args.strict, force_archive=args.force_archive
            )
            print(json.dumps({"action": "marked_planned", "project": proj}, indent=2))
        elif args.command == "revise-plan":
            proj = mgr.revise_plan(args.identifier, reason=args.reason)
            print(json.dumps({"action": "plan_revision_started", "project": proj}, indent=2))
        elif args.command == "approve":
            proj = mgr.approve_project(
                args.identifier, strict=args.strict, force_archive=args.force_archive
            )
            print(json.dumps({"action": "approved_queued", "project": proj}, indent=2))
        elif args.command == "start-next":
            proj = mgr.start_next(args.identifier, resume=args.resume)
            print(
                json.dumps(
                    {
                        "action": "started_stage_2",
                        "project": proj,
                        "instructions_path": f"{proj['folder']}/AGENT_INSTRUCTIONS.md",
                    },
                    indent=2,
                )
            )
        elif args.command == "pause":
            proj = mgr.pause_project(args.identifier)
            print(json.dumps({"action": "paused", "project": proj}, indent=2))
        elif args.command == "mark-verified":
            proj = mgr.mark_verified(args.identifier, strict=args.strict)
            print(
                json.dumps({"action": "entered_satisfaction_gate", "project": proj}, indent=2)
            )
        elif args.command == "complete":
            proj = mgr.complete_project(args.identifier, strict=args.strict)
            print(json.dumps({"action": "completed", "project": proj}, indent=2))
        return 0
    except QueueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

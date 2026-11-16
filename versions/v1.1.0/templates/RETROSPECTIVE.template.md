# Post-Project Retrospective & Generator Evolution (`{{PROJECT_ID}}-{{SLUG}}`)

- **Project ID**: `{{PROJECT_ID}}`
- **Pinned Generator Version**: `v{{GENERATOR_VERSION}}`
- **Pinned Plan Version**: `v{{PLAN_VERSION}}`
- **Target Video URL**: {{YOUTUBE_URL}}

---

## 1. What Worked Smoothly vs. What Needed Iteration
- **Worked on first pass**: ...
- **Required debugging / iteration**: ...

## 2. New Off-Camera Traps or `[UNSPECIFIED]` Gaps Discovered
- **Gap / Trap**: ...
- **Verified Fix**: ...

## 3. Recommended Lessons to Promote to `evolution/LESSONS_LEARNED.json`
Run `python3 scripts/yt_evolve.py record-lesson ...` for each reusable insight:
```bash
python3 scripts/yt_evolve.py record-lesson \
  --project "{{PROJECT_ID}}-{{SLUG}}" \
  --archetype "Archetype B/C" \
  --category "off-camera-trap" \
  --title "Short descriptive title" \
  --problem "What broke or was missing in the video" \
  --solution "Exact verified fix to reuse in future sub-projects"
```
If templates or playbooks were improved based on this project, snapshot a new generator release without breaking in-progress projects:
```bash
python3 scripts/yt_evolve.py bump-version <X.Y.Z> --summary "What the generator learned from {{PROJECT_ID}}"
```

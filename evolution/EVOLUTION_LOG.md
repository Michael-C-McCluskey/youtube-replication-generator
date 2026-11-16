# Generator Evolution & Learning Log (`EVOLUTION_LOG.md`)

> **Auto-Synced by `scripts/yt_evolve.py` from [`LESSONS_LEARNED.json`](LESSONS_LEARNED.json)**
> Every completed sub-project feeds verified lessons, off-camera traps, and better defaults back into the generator—while [`versions/`](../versions) keeps older generator versions and in-progress project plans isolated and unbroken.

---

## 1. Recorded Lessons Learned

| Lesson ID | Source Sub-Project | Archetype | Category | Title | Problem & Solution | Added In |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `L-001` | `001-ai-niche-directory-side-hustle` | Archetype B/C | `off-camera-trap` | Negative-Override Precedence in AI Review Enrichment | **Problem:** Keyword matching or unconstrained LLM tagging on phrases like 'BYOB' produces false-positive filter badges when a venue policy actually states 'no BYOB' or '$500 outside kitchen cleanup fee'.<br/>**Solution:** Always pair positive pattern extraction with explicit negative-override rules and attach verbatim evidence sentences (`verified_evidence`) to every listing badge. | `v1.1.0` |
| `L-002` | `001-ai-niche-directory-side-hustle` | Archetype B/C | `monetization-cold-start` | Free-Lead-First Outreach Before Pitching $30/mo Featured Placements | **Problem:** Local businesses ignore cold $30/mo directory pitches when a brand-new site is in the Months 1-3 SEO Valley of Despair with low organic traffic.<br/>**Solution:** Capture early buyer leads via free local group posts + a 'Get 3 Free Quotes' modal, forward 1-2 real leads for free, and only pitch the $30/mo Featured Partner upgrade after proving lead value. | `v1.1.0` |
| `L-003` | `001-ai-niche-directory-side-hustle` | All Archetypes | `research-resilience` | Multi-Tier Web Fallback When Transcript Summary Sites Block Scraping | **Problem:** Third-party YouTube transcript/summary websites frequently block direct HTTP fetches or paywall full transcripts.<br/>**Solution:** Combine targeted `google_search` snippets with creator newsletters/blogs and `gh` repository searches in Stage 1.2 (`RESEARCH_SYNTHESIS.md`) rather than relying on a single transcript endpoint. | `v1.1.0` |

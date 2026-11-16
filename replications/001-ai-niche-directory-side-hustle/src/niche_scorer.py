#!/usr/bin/env python3
"""
Niche Filter-Gap Scorer (Resolves [UNSPECIFIED] Parameter #1).

Evaluates candidate directory niches against Chris Koerner's criteria:
1. Low Keyword Difficulty (KD <= 30)
2. Meaningful Search Demand (Volume >= 500/mo)
3. High Filter-Gap Uniqueness (Google Maps / Yelp lacks native filter for the user's primary pain point)
4. High Commercial Monetization Value ($30/mo Featured Upgrade + Lead Value + Display Ad RPM)
"""

from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any, Dict, List


def score_niche(candidate: Dict[str, Any]) -> Dict[str, Any]:
    kd = float(candidate["keyword_difficulty"])
    volume = float(candidate["monthly_search_volume"])
    filter_gap = float(candidate["filter_gap_index"])
    lead_value = float(candidate["estimated_lead_value_usd"])
    rpm = float(candidate["display_ad_rpm_usd"])

    # 1. Keyword Difficulty Component (0-30 pts): Full points at KD <= 10, linear decay up to KD 45, 0 above KD 45
    if kd <= 10:
        kd_score = 30.0
    elif kd <= 45:
        kd_score = max(0.0, (45.0 - kd) / 35.0 * 30.0)
    else:
        kd_score = 0.0

    # 2. Search Volume Component (0-25 pts): Sweet spot 500 - 10,000 searches/mo
    if volume < 100:
        vol_score = 0.0
    else:
        vol_score = min(25.0, (math.log10(volume) / math.log10(5000.0)) * 22.0)

    # 3. Filter-Gap Moat Component (0-25 pts)
    gap_score = max(0.0, min(1.0, filter_gap)) * 25.0

    # 4. Monetization Potential Component (0-20 pts): Combines lead value + display RPM
    lead_norm = min(1.0, lead_value / 50.0)
    rpm_norm = min(1.0, rpm / 20.0)
    mon_score = (0.65 * lead_norm + 0.35 * rpm_norm) * 20.0

    total_score = round(kd_score + vol_score + gap_score + mon_score, 2)
    passes_koerner_gate = (kd <= 30.0) and (volume >= 500.0) and (filter_gap >= 0.75)

    return {
        **candidate,
        "score_breakdown": {
            "kd_score_max_30": round(kd_score, 2),
            "volume_score_max_25": round(vol_score, 2),
            "filter_gap_score_max_25": round(gap_score, 2),
            "monetization_score_max_20": round(mon_score, 2),
        },
        "composite_opportunity_score": total_score,
        "passes_koerner_gate": passes_koerner_gate,
        "verdict": "BUILD IMMEDIATELY" if passes_koerner_gate and total_score >= 80 else (
            "VIABLE" if passes_koerner_gate else "REJECT (Fails KD/Filter-Gap Gate)"
        ),
    }


def run_niche_scoring(input_path: Path, output_path: Path) -> List[Dict[str, Any]]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    scored = [score_niche(c) for c in data["candidate_niches"]]
    scored.sort(key=lambda x: x["composite_opportunity_score"], reverse=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"ranked_niches": scored}, indent=2), encoding="utf-8")
    return scored


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    ranked = run_niche_scoring(
        base_dir / "data" / "candidate_niches.json",
        base_dir / "artifacts" / "niche_scores_report.json",
    )
    print(f"Scored {len(ranked)} candidate niches. Top winner: {ranked[0]['name']} ({ranked[0]['composite_opportunity_score']}/100)")

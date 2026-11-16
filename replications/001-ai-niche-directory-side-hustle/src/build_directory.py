#!/usr/bin/env python3
"""
Config-Driven Multi-Niche AI Directory Compiler (src/build_directory.py).

Compiles any niche JSON configuration into a full, self-contained interactive directory web app
with:
1. Enriched Filter-Gap listings & verbatim review evidence quotes
2. Validated Schema.org JSON-LD (@graph: WebSite, ItemList, EventVenue/LocalBusiness, FAQPage)
3. Three Monetization Flows ($30/mo Featured Upgrade Checkout, Multi-Vendor Lead Capture, Ad/Newsletter slots)
4. Live 10-Second Niche Switcher (CaterFree Venues <-> Estate Cleanout Pros)
5. Interactive 80/20 Power-Law Portfolio & 12-Month SEO Valley Simulator
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

from enrich_pipeline import enrich_niche_config
from niche_scorer import run_niche_scoring
from portfolio_simulator import simulate_vending_vs_directory_power_law
from schema_validator import generate_jsonld_schema, validate_jsonld_schema


def build_html_app(
    primary_enriched: Dict[str, Any],
    secondary_enriched: Dict[str, Any],
    primary_schema: Dict[str, Any],
    niche_scores: Any,
    portfolio_sim: Dict[str, Any],
) -> str:
    schema_json_str = json.dumps(primary_schema, indent=2)
    app_state_json = json.dumps(
        {
            "niches": {
                primary_enriched["slug"]: primary_enriched,
                secondary_enriched["slug"]: secondary_enriched,
            },
            "activeNicheSlug": primary_enriched["slug"],
            "nicheScores": niche_scores,
            "portfolioSim": portfolio_sim,
        }
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{primary_enriched['brand_name']} — {primary_enriched['tagline']}</title>
  <meta name="description" content="{primary_enriched['hero_subheadline']}" />
  <script type="application/ld+json" id="schema-jsonld">
{schema_json_str}
  </script>
  <style>
    :root {{
      --primary: {primary_enriched['primary_color']};
      --accent: {primary_enriched['accent_color']};
      --bg: #f8fafc;
      --surface: #ffffff;
      --text: #0f172a;
      --muted: #475569;
      --border: #e2e8f0;
      --gold-bg: #fef3c7;
      --gold-text: #92400e;
      --emerald-bg: #ecfdf5;
      --emerald-text: #065f46;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .topbar {{
      background: #0f172a;
      color: #f8fafc;
      padding: 0.65rem 1.25rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      font-size: 0.85rem;
      border-bottom: 1px solid #1e293b;
    }}
    .topbar-left {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }}
    .badge-pill {{
      background: #1e293b;
      color: #38bdf8;
      border: 1px solid #334155;
      padding: 0.2rem 0.6rem;
      border-radius: 999px;
      font-weight: 600;
      font-size: 0.75rem;
    }}
    .niche-switcher {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .niche-btn {{
      background: #1e293b;
      color: #cbd5e1;
      border: 1px solid #334155;
      padding: 0.3rem 0.7rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all 0.15s;
    }}
    .niche-btn.active {{
      background: #38bdf8;
      color: #0f172a;
      border-color: #38bdf8;
    }}
    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1rem 1.5rem;
      position: sticky;
      top: 0;
      z-index: 20;
    }}
    .nav-container {{
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }}
    .brand {{
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--primary);
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .nav-tabs {{
      display: flex;
      gap: 0.4rem;
      flex-wrap: wrap;
    }}
    .tab-btn {{
      background: transparent;
      border: 1px solid var(--border);
      color: var(--muted);
      padding: 0.45rem 0.85rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.85rem;
      cursor: pointer;
    }}
    .tab-btn.active {{
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
    }}
    .cta-group {{
      display: flex;
      gap: 0.5rem;
    }}
    .btn-primary {{
      background: var(--primary);
      color: #fff;
      border: none;
      padding: 0.5rem 0.95rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.85rem;
      cursor: pointer;
    }}
    .btn-accent {{
      background: var(--accent);
      color: #fff;
      border: none;
      padding: 0.5rem 0.95rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.85rem;
      cursor: pointer;
    }}
    .hero {{
      background: linear-gradient(135deg, #0f172a 0%, #134e4a 100%);
      color: #fff;
      padding: 2.5rem 1.5rem;
    }}
    .hero-inner {{
      max-width: 1200px;
      margin: 0 auto;
    }}
    .hero h1 {{
      font-size: 2rem;
      font-weight: 800;
      margin-bottom: 0.5rem;
      letter-spacing: -0.02em;
    }}
    .hero p {{
      color: #cbd5e1;
      max-width: 780px;
      font-size: 1rem;
      margin-bottom: 1.25rem;
    }}
    .search-bar {{
      display: grid;
      grid-template-columns: 1fr 220px auto;
      gap: 0.65rem;
      background: #fff;
      padding: 0.55rem;
      border-radius: 12px;
      max-width: 900px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }}
    @media (max-width: 720px) {{
      .search-bar {{ grid-template-columns: 1fr; }}
    }}
    .search-bar input, .search-bar select {{
      border: 1px solid var(--border);
      padding: 0.65rem 0.85rem;
      border-radius: 8px;
      font-size: 0.95rem;
      color: var(--text);
    }}
    .filter-strip {{
      max-width: 1200px;
      margin: 1rem auto 0;
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      align-items: center;
    }}
    .filter-pill {{
      background: rgba(255,255,255,0.12);
      color: #f8fafc;
      border: 1px solid rgba(255,255,255,0.24);
      padding: 0.4rem 0.8rem;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .filter-pill.active {{
      background: #10b981;
      color: #052e16;
      border-color: #10b981;
    }}
    main {{
      max-width: 1200px;
      margin: 1.5rem auto 3rem;
      padding: 0 1.5rem;
    }}
    .stats-bar {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding: 0.75rem 1rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      font-size: 0.88rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.15rem;
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.2rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s, box-shadow 0.15s;
    }}
    .card.featured {{
      border: 2px solid #f59e0b;
      box-shadow: 0 6px 20px rgba(245, 158, 11, 0.12);
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }}
    .featured-badge {{
      background: var(--gold-bg);
      color: var(--gold-text);
      font-size: 0.72rem;
      font-weight: 800;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      text-transform: uppercase;
    }}
    .verified-badge {{
      background: var(--emerald-bg);
      color: var(--emerald-text);
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
    }}
    .card h3 {{
      font-size: 1.12rem;
      margin-bottom: 0.2rem;
    }}
    .meta-line {{
      color: var(--muted);
      font-size: 0.84rem;
      margin-bottom: 0.75rem;
    }}
    .badge-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin-bottom: 0.85rem;
    }}
    .tag-true {{
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
      font-size: 0.74rem;
      font-weight: 600;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
    }}
    .tag-false {{
      background: #f1f5f9;
      color: #94a3b8;
      font-size: 0.74rem;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      text-decoration: line-through;
    }}
    .evidence-box {{
      background: #f8fafc;
      border-left: 3px solid var(--primary);
      padding: 0.55rem 0.7rem;
      font-size: 0.8rem;
      color: #334155;
      border-radius: 0 6px 6px 0;
      margin-bottom: 0.9rem;
    }}
    .card-footer {{
      border-top: 1px solid var(--border);
      padding-top: 0.8rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 0.5rem;
    }}
    .price-box {{
      font-size: 0.85rem;
    }}
    .price-box strong {{
      font-size: 1.05rem;
      color: var(--text);
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.25rem;
    }}
    .panel h2 {{
      font-size: 1.3rem;
      margin-bottom: 0.5rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.86rem;
      margin-top: 0.75rem;
    }}
    th, td {{
      border-bottom: 1px solid var(--border);
      padding: 0.6rem 0.5rem;
      text-align: left;
    }}
    th {{
      background: #f1f5f9;
      font-weight: 700;
    }}
    .modal-backdrop {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.65);
      z-index: 50;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }}
    .modal-backdrop.open {{ display: flex; }}
    .modal {{
      background: #fff;
      border-radius: 12px;
      max-width: 520px;
      width: 100%;
      padding: 1.5rem;
      box-shadow: 0 20px 35px rgba(0,0,0,0.25);
    }}
    .modal h3 {{ margin-bottom: 0.5rem; }}
    .form-group {{ margin-bottom: 0.8rem; }}
    .form-group label {{ display: block; font-size: 0.82rem; font-weight: 600; margin-bottom: 0.25rem; }}
    .form-group input, .form-group select, .form-group textarea {{
      width: 100%;
      padding: 0.55rem;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 0.9rem;
    }}
    pre.code-block {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 1rem;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 0.8rem;
      max-height: 440px;
    }}
    .hidden {{ display: none !important; }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-left">
      <span class="badge-pill">REPLICATION LIVE DEMO (Video: NhqSuQPPvbg)</span>
      <span>Chris Koerner's AI Niche Directory + 80/20 Portfolio Engine</span>
    </div>
    <div class="niche-switcher">
      <span>10-Second Copy-Paste Niche Clone:</span>
      <button class="niche-btn active" id="switch-outside-catering" onclick="switchNiche('outside-catering-venues')">Niche #1: CaterFree Venues</button>
      <button class="niche-btn" id="switch-estate-cleanout" onclick="switchNiche('estate-cleanout-pros')">Niche #2: Estate Cleanout Pros</button>
    </div>
  </div>

  <header>
    <div class="nav-container">
      <div class="brand" id="brand-title">{primary_enriched['brand_name']}</div>
      <div class="nav-tabs">
        <button class="tab-btn active" id="tab-btn-directory" onclick="showTab('directory')">1. Live Searchable Directory</button>
        <button class="tab-btn" id="tab-btn-scorer" onclick="showTab('scorer')">2. Niche Scorer & FB Validation</button>
        <button class="tab-btn" id="tab-btn-simulator" onclick="showTab('simulator')">3. 80/20 Vending vs. Directory Math</button>
        <button class="tab-btn" id="tab-btn-schema" onclick="showTab('schema')">4. Schema.org JSON-LD Moat</button>
      </div>
      <div class="cta-group">
        <button class="btn-accent" onclick="openFeaturedModal()">★ Upgrade Listing ($30/mo)</button>
        <button class="btn-primary" id="header-lead-btn" onclick="openLeadModal('Any Matching Listing')">{primary_enriched['lead_cta_label']}</button>
      </div>
    </div>
  </header>

  <section class="hero" id="hero-section">
    <div class="hero-inner">
      <h1 id="hero-headline">{primary_enriched['hero_headline']}</h1>
      <p id="hero-subheadline">{primary_enriched['hero_subheadline']}</p>
      <div class="search-bar">
        <input type="text" id="search-input" placeholder="Search by name, neighborhood, or policy keyword..." oninput="renderDirectory()" />
        <select id="city-select" onchange="renderDirectory()">
          <option value="ALL">All Metro Areas</option>
        </select>
        <button class="btn-primary" onclick="resetFilters()">Reset Filters</button>
      </div>
      <div class="filter-strip" id="filter-strip"></div>
    </div>
  </section>

  <main>
    <!-- TAB 1: DIRECTORY -->
    <div id="tab-directory">
      <div class="stats-bar">
        <div>Showing <strong id="visible-count">0</strong> of <strong id="total-count">0</strong> AI-Enriched & Review-Verified Listings</div>
        <div>Monetization Active: <strong>$30/mo Featured Upgrades</strong> · <strong>Lead Generation Capture</strong> · <strong>Display Ad RPM ($16.50)</strong></div>
      </div>
      <div class="grid" id="listings-grid"></div>

      <div class="panel" style="margin-top: 2rem;">
        <h2>Frequently Asked Questions (Indexed via FAQPage Schema.org)</h2>
        <div id="faq-container" style="margin-top: 0.75rem;"></div>
      </div>
    </div>

    <!-- TAB 2: NICHE SCORER & FB MARKETPLACE VALIDATION -->
    <div id="tab-scorer" class="hidden">
      <div class="panel">
        <h2>Niche Filter-Gap Scorer (KD &le; 30, Volume &ge; 500/mo, High Filter-Gap Moat)</h2>
        <p style="color: var(--muted); font-size: 0.9rem;">
          Resolves <code>[UNSPECIFIED]</code> Parameter #1 from the video: quantitatively scoring candidate "Near Me" & Facebook Group niches so you never waste time competing with Yelp on generic keywords.
        </p>
        <table id="niche-table">
          <thead>
            <tr>
              <th>Niche Candidate</th>
              <th>Seed Query</th>
              <th>KD</th>
              <th>Monthly Vol</th>
              <th>Filter-Gap Index</th>
              <th>Est. Lead Value</th>
              <th>Score (/100)</th>
              <th>Verdict</th>
            </tr>
          </thead>
          <tbody id="niche-tbody"></tbody>
        </table>
      </div>

      <div class="panel">
        <h2>1-Hour / $0 Facebook Marketplace & Local Group Demand Validator</h2>
        <p style="color: var(--muted); font-size: 0.9rem; margin-bottom: 0.75rem;">
          Chris Koerner's Rule: <em>"Test ideas in hours, not months. Post a mockup or service offer on Facebook Marketplace or local groups and count real inbound messages before scaling."</em>
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="evidence-box">
            <strong>Step 1: Facebook Group Mining Queries</strong><br/>
            Search local city groups for:<br/>
            <code>"Looking for a venue that lets us bring"</code><br/>
            <code>"Anyone know a good estate sale liquidator"</code><br/>
            <code>"Recommend a mobile dog groomer for large dogs"</code>
          </div>
          <div class="evidence-box">
            <strong>Step 2: 48-Hour Validation Threshold</strong><br/>
            Post the free Concierge Matching Offer below. Target: <strong>&ge; 5 inbound DMs within 48 hours</strong> on $0 ad spend (or $25 Meta local test).
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: 80/20 PORTFOLIO & VENDING MACHINE SIMULATOR -->
    <div id="tab-simulator" class="hidden">
      <div class="panel">
        <h2>The 80/20 Power Law: 100 Vending Machines vs. 10 AI Niche Directories (18:00–21:25)</h2>
        <p style="color: var(--muted); font-size: 0.9rem; margin-bottom: 1rem;">
          In the final segment of <code>NhqSuQPPvbg</code>, Chris Koerner compares niche directories to a 100-machine vending route: <strong>20% of locations (Apartment Lobbies) make $3,000/mo each</strong> while <strong>80% make $400/mo each</strong>—and explains why testing healthy snacks in auto shops failed while Doritos &amp; Diet Coke in apartment complexes crushed it.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.25rem;">
          <div class="card">
            <h3>100-Unit Vending Route (Video Benchmark)</h3>
            <p class="meta-line">20 Apartment Lobbies ($3,000/mo) + 80 Standard ($400/mo)</p>
            <div style="font-size: 1.5rem; font-weight: 800; color: var(--primary); margin: 0.5rem 0;">$92,000 / mo Gross</div>
            <p style="font-size: 0.83rem; color: var(--muted);">Est. Net Profit: <strong>$32,200/mo</strong> · Upfront CapEx: <strong>~$350,000</strong></p>
          </div>
          <div class="card featured">
            <h3>10-Site Cloned AI Directory Portfolio (Month 12)</h3>
            <p class="meta-line">2 Top-20% Winner Sites (~60k visits/mo) + 8 Baseline Sites (~10k visits/mo)</p>
            <div style="font-size: 1.5rem; font-weight: 800; color: #b45309; margin: 0.5rem 0;" id="sim-m12-gross">$11,740 / mo Gross</div>
            <p style="font-size: 0.83rem; color: var(--muted);">Est. Net Profit: <strong>$11,695/mo</strong> · Upfront CapEx: <strong>~$150 (Domains)</strong></p>
          </div>
        </div>

        <h3>Interactive Portfolio & RPM Calculator</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin: 0.85rem 0; background: #f8fafc; padding: 1rem; border-radius: 8px;">
          <div>
            <label style="font-size: 0.82rem; font-weight: 700;">Total Cloned Directory Sites: <span id="lbl-sites">10</span></label>
            <input type="range" id="rng-sites" min="1" max="50" value="10" style="width:100%;" oninput="updatePortfolioCalc()" />
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 700;">Display Ad RPM ($): <span id="lbl-rpm">16.50</span></label>
            <input type="range" id="rng-rpm" min="8" max="30" step="0.5" value="16.5" style="width:100%;" oninput="updatePortfolioCalc()" />
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 700;">Featured Tier Price ($/mo): <span id="lbl-feat">30</span></label>
            <input type="range" id="rng-feat" min="19" max="99" step="1" value="30" style="width:100%;" oninput="updatePortfolioCalc()" />
          </div>
          <div>
            <div style="font-size: 0.8rem; color: var(--muted);">Projected Month-12 Portfolio Net:</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: var(--primary);" id="calc-net-output">$11,695 / mo</div>
          </div>
        </div>

        <h3 style="margin-top: 1.25rem;">Month 1–12 Trajectory (Including the Months 1–3 "SEO Valley of Despair")</h3>
        <table>
          <thead>
            <tr>
              <th>Month</th>
              <th>Growth Phase</th>
              <th>Winner Site Visits</th>
              <th>Winner Site Rev</th>
              <th>Baseline Site Visits</th>
              <th>Baseline Site Rev</th>
              <th>10-Site Portfolio Net</th>
            </tr>
          </thead>
          <tbody id="trajectory-tbody"></tbody>
        </table>
      </div>
    </div>

    <!-- TAB 4: SCHEMA.ORG JSON-LD MOAT -->
    <div id="tab-schema" class="hidden">
      <div class="panel">
        <h2>Automated Schema.org JSON-LD Structured Data (The SEO Moat)</h2>
        <p style="color: var(--muted); font-size: 0.9rem; margin-bottom: 0.75rem;">
          Chris Koerner explains that AI-generated directories outrank major sites because they embed rich <code>LocalBusiness</code> / <code>EventVenue</code>, <code>ItemList</code>, <code>AggregateRating</code>, and <code>LocationFeatureSpecification</code> Schema.org markup on every page. Below is the live validated JSON-LD injected into this page's <code>&lt;head&gt;</code>:
        </p>
        <pre class="code-block" id="schema-code-view"></pre>
      </div>
    </div>
  </main>

  <!-- MODAL 1: LEAD CAPTURE ("GET 3 FREE QUOTES") -->
  <div class="modal-backdrop" id="lead-modal">
    <div class="modal">
      <h3 id="lead-modal-title">Get 3 Free Verified Quotes</h3>
      <p style="font-size: 0.85rem; color: var(--muted); margin-bottom: 1rem;">
        Your inquiry is routed to up to 3 verified providers matching your exact filter criteria. (Cold-Start Strategy: Free leads prove value to vendors before pitching the $30/mo Featured Spot!)
      </p>
      <div class="form-group">
        <label>Target Listing / Preference</label>
        <input type="text" id="lead-target-input" readonly />
      </div>
      <div class="form-group">
        <label>Your Name &amp; Email</label>
        <input type="text" id="lead-contact-input" placeholder="Alex Rivera · alex@example.com" />
      </div>
      <div class="form-group">
        <label>Event Date / Project Timeline &amp; Guest Count</label>
        <input type="text" id="lead-details-input" placeholder="October 2027 · 180 Guests · Bringing Outside Taco Truck + BYOB" />
      </div>
      <div id="lead-confirm-msg" class="evidence-box hidden"></div>
      <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem;">
        <button class="tab-btn" onclick="closeModals()">Close</button>
        <button class="btn-primary" onclick="submitLeadForm()">Send Inquiry to Verified Vendors</button>
      </div>
    </div>
  </div>

  <!-- MODAL 2: $30/MO FEATURED UPGRADE (STRIPE CHECKOUT SIMULATION) -->
  <div class="modal-backdrop" id="featured-modal">
    <div class="modal">
      <h3>★ Upgrade to Verified Featured Placement ($30/month)</h3>
      <p style="font-size: 0.85rem; color: var(--muted); margin-bottom: 1rem;">
        Pin your business to the top of your city &amp; filter category, display the gold <strong>Featured Partner</strong> badge, and receive priority lead routing.
      </p>
      <div class="form-group">
        <label>Select Your Business Listing to Upgrade</label>
        <select id="upgrade-listing-select"></select>
      </div>
      <div class="form-group">
        <label>Owner / Manager Email for Stripe Receipt</label>
        <input type="email" id="upgrade-email-input" value="owner@venuepartner.com" />
      </div>
      <div id="upgrade-confirm-msg" class="evidence-box hidden"></div>
      <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem;">
        <button class="tab-btn" onclick="closeModals()">Cancel</button>
        <button class="btn-accent" onclick="submitFeaturedUpgrade()">Activate $30/mo Featured Spot</button>
      </div>
    </div>
  </div>

  <script>
    const APP_STATE = {app_state_json};
    let activeFilters = new Set();

    function getActiveNiche() {{
      return APP_STATE.niches[APP_STATE.activeNicheSlug];
    }}

    function switchNiche(slug) {{
      APP_STATE.activeNicheSlug = slug;
      activeFilters.clear();
      document.getElementById('search-input').value = '';
      document.getElementById('switch-outside-catering').classList.toggle('active', slug === 'outside-catering-venues');
      document.getElementById('switch-estate-cleanout').classList.toggle('active', slug === 'estate-cleanout-pros');

      const niche = getActiveNiche();
      document.documentElement.style.setProperty('--primary', niche.primary_color);
      document.documentElement.style.setProperty('--accent', niche.accent_color);
      document.getElementById('brand-title').textContent = niche.brand_name;
      document.getElementById('hero-headline').textContent = niche.hero_headline;
      document.getElementById('hero-subheadline').textContent = niche.hero_subheadline;
      document.getElementById('header-lead-btn').textContent = niche.lead_cta_label;

      populateCitiesAndFilters();
      renderDirectory();
    }}

    function populateCitiesAndFilters() {{
      const niche = getActiveNiche();
      const citySelect = document.getElementById('city-select');
      citySelect.innerHTML = '<option value="ALL">All Metro Areas (' + niche.enriched_listings.length + ')</option>';
      niche.cities.forEach(city => {{
        const opt = document.createElement('option');
        opt.value = city;
        opt.textContent = city;
        citySelect.appendChild(opt);
      }});

      const strip = document.getElementById('filter-strip');
      strip.innerHTML = '';
      niche.filter_definitions.forEach(fdef => {{
        const btn = document.createElement('button');
        btn.className = 'filter-pill' + (activeFilters.has(fdef.key) ? ' active' : '');
        btn.textContent = (activeFilters.has(fdef.key) ? '✓ ' : '+ ') + fdef.label;
        btn.onclick = () => {{
          if (activeFilters.has(fdef.key)) activeFilters.delete(fdef.key);
          else activeFilters.add(fdef.key);
          populateCitiesAndFilters();
          renderDirectory();
        }};
        strip.appendChild(btn);
      }});
    }}

    function resetFilters() {{
      activeFilters.clear();
      document.getElementById('search-input').value = '';
      document.getElementById('city-select').value = 'ALL';
      populateCitiesAndFilters();
      renderDirectory();
    }}

    function renderDirectory() {{
      const niche = getActiveNiche();
      const q = document.getElementById('search-input').value.toLowerCase().trim();
      const city = document.getElementById('city-select').value;

      const filtered = niche.enriched_listings.filter(item => {{
        if (city !== 'ALL' && item.city !== city) return false;
        if (q) {{
          const hay = (item.name + ' ' + item.city + ' ' + item.neighborhood + ' ' + item.raw_policy_and_reviews).toLowerCase();
          if (!hay.includes(q)) return false;
        }}
        for (const fkey of activeFilters) {{
          if (!item.filters[fkey]) return false;
        }}
        return true;
      }});

      document.getElementById('visible-count').textContent = filtered.length;
      document.getElementById('total-count').textContent = niche.enriched_listings.length;

      const grid = document.getElementById('listings-grid');
      grid.innerHTML = '';
      filtered.forEach(item => {{
        const card = document.createElement('div');
        card.className = 'card' + (item.featured ? ' featured' : '');

        const badgesHtml = niche.filter_definitions.map(fdef => {{
          const has = item.filters[fdef.key];
          return `<span class="${{has ? 'tag-true' : 'tag-false'}}">${{has ? '✓ ' : ''}}${{fdef.label}}</span>`;
        }}).join('');

        const firstEvidence = Object.values(item.verified_evidence || {{}})[0] || item.raw_policy_and_reviews;

        card.innerHTML = `
          <div>
            <div class="card-top">
              ${{item.featured ? '<span class="featured-badge">★ Featured Partner ($30/mo)</span>' : '<span class="verified-badge">✓ AI Review-Verified</span>'}}
              <span style="font-size:0.82rem; font-weight:700;">★ ${{item.rating}} (${{item.review_count}})</span>
            </div>
            <h3>${{item.name}}</h3>
            <div class="meta-line">📍 ${{item.neighborhood}} · ${{item.city}} · Cap/Scale: ${{item.capacity}}</div>
            <div class="badge-list">${{badgesHtml}}</div>
            <div class="evidence-box">
              <strong>Verified Policy Evidence:</strong> "${{firstEvidence}}"
            </div>
          </div>
          <div class="card-footer">
            <div class="price-box">
              Base: <strong>$${{item.base_rental_usd.toLocaleString()}}</strong>
              <div style="font-size:0.74rem; color:#047857; font-weight:600;">Est. Client Savings: $${{item.estimated_client_savings_usd.toLocaleString()}}+</div>
            </div>
            <button class="btn-primary" onclick="openLeadModal('${{item.name.replace(/'/g, "\\'")}}')">Request Quote</button>
          </div>
        `;
        grid.appendChild(card);
      }});

      const faqContainer = document.getElementById('faq-container');
      faqContainer.innerHTML = niche.faqs.map(f => `
        <div style="margin-bottom:0.85rem; padding-bottom:0.85rem; border-bottom:1px solid var(--border);">
          <div style="font-weight:700; margin-bottom:0.25rem;">Q: ${{f.question}}</div>
          <div style="font-size:0.88rem; color:var(--muted);">A: ${{f.answer}}</div>
        </div>
      `).join('');
    }}

    function showTab(tabName) {{
      ['directory', 'scorer', 'simulator', 'schema'].forEach(t => {{
        document.getElementById('tab-' + t).classList.toggle('hidden', t !== tabName);
        document.getElementById('tab-btn-' + t).classList.toggle('active', t === tabName);
      }});
    }}

    function openLeadModal(targetName) {{
      document.getElementById('lead-target-input').value = targetName;
      document.getElementById('lead-confirm-msg').classList.add('hidden');
      document.getElementById('lead-modal').classList.add('open');
    }}

    function submitLeadForm() {{
      const target = document.getElementById('lead-target-input').value;
      const contact = document.getElementById('lead-contact-input').value || 'Demo User (alex@example.com)';
      const msg = document.getElementById('lead-confirm-msg');
      msg.innerHTML = `<strong>✓ Lead Captured &amp; Routed!</strong> Sent inquiry from <em>${{contact}}</em> to <strong>${{target}}</strong> + 2 matching Featured Partners. (Est. Lead Value: $45.00)`;
      msg.classList.remove('hidden');
    }}

    function openFeaturedModal() {{
      const niche = getActiveNiche();
      const sel = document.getElementById('upgrade-listing-select');
      sel.innerHTML = '';
      niche.enriched_listings.forEach(item => {{
        const opt = document.createElement('option');
        opt.value = item.id;
        opt.textContent = item.name + ' (' + item.city + ')' + (item.featured ? ' [Already Featured]' : '');
        sel.appendChild(opt);
      }});
      document.getElementById('upgrade-confirm-msg').classList.add('hidden');
      document.getElementById('featured-modal').classList.add('open');
    }}

    function submitFeaturedUpgrade() {{
      const niche = getActiveNiche();
      const listingId = document.getElementById('upgrade-listing-select').value;
      const item = niche.enriched_listings.find(x => x.id === listingId);
      if (item) {{
        item.featured = true;
        niche.enriched_listings.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0) || b.active_filter_count - a.active_filter_count);
        renderDirectory();
      }}
      const msg = document.getElementById('upgrade-confirm-msg');
      msg.innerHTML = `<strong>✓ $30/mo Featured Subscription Activated!</strong> <em>${{item ? item.name : ''}}</em> is now pinned to the top of directory results with a Featured Partner badge.`;
      msg.classList.remove('hidden');
    }}

    function closeModals() {{
      document.getElementById('lead-modal').classList.remove('open');
      document.getElementById('featured-modal').classList.remove('open');
    }}

    function renderScorerAndSimulator() {{
      const tbody = document.getElementById('niche-tbody');
      tbody.innerHTML = APP_STATE.nicheScores.map(n => `
        <tr>
          <td><strong>${{n.name}}</strong></td>
          <td><code>${{n.seed_query}}</code></td>
          <td>${{n.keyword_difficulty}}</td>
          <td>${{n.monthly_search_volume.toLocaleString()}}</td>
          <td>${{(n.filter_gap_index * 100).toFixed(0)}}%</td>
          <td>$${{n.estimated_lead_value_usd}}</td>
          <td><strong>${{n.composite_opportunity_score}}</strong></td>
          <td><span class="${{n.passes_koerner_gate ? 'tag-true' : 'tag-false'}}">${{n.verdict}}</span></td>
        </tr>
      `).join('');

      const trajBody = document.getElementById('trajectory-tbody');
      const traj = APP_STATE.portfolioSim.directory_10_site_portfolio_benchmark.monthly_trajectory;
      trajBody.innerHTML = traj.map(row => `
        <tr>
          <td><strong>Month ${{row.month}}</strong></td>
          <td>${{row.phase}}</td>
          <td>${{row.winner_site_visits.toLocaleString()}}</td>
          <td>$${{row.winner_site_revenue_usd.toLocaleString()}}</td>
          <td>${{row.baseline_site_visits.toLocaleString()}}</td>
          <td>$${{row.baseline_site_revenue_usd.toLocaleString()}}</td>
          <td><strong>$${{row.portfolio_10_sites_net_usd.toLocaleString()}}/mo</strong></td>
        </tr>
      `).join('');

      document.getElementById('schema-code-view').textContent = document.getElementById('schema-jsonld').textContent.trim();
    }}

    function updatePortfolioCalc() {{
      const sites = parseInt(document.getElementById('rng-sites').value, 10);
      const rpm = parseFloat(document.getElementById('rng-rpm').value);
      const featPrice = parseFloat(document.getElementById('rng-feat').value);

      document.getElementById('lbl-sites').textContent = sites;
      document.getElementById('lbl-rpm').textContent = rpm.toFixed(2);
      document.getElementById('lbl-feat').textContent = featPrice;

      const winners = Math.max(1, Math.round(sites * 0.2));
      const baselines = sites - winners;

      const winnerRev = (60000 / 1000) * rpm + (34 * featPrice) + (60000 * 0.0012 * 25);
      const baseRev = (10000 / 1000) * rpm + (5 * featPrice) + (10000 * 0.0008 * 25);
      const net = Math.round((winners * winnerRev) + (baselines * baseRev) - (sites * 4.5));
      document.getElementById('calc-net-output').textContent = '$' + net.toLocaleString() + ' / mo';
    }}

    populateCitiesAndFilters();
    renderDirectory();
    renderScorerAndSimulator();
    updatePortfolioCalc();
  </script>
</body>
</html>
"""


def compile_all() -> Dict[str, Any]:
    base_dir = Path(__file__).resolve().parent.parent
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run Niche Scorer
    niche_scores = run_niche_scoring(
        base_dir / "data" / "candidate_niches.json",
        artifacts_dir / "niche_scores_report.json",
    )

    # 2. Run Enrichment Pipeline on Niche #1 and Niche #2
    enriched_1 = enrich_niche_config(
        base_dir / "configs" / "outside_catering_venues.json",
        artifacts_dir / "enriched_outside_catering_venues.json",
    )
    enriched_2 = enrich_niche_config(
        base_dir / "configs" / "estate_cleanout_pros.json",
        artifacts_dir / "enriched_estate_cleanout_pros.json",
    )

    # 3. Generate & Validate Schema.org JSON-LD for both niches
    schema_1 = generate_jsonld_schema(enriched_1)
    ok_1, errs_1 = validate_jsonld_schema(schema_1)
    if not ok_1:
        raise RuntimeError(f"Schema validation failed for Niche 1: {errs_1}")
    (artifacts_dir / "schema_outside_catering_venues.json").write_text(
        json.dumps(schema_1, indent=2), encoding="utf-8"
    )

    schema_2 = generate_jsonld_schema(enriched_2)
    ok_2, errs_2 = validate_jsonld_schema(schema_2)
    if not ok_2:
        raise RuntimeError(f"Schema validation failed for Niche 2: {errs_2}")
    (artifacts_dir / "schema_estate_cleanout_pros.json").write_text(
        json.dumps(schema_2, indent=2), encoding="utf-8"
    )

    # 4. Run 80/20 Portfolio & Vending Machine Simulator
    portfolio_sim = simulate_vending_vs_directory_power_law()
    (artifacts_dir / "portfolio_economics_report.json").write_text(
        json.dumps(portfolio_sim, indent=2), encoding="utf-8"
    )

    # 5. Compile HTML5 Web Apps for Niche #1 and Niche #2
    html_1 = build_html_app(enriched_1, enriched_2, schema_1, niche_scores, portfolio_sim)
    out_app_1 = artifacts_dir / "outside-catering-venues" / "index.html"
    out_app_1.parent.mkdir(parents=True, exist_ok=True)
    out_app_1.write_text(html_1, encoding="utf-8")

    html_2 = build_html_app(enriched_2, enriched_1, schema_2, niche_scores, portfolio_sim)
    out_app_2 = artifacts_dir / "estate-cleanout-pros" / "index.html"
    out_app_2.parent.mkdir(parents=True, exist_ok=True)
    out_app_2.write_text(html_2, encoding="utf-8")

    return {
        "niche_1_app": str(out_app_1),
        "niche_2_app": str(out_app_2),
        "niche_1_listings": len(enriched_1["enriched_listings"]),
        "niche_2_listings": len(enriched_2["enriched_listings"]),
        "schema_1_valid": ok_1,
        "schema_2_valid": ok_2,
        "top_scored_niche": niche_scores[0]["name"],
        "top_score": niche_scores[0]["composite_opportunity_score"],
    }


if __name__ == "__main__":
    summary = compile_all()
    print("Compiled Multi-Niche AI Directory Apps Successfully:")
    print(json.dumps(summary, indent=2))

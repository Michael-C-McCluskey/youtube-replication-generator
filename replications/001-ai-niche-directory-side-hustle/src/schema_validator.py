#!/usr/bin/env python3
"""
JSON-LD Schema.org Generator & Structural Validator
(Resolves [UNSPECIFIED] Parameter #3).

Generates rich Schema.org JSON-LD (@graph with WebSite, ItemList, LocalBusiness/EventVenue,
AggregateRating, LocationFeatureSpecification for Filter-Gap badges, and FAQPage) so AI-built
directories outrank generic sites in search results.
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Tuple


def generate_jsonld_schema(enriched_niche: Dict[str, Any]) -> Dict[str, Any]:
    slug = enriched_niche["slug"]
    brand = enriched_niche["brand_name"]
    schema_type = enriched_niche.get("schema_type", "LocalBusiness")
    filter_label_map = {f["key"]: f["label"] for f in enriched_niche["filter_definitions"]}

    item_elements: List[Dict[str, Any]] = []
    for idx, listing in enumerate(enriched_niche["enriched_listings"], start=1):
        amenities = [
            {
                "@type": "LocationFeatureSpecification",
                "name": filter_label_map.get(k, k),
                "value": bool(v),
            }
            for k, v in listing.get("filters", {}).items()
        ]
        entity: Dict[str, Any] = {
            "@type": schema_type,
            "@id": f"https://{slug}.example.com/#{listing['id']}",
            "name": listing["name"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": listing["address"],
                "addressLocality": listing["city"].split(",")[0].strip(),
                "addressRegion": listing["city"].split(",")[1].strip() if "," in listing["city"] else "US",
            },
            "telephone": listing["phone"],
            "url": listing["website"],
            "priceRange": f"${listing['base_rental_usd']}",
            "maximumAttendeeCapacity": listing["capacity"],
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": listing["rating"],
                "reviewCount": listing["review_count"],
                "bestRating": 5,
            },
            "amenityFeature": amenities,
        }
        item_elements.append(
            {
                "@type": "ListItem",
                "position": idx,
                "item": entity,
            }
        )

    faq_entities = [
        {
            "@type": "Question",
            "name": faq["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["answer"],
            },
        }
        for faq in enriched_niche.get("faqs", [])
    ]

    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"https://{slug}.example.com/#website",
                "name": brand,
                "description": enriched_niche["tagline"],
                "url": f"https://{slug}.example.com/",
            },
            {
                "@type": "ItemList",
                "@id": f"https://{slug}.example.com/#directory-list",
                "name": f"{brand} Verified Directory Listings",
                "numberOfItems": len(item_elements),
                "itemListElement": item_elements,
            },
            {
                "@type": "FAQPage",
                "@id": f"https://{slug}.example.com/#faq",
                "mainEntity": faq_entities,
            },
        ],
    }


def validate_jsonld_schema(schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if schema.get("@context") != "https://schema.org":
        errors.append("Missing or invalid @context")

    graph = schema.get("@graph", [])
    if not isinstance(graph, list) or len(graph) < 3:
        errors.append("@graph must contain WebSite, ItemList, and FAQPage nodes")
        return False, errors

    types_found = {node.get("@type") for node in graph}
    for req_type in ("WebSite", "ItemList", "FAQPage"):
        if req_type not in types_found:
            errors.append(f"Missing required @graph node type: {req_type}")

    for node in graph:
        if node.get("@type") == "ItemList":
            items = node.get("itemListElement", [])
            if not items:
                errors.append("ItemList has 0 elements")
            for elem in items:
                item = elem.get("item", {})
                if not item.get("name") or not item.get("telephone"):
                    errors.append(f"Listing missing name or telephone: {item}")
                if not item.get("amenityFeature"):
                    errors.append(f"Listing missing LocationFeatureSpecification amenities: {item.get('name')}")
                if "aggregateRating" not in item:
                    errors.append(f"Listing missing aggregateRating: {item.get('name')}")

    return (len(errors) == 0), errors


if __name__ == "__main__":
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    enriched = json.loads((base_dir / "artifacts" / "enriched_outside_catering_venues.json").read_text(encoding="utf-8"))
    schema = generate_jsonld_schema(enriched)
    ok, errs = validate_jsonld_schema(schema)
    print(f"Schema validation passed={ok}, errors={errs}, items={len(schema['@graph'][1]['itemListElement'])}")

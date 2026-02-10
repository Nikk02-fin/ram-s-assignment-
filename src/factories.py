import json
import os
from pathlib import Path

def load_factories(path=None):
    if path is None:
        # Get the path relative to this file
        base_dir = Path(__file__).parent.parent
        path = base_dir / "data" / "factories.json"
    with open(path, "r") as f:
        return json.load(f)

def score_factory(factory, req):
    score = 0
    reasons = []

    # Check product type match
    if req.product_type in factory["product_types"]:
        score += 3
        reasons.append(f"Specializes in {req.product_type}")

    # Check material compatibility
    material_matches = set(req.materials) & set(factory["materials"])
    if material_matches:
        score += 2
        reasons.append(f"Works with {', '.join(material_matches)}")

    # Check MOQ capability
    if req.moq >= factory["moq_min"]:
        score += 2
        reasons.append(f"Can handle MOQ of {req.moq} units (minimum: {factory['moq_min']})")
    else:
        # Still consider if close to minimum
        if req.moq >= factory["moq_min"] * 0.5:
            score += 1
            reasons.append(f"MOQ negotiable (you need {req.moq}, minimum is {factory['moq_min']})")

    # Check geography match (flexible matching)
    if req.geography:
        req_geo_lower = req.geography.lower()
        factory_geo_lower = factory["geography"].lower()
        if req_geo_lower in factory_geo_lower or factory_geo_lower in req_geo_lower:
            score += 1
            reasons.append(f"Located in {factory['geography']}")

    # Check budget tier alignment
    if req.budget_tier and req.budget_tier == factory["cost_tier"]:
        score += 1
        reasons.append(f"Matches {req.budget_tier} budget tier")

    # Add certification info
    if factory["certifications"]:
        reasons.append(f"Certified: {', '.join(factory['certifications'])}")

    return score, reasons

def recommend_factories(req, top_n=3):
    factories = load_factories()
    scored = []

    for f in factories:
        score, reasons = score_factory(f, req)
        if score > 0:
            scored.append({
                "factory": f,
                "score": score,
                "reasons": reasons
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]

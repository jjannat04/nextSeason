"""Inspectable qualitative screening, evidence tiers and confidence; no probabilities."""
from ..knowledge.repository import usable
from .evaluation import insufficient, UNSUPPORTED

ORDER = {"good_fit": 0, "acceptable": 1, "potential_concern": 2}
GAP_REASONS = {
    "water_resilience": "Numerical irrigation demand is not evaluated: supported stage timing, effective rainfall and irrigation assumptions are incomplete. Rainfall is not irrigation demand.",
    "salinity_risk": "Field salinity is not included because available crop thresholds are conflicting or lack applicable measurement and cultivar support.",
    "stage_stress": "Stage-specific heat sensitivity is not evaluated because sufficiently supported thresholds and stage dates are unavailable.",
    "soil_health_contribution": "Calibrated soil-health contribution is not evaluated: residue management and supported response methods are unavailable.",
    "income": "Income is not evaluated without local dated yield, price and cost evidence.",
    "low_input_cost": "Input cost is not evaluated without applicable local management and cost records.",
}


def supported(field):
    return usable(field, "prototype_recommendation")


def tier(fields):
    if not fields:
        return "missing"
    return "provisional" if any(f.get("verification") == "provisional" or f.get("applicability_status") == "provisional" for f in fields) else "verified"


def climate(crop, environment, months=None):
    names = ("temp_optimal_min_c", "temp_optimal_max_c", "temp_absolute_min_c", "temp_absolute_max_c")
    fields = [crop["temperature"].get(k) for k in names]
    if not all(supported(f) for f in fields):
        return insufficient("Usable crop temperature requirements are unavailable")
    if environment.get("status") != "available" or not environment.get("coverage", {}).get("T2M", {}).get("complete"):
        return insufficient("Complete historical NASA POWER T2M observations are required")
    selected = [p for p in environment["series"]["T2M"]["daily"] if months is None or int(p["date"][5:7]) in months]
    if not selected or any(p["value"] is None for p in selected):
        return insufficient("The selected historical period has no complete observations for this crop's calendar months")
    values = [p["value"] for p in selected]
    lo, hi, absolute_lo, absolute_hi = [f["normalized_value"] for f in fields]
    minimum, maximum = min(values), max(values)
    interpretation = "good_fit" if lo <= minimum and maximum <= hi else "acceptable" if absolute_lo <= minimum and maximum <= absolute_hi else "potential_concern"
    source = {"provider": "NASA POWER", "parameter": "T2M", "value": {"minimum_daily_mean": minimum, "maximum_daily_mean": maximum, "mean": sum(values) / len(values)},
        "unit": "degC", "period": environment["period"], "observed_dates": {"start": selected[0]["date"], "end": selected[-1]["date"]},
        "calendar_months_used": sorted(months) if months else "all_selected_period_months", "observed_days": len(values),
        "calendar_months_without_observations": sorted(months - {int(p["date"][5:7]) for p in selected}) if months else [],
        "time_standard": environment["time_standard"], "source": environment.get("request_url", "https://power.larc.nasa.gov/api/temporal/daily/point"),
        "location": environment.get("location"), "response_sha256": environment["response_sha256"]}
    return {"status": "qualitative_screening", "value": interpretation, "verification": tier(fields), "evidence": fields,
        "crop_requirement_used": {name: f["normalized_value"] for name, f in zip(names, fields)}, "environment_source": source,
        "method": "Range of historical daily mean T2M versus published species temperature envelopes: all within optimum=good_fit; all within absolute=acceptable; otherwise potential_concern.",
        "limitation": "Calendar-month subset of the selected historical period, not a future forecast, yield response, lethal threshold or stage-specific heat assessment. Broad calendar occupancy and global species applicability are provisional."}


def soil(crop, inputs):
    fields = [crop["soil_ph"].get(k) for k in ("soil_ph_opt_min", "soil_ph_opt_max")]
    ph = inputs.get("ph")
    if ph is None:
        return insufficient("Field pH is unknown; no regional value or zero was substituted")
    if not all(supported(f) for f in fields):
        return insufficient("Usable crop pH requirements are unavailable")
    lo, hi = [f["normalized_value"] for f in fields]
    return {"status": "qualitative_screening", "value": "good_fit" if lo <= ph <= hi else "potential_concern", "verification": tier(fields),
        "farmer_value": ph, "measurement_method": inputs.get("ph_method", "unspecified"), "evidence": fields,
        "method": "Field pH inside published optimal interval=good_fit; outside=potential_concern, not a crop exclusion.",
        "limitation": "Basic pH screening only; test method, texture and drainage applicability are not calibrated. Outside the optimum does not imply infeasibility."}


def assess(crop, environment, inputs):
    return {"crop_id": crop["id"], "label": crop["label"], "prototype_eligible": crop["prototype_eligible"],
        "exclusion_reason": crop.get("prototype_exclusion"), "climate_suitability": climate(crop, environment), "soil_suitability": soil(crop, inputs),
        **{key: insufficient(GAP_REASONS[key]) for key in UNSUPPORTED}}


def confidence(required, context_incomplete=False):
    """All required evidence verified=high; any provisional=moderate; gaps=limited."""
    if context_incomplete or not required or any(state not in ("verified", "provisional") for state in required):
        return "limited"
    return "moderate" if "provisional" in required else "high"


def evaluate(candidate, crops, environment, request, space_profile=None):
    dimensions = {}
    climate_components, soil_components = [], []
    for activity in candidate["activities"]:
        start = int(activity["planting_window"]["start"][5:7])
        finish = int(activity["harvest_window"]["end"][5:7])
        months = set()
        m = start
        for _ in range(12):
            months.add(m)
            if m == finish:
                break
            m = m % 12 + 1
        crop = crops[activity["crop_id"]]
        climate_components.append(climate(crop, environment, months))
        soil_components.append(soil(crop, request.get("soil", {})))
    for name, components in (("climate_suitability", climate_components), ("soil_suitability", soil_components)):
        if any(c["status"] == "insufficient_data" for c in components):
            dimensions[name] = insufficient("One or more crop comparisons are unavailable; unknown values were not scored")
            dimensions[name]["components"] = components
        else:
            dimensions[name] = {"status": "qualitative_screening", "value": max((c["value"] for c in components), key=ORDER.get),
                "verification": tier(components), "components": components, "evidence": [f for c in components for f in c["evidence"]],
                "method": "Most concerning supported crop interpretation; no numerical average or overall score."}
    rules = candidate["sequence_evidence"]
    dimensions["rotation_quality"] = {"status": "qualitative_sequence_evidence", "value": "acceptable", "verification": tier(rules),
        "evidence": rules, "method": "Documented conditional rice/dry-crop system. No family-diversity bonus, numerical legume credit or unknown-pair penalty."} if rules else insufficient("No usable sequence evidence")
    preferred = set(request.get("preferred_crop_ids", []))
    dimensions["farmer_priority_fit"] = {"status": "farmer_preference", "value": sum(a["crop_id"] in preferred for a in candidate["activities"]), "metric": "preferred_crop_occurrences", "evidence": []}
    dimensions.update({k: insufficient(GAP_REASONS[k]) for k in UNSUPPORTED})
    if space_profile is not None:
        from .environmental_evaluation import apply
        apply(dimensions, candidate, crops, space_profile)
    candidate["dimension_results"] = dimensions
    candidate["explanations"] = [{"dimension": key, "interpretation": value["value"], "verification": value.get("verification"),
        "agronomic_evidence": value["evidence"], "environment_source": [c["environment_source"] for c in value.get("components", []) + value.get("additional_components", []) if "environment_source" in c],
        "environmental_context": value.get("components") if key=="historical_moisture_context" else None,
        "method": value.get("method"), "reason": value.get("reason")} for key, value in dimensions.items()]
    candidate["explanations"].extend({"dimension": "calendar", "crop_id": a["crop_id"], "verification": a["calendar_evidence"]["verification"],
        "claim": a["calendar_evidence"]["notes"], "agronomic_evidence": [a["calendar_evidence"]]} for a in candidate["activities"])
    required = [a["calendar_evidence"]["verification"] for a in candidate["activities"]] + [r["verification"] for r in rules]
    required += [c.get("verification", "missing") for c in climate_components + soil_components]
    context_incomplete = any(c["status"] == "insufficient_data" for c in climate_components + soil_components) or any(c.get("environment_source",{}).get("calendar_months_without_observations") for c in climate_components) or request.get("soil", {}).get("ph_method", "unspecified") == "unspecified"
    candidate["evidence_confidence"] = {"label": confidence(required, context_incomplete), "rule": "high=all required verified; moderate=all required usable with provisional evidence; limited=missing comparisons/calendar-month observations or unspecified field pH method. Optional unsupported dimensions do not lower confidence.",
        "supported_by": [{"dimension": "NASA climate observations", "status": "verified" if all(c["status"] != "insufficient_data" for c in climate_components) else "missing"},
            {"dimension": "Crop climate requirements/applicability", "status": tier([f for c in climate_components for f in c.get("evidence", [])])},
            {"dimension": "Crop calendar", "status": tier([a["calendar_evidence"] for a in candidate["activities"]])},
            {"dimension": "Sequence evidence", "status": tier(rules)},
            {"dimension": "Basic soil comparison", "status": "missing" if any(c["status"] == "insufficient_data" for c in soil_components) else tier(soil_components)},
            *[{"dimension": k, "status": "insufficient_data", "reason": GAP_REASONS[k]} for k in UNSUPPORTED]]}
    return candidate

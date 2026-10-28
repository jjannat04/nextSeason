"""NASA-depth evaluation additions: annual rainfall reference and moisture context."""
from ..environment.indicators import moisture
from ..knowledge.repository import usable
from .evaluation import insufficient

ORDER = {"good_fit": 0, "acceptable": 1, "potential_concern": 2}


def annual_rainfall(crop, gpm):
    fields = crop.get("annual_rainfall", {})
    keys = ("rainfall_min_mm", "rainfall_optimal_min_mm", "rainfall_optimal_max_mm", "rainfall_max_mm")
    period = gpm.get("period", {})
    rain = gpm.get("series", {}).get("precipitation", {})
    start, end = period.get("start", ""), period.get("end", "")
    if not (start.endswith("01-01") and end.endswith("12-31") and start[:4] == end[:4]):
        return insufficient("Annual crop rainfall references require a complete calendar year; shorter-period totals are not annualized")
    if gpm.get("status") != "available" or not rain.get("coverage", {}).get("complete") or rain.get("total_mm") is None:
        return insufficient("Complete IMERG daily observations are unavailable; annual rainfall remains unknown")
    if not all(usable(fields.get(k), "annual_rainfall_reference_comparison") for k in keys):
        return insufficient("Supported annual species rainfall requirements are unavailable")
    lo, opt_lo, opt_hi, hi = [fields[k]["normalized_value"] for k in keys]
    value = rain["total_mm"]
    category = "good_fit" if opt_lo <= value <= opt_hi else "acceptable" if lo <= value <= hi else "potential_concern"
    return {"status": "qualitative_screening", "value": category, "verification": "provisional", "evidence": [fields[k] for k in keys],
        "crop_id": crop["id"], "environment_source": {"provider": "GPM IMERG", "product": gpm["product"], "parameter": "precipitation", "value": value, "unit": "mm", "measurement_basis":"complete_calendar_year_total",
            "period": period, "provenance": gpm.get("provenance")},
        "method": "Complete observed annual precipitation versus source-verified annual species envelope: optimum=good_fit; absolute=acceptable; outside=potential_concern.",
        "limitation": "Global annual rainfall context only, not rain during this crop's season, delivered irrigation, crop water balance or a hard crop exclusion."}


def apply(dimensions, candidate, crops, space):
    gpm = space.get("gpm", {})
    parts = [annual_rainfall(crops[a["crop_id"]], gpm) for a in candidate["activities"]]
    if all(p["status"] != "insufficient_data" for p in parts):
        rainfall = {"status": "qualitative_screening", "value": max((p["value"] for p in parts), key=ORDER.get),
            "verification": "provisional", "components": parts, "evidence": [f for p in parts for f in p["evidence"]],
            "method": "Most concerning annual rainfall reference category, not an irrigation estimate."}
        dimensions["rainfall_suitability"] = rainfall
        climate = dimensions["climate_suitability"]
        if climate["status"] != "insufficient_data":
            climate["temperature_interpretation"] = climate["value"]
            climate["value"] = max((climate["value"], rainfall["value"]), key=ORDER.get)
            climate["additional_components"] = parts
            climate["evidence"] += rainfall["evidence"]
            climate["sources_used"] = ["NASA POWER", "GPM IMERG"]
            climate["method"] = "Most concerning supported temperature or annual rainfall reference category. Rainfall is provisional global annual context, not season water demand. Missing IMERG has no penalty."
    else:
        dimensions["rainfall_suitability"] = insufficient("IMERG annual screening is incomplete or inapplicable; no penalty applied")
        dimensions["rainfall_suitability"]["components"] = parts
        dimensions["climate_suitability"]["sources_used"] = ["NASA POWER"]
    moisture_parts = []
    for activity in candidate["activities"]:
        first = int(activity["planting_window"]["start"][5:7]); last = int(activity["harvest_window"]["end"][5:7])
        months, m = set(), first
        for _ in range(12):
            months.add(m)
            if m == last:
                break
            m = m % 12 + 1
        result = moisture(space.get("smap", {}), months)
        if result["status"] == "available":
            actual = {int(p["time"][5:7]) for p in space["smap"]["series"]["root_zone_percentile"]["points"]}
            if months - actual:
                result = {"status": "insufficient_data", "value": None, "reason": "SMAP does not cover every activity calendar month"}
        moisture_parts.append(result)
    if all(p["status"] == "available" for p in moisture_parts):
        exposure = max(p["exact_values"]["below_median_fraction"] for p in moisture_parts)
        dimensions["historical_moisture_context"] = {"status": "observed_environmental_context", "value": "below_median_observations_present" if exposure else "no_below_median_observations_in_selected_period",
            "verification": "provisional", "ranking_value": exposure, "comparison_direction": "lower_is_preferred", "components": moisture_parts, "evidence": [],
            "method": "Largest observed below-product-median sample fraction among activity calendar windows. Only the explicit moisture-context preference can rank by less exposure; not a crop-damage or water-use score."}
    else:
        dimensions["historical_moisture_context"] = insufficient("Supported SMAP seasonal percentile coverage is unavailable for one or more activity windows; no penalty applied")
        dimensions["historical_moisture_context"]["components"] = moisture_parts

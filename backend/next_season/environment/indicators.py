"""Observed qualitative context. No guessed drought or irrigation thresholds."""
from datetime import date, timedelta


def absent(reason, sources):
    return {"status": "insufficient_data", "value": None, "reason": reason, "sources": sources, "rotation_impact": "Not scored; missing values do not become zero."}


def moisture(profile, months=None):
    series = profile.get("series", {}).get("root_zone_percentile", {})
    if profile.get("status") != "available" or not series.get("coverage", {}).get("complete"):
        return absent("Complete supported SMAP root-zone percentiles are unavailable; volumetric moisture is not converted to an invented percentile.", ["smap"])
    points = [p for p in series["points"] if months is None or int(p["time"][5:7]) in months]
    if not points or any(p["value"] is None for p in points):
        return absent("No usable root-zone percentile observations for these calendar months.", ["smap"])
    mean = sum(p["value"] for p in points) / len(points)
    return {"status": "available", "value": "below_product_seasonal_median" if mean < 50 else "above_product_seasonal_median" if mean > 50 else "at_product_seasonal_median",
        "exact_values": {"mean_root_zone_percentile": mean, "unit": "percentile", "samples": len(points), "below_median_fraction": sum(p["value"] < 50 for p in points)/len(points)},
        "sources": ["smap"], "provenance": profile.get("provenance"),
        "method": "Mean of NASA's seasonally resolved root-zone percentile; 50 is the statistical median, not a crop drought threshold.",
        "rotation_impact": "Historical moisture-exposure context for rotation calendar months. A farmer may prefer fewer below-median observations; no crop damage, irrigation saving or biological hard constraint is inferred.",
        "limitations": ["Percentile of a model-assimilated 9 km grid, not field root measurements.", "A mean percentile is a summary, not the percentile of the period's mean moisture."]}


def rainfall(profile):
    series = profile.get("series", {}).get("precipitation", {})
    if profile.get("status") != "available" or not series.get("coverage", {}).get("complete"):
        return absent("Complete IMERG daily precipitation is unavailable; partial observations are not treated as a complete rainfall total.", ["gpm"])
    return {"status": "available", "value": "historical_rainfall_available", "exact_values": {"total_mm": series["total_mm"], "unit": "mm", "period": profile["period"]},
        "sources": ["gpm"], "provenance": profile.get("provenance"),
        "rotation_impact": "A complete January–December year can inform global-species annual-rainfall screening. Shorter periods are context only, not compared with annual crop requirements.",
        "limitations": ["Rainfall is not irrigation requirement, flood probability or a forecast."]}


def rainfall_comparison(current, baseline):
    if baseline is None:
        return absent("No matching historical comparison window was requested. A dry/wet anomaly or climate normal has not been invented.", ["gpm"])
    if rainfall(current)["status"] != "available" or rainfall(baseline)["status"] != "available":
        return absent("Complete same-product rainfall is required for both comparison windows.", ["gpm"])
    a = current["series"]["precipitation"]["daily"]
    b = baseline["series"]["precipitation"]["daily"]
    # Exclude Feb 29 from the comparison only, preserving original observations.
    a = {p["date"][5:]: p["value"] for p in a if p["date"][5:] != "02-29"}
    b = {p["date"][5:]: p["value"] for p in b if p["date"][5:] != "02-29"}
    if a.keys() != b.keys() or current["product"] != baseline["product"] or current["location"] != baseline["location"]:
        return absent("Rainfall comparison needs the same point/product and matching calendar days.", ["gpm"])
    x, y = sum(a.values()), sum(b.values())
    return {"status": "available", "value": "drier_than_selected_comparison" if x < y else "wetter_than_selected_comparison" if x > y else "equal_to_selected_comparison",
        "exact_values": {"selected_total_mm": x, "comparison_total_mm": y, "difference_mm": x-y, "matched_days": len(a)}, "sources": ["gpm"],
        "provenance": {"selected": current.get("provenance"), "comparison": baseline.get("provenance")},
        "rotation_impact": "Historical rainfall context; not itself a crop-specific bonus or penalty.",
        "limitations": ["A selected prior window is not a multi-decade climate normal or a significant-trend test.", "No percentage anomaly is calculated against a zero baseline; leap day omitted from comparison only."]}


def interpret(smap, gpm, baseline=None):
    return {"root_zone_moisture": moisture(smap), "historical_rainfall": rainfall(gpm),
        "rainfall_vs_historical_comparison": rainfall_comparison(gpm, baseline)}

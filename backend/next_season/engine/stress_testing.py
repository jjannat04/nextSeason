"""Deterministic retrospective stress tests from complete NASA POWER years."""

from datetime import date
import math
from statistics import median

from ..knowledge.repository import usable
from .evaluation import insufficient
from .prototype_evaluation import ORDER, climate

YEARS = tuple(range(2015, 2025))
SCENARIOS = ("historical_normal", "historical_dry", "historical_hot", "historical_wet")
PARAMETERS = ("T2M", "T2M_MIN", "T2M_MAX", "PRECTOTCORR")
UNSUPPORTED = {
    "irrigation_demand": "Historical precipitation is not delivered irrigation or a field water balance.",
    "salinity_risk": "No supported field salinity response model is available.",
    "crop_stage_stress": "Month-level calendars and crop-stage thresholds do not support stage-specific stress estimates.",
    "yield_or_income_loss": "No calibrated yield, price or loss model is available.",
    "soil_health_change": "No calibrated soil-health response model is available.",
}


def annual_record(profile, year, latitude, longitude):
    start, end = f"{year}-01-01", f"{year}-12-31"
    if profile.get("status") != "available" or profile.get("provider") != "NASA POWER":
        return None
    if profile.get("period") != {"start": start, "end": end} or profile.get("location") != {"latitude": latitude, "longitude": longitude}:
        return None
    if any(not profile.get("coverage", {}).get(name, {}).get("complete") for name in PARAMETERS):
        return None
    expected = (date(year + 1, 1, 1) - date(year, 1, 1)).days
    if any(profile["coverage"][name].get("valid_days") != expected or
           len(profile.get("series", {}).get(name, {}).get("daily", [])) != expected for name in PARAMETERS):
        return None
    temp = profile["series"]["T2M"]
    rain = profile["series"]["PRECTOTCORR"]
    values = [point["value"] for point in rain["daily"]]
    if (temp.get("unit") != "degC" or rain.get("unit") != "mm/day" or
            any(value is None or not math.isfinite(value) or value < 0 for value in values) or
            temp.get("mean") is None or not math.isfinite(temp["mean"])):
        return None
    return {"year": year, "temperature_mean_c": temp["mean"], "precipitation_total_mm": math.fsum(values),
            "profile": profile}


def select_scenarios(records):
    """Choose observed years using empirical ranks, not fabricated anomaly values."""
    if len(records) != len(YEARS) or {r["year"] for r in records} != set(YEARS):
        return None
    temperature = sorted(records, key=lambda r: (r["temperature_mean_c"], r["year"]))
    precipitation = sorted(records, key=lambda r: (r["precipitation_total_mm"], r["year"]))
    temp_rank = {r["year"]: i for i, r in enumerate(temperature)}
    rain_rank = {r["year"]: i for i, r in enumerate(precipitation)}
    midpoint = (len(records) - 1) / 2
    normal = min(records, key=lambda r: (max(abs(temp_rank[r["year"]] - midpoint), abs(rain_rank[r["year"]] - midpoint)),
                                          abs(temp_rank[r["year"]] - midpoint) + abs(rain_rank[r["year"]] - midpoint), r["year"]))
    selected = {"historical_normal": normal, "historical_dry": precipitation[0],
                "historical_hot": temperature[-1], "historical_wet": precipitation[-1]}
    baseline = {"period": {"start": f"{YEARS[0]}-01-01", "end": f"{YEARS[-1]}-12-31"},
                "complete_years": list(YEARS), "sample_size": len(records),
                "annual_temperature_median_c": median(r["temperature_mean_c"] for r in records),
                "annual_precipitation_median_mm": median(r["precipitation_total_mm"] for r in records),
                "annual_values": [{"year": r["year"], "mean_t2m_c": r["temperature_mean_c"],
                                   "precipitation_total_mm": r["precipitation_total_mm"],
                                   "power_response_sha256": r["profile"]["response_sha256"]} for r in sorted(records, key=lambda r: r["year"])],
                "method": "Ten complete observed calendar years, 2015–2024. Empirical ranks are relative to this sample, not a climatological normal or probability distribution."}
    classifications = {
        "historical_normal": "Observed year minimizing the largest absolute rank distance from the ten-year midpoint across annual mean T2M and annual PRECTOTCORR total; then smaller rank-distance sum; then earlier year.",
        "historical_dry": "Observed year with the lowest complete annual PRECTOTCORR total; earlier year breaks ties.",
        "historical_hot": "Observed year with the highest complete annual mean T2M; later year breaks ties.",
        "historical_wet": "Observed year with the highest complete annual PRECTOTCORR total; later year breaks ties.",
    }
    return selected, baseline, classifications, temp_rank, rain_rank


def activity_months(activity):
    first = int(activity["planting_window"]["start"][5:7])
    last = int(activity["harvest_window"]["end"][5:7])
    months, month = set(), first
    for _ in range(12):
        months.add(month)
        if month == last:
            return months
        month = month % 12 + 1
    return months


def annual_rainfall_reference(crop, record):
    fields = crop.get("annual_rainfall", {})
    keys = ("rainfall_min_mm", "rainfall_optimal_min_mm", "rainfall_optimal_max_mm", "rainfall_max_mm")
    if not all(usable(fields.get(key), "annual_rainfall_reference_comparison") for key in keys):
        return insufficient("Supported annual species rainfall requirements are unavailable")
    lo, opt_lo, opt_hi, hi = [fields[key]["normalized_value"] for key in keys]
    value = record["precipitation_total_mm"]
    category = "good_fit" if opt_lo <= value <= opt_hi else "acceptable" if lo <= value <= hi else "potential_concern"
    power = record["profile"]
    return {"status": "qualitative_screening", "value": category, "verification": "provisional", "crop_id": crop["id"],
            "annual_precipitation_mm": value,
            "crop_requirement_used": {key: fields[key]["normalized_value"] for key in keys},
            "environment_source": {"provider": "NASA POWER", "product": "daily point AG", "parameter": "PRECTOTCORR",
                                   "unit": "mm/day summed over a complete calendar year", "period": power["period"],
                                   "response_sha256": power["response_sha256"], "query": power["query"]},
            "method": "Complete POWER annual precipitation versus the existing published annual species envelope: optimum=good_fit; absolute=acceptable; outside=potential_concern.",
            "limitation": "Global annual species reference applied provisionally in Bangladesh; not crop-season rainfall, effective rainfall, irrigation need, flood risk or yield."}


def evaluate_candidate(candidate, crops, record):
    temperature, rainfall = [], []
    for activity in candidate["activities"]:
        crop = crops[activity["crop_id"]]
        temperature.append(climate(crop, record["profile"], activity_months(activity)))
        rainfall.append(annual_rainfall_reference(crop, record))
    components = temperature + rainfall
    if any(part["status"] == "insufficient_data" for part in components):
        return {"status": "insufficient_data", "value": None, "temperature": temperature,
                "annual_rainfall": rainfall, "reason": "At least one supported crop comparison lacks evidence; no stress interpretation was assigned.",
                "unsupported_dimensions": {key: insufficient(reason) for key, reason in UNSUPPORTED.items()}}
    return {"status": "qualitative_screening", "value": max((part["value"] for part in components), key=ORDER.get),
            "temperature": temperature, "annual_rainfall": rainfall,
            "method": "Most concerning supported crop temperature or complete annual rainfall reference category; no numerical loss or risk probability.",
            "unsupported_dimensions": {key: insufficient(reason) for key, reason in UNSUPPORTED.items()}}


def robustness(scenarios, candidates):
    results = {}
    for candidate in candidates:
        observed = {}
        for name in SCENARIOS:
            item = scenarios[name]
            interpretation = item.get("rotation_interpretation", {}).get(candidate["id"])
            if item["evidence_status"] != "supported" or not interpretation or interpretation["status"] == "insufficient_data":
                results[candidate["id"]] = {"status": "insufficient_data", "label": None,
                                            "reason": "All four historical scenarios need supported temperature and annual rainfall comparisons."}
                break
            observed.setdefault(item["selected_year"], []).append(interpretation["value"])
        else:
            concerning = sorted(year for year, values in observed.items() if "potential_concern" in values)
            label = "robust" if not concerning else "moderately_robust" if len(concerning) == 1 else "sensitive"
            results[candidate["id"]] = {"status": "supported", "label": label,
                                        "concerning_distinct_years": concerning,
                                        "rule": "All supported scenarios acceptable/good=robust; concern in one distinct observed year=moderately_robust; concern in two or more distinct observed years=sensitive. Shared scenario years count once; no probabilities."}
    supported = {key: item for key, item in results.items() if item["status"] == "supported"}
    best = []
    if supported:
        fewest = min(len(item["concerning_distinct_years"]) for item in supported.values())
        best = sorted(key for key, item in supported.items() if len(item["concerning_distinct_years"]) == fewest)
    return {"by_candidate": results, "most_robust_candidate_ids": best,
            "selection_rule": "All tied candidates with the fewest distinct concerning observed years are highlighted; no synthetic score or arbitrary tie-break."}


def build_stress_tests(latitude, longitude, provider, candidates, crops):
    records, failures = [], []
    for year in YEARS:
        try:
            profile = provider.profile(latitude, longitude, f"{year}-01-01", f"{year}-12-31")
            record = annual_record(profile, year, latitude, longitude)
        except Exception:
            record = None
        if record is None:
            failures.append(year)
        else:
            records.append(record)
    if failures:
        reason = "Complete NASA POWER daily T2M, T2M_MIN, T2M_MAX and PRECTOTCORR coverage is unavailable for baseline year(s): " + ", ".join(map(str, failures))
        scenarios = {name: {"evidence_status": "insufficient_data", "selected_year": None,
                            "environmental_conditions": None, "rotation_interpretation": {},
                            "provenance": {"provider": "NASA POWER", "baseline_period": {"start": "2015-01-01", "end": "2024-12-31"}},
                            "limitations": [reason, "Historical scenarios are unavailable; no values were invented."]} for name in SCENARIOS}
        return {**scenarios, "baseline": {"status": "insufficient_data", "missing_years": failures, "rule": "All ten complete annual POWER years are required."},
                "robustness": robustness(scenarios, candidates), "notice": "Historical observations, not a forecast."}
    selected, baseline, rules, temp_rank, rain_rank = select_scenarios(records)
    scenarios = {}
    for name in SCENARIOS:
        record = selected[name]
        power = record["profile"]
        scenarios[name] = {"evidence_status": "supported", "selected_year": record["year"],
                           "environmental_conditions": {"annual_mean_t2m_c": record["temperature_mean_c"],
                                                        "annual_precipitation_mm": record["precipitation_total_mm"],
                                                        "temperature_rank_low_to_high": temp_rank[record["year"]] + 1,
                                                        "precipitation_rank_low_to_high": rain_rank[record["year"]] + 1,
                                                        "sample_size": len(records), "classification_rule": rules[name],
                                                        "baseline_medians": {"annual_mean_t2m_c": baseline["annual_temperature_median_c"],
                                                                             "annual_precipitation_mm": baseline["annual_precipitation_median_mm"]}},
                           "rotation_interpretation": {candidate["id"]: evaluate_candidate(candidate, crops, record) for candidate in candidates},
                           "provenance": {"provider": "NASA POWER", "product": "daily point AG", "variables": list(PARAMETERS),
                                          "period": power["period"], "baseline_period": baseline["period"],
                                          "query": power["query"], "request_url": power["request_url"],
                                          "response_sha256": power["response_sha256"], "cache_status": power["cache_status"],
                                          "coverage": {key: power["coverage"][key] for key in PARAMETERS}},
                           "limitations": ["Observed year selected from a fixed ten-year local sample, not a forecast or formal climate normal.",
                                           "GPM IMERG and SMAP are not substituted for missing annual POWER observations; their limited validated windows do not support year-wide stress scoring.",
                                           "Annual global species rainfall envelopes and month-level crop occupancy are provisional; no irrigation, flood, crop-stage damage or yield claim."]}
    return {**scenarios, "baseline": {"status": "supported", **baseline},
            "robustness": robustness(scenarios, candidates), "notice": "Historical environmental scenarios, not a forecast or probability."}

"""Water Commons: compare declared irrigation plans, never infer demand from Kc or rain."""
from collections import defaultdict
from datetime import date, timedelta
import math
from ..knowledge.repository import load_dataset
from .month_generation import generate_months, month_end


class CommonsError(ValueError):
    pass


def options_for(plan, dataset=None):
    dataset = dataset or load_dataset("prototype_recommendation")
    candidates, _ = generate_months(dataset, plan)
    return [{"id": c["id"], "activities": [{"crop_id": a["crop_id"], "label": a["label"],
        "planting_window": a["planting_window"], "harvest_window": a["harvest_window"], "calendar_id": a["calendar_id"]}
        for a in c["activities"]], "hard_constraints": c["hard_constraints"]} for c in candidates]


def monday(day):
    return day - timedelta(days=day.weekday())


def weeks_between(start, end):
    week = monday(start)
    last = monday(end)
    while week <= last:
        yield week
        week += timedelta(days=7)


def _validated_farm(raw, dataset):
    choices = [c for c in options_for(raw["plan"], dataset) if c["id"] == raw["selected_rotation_id"]]
    if len(choices) != 1:
        raise CommonsError(f"{raw['farm_id']}: selected rotation is not a unique, currently eligible calendar/constraint-backed option")
    selected = choices[0]
    if any(check["status"] != "satisfied" for check in selected["hard_constraints"]):
        raise CommonsError(f"{raw['farm_id']}: selected rotation violates a farmer constraint")
    if len(raw["activities"]) != len(selected["activities"]):
        raise CommonsError(f"{raw['farm_id']}: supply one intended planting/harvest period per selected crop")
    activities = []
    previous_end = None
    numeric = True
    for index, (entry, crop) in enumerate(zip(raw["activities"], selected["activities"])):
        start = entry["planting_date"]
        end = entry["harvest_date"]
        if entry["crop_id"] != crop["crop_id"]:
            raise CommonsError(f"{raw['farm_id']}: activity {index + 1} does not match the selected rotation")
        p = crop["planting_window"]
        h = crop["harvest_window"]
        if not date.fromisoformat(p["start"] + "-01") <= start <= month_end(p["end"]):
            raise CommonsError(f"{raw['farm_id']}: planting date is outside the selected month window")
        if not date.fromisoformat(h["start"] + "-01") <= end <= month_end(h["end"]):
            raise CommonsError(f"{raw['farm_id']}: harvest date is outside the selected month window")
        if end <= start or (previous_end and start <= previous_end):
            raise CommonsError(f"{raw['farm_id']}: crop periods must be ordered without overlap")
        weeks = list(weeks_between(start, end))
        volumes = entry.get("weekly_irrigation_m3")
        if volumes is None and entry.get("schedule_complete"):
            events = entry.get("weekly_irrigation_events", [])
            event_map = {}
            for event in events:
                week = event["week_start"]
                if week.weekday() != 0 or week not in weeks or week in event_map or not math.isfinite(event["volume_m3"]) or event["volume_m3"] < 0:
                    raise CommonsError(f"{raw['farm_id']}: irrigation events must use unique occupied Monday weeks and nonnegative finite volumes")
                event_map[week] = event["volume_m3"]
            volumes = [event_map.get(week, 0.0) for week in weeks]
        if volumes is None:
            numeric = False
        elif len(volumes) != len(weeks) or any(not math.isfinite(v) or v < 0 for v in volumes):
            raise CommonsError(f"{raw['farm_id']}: supply one finite, nonnegative planned volume for each occupied Monday week")
        activities.append({**crop, "planting_date": start, "harvest_date": end,
            "duration_days": (end - start).days + 1, "weeks": weeks, "volumes": volumes,
            "timing_locked": entry.get("timing_locked", False),
            "water_provenance": {"basis": "farmer_entered_delivered_irrigation_plan" if volumes is not None else "insufficient_data",
                "source_title": entry.get("water_plan_source") or "Farmer-entered planning scenario" if volumes is not None else None,
                "crop_water_requirement": "insufficient_data", "rainfall_contribution": "not_subtracted",
                "calendar_id": crop["calendar_id"], "assumption": "Weekly volumes are planned delivered irrigation for the whole farm, not crop ET or NASA measurements. Omitted event weeks count as zero only where the farmer explicitly declared the schedule complete." if volumes is not None else "No complete numeric irrigation schedule supplied."}})
        previous_end = end
    limits = raw["plan"].get("constraints", {})
    if limits.get("earliest_planting") and activities[0]["planting_date"] < limits["earliest_planting"]:
        raise CommonsError(f"{raw['farm_id']}: intended planting violates the earliest planting constraint")
    if limits.get("latest_harvest") and activities[-1]["harvest_date"] > limits["latest_harvest"]:
        raise CommonsError(f"{raw['farm_id']}: intended harvest violates the latest harvest constraint")
    current = raw["plan"].get("current_crop")
    if current and activities[0]["planting_date"] <= current["harvest_date"]:
        raise CommonsError(f"{raw['farm_id']}: intended planting overlaps the current crop")
    return {"farm_id": raw["farm_id"], "farm_name": raw["farm_name"], "area_ha": raw["area_ha"], "plan": raw["plan"],
        "selected_rotation_id": selected["id"], "rotation": selected["activities"],
        "hard_constraints": selected["hard_constraints"], "flexibility_weeks": raw["flexibility_weeks"],
        "activities": activities, "numeric_complete": numeric}


def _dates_valid_for_shift(farm, shift_weeks):
    if any(a["timing_locked"] for a in farm["activities"]):
        return False
    delta = timedelta(days=shift_weeks * 7)
    for activity in farm["activities"]:
        start = activity["planting_date"] + delta
        end = activity["harvest_date"] + delta
        p, h = activity["planting_window"], activity["harvest_window"]
        if not (date.fromisoformat(p["start"] + "-01") <= start <= month_end(p["end"])):
            return False
        if not (date.fromisoformat(h["start"] + "-01") <= end <= month_end(h["end"])):
            return False
    limits = farm["plan"].get("constraints", {})
    first = farm["activities"][0]["planting_date"] + delta
    last = farm["activities"][-1]["harvest_date"] + delta
    if limits.get("earliest_planting") and first < limits["earliest_planting"]:
        return False
    if limits.get("latest_harvest") and last > limits["latest_harvest"]:
        return False
    current = farm["plan"].get("current_crop")
    if current and first <= current["harvest_date"]:
        return False
    return True


def _profile(farms, capacity, shifts=None):
    shifts = shifts or {}
    contributions = defaultdict(lambda: defaultdict(float))
    active = defaultdict(set)
    for farm in farms:
        delta = timedelta(days=7 * shifts.get(farm["farm_id"], 0))
        for activity in farm["activities"]:
            for index, week in enumerate(activity["weeks"]):
                day = week + delta
                active[day].add(farm["farm_id"])
                if activity["volumes"] is not None:
                    contributions[day][farm["farm_id"]] += activity["volumes"][index]
    complete = all(farm["numeric_complete"] for farm in farms)
    rows = []
    for week in sorted(active):
        by_farm = contributions.get(week, {}) if complete else {}
        total = math.fsum(by_farm.values()) if complete else None
        rows.append({"week_start": week.isoformat(), "active_farm_ids": sorted(active[week]),
            "contributing_farms": sorted(k for k, v in by_farm.items() if v > 0) if complete else [],
            "by_farm_m3": dict(sorted(by_farm.items())) if complete else None,
            "community_m3": total, "capacity_m3": capacity,
            "capacity_status": "exceeds_capacity" if total is not None and total > capacity else "within_capacity" if total is not None else "insufficient_data"})
    conflicts = [{"week_start": row["week_start"], "contributing_farms": row["contributing_farms"],
        "excess_m3": row["community_m3"] - capacity, "demand_m3": row["community_m3"],
        "capacity_m3": capacity, "ratio_to_capacity": row["community_m3"] / capacity,
        "evidence_status": "farmer_entered_plan", "assumption": "Delivered weekly irrigation volumes were entered by farmers; no rainfall was subtracted."}
        for row in rows if row["capacity_status"] == "exceeds_capacity"]
    peak = max((row["community_m3"] for row in rows if row["community_m3"] is not None), default=None)
    return {"status": "quantitative_plan_comparison" if complete else "qualitative_overlap_only",
        "rows": rows, "conflicts": conflicts, "peak_m3": peak,
        "excess_m3_total_across_weeks": math.fsum(c["excess_m3"] for c in conflicts) if complete else None,
        "total_planned_m3": math.fsum(row["community_m3"] for row in rows) if complete else None}


def analyze_community(data):
    dataset = load_dataset("prototype_recommendation")
    farms = [_validated_farm(farm, dataset) for farm in data["farms"]]
    ids = [farm["farm_id"] for farm in farms]
    if len(ids) != len(set(ids)):
        raise CommonsError("Farm identifiers must be unique")
    capacity = data["capacity_m3_per_week"]
    before = _profile(farms, capacity)
    suggestions = []
    if before["status"] == "quantitative_plan_comparison" and before["conflicts"]:
        for farm in farms:
            for delta in range(-farm["flexibility_weeks"], farm["flexibility_weeks"] + 1):
                if delta == 0 or not _dates_valid_for_shift(farm, delta):
                    continue
                after = _profile(farms, capacity, {farm["farm_id"]: delta})
                if after["excess_m3_total_across_weeks"] >= before["excess_m3_total_across_weeks"]:
                    continue
                suggestions.append({"type": "planting_window_shift", "farm_id": farm["farm_id"], "farm_name": farm["farm_name"],
                    "shift_weeks": delta, "changed_activity_dates": [{"crop_id": a["crop_id"], "planting_date": (a["planting_date"] + timedelta(days=7 * delta)).isoformat(),
                        "harvest_date": (a["harvest_date"] + timedelta(days=7 * delta)).isoformat()} for a in farm["activities"]],
                    "why_it_helps": "Moves the farmer-entered weekly irrigation schedule away from one or more shared-capacity conflicts.",
                    "trade_off": "All intended planting and harvest dates move; local field readiness and labor timing require the farmer's approval.",
                    "preserved_constraints": [c["constraint"] for c in farm["hard_constraints"] if c["status"] == "satisfied"],
                    "total_water_change_m3": 0.0, "before_peak_m3": before["peak_m3"], "after_peak_m3": after["peak_m3"],
                    "before_conflict_excess_m3": before["excess_m3_total_across_weeks"], "after_conflict_excess_m3": after["excess_m3_total_across_weeks"],
                    "adjusted_profile": after})
        suggestions.sort(key=lambda s: (s["after_conflict_excess_m3"], s["after_peak_m3"], abs(s["shift_weeks"]), s["farm_id"], s["shift_weeks"]))
        suggestions = suggestions[:5]
    qualitative_overlap = [{"week_start": row["week_start"], "active_farm_ids": row["active_farm_ids"],
        "meaning": "Overlapping crop periods only; irrigation demand and capacity conflict are unknown."}
        for row in before["rows"] if len(row["active_farm_ids"]) > 1] if before["status"] == "qualitative_overlap_only" else []
    return {"group_name": data["group_name"], "capacity": {"value": capacity, "unit": "m3/week", "time_resolution": "Monday-starting calendar week",
        "source_title": data.get("capacity_source") or "Group-entered shared irrigation capacity"},
        "farms": [{"farm_id": f["farm_id"], "farm_name": f["farm_name"], "area_ha": f["area_ha"],
            "selected_rotation_id": f["selected_rotation_id"], "rotation": f["rotation"], "hard_constraints": f["hard_constraints"],
            "flexibility_weeks": f["flexibility_weeks"], "demand_evidence_status": "farmer_entered_plan" if f["numeric_complete"] else "insufficient_data",
            "activity_provenance": [{"crop_id": a["crop_id"], "planting_date": a["planting_date"].isoformat(), "harvest_date": a["harvest_date"].isoformat(),
                "duration_days": a["duration_days"], "water_evidence": a["water_provenance"]} for a in f["activities"]]} for f in farms],
        "original_profile": before, "conflict_windows": before["conflicts"], "qualitative_overlap_windows": qualitative_overlap,
        "suggested_adjustments": suggestions, "adjusted_profile": suggestions[0]["adjusted_profile"] if suggestions else None,
        "before_after_peak": {"before_m3": before["peak_m3"], "after_m3": suggestions[0]["after_peak_m3"] if suggestions else None,
            "total_water_change_m3": 0.0 if suggestions else None},
        "evidence_confidence": "farmer_plan_only" if before["status"] == "quantitative_plan_comparison" else "insufficient_data",
        "limitations": ["Crop-water requirement and irrigation requirement are not inferred from the existing FAO Kc rows or NASA rainfall/moisture.",
            "Farmer-entered weekly volumes are planning assumptions for delivered irrigation, not measured withdrawals or scientifically validated crop demand.",
            "A timing shift preserves each supplied weekly volume and total; it can reduce simultaneous peak load but does not by itself save water.",
            "No alternative crop/rotation receives a water benefit without its own supported or farmer-entered volume schedule.",
            "This is weekly schedule arithmetic, not a hydraulic, groundwater, rainfall-runoff or field-water simulation."]}

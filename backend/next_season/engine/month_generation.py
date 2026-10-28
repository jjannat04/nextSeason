"""Conservative month-envelope scheduling; no fabricated maturity/turnaround days."""
import calendar
from datetime import date, timedelta
from ..knowledge.repository import usable
from .constraints import check_plan


def month_start(value):
    return date.fromisoformat(value + "-01")


def month_end(value):
    first = month_start(value)
    return first.replace(day=calendar.monthrange(first.year, first.month)[1])


def eligible_crop(crop):
    fields = [crop.get("temperature", {}).get(k) for k in ("temp_optimal_min_c", "temp_optimal_max_c", "temp_absolute_min_c", "temp_absolute_max_c")]
    fields += [crop.get("soil_ph", {}).get(k) for k in ("soil_ph_opt_min", "soil_ph_opt_max")]
    return crop.get("prototype_eligible") and any(usable(c, "prototype_recommendation") for c in crop.get("calendars", [])) and all(usable(f, "prototype_recommendation") for f in fields)


def generate_months(dataset, request, today=None):
    today = today or date.today()
    crops = {c["id"]: c for c in dataset["crops"] if eligible_crop(c)}
    rules = {(r["previous"], r["next"]): r for r in dataset["rotation_rules"] if usable(r, "prototype_recommendation") and r.get("compatibility_class") not in ("unresolved", None)}
    if len(crops) < 3:
        return [], [{"reason": "Fewer than three crops have usable required evidence"}]
    current = request.get("current_crop")
    previous = (current or {}).get("crop_id") or (request.get("crop_history") or [None])[-1]
    end = date.fromisoformat(current["harvest_date"]) if current else today
    limits = request.get("constraints", {})
    candidates, rejected = [], []
    horizon = request.get("horizon", 3)
    cutoff_year = today.year + 4  # bounded search, not an agronomic duration claim

    def visit(activities, prev, occupied, trace):
        if len(activities) == horizon:
            checks = check_plan(activities, request)
            if any(c["status"] == "violated" for c in checks):
                rejected.append({"crop_ids": [a["crop_id"] for a in activities], "checks": checks})
                return
            candidates.append({"id": "rotation-" + "-".join(a["crop_id"] for a in activities),
                "activities": activities, "hard_constraints": checks, "sequence_evidence": trace,
                "scheduling_precision": "conservative_month_envelopes"})
            return
        for crop in crops.values():
            if crop["id"] in limits.get("excluded_crop_ids", []):
                continue
            if limits.get("locked_slots", {}).get(str(len(activities)), crop["id"]) != crop["id"]:
                continue
            rule = rules.get((prev, crop["id"])) if prev else None
            # This search enumerates documented systems, not a universal pair filter.
            if prev and not rule:
                continue
            for evidence in crop["calendars"]:
                if not usable(evidence, "prototype_recommendation"):
                    continue
                m = evidence["months"]
                for year in range(today.year, cutoff_year + 1):
                    first = date(year, m["planting_start_month"], 1)
                    last = month_end(f"{year:04}-{m['planting_end_month']:02}")
                    lower = max(today + timedelta(days=1), occupied + timedelta(days=1), date.fromisoformat(limits.get("earliest_planting", today.isoformat())))
                    # Retain complete future months only. Never translate 'mid' to day 15.
                    while first < lower and first <= last:
                        first = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
                    if first > last:
                        continue
                    harvest_first_year = year + int(m["harvest_start_month"] < m["planting_start_month"])
                    harvest_first = date(harvest_first_year, m["harvest_start_month"], 1)
                    harvest_last = month_end(f"{year + m['harvest_end_year_offset']:04}-{m['harvest_end_month']:02}")
                    if harvest_first <= last or harvest_last.year > cutoff_year:
                        continue
                    if limits.get("latest_harvest") and harvest_last > date.fromisoformat(limits["latest_harvest"]):
                        continue
                    planting = {"start": first.strftime("%Y-%m"), "end": last.strftime("%Y-%m")}
                    harvest = {"start": harvest_first.strftime("%Y-%m"), "end": harvest_last.strftime("%Y-%m")}
                    idle = max(0, (first.year - occupied.year) * 12 + first.month - occupied.month - 1)
                    activity = {"crop_id": crop["id"], "label": crop["label"],
                        "planting": planting["start"] + " to " + planting["end"],
                        "harvest": harvest["start"] + " to " + harvest["end"],
                        "planting_window": planting, "harvest_window": harvest,
                        "calendar_id": evidence["id"], "calendar_evidence": evidence,
                        "sequence_rule_id": rule["id"] if rule else None,
                        "idle_before": {"whole_months": idle, "after": occupied.isoformat() if not activities else activities[-1]["harvest_window"]["end"],
                            "before": planting["start"], "meaning": "Uncropped interval in this option; not a prescribed biological minimum gap"},
                        "timing_limitation": "Broad month envelopes; mid/late/early source qualifiers retained. Field readiness and turnaround require local checking."}
                    visit(activities + [activity], crop["id"], harvest_last, trace + ([rule] if rule else []))
                    break  # earliest conservative occurrence, no hidden later-date optimization
    visit([], previous, end, [])
    return candidates, rejected
